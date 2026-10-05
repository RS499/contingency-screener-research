import os
import sys
import json
import time
import hashlib
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
import n5_gate_eval as n5
import n9_budget_curve as bc
import n11_n2_eval as n2e
import n12_condhist as ch
import n12_guarantee as gu
import n12_crossnet as cx

# N13 Step 4, arm S analyses (scratch/n13_decision_rule.md §3, tier-A rows), each through the original procedure with
# only input paths changed: the rebuilt datasets (data/sts_n13_<name>.parquet, labels = their own corrected min_vm)
# and the rebuilt gate results (data/sts_n13_gate_<name>.json: M2 configs, held-out targets, per-split points).
# argv[1] = analysis: condhist | budget | guarantee | crossnet | mondrian | floor | n2 | classical
# Each writes data/sts_n13_<analysis>.json + manifest. Where an original script is a single main() with hardcoded
# paths, its loop is reproduced here calling the same imported functions (rule 4: thin wrapper, nothing edited).

WHICH = sys.argv[1] if len(sys.argv) > 1 else "condhist"
LIMIT = 0.94
SEEDS = [0, 1, 2, 3, 4]
N_LINE = {"D94": 173, "D95a": 173, "D95b": 173, "D95c": 173, "ILL": 179, "C30": 41, "C24": 33, "D93": 173, "D96": 173}
N_BRANCH = {"D94": 186, "D95a": 186, "ILL": 245, "C30": 41, "C24": 38}
TIER_A_NETS = ["D94", "ILL", "C30", "C24"]
RULE = "scratch/n13_decision_rule.md"
RULE_SHA = "scratch/n13_decision_rule.sha256"


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def check_hash():
    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    return h


def load(name):
    df, feature_cols, info = n5.load_relabeled(f"data/sts_n13_{name}.parquet", "")
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    is_trafo = df["outaged_type"].to_numpy() == "trafo"
    ek = df["outaged_idx"].to_numpy(np.int64) + np.where(is_trafo, N_LINE[name], 0)
    return dict(name=name, df=df, X=X, y=y, groups=groups, elem_key=ek, info=info)


def gate(name):
    return json.load(open(f"data/sts_n13_gate_{name}.json"))


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


def available(names):
    return [n for n in names if os.path.exists(f"data/sts_n13_gate_{n}.json") and os.path.exists(f"data/sts_n13_{n}.parquet")]


def write(name, out, inputs, params):
    path = f"data/sts_n13_{name}.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    man = sm.build_manifest([path], "scratch/n13_analyses.py", [".venv/bin/python", "scratch/n13_analyses.py", WHICH],
                            inputs + [RULE], params, "")
    man["no_new_solves"] = "No AC solve unless stated in the output."
    sm.write_manifest(man, path)
    print(f"wrote {path}", flush=True)


def gate_hyper(names):
    hp = {}
    for n in names:
        hp[n] = [dict(seed=f["seed"], family=f["family"], tag=f["tag"], config=f["config"]) for f in gate(n)["fits"]]
    return hp


# ------------------------------------------------------------------ COND-HIST, GLOBAL-STATIC, fixed static (N12 A)

def a_condhist():
    nets = available(TIER_A_NETS)
    res = {}
    for name in nets:
        d = load(name)
        pts = held(gate(name), "histgb")
        per = [ch.run_split(d, s, pts[s]) for s in SEEDS]
        s = {}
        for k in ["gate_catch", "static_fixed_catch", "condhist_catch", "global_static_catch", "s_B"]:
            s[k + "_mean"], s[k + "_std"] = ms_([r[k] for r in per])
        res[name] = dict(per_split=per, summary=s)
        print(f"{name}: gate {100 * s['gate_catch_mean']:.2f} static {100 * s['static_fixed_catch_mean']:.2f} cond "
              f"{100 * s['condhist_catch_mean']:.2f} global {100 * s['global_static_catch_mean']:.2f}", flush=True)
    write("condhist", dict(analysis="N12 Part A procedure on rebuilt data", networks=res, settings=dict(
        smoothing_a=ch.A_SMOOTH, n_bins=ch.N_BINS, quantiles=ch.QUANTILES)),
        [f"data/sts_n13_{n}.parquet" for n in nets] + [f"data/sts_n13_gate_{n}.json" for n in nets],
        dict(seeds=SEEDS, bins=ch.N_BINS, smoothing=ch.A_SMOOTH, model_hyperparameters="none: lookup table; gate from data/sts_n13_gate_<net>.json"))


# ------------------------------------------------------------------ budget curve (N9 Part 1) on D94

def a_budget(name):
    gj = gate(name)
    d = load(name)
    repro, per_seed, curves = [], [], []
    for seed in SEEDS:
        splits = ms.make_splits(d["groups"], seed)
        kept = ms.select_features(d["X"], splits["train"])
        te = splits["test"]
        Xte = d["X"][kept].iloc[te].to_numpy(np.float32)
        y_te = d["y"][te]
        scen = d["df"]["scenario_id"].to_numpy(np.int64)[te]
        viol = y_te < LIMIT
        tb = d["elem_key"][te].astype(float)
        tm = np.zeros(len(d["df"]), dtype=bool)
        tm[splits["train"]] = True
        stat, _ = bl.static_severity_score(d["df"], tm, d["elem_key"])
        c_static, _, _ = bl.capture_curve(scen, stat[te], tb, viol, bc.K_MAX)
        c_oracle, _, _ = bl.capture_curve(scen, y_te, tb, viol, bc.K_MAX)
        for fam in ["ridge", "histgb"]:
            f = fit_of(gj, seed, fam)
            p_ca, y_ca, p_te = bc.fit_predict(d, seed, fam, f["config"], Xte, kept)
            mae, r2 = tu.mae_r2(p_te, y_te)
            h = held(gj, fam)[seed]
            g = bc.gate_point(p_ca, y_ca, p_te, y_te, h["target"])
            ok = bool(mae == f["mae"] and g["escalation"] == h["escalation"] and g["missed"] == h["missed"])
            repro.append(dict(seed=seed, family=fam, exact=ok))
            if not ok:
                raise SystemExit(f"budget: refit does not reproduce the rebuilt gate (seed {seed} {fam}); stop this analysis")
            c_surr, _, _ = bl.capture_curve(scen, p_te, tb, viol, bc.K_MAX)
            row = dict(seed=seed, family=fam)
            for k in bc.K_DECLARED:
                row[f"surr_{k}"] = float(c_surr[k - 1])
                row[f"static_{k}"] = float(c_static[k - 1])
                row[f"oracle_{k}"] = float(c_oracle[k - 1])
            per_seed.append(row)
            curves.append(dict(seed=seed, family=fam, surr=c_surr.tolist(), static=c_static.tolist(), oracle=c_oracle.tolist()))
    ps = pd.DataFrame(per_seed)
    table = []
    for fam in ["ridge", "histgb"]:
        m = ps[ps.family == fam]
        cross = None
        rows = []
        for k in bc.K_DECLARED:
            r = dict(family=fam, k=k)
            for kind in ["surr", "static", "oracle"]:
                r[kind + "_mean"], r[kind + "_std"] = ms_(m[f"{kind}_{k}"])
            r["verdict"] = bc.verdict(m[f"surr_{k}"], m[f"static_{k}"])
            if cross is None and r["verdict"] != "SURR higher":
                cross = k
            rows.append(r)
        for r in rows:
            r["crossover_k"] = cross
        table.extend(rows)
    for r in table:
        print(f"{r['family']} k={r['k']}: SURR {100 * r['surr_mean']:.2f} STATIC {100 * r['static_mean']:.2f} [{r['verdict']}]", flush=True)
    write("budget" if name == "D94" else f"budget_{name}", dict(analysis=f"N9 Part 1 procedure on rebuilt {name}", k_declared=bc.K_DECLARED,
                                                              reproduction=repro, table=table, per_seed=per_seed, curves=curves),
          [f"data/sts_n13_{name}.parquet", f"data/sts_n13_gate_{name}.json"],
          dict(seeds=SEEDS, k_declared=bc.K_DECLARED, model_hyperparameters=gate_hyper([name])))


# ------------------------------------------------------------------ price of a guarantee (N12 Part B) on D94, ILL

def a_guarantee():
    ms_solver = mf.load_solve_time()["ms_solver"]
    nets = available(["D94", "ILL"])
    res = {}
    for name in nets:
        gj = gate(name)
        d = load(name)
        res[name] = {}
        for fam in ["histgb", "ridge"]:
            pts = held(gj, fam)
            per = []
            stop = None
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
                scen_ca = d["df"]["scenario_id"].to_numpy(np.int64)[ca]
                scen_te = d["df"]["scenario_id"].to_numpy(np.int64)[te]
                p = pts[seed]
                q = ge.calibrate_qhat(p_ca, y_ca, p["target"])
                glob = gu.gate_metrics(p_te, y_te, scen_te, q, f["ms_surrogate"], ms_solver)
                if glob["escalation"] != p["escalation"] or glob["missed"] != p["missed"]:
                    stop = dict(seed=seed)
                    break
                v_ca = y_ca < LIMIT
                t_row, n_v, k_v = gu.kth(p_ca[v_ca] - LIMIT, gu.ALPHA_ROW)
                mb = pd.Series(p_ca[v_ca] - LIMIT).groupby(scen_ca[v_ca]).max().to_numpy()
                t_base, n_b, k_b = gu.kth(mb, gu.ALPHA_BASE)
                per.append(dict(seed=seed, target=float(p["target"]), global_gate=glob,
                                row_level=dict(gu.gate_metrics(p_te, y_te, scen_te, t_row, f["ms_surrogate"], ms_solver), n_cal_violation_rows=n_v),
                                base_level=dict(gu.gate_metrics(p_te, y_te, scen_te, t_base, f["ms_surrogate"], ms_solver), n_cal_bases_with_violation=n_b)))
            if stop is not None:
                res[name][fam] = dict(stopped="refit does not reproduce the rebuilt gate", detail=stop)
                continue
            summ = {}
            for cal in ["global_gate", "row_level", "base_level"]:
                summ[cal] = {}
                for k in ["t", "escalation", "flag_share", "missed", "any_miss_share", "speedup_A", "speedup_B", "overlap_certify_and_flag"]:
                    summ[cal][k + "_mean"], summ[cal][k + "_std"] = ms_([r[cal][k] for r in per])
            summ["base_level"]["splits_any_miss_le_alpha"] = len([r for r in per if r["base_level"]["any_miss_share"] <= gu.ALPHA_BASE])
            summ["row_level"]["splits_missed_le_alpha"] = len([r for r in per if r["row_level"]["missed"] <= gu.ALPHA_ROW])
            res[name][fam] = dict(per_split=per, summary=summ)
            print(f"{name} {fam}: base-level any-miss {100 * summ['base_level']['any_miss_share_mean']:.1f}% spB "
                  f"{summ['base_level']['speedup_B_mean']:.2f}", flush=True)
    write("guarantee", dict(analysis="N12 Part B procedure on rebuilt data", networks=res, alpha_row=gu.ALPHA_ROW,
                            alpha_base=gu.ALPHA_BASE), [f"data/sts_n13_{n}.parquet" for n in nets] + [f"data/sts_n13_gate_{n}.json" for n in nets],
          dict(seeds=SEEDS, alpha_row=gu.ALPHA_ROW, alpha_base=gu.ALPHA_BASE, model_hyperparameters=gate_hyper(nets)))


# ------------------------------------------------------------------ cross-network table (N12 Part C)

def a_crossnet():
    chj = json.load(open("data/sts_n13_condhist.json"))["networks"]
    rows = []
    nets = available(TIER_A_NETS)
    for name in nets:
        d = load(name)
        y = d["y"]
        viol = y < LIMIT
        scen = d["df"]["scenario_id"].to_numpy(np.int64)
        spread, conc = [], []
        for seed in SEEDS:
            sp = ms.make_splits(d["groups"], seed)
            te = sp["test"]
            spread.append(float(pd.Series(viol[te].astype(float)).groupby(scen[te]).mean().std(ddof=0)))
            conc.append(cx.top_share(viol, d["elem_key"], sp["train"], te))
        r = dict(network=name, n_rows=int(len(y)), boundary_mass=float(((y >= LIMIT) & (y < 0.945)).mean()),
                 violation_rate=float(viol.mean()))
        r["risk_spread_mean"], r["risk_spread_std"] = ms_(spread)
        r["top10_concentration_mean"], r["top10_concentration_std"] = ms_(conc)
        if name in chj:
            for k in ["gate_catch", "static_fixed_catch", "condhist_catch", "global_static_catch"]:
                r[k + "_mean"] = chj[name]["summary"][k + "_mean"]
                r[k + "_std"] = chj[name]["summary"][k + "_std"]
        rows.append(r)
        print(f"{name}: BM {100 * r['boundary_mass']:.2f} VR {100 * r['violation_rate']:.2f} top10 {100 * r['top10_concentration_mean']:.1f}", flush=True)
    write("crossnet", dict(analysis="N12 Part C procedure on rebuilt data (n = 4, no law claimed)", table=rows),
          [f"data/sts_n13_{n}.parquet" for n in nets] + ["data/sts_n13_condhist.json"],
          dict(seeds=SEEDS, top_n=cx.TOP, model_hyperparameters="none here; catches from data/sts_n13_condhist.json"))


# ------------------------------------------------------------------ Mondrian (N11 Part 6) on D94

def a_mondrian():
    ms_solver = mf.load_solve_time()["ms_solver"]
    gj = gate("D94")
    d = load("D94")
    per = []
    for seed in SEEDS:
        splits = ms.make_splits(d["groups"], seed)
        kept = ms.select_features(d["X"], splits["train"])
        te, ca, tr = splits["test"], splits["cal"], splits["train"]
        Xte = d["X"][kept].iloc[te].to_numpy(np.float32)
        y_te = d["y"][te]
        ek_te = d["elem_key"][te]
        ek_ca = d["elem_key"][ca]
        scen = d["df"]["scenario_id"].to_numpy(np.int64)[te]
        viol = y_te < LIMIT
        rps = len(te) / len(np.unique(scen))
        tm = np.zeros(len(d["df"]), dtype=bool)
        tm[tr] = True
        stat, _ = bl.static_severity_score(d["df"], tm, d["elem_key"])
        k_max = int(pd.Series(scen).value_counts().max())
        c_static, _, _ = bl.capture_curve(scen, stat[te], ek_te.astype(float), viol, k_max)
        for fam in ["ridge", "histgb"]:
            f = fit_of(gj, seed, fam)
            h = held(gj, fam)[seed]
            tgt = h["target"]
            p_ca, y_ca, p_te = bc.fit_predict(d, seed, fam, f["config"], Xte, kept)
            q_glob = ge.calibrate_qhat(p_ca, y_ca, tgt)
            g_glob = bc.gate_point(p_ca, y_ca, p_te, y_te, tgt)
            if g_glob["missed"] != h["missed"] or g_glob["escalation"] != h["escalation"]:
                raise SystemExit("mondrian: global-q refit does not reproduce the rebuilt gate; stop this analysis")
            q_row = np.full(len(y_te), q_glob)
            own = 0
            fb = 0
            for e in np.unique(ek_te):
                m_ca = ek_ca == e
                if m_ca.sum() >= 20:
                    q_row[ek_te == e] = ge.calibrate_qhat(p_ca[m_ca], y_ca[m_ca], tgt)
                    own += 1
                else:
                    fb += 1
            certify = (p_te - q_row) >= LIMIT
            flag = p_te < LIMIT
            esc = (~certify) & (~flag)
            n = len(y_te)
            missed = float((certify & viol).sum() / max(int(viol.sum()), 1))
            sb = float((esc | flag).mean())
            k_b = int(round(sb * rps))
            per.append(dict(seed=seed, family=fam, target=tgt, n_elements_own_q=own, n_elements_global_fallback=fb,
                            escalation=float(esc.mean()), flag_share=float(flag.mean()), solve_share_B=sb, missed=missed,
                            gate_catch=1.0 - missed,
                            speedup_B=float(n * ms_solver / (n * f["ms_surrogate"] + (esc.sum() + flag.sum()) * ms_solver)),
                            k_B=k_b, static_catch_B=float(bl.at_k(c_static, k_b)) if k_b > 0 else 0.0,
                            global_gate=dict(escalation=h["escalation"], missed=h["missed"], gate_catch=h["gate_catch"],
                                             speedup_B=h["speedup_B"], static_catch_B=h["static_catch_B"])))
    summ = []
    for fam in ["ridge", "histgb"]:
        m = [r for r in per if r["family"] == fam]
        s = dict(family=fam)
        for k in ["escalation", "missed", "gate_catch", "speedup_B", "static_catch_B", "solve_share_B"]:
            s[k + "_mean"], s[k + "_std"] = ms_([r[k] for r in m])
        s["splits_missed_le_1pct"] = len([r for r in m if r["missed"] <= 0.01])
        summ.append(s)
        print(f"mondrian {fam}: catch {100 * s['gate_catch_mean']:.2f}±{100 * s['gate_catch_std']:.2f} static "
              f"{100 * s['static_catch_B_mean']:.2f}±{100 * s['static_catch_B_std']:.2f}", flush=True)
    write("mondrian", dict(analysis="N11 Part 6 procedure on rebuilt D94", summary=summ, per_split=per, min_cal_rows=20),
          ["data/sts_n13_D94.parquet", "data/sts_n13_gate_D94.json"],
          dict(seeds=SEEDS, min_cal_rows=20, model_hyperparameters=gate_hyper(["D94"])))


# ------------------------------------------------------------------ floor numbers (N11 Part 3) on D93-D96

def a_floor():
    per = []
    ins = []
    for floor, name in [(0.93, "D93"), (0.94, "D94"), (0.95, "D95a"), (0.96, "D96")]:
        path = f"data/sts_n13_{name}.parquet"
        if not os.path.exists(path):
            per.append(dict(floor=floor, dataset=name, available=False))
            continue
        ins.append(path)
        df = pd.read_parquet(path, columns=["outaged_type", "converged", "min_vm"])
        v = df[(df.outaged_type != "none") & df.converged.astype(bool)]["min_vm"].to_numpy(np.float64)
        strip = (v >= 0.94) & (v < 0.945)
        per.append(dict(floor=floor, dataset=name, available=True, n_rows=int(len(v)), BM=100.0 * strip.mean(),
                        CBM=100.0 * strip.sum() / (v >= 0.94).sum(), VR=100.0 * (v < 0.94).mean()))
        print(f"floor {floor}: BM {per[-1]['BM']:.2f} CBM {per[-1]['CBM']:.2f} VR {per[-1]['VR']:.2f}", flush=True)
    write("floor", dict(analysis="N11 Part 3 numbers on rebuilt data (rebuilt labels = corrected solver)", per_floor=per),
          ins, dict(model_hyperparameters="none (no model fit)"))


# ------------------------------------------------------------------ N-2 coverage (N11 Part 1) on rebuilt D94 + N2R

def a_n2():
    ms_solver = mf.load_solve_time()["ms_solver"]
    gj = gate("D94")
    d = load("D94")
    rows = pd.read_parquet("data/sts_n13_N2R.parquet")
    conv = rows["pinned_converged"].to_numpy(bool)
    ok = rows["corrected_status"].isin(["converged", "not_needed"]).to_numpy()
    use = rows[conv & ok].reset_index(drop=True)
    per = []
    checks = []
    for seed in SEEDS:
        splits = ms.make_splits(d["groups"], seed)
        kept = ms.select_features(d["X"], splits["train"])
        te = splits["test"]
        test_scen = set(d["df"]["scenario_id"].to_numpy()[te].tolist())
        sub = use[use["scenario_id"].isin(test_scen)].reset_index(drop=True)
        X2, missing = n2e.two_hot_matrix(d, kept, sub)
        Xk = d["X"][kept]
        X1 = Xk.iloc[te].to_numpy(np.float32)
        y1 = d["y"][te]
        y2 = sub["corrected_min_vm"].to_numpy(np.float64)
        for fam in ["ridge", "histgb"]:
            f = fit_of(gj, seed, fam)
            h = held(gj, fam)[seed]
            g90 = [p for p in gj["points"] if p["seed"] == seed and p["family"] == fam and p["point"] == "grid" and abs(p["target"] - 0.90) < 1e-9][0]
            fitted = tu.fit_one(fam, f["config"], Xk.iloc[splits["train"]].to_numpy(np.float32), d["y"][splits["train"]], seed)
            p_ca = tu.predict(fitted, Xk.iloc[splits["cal"]].to_numpy(np.float32))
            y_ca = d["y"][splits["cal"]]
            p1 = tu.predict(fitted, X1)
            p2 = tu.predict(fitted, X2)
            m1 = n2e.gate_metrics(p_ca, y_ca, p1, y1, 0.90, f["ms_surrogate"], ms_solver)
            exact = bool(m1["escalation"] == g90["escalation"] and m1["missed"] == g90["missed"])
            checks.append(dict(seed=seed, family=fam, exact=exact))
            if not exact:
                raise SystemExit("n2: refit does not reproduce the rebuilt gate N-1 numbers at 0.90; stop this analysis")
            for tgt, kind in [(0.90, "t090"), (h["target"], "held_out")]:
                r2 = n2e.gate_metrics(p_ca, y_ca, p2, y2, tgt, f["ms_surrogate"], ms_solver)
                r1 = n2e.gate_metrics(p_ca, y_ca, p1, y1, tgt, f["ms_surrogate"], ms_solver)
                adj = sub["adjacent"].to_numpy(bool)
                q = r2["q_hat"]
                per.append(dict(seed=seed, family=fam, point=kind, n2=r2, n1=r1, two_hot_missing_cols=int(missing),
                                coverage_n2_adjacent=float((y2[adj] >= p2[adj] - q).mean()) if adj.any() else None,
                                coverage_n2_nonadjacent=float((y2[~adj] >= p2[~adj] - q).mean()) if (~adj).any() else None,
                                n2_violation_rate=float((y2 < LIMIT).mean())))
    summary = []
    for fam in ["ridge", "histgb"]:
        for kind in ["t090", "held_out"]:
            m = [r for r in per if r["family"] == fam and r["point"] == kind]
            s = dict(family=fam, point=kind)
            for side in ["n2", "n1"]:
                for k in ["coverage", "missed", "escalation", "flag_share", "speedup_A", "speedup_B", "target"]:
                    s[f"{side}_{k}_mean"], s[f"{side}_{k}_std"] = ms_([r[side][k] for r in m])
            s["n2_splits_missed_le_1pct"] = len([r for r in m if r["n2"]["missed"] <= 0.01])
            for k in ["coverage_n2_adjacent", "coverage_n2_nonadjacent", "n2_violation_rate"]:
                s[k + "_mean"], s[k + "_std"] = ms_([r[k] for r in m])
            summary.append(s)
            print(f"n2 {fam} {kind}: N-2 cov {s['n2_coverage_mean']:.4f}±{s['n2_coverage_std']:.4f} N-1 cov {s['n1_coverage_mean']:.4f}", flush=True)
    write("n2", dict(analysis="N11 Part 1 procedure on rebuilt D94 + N2R", summary=summary, per_split=per, reproduction=checks,
                     n2_rows=dict(total=int(len(rows)), pinned_nonconverged=int((~conv).sum()), corrected_failed=int((conv & ~ok).sum()),
                                  used=int(len(use)))),
          ["data/sts_n13_D94.parquet", "data/sts_n13_N2R.parquet", "data/sts_n13_gate_D94.json"],
          dict(seeds=SEEDS, model_hyperparameters=gate_hyper(["D94"]), encoding="two-hot (N11)"))


# ------------------------------------------------------------------ tier B: shift test (N9 Part 2), D94 -> D95a and reverse

def a_shift():
    import n9_shift as sh
    data = dict(D94=load("D94"), D95a=load("D95a"))
    gjs = dict(D94=gate("D94"), D95a=gate("D95a"))
    rows = []
    for src_name, tgt_name in [("D94", "D95a"), ("D95a", "D94")]:
        src = data[src_name]
        tgt = data[tgt_name]
        for seed in SEEDS:
            s_spl = ms.make_splits(src["groups"], seed)
            t_spl = ms.make_splits(tgt["groups"], seed)
            kept = ms.select_features(src["X"], s_spl["train"])
            te = t_spl["test"]
            Xte = tgt["X"].reindex(columns=kept, fill_value=0.0).iloc[te].to_numpy(np.float32)
            y_te = tgt["y"][te]
            scen = tgt["df"]["scenario_id"].to_numpy(np.int64)[te]
            viol = y_te < LIMIT
            tb = tgt["elem_key"][te].astype(float)
            rps = len(te) / len(np.unique(scen))
            k_max = int(pd.Series(scen).value_counts().max())
            s_mask = np.zeros(len(src["df"]), dtype=bool)
            s_mask[s_spl["train"]] = True
            _, s_freq = bl.static_severity_score(src["df"], s_mask, src["elem_key"])
            c_shift, _, _ = bl.capture_curve(scen, sh.static_scores(s_freq, tgt["elem_key"][te]), tb, viol, k_max)
            t_mask = np.zeros(len(tgt["df"]), dtype=bool)
            t_mask[t_spl["train"]] = True
            t_score, _ = bl.static_severity_score(tgt["df"], t_mask, tgt["elem_key"])
            c_ind, _, _ = bl.capture_curve(scen, t_score[te], tb, viol, k_max)
            for fam in ["ridge", "histgb"]:
                f = fit_of(gjs[src_name], seed, fam)
                target = gjs[src_name]["selections"][str(seed)][fam]["m2_inner_cov_at"]
                p_ca, y_ca, p_te = bc.fit_predict(src, seed, fam, f["config"], Xte, kept)
                g = bc.gate_point(p_ca, y_ca, p_te, y_te, target)
                k_b = int(round(g["solve_share_B"] * rps))
                ref = held(gjs[tgt_name], fam)[seed]
                r = dict(source=src_name, target=tgt_name, seed=seed, family=fam, held_out_target=target, escalation=g["escalation"],
                         flag_share=g["flag_share"], solve_share_B=g["solve_share_B"], missed=g["missed"], gate_catch=1.0 - g["missed"],
                         coverage_emp=g["coverage_emp"], k_B=k_b, static_catch_B=float(bl.at_k(c_shift, k_b)) if k_b > 0 else 0.0,
                         static_indist_catch_at_same_k=float(bl.at_k(c_ind, k_b)) if k_b > 0 else 0.0,
                         target_indist_gate_catch=ref["gate_catch"])
                r["gate_degradation"] = r["gate_catch"] - r["target_indist_gate_catch"]
                r["static_degradation"] = r["static_catch_B"] - r["static_indist_catch_at_same_k"]
                rows.append(r)
    df = pd.DataFrame(rows)
    summary = []
    for src_name, tgt_name in [("D94", "D95a"), ("D95a", "D94")]:
        for fam in ["ridge", "histgb"]:
            m = df[(df.source == src_name) & (df.target == tgt_name) & (df.family == fam)]
            s2 = dict(source=src_name, target=tgt_name, family=fam)
            for col in ["held_out_target", "solve_share_B", "escalation", "missed", "gate_catch", "static_catch_B", "coverage_emp",
                        "gate_degradation", "static_degradation"]:
                s2[col + "_mean"], s2[col + "_std"] = ms_(m[col])
            s2["splits_missed_le_1pct"] = int((m["missed"] <= 0.01).sum())
            gm, gs = ms_(m["gate_catch"])
            smu, ss = ms_(m["static_catch_B"])
            s2["gap"] = gm - smu
            s2["STD"] = max(gs, ss)
            s2["gate_higher_by_std_rule"] = bool(s2["gap"] > s2["STD"])
            summary.append(s2)
            print(f"shift {src_name}->{tgt_name} {fam}: gate {100 * gm:.2f} static {100 * smu:.2f} -> {s2['gate_higher_by_std_rule']}", flush=True)
    write("shift", dict(analysis="N9 Part 2 procedure on rebuilt D94 / D95a", summary=summary, per_split=rows),
          ["data/sts_n13_D94.parquet", "data/sts_n13_D95a.parquet", "data/sts_n13_gate_D94.json", "data/sts_n13_gate_D95a.json"],
          dict(seeds=SEEDS, model_hyperparameters=gate_hyper(["D94", "D95a"])))


# ------------------------------------------------------------------ tier B: floor replication over the three 0.95 builds (N9 Part 3)

def a_floorrep():
    pred = {"BM": (33.0, 20.0, 45.0), "CBM": (40.0, 28.0, 55.0), "VR": (15.5, 12.0, 18.0)}
    per = []
    ins = []
    for name in ["D95a", "D95b", "D95c"]:
        path = f"data/sts_n13_{name}.parquet"
        if not os.path.exists(path):
            per.append(dict(build=name, available=False))
            continue
        ins.append(path)
        df = pd.read_parquet(path, columns=["outaged_type", "converged", "min_vm"])
        v = df[(df.outaged_type != "none") & df.converged.astype(bool)]["min_vm"].to_numpy(np.float64)
        strip = (v >= 0.94) & (v < 0.945)
        r = dict(build=name, available=True, BM=100.0 * strip.mean(), CBM=100.0 * strip.sum() / (v >= 0.94).sum(), VR=100.0 * (v < 0.94).mean())
        r["in_n3_range_descriptive"] = {k: bool(pred[k][1] <= r[k] <= pred[k][2]) for k in pred}
        per.append(r)
    av = [r for r in per if r.get("available")]
    across = {}
    for k in ["BM", "CBM", "VR"]:
        v = np.array([r[k] for r in av])
        across[k] = dict(mean=float(v.mean()), std_ddof0=float(v.std()), std_ddof1=float(v.std(ddof=1)) if len(v) > 1 else None)
    print(json.dumps(across), flush=True)
    write("floorrep", dict(analysis="N9 Part 3 replication over the rebuilt 0.95 builds (rebuilt labels)", per_build=per, across=across,
                           n3_ranges_note="N3 ranges were made for the old builds; shown as descriptive in-range flags only"),
          ins, dict(model_hyperparameters="none (no model fit)"))


# ------------------------------------------------------------------ tier B: gate on D95b, D95c (N11 Part 5)

def a_gate095bc():
    res = {}
    h94 = [held(gate("D94"), "histgb")[s] for s in SEEDS]
    for name in ["D95a", "D95b", "D95c"]:
        if not os.path.exists(f"data/sts_n13_gate_{name}.json"):
            res[name] = "not run"
            continue
        h = [held(gate(name), "histgb")[s] for s in SEEDS]
        summ = {}
        for k in ["target", "escalation", "missed", "gate_catch", "static_catch_B", "speedup_B"]:
            summ[k] = dict(zip(["mean", "std"], ms_([p[k] for p in h])))
        n_ok = len([p for p in h if p["missed"] <= 0.01])
        m95, s95 = ms_([p["speedup_B"] for p in h])
        m94, s94 = ms_([p["speedup_B"] for p in h94])
        gm, gs = ms_([p["gate_catch"] for p in h])
        smu, ss = ms_([p["static_catch_B"] for p in h])
        res[name] = dict(histgb_held_out=summ, missed_per_split=[p["missed"] for p in h],
                         n5_rules_replication=dict(label="replication of N5 rule, not a new verdict" if name != "D95a" else "see tier-B verdicts",
                                                   SAFER=bool(n_ok >= 4), splits_missed_le_1pct=n_ok,
                                                   FASTER=bool((m95 - m94 > max(s94, s95)) and (gm - smu > max(gs, ss))),
                                                   clause1=bool(m95 - m94 > max(s94, s95)), clause2=bool(gm - smu > max(gs, ss))))
    across = {}
    names = [n for n in res if isinstance(res[n], dict)]
    for k in ["escalation", "missed", "gate_catch", "speedup_B", "static_catch_B"]:
        v = np.array([res[n]["histgb_held_out"][k]["mean"] for n in names])
        across[k] = dict(builds=names, mean=float(v.mean()), std_ddof0=float(v.std()), std_ddof1=float(v.std(ddof=1)) if len(v) > 1 else None)
    write("gate095bc", dict(analysis="N11 Part 5 procedure on the rebuilt 0.95 builds", builds=res, across=across),
          [f"data/sts_n13_gate_{n}.json" for n in names] + ["data/sts_n13_gate_D94.json"],
          dict(model_hyperparameters=gate_hyper(names)))


def main():
    t0 = time.time()
    check_hash()
    if WHICH == "condhist":
        a_condhist()
    elif WHICH == "budget":
        a_budget(sys.argv[2] if len(sys.argv) > 2 else "D94")
    elif WHICH == "shift":
        a_shift()
    elif WHICH == "floorrep":
        a_floorrep()
    elif WHICH == "gate095bc":
        a_gate095bc()
    elif WHICH == "guarantee":
        a_guarantee()
    elif WHICH == "crossnet":
        a_crossnet()
    elif WHICH == "mondrian":
        a_mondrian()
    elif WHICH == "floor":
        a_floor()
    elif WHICH == "n2":
        a_n2()
    else:
        raise SystemExit(f"unknown analysis {WHICH}")
    print(f"wall {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
