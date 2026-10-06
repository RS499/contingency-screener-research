import os
import sys
import json
import time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import make_splits as ms
import gate_eval as ge
import baselines as bl
import tune_surrogates as tu
import manifest as mf
import sts_manifest as sm
import n9_budget_curve as bc
import n12_condhist as ch
import n12_guarantee as gu
import n12_crossnet as cx
import n14_common as cm

# N14 analyses (scratch/n14_decision_rule.md §A, §B), on the rebuilt N13 datasets with outages removed per mode.
# argv[1]:
#   condhist   primary fixed-budget static, COND-HIST, GLOBAL-STATIC (N12 Part A run_split) for ILL (trafo 63 removed)
#              and C24; D94 and C30 restated from data/sts_n13_condhist.json (hash-checked in Step 2)
#   guarantee  primary price of a guarantee (N12 Part B) for ILL; D94 restated from data/sts_n13_guarantee.json
#   crossnet   primary cross-network table (N12 Part C): ILL and C24 computed; D94 and C30 restated
#   sensitivity  every islanding outage removed: COND-HIST etc. on the sensitivity data with the sensitivity gates;
#              assembles held-out gate numbers, BEATS-STATIC and GATE-BEATS-CONDHIST inputs per network
#   islsplit   descriptive: catch of gate, fixed-budget static and COND-HIST on islanding vs non-islanding rows
# Each writes data/sts_n14_<analysis>.json + manifest.

WHICH = sys.argv[1] if len(sys.argv) > 1 else "condhist"
SEEDS = [0, 1, 2, 3, 4]
LIMIT = 0.94


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def gate_path(name, mode):
    if mode == "sensitivity":
        return f"data/sts_n14_gate_{name}_sens.json"
    if name in ("D94", "C30"):
        return f"data/sts_n13_gate_{name}.json"
    return f"data/sts_n14_gate_{name}.json"


def held(gj, fam):
    out = {}
    for p in gj["points"]:
        if p["family"] == fam and p["point"] == "held_out":
            out[int(p["seed"])] = p
    return out


def fit_of(gj, seed, fam):
    for f in gj["fits"]:
        if f["seed"] == seed and f["family"] == fam:
            return f
    return None


def write(name, out, inputs, params):
    path = f"data/sts_n14_{name}.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    man = sm.build_manifest([path], "scratch/n14_analyses.py", [".venv/bin/python", "scratch/n14_analyses.py", WHICH],
                            sorted(set(inputs + [cm.RULE])), params, "")
    man["no_new_solves"] = "No AC solve."
    sm.write_manifest(man, path)
    print(f"wrote {path}", flush=True)


def condhist_for(name, mode):
    d = cm.load(name, mode)
    gj = json.load(open(gate_path(name, mode)))
    pts = held(gj, "histgb")
    per = [ch.run_split(d, s, pts[s]) for s in SEEDS]
    s = {}
    for k in ["gate_catch", "static_fixed_catch", "condhist_catch", "global_static_catch", "s_B"]:
        s[k + "_mean"], s[k + "_std"] = ms_([r[k] for r in per])
    return dict(per_split=per, summary=s, removed=d["info"]["removed_outages"], n_rows_removed=d["info"]["n_rows_removed"])


def a_condhist():
    old = json.load(open("data/sts_n13_condhist.json"))["networks"]
    res = {}
    for name in ["D94", "C30"]:
        res[name] = dict(restated_from="data/sts_n13_condhist.json", summary=old[name]["summary"], per_split=old[name]["per_split"])
    for name in ["ILL", "C24"]:
        res[name] = condhist_for(name, "primary")
        s = res[name]["summary"]
        print(f"{name}: gate {100 * s['gate_catch_mean']:.2f} static {100 * s['static_fixed_catch_mean']:.2f} cond {100 * s['condhist_catch_mean']:.2f}", flush=True)
    write("condhist", dict(analysis="N12 Part A procedure, N14 primary", networks=res),
          ["data/sts_n13_condhist.json", "data/sts_n13_ILL.parquet", "data/sts_n13_C24.parquet", "data/sts_n14_gate_ILL.json", "data/sts_n14_gate_C24.json"],
          dict(seeds=SEEDS, bins=ch.N_BINS, smoothing=ch.A_SMOOTH, model_hyperparameters="none (lookup table); gates from the listed gate files"))


def a_guarantee():
    ms_solver = mf.load_solve_time()["ms_solver"]
    old = json.load(open("data/sts_n13_guarantee.json"))["networks"]
    res = dict(D94=dict(restated_from="data/sts_n13_guarantee.json", **old["D94"]))
    d = cm.load("ILL", "primary")
    gj = json.load(open(gate_path("ILL", "primary")))
    res["ILL"] = {}
    for fam in ["histgb", "ridge"]:
        pts = held(gj, fam)
        per = []
        for seed in SEEDS:
            f = fit_of(gj, seed, fam)
            splits = ms.make_splits(d["groups"], seed)
            kept = ms.select_features(d["X"], splits["train"])
            Xk = d["X"][kept]
            fitted = tu.fit_one(fam, f["config"], Xk.iloc[splits["train"]].to_numpy(np.float32), d["y"][splits["train"]], seed)
            ca, te = splits["cal"], splits["test"]
            p_ca = tu.predict(fitted, Xk.iloc[ca].to_numpy(np.float32))
            p_te = tu.predict(fitted, Xk.iloc[te].to_numpy(np.float32))
            y_ca, y_te = d["y"][ca], d["y"][te]
            sc_ca = d["df"]["scenario_id"].to_numpy(np.int64)[ca]
            sc_te = d["df"]["scenario_id"].to_numpy(np.int64)[te]
            p = pts[seed]
            q = ge.calibrate_qhat(p_ca, y_ca, p["target"])
            glob = gu.gate_metrics(p_te, y_te, sc_te, q, f["ms_surrogate"], ms_solver)
            if glob["escalation"] != p["escalation"] or glob["missed"] != p["missed"]:
                raise SystemExit("guarantee: refit does not reproduce the N14 ILL gate; stop this analysis")
            v = y_ca < LIMIT
            t_row, _n, _k = gu.kth(p_ca[v] - LIMIT, gu.ALPHA_ROW)
            mb = pd.Series(p_ca[v] - LIMIT).groupby(sc_ca[v]).max().to_numpy()
            t_base, _n2, _k2 = gu.kth(mb, gu.ALPHA_BASE)
            per.append(dict(seed=seed, global_gate=glob, row_level=gu.gate_metrics(p_te, y_te, sc_te, t_row, f["ms_surrogate"], ms_solver),
                            base_level=gu.gate_metrics(p_te, y_te, sc_te, t_base, f["ms_surrogate"], ms_solver)))
        summ = {}
        for cal in ["global_gate", "row_level", "base_level"]:
            summ[cal] = {}
            for k in ["t", "escalation", "flag_share", "missed", "any_miss_share", "speedup_A", "speedup_B"]:
                summ[cal][k + "_mean"], summ[cal][k + "_std"] = ms_([r[cal][k] for r in per])
        summ["base_level"]["splits_any_miss_le_alpha"] = len([r for r in per if r["base_level"]["any_miss_share"] <= gu.ALPHA_BASE])
        res["ILL"][fam] = dict(per_split=per, summary=summ)
        print(f"ILL {fam}: base any-miss {100 * summ['base_level']['any_miss_share_mean']:.1f}", flush=True)
    write("guarantee", dict(analysis="N12 Part B procedure, N14 primary", networks=res, alpha_row=gu.ALPHA_ROW, alpha_base=gu.ALPHA_BASE),
          ["data/sts_n13_guarantee.json", "data/sts_n13_ILL.parquet", "data/sts_n14_gate_ILL.json"],
          dict(seeds=SEEDS, model_hyperparameters="M2 configs from data/sts_n14_gate_ILL.json"))


def a_crossnet():
    old = {r["network"]: r for r in json.load(open("data/sts_n13_crossnet.json"))["table"]}
    chn = json.load(open("data/sts_n14_condhist.json"))["networks"]
    rows = []
    for name in ["D94", "ILL", "C30", "C24"]:
        if name in ("D94", "C30"):
            r = dict(old[name])
            r["restated_from"] = "data/sts_n13_crossnet.json"
            rows.append(r)
            continue
        d = cm.load(name, "primary")
        y = d["y"]
        viol = y < LIMIT
        scen = d["df"]["scenario_id"].to_numpy(np.int64)
        spread, conc = [], []
        for seed in SEEDS:
            sp = ms.make_splits(d["groups"], seed)
            te = sp["test"]
            spread.append(float(pd.Series(viol[te].astype(float)).groupby(scen[te]).mean().std(ddof=0)))
            conc.append(cx.top_share(viol, d["elem_key"], sp["train"], te))
        r = dict(network=name, n_rows=int(len(y)), boundary_mass=float(((y >= LIMIT) & (y < 0.945)).mean()), violation_rate=float(viol.mean()))
        r["risk_spread_mean"], r["risk_spread_std"] = ms_(spread)
        r["top10_concentration_mean"], r["top10_concentration_std"] = ms_(conc)
        for k in ["gate_catch", "static_fixed_catch", "condhist_catch", "global_static_catch"]:
            r[k + "_mean"] = chn[name]["summary"][k + "_mean"]
            r[k + "_std"] = chn[name]["summary"][k + "_std"]
        rows.append(r)
    write("crossnet", dict(analysis="N12 Part C procedure, N14 primary (n = 4, no law claimed)", table=rows),
          ["data/sts_n13_crossnet.json", "data/sts_n14_condhist.json", "data/sts_n13_ILL.parquet", "data/sts_n13_C24.parquet"],
          dict(seeds=SEEDS, top_n=cx.TOP, model_hyperparameters="none here"))


def a_sensitivity():
    res = {}
    for name in ["D94", "ILL", "C30", "C24"]:
        gp = gate_path(name, "sensitivity")
        if not os.path.exists(gp):
            res[name] = "not run"
            continue
        gj = json.load(open(gp))
        h = [held(gj, "histgb")[s] for s in SEEDS]
        g = {}
        for k in ["target", "escalation", "missed", "speedup_A", "speedup_B", "gate_catch", "static_catch_B", "solve_share_B"]:
            g[k + "_mean"], g[k + "_std"] = ms_([p[k] for p in h])
        g["missed_per_split"] = [p["missed"] for p in h]
        chs = condhist_for(name, "sensitivity")
        res[name] = dict(held_out_histgb=g, condhist=chs, removed=chs["removed"], n_rows_removed=chs["n_rows_removed"])
        print(f"{name} sens: gate {100 * g['gate_catch_mean']:.2f} static {100 * g['static_catch_B_mean']:.2f} cond "
              f"{100 * chs['summary']['condhist_catch_mean']:.2f}", flush=True)
    write("sensitivity", dict(analysis="N14 sensitivity: every islanding outage removed", networks=res),
          [gate_path(n, "sensitivity") for n in ["D94", "ILL", "C30", "C24"] if os.path.exists(gate_path(n, "sensitivity"))]
          + [f"data/sts_n13_{n}.parquet" for n in ["D94", "ILL", "C30", "C24"]],
          dict(seeds=SEEDS, model_hyperparameters="from the sensitivity gate files"))


def condhist_scores(d, seed):
    # the COND-HIST score of scratch/n12_condhist.py run_split, returned per test row (same code path)
    splits = ms.make_splits(d["groups"], seed)
    tr, te = splits["train"], splits["test"]
    df = d["df"]
    ek = d["elem_key"]
    viol_all = d["y"] < LIMIT
    margin = df["n0_min_vm"].to_numpy(np.float64) - LIMIT
    scen_all = df["scenario_id"].to_numpy(np.int64)
    tr_base = pd.Series(margin[tr], index=scen_all[tr]).groupby(level=0).first()
    edges = np.quantile(tr_base.to_numpy(), ch.QUANTILES)
    bins = np.searchsorted(edges, margin, side="right")
    t = pd.DataFrame(dict(e=ek[tr], b=bins[tr], v=viol_all[tr].astype(float)))
    f = t.groupby("e")["v"].mean()
    cell = t.groupby(["e", "b"])["v"].agg(["sum", "count"])
    f_te = f.reindex(ek[te]).fillna(0.0).to_numpy()
    idx = pd.MultiIndex.from_arrays([ek[te], bins[te]])
    v_te = cell["sum"].reindex(idx).fillna(0.0).to_numpy()
    n_te = cell["count"].reindex(idx).fillna(0.0).to_numpy()
    return (v_te + ch.A_SMOOTH * f_te) / (n_te + ch.A_SMOOTH)


def catch_on(solved, viol, mask):
    nv = int((viol & mask).sum())
    return float((solved & viol & mask).sum() / nv) if nv else None


def a_islsplit():
    res = {}
    for name in ["D94", "ILL", "C30", "C24"]:
        d = cm.load(name, "primary")
        gj = json.load(open(gate_path(name, "primary")))
        isl = cm.islanding_mask(name, d["df"])
        pts = held(gj, "histgb")
        per = []
        for seed in SEEDS:
            f = fit_of(gj, seed, "histgb")
            p = pts[seed]
            splits = ms.make_splits(d["groups"], seed)
            kept = ms.select_features(d["X"], splits["train"])
            te = splits["test"]
            Xte = d["X"][kept].iloc[te].to_numpy(np.float32)
            p_ca, y_ca, p_te = bc.fit_predict(d, seed, "histgb", f["config"], Xte, kept)
            y_te = d["y"][te]
            g = bc.gate_point(p_ca, y_ca, p_te, y_te, p["target"])
            if g["missed"] != p["missed"]:
                raise SystemExit(f"islsplit: refit does not reproduce the gate for {name} seed {seed}; stop this analysis")
            viol = y_te < LIMIT
            m_isl = isl[te]
            gate_solved = ~((p_te - g["q_hat"]) >= LIMIT)
            scen = d["df"]["scenario_id"].to_numpy(np.int64)[te]
            ek = d["elem_key"][te]
            tm = np.zeros(len(d["df"]), dtype=bool)
            tm[splits["train"]] = True
            stat, _ = bl.static_severity_score(d["df"], tm, d["elem_key"])
            order = bl.within_scenario_order(scen, stat[te], ek.astype(float))
            rank = np.empty(len(order), dtype=np.int64)
            _u, starts, counts = bl.scenario_offsets(scen[order])
            rank[order] = np.arange(len(order)) - np.repeat(starts, counts)
            static_solved = rank < int(p["k_B"])
            sc = condhist_scores(d, seed)
            n_solve = int(round(float(p["solve_share_B"]) * len(te)))
            top = np.lexsort((scen, ek, -sc))[:n_solve]
            cond_solved = np.zeros(len(te), dtype=bool)
            cond_solved[top] = True
            per.append(dict(seed=seed, n_isl_test_viol=int((viol & m_isl).sum()), n_non_test_viol=int((viol & ~m_isl).sum()),
                            gate_isl=catch_on(gate_solved, viol, m_isl), gate_non=catch_on(gate_solved, viol, ~m_isl),
                            static_isl=catch_on(static_solved, viol, m_isl), static_non=catch_on(static_solved, viol, ~m_isl),
                            cond_isl=catch_on(cond_solved, viol, m_isl), cond_non=catch_on(cond_solved, viol, ~m_isl)))
        s = {}
        for k in ["gate_isl", "gate_non", "static_isl", "static_non", "cond_isl", "cond_non"]:
            vals = [r[k] for r in per if r[k] is not None]
            s[k + "_mean"], s[k + "_std"] = ms_(vals) if vals else (None, None)
        res[name] = dict(per_split=per, summary=s, n_islanding_outages_kept=int(len(set(zip(d["df"]["outaged_type"][isl], d["df"]["outaged_idx"][isl])))))
        print(f"{name}: " + " ".join([f"{k} {100 * s[k + '_mean']:.2f}" for k in ["gate_isl", "gate_non", "static_isl", "static_non", "cond_isl", "cond_non"]
                                       if s[k + "_mean"] is not None]), flush=True)
    write("islanding_split", dict(analysis="N14 descriptive: catch on islanding vs non-islanding rows, primary, histgb held-out", networks=res),
          [gate_path(n, "primary") for n in ["D94", "ILL", "C30", "C24"]] + [f"data/sts_n13_{n}.parquet" for n in ["D94", "ILL", "C30", "C24"]],
          dict(seeds=SEEDS, model_hyperparameters="M2 configs from the primary gate files (refit, no search)"))


def main():
    t0 = time.time()
    cm.check_hash()
    if WHICH == "condhist":
        a_condhist()
    elif WHICH == "guarantee":
        a_guarantee()
    elif WHICH == "crossnet":
        a_crossnet()
    elif WHICH == "sensitivity":
        a_sensitivity()
    elif WHICH == "islsplit":
        a_islsplit()
    else:
        raise SystemExit(f"unknown analysis {WHICH}")
    print(f"wall {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
