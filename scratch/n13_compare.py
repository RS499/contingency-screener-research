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
import surrogate as sg
import tune_surrogates as tu
import manifest as mf
import sts_manifest as sm
import n5_gate_eval as n5

# N13 Step 8 (scratch/n13_decision_rule.md §5): old vs rebuilt, side by side, for every number in the paper's tables,
# unpaired (different base sets and splits), with the std rule: "differs" only if |rebuilt - old| > max(old std,
# rebuilt std); single numbers without a std are reported without a verdict. Rebuilt values that were not produced
# (stopped analysis or dataset, or not yet run) are reported as "not run".
# Tables: tab:ops (ridge/histgb x targets 0.90, 0.94-0.98 + held-out: escalation, coverage, missed, speedup A, speedup B),
# tab:models (persistence, train mean, ridge, histgb at 0.90: MAE, R2, escalation, missed, speedup A), the floor table
# (BM, CBM, VR), gate vs static (held-out, rule B, per network), and the descriptive tables of N9 (budget curve),
# N11 (N-2, Mondrian), N12 (COND-HIST, guarantee, cross-network).
# Output: data/sts_n13_compare.json + manifest.

OUT = "data/sts_n13_compare.json"
LIMIT = 0.94
SEEDS = [0, 1, 2, 3, 4]
OPS_TARGETS = [0.90, 0.94, 0.95, 0.96, 0.97, 0.98]


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def row(table, key, old, new):
    # old/new: (mean, std) or None
    r = dict(table=table, key=key)
    if old is None:
        r["old"] = None
    else:
        r["old_mean"], r["old_std"] = old
    if new is None:
        r["rebuilt"] = "not run"
        return r
    r["rebuilt_mean"], r["rebuilt_std"] = new
    if old is not None:
        r["diff"] = new[0] - old[0]
        r["std_rule"] = "differs" if abs(r["diff"]) > max(old[1], new[1]) else "within std"
    return r


def gate_points(path, key=None):
    if not os.path.exists(path):
        return None
    g = json.load(open(path))
    if key:
        g = g["networks"][key]
    return pd.DataFrame([p for p in g["points"] if p["point"] in ("grid", "held_out")])


def agg(pts, fam, kind, tgt, col):
    if pts is None:
        return None
    m = pts[(pts.family == fam) & (pts.point == kind)]
    if kind == "grid":
        m = m[m.target.round(2) == round(tgt, 2)]
    if len(m) == 0 or col not in m:
        return None
    return ms_(m[col])


def baselines(path, labels):
    # persistence and train mean at target 0.90, as feasibility/run_all.py (timed predict), on one dataset
    df, fc, _ = n5.load_relabeled(path, labels)
    X, y, groups, _ = ms.build_design_matrix(df, fc)
    n0 = df["n0_min_vm"].to_numpy(np.float64)
    ms_solver = mf.load_solve_time()["ms_solver"]
    out = {"persistence": [], "train_mean": []}
    for seed in SEEDS:
        sp = ms.make_splits(groups, seed)
        te, ca, tr = sp["test"], sp["cal"], sp["train"]
        for kind in out:
            t0 = time.time()
            if kind == "persistence":
                pt = sg.predict_persistence(n0[te])
                pc = sg.predict_persistence(n0[ca])
            else:
                pt = sg.predict_mean(y[tr], len(te))
                pc = sg.predict_mean(y[tr], len(ca))
            dt = (time.time() - t0) / len(te) * 1000.0
            mae, r2 = tu.mae_r2(pt, y[te])
            q = ge.calibrate_qhat(pc, y[ca], 0.90)
            s = ge.score(ge.run_gate(pt, q, LIMIT), y[te], dt, ms_solver, LIMIT)
            out[kind].append(dict(mae=mae, r2=r2, escalation=s["escalation"], missed=s["missed_viol"], speedup_A=s["net_speedup"]))
    return out


def main():
    t0 = time.time()
    rows = []
    old94 = gate_points("data/sts_n5_gate_094.json")
    new94 = gate_points("data/sts_n13_gate_D94.json")
    for fam in ["ridge", "histgb"]:
        for tgt in OPS_TARGETS:
            for col in ["escalation", "coverage_emp", "missed", "speedup_A", "speedup_B"]:
                rows.append(row("tab:ops", f"{fam} {tgt:.2f} {col}", agg(old94, fam, "grid", tgt, col), agg(new94, fam, "grid", tgt, col)))
        for col in ["target", "escalation", "coverage_emp", "missed", "speedup_A", "speedup_B"]:
            rows.append(row("tab:ops", f"{fam} held-out {col}", agg(old94, fam, "held_out", None, col), agg(new94, fam, "held_out", None, col)))
    # tab:models
    oldfits = pd.DataFrame(json.load(open("data/sts_n5_gate_094.json"))["fits"])
    newfits = pd.DataFrame(json.load(open("data/sts_n13_gate_D94.json"))["fits"]) if new94 is not None else None
    for fam in ["ridge", "histgb"]:
        for col, scale in [("mae", 1000.0), ("r2", 1.0)]:
            o = ms_(oldfits[oldfits.family == fam][col] * scale)
            n = ms_(newfits[newfits.family == fam][col] * scale) if newfits is not None else None
            rows.append(row("tab:models", f"{fam} {col}{' (mV)' if col == 'mae' else ''}", o, n))
        for col in ["escalation", "missed", "speedup_A"]:
            rows.append(row("tab:models", f"{fam} 0.90 {col}", agg(old94, fam, "grid", 0.90, col), agg(new94, fam, "grid", 0.90, col)))
    ob = baselines("data/dataset.parquet", "data/sts_n2_label_audit.parquet")
    nbl = baselines("data/sts_n13_D94.parquet", "") if os.path.exists("data/sts_n13_D94.parquet") else None
    for kind in ["persistence", "train_mean"]:
        for col in ["mae", "r2", "escalation", "missed", "speedup_A"]:
            sc = 1000.0 if col == "mae" else 1.0
            o = ms_([r[col] * sc for r in ob[kind]])
            n = ms_([r[col] * sc for r in nbl[kind]]) if nbl else None
            rows.append(row("tab:models", f"{kind} 0.90 {col}", o, n))
    # floor table (old: N11 dose-response stored and corrected; rebuilt: corrected solver)
    dose = json.load(open("data/sts_n11_dose_response.json"))["per_floor"]
    newfl = {}
    if os.path.exists("data/sts_n13_floor.json"):
        for r in json.load(open("data/sts_n13_floor.json"))["per_floor"]:
            if r.get("available"):
                newfl[r["floor"]] = r
    for r in dose:
        for col in ["BM", "CBM", "VR"]:
            for lab in ["stored", "corrected"]:
                n = (newfl[r["floor"]][col], 0.0) if r["floor"] in newfl else None
                rows.append(row("floor", f"floor {r['floor']:.2f} {col} (old {lab} labels vs rebuilt)", (r[lab][col], 0.0), n))
    # gate vs static, held-out, rule B, histgb and ridge, per network
    nets = [("D94", "data/sts_n5_gate_094.json", None), ("ILL", "data/sts_n10_illinois.json", None),
            ("C30", "data/sts_n11_smallnets.json", "case30_thermal"), ("C24", "data/sts_n11_smallnets.json", "case24_ieee_rts")]
    for name, op, key in nets:
        o = gate_points(op, key)
        n = gate_points(f"data/sts_n13_gate_{name}.json")
        for fam in ["histgb", "ridge"]:
            for col in ["escalation", "missed", "solve_share_B", "gate_catch", "static_catch_B", "speedup_B"]:
                rows.append(row("gate_vs_static", f"{name} {fam} held-out {col}", agg(o, fam, "held_out", None, col), agg(n, fam, "held_out", None, col)))
    # descriptive tables
    def pair_json(old_path, new_path, table, extract):
        o = extract(json.load(open(old_path))) if os.path.exists(old_path) else {}
        n = extract(json.load(open(new_path))) if os.path.exists(new_path) else {}
        for k in o:
            rows.append(row(table, k, o[k], n.get(k)))

    def ex_budget(j):
        out = {}
        tab = j["table"]
        for r in tab:
            if r.get("dataset", "D94") in ("D94",):
                for kind in ["surr", "static", "oracle"]:
                    out[f"{r['family']} k={r['k']} {kind}"] = (r[kind + "_mean"], r[kind + "_std"])
        return out
    pair_json("data/sts_n9_budget_curve.json", "data/sts_n13_budget.json", "budget_curve_D94", ex_budget)

    def ex_budget95(j):
        out = {}
        for r in j["table"]:
            if r.get("dataset", "D95a") == "D95a":
                for kind in ["surr", "static", "oracle"]:
                    out[f"{r['family']} k={r['k']} {kind}"] = (r[kind + "_mean"], r[kind + "_std"])
        return out
    pair_json("data/sts_n9_budget_curve.json", "data/sts_n13_budget_D95a.json", "budget_curve_D95a", ex_budget95)

    def ex_n2(j):
        out = {}
        for s in j["summary"]:
            for k in ["n2_coverage", "n1_coverage", "n2_missed", "n2_escalation", "n2_speedup_B"]:
                out[f"{s['family']} {s['point']} {k}"] = (s[k + "_mean"], s[k + "_std"])
        return out
    pair_json("data/sts_n11_n2.json", "data/sts_n13_n2.json", "n2", ex_n2)

    def ex_mond(j):
        out = {}
        for s in j["summary"]:
            for k in ["escalation", "missed", "gate_catch", "static_catch_B", "speedup_B"]:
                out[f"{s['family']} {k}"] = (s[k + "_mean"], s[k + "_std"])
        return out
    pair_json("data/sts_n11_mondrian.json", "data/sts_n13_mondrian.json", "mondrian", ex_mond)

    def ex_cond_old(j):
        out = {}
        for o_name, name in [("case118", "D94"), ("case_illinois200", "ILL"), ("case30_thermal", "C30"), ("case24_ieee_rts", "C24")]:
            s = j["networks"][o_name]["summary"]
            for k in ["gate_catch", "static_fixed_catch", "condhist_catch", "global_static_catch"]:
                out[f"{name} {k}"] = (s[k + "_mean"], s[k + "_std"])
        return out

    def ex_cond_new(j):
        out = {}
        for name in j["networks"]:
            s = j["networks"][name]["summary"]
            for k in ["gate_catch", "static_fixed_catch", "condhist_catch", "global_static_catch"]:
                out[f"{name} {k}"] = (s[k + "_mean"], s[k + "_std"])
        return out
    o = ex_cond_old(json.load(open("data/sts_n12_condhist.json")))
    n = ex_cond_new(json.load(open("data/sts_n13_condhist.json"))) if os.path.exists("data/sts_n13_condhist.json") else {}
    for k in o:
        rows.append(row("condhist", k, o[k], n.get(k)))

    def ex_guar(j, names):
        out = {}
        for name, key in names:
            if key not in j["networks"]:
                continue
            for fam in j["networks"][key]:
                s = j["networks"][key][fam].get("summary")
                if s is None:
                    continue
                for cal in ["global_gate", "row_level", "base_level"]:
                    for k in ["escalation", "missed", "any_miss_share", "speedup_B"]:
                        out[f"{name} {fam} {cal} {k}"] = (s[cal][k + "_mean"], s[cal][k + "_std"])
        return out
    o = ex_guar(json.load(open("data/sts_n12_guarantee.json")), [("D94", "case118"), ("ILL", "case_illinois200")])
    n = ex_guar(json.load(open("data/sts_n13_guarantee.json")), [("D94", "D94"), ("ILL", "ILL")]) if os.path.exists("data/sts_n13_guarantee.json") else {}
    for k in o:
        rows.append(row("guarantee", k, o[k], n.get(k)))
    oc = {r["network"]: r for r in json.load(open("data/sts_n12_crossnet.json"))["table"]}
    nc = {r["network"]: r for r in json.load(open("data/sts_n13_crossnet.json"))["table"]} if os.path.exists("data/sts_n13_crossnet.json") else {}
    for o_name, name in [("case118", "D94"), ("case_illinois200", "ILL"), ("case30_thermal", "C30"), ("case24_ieee_rts", "C24")]:
        for k in ["boundary_mass", "violation_rate"]:
            rows.append(row("crossnet", f"{name} {k}", (oc[o_name][k], 0.0), (nc[name][k], 0.0) if name in nc else None))
        for k in ["risk_spread", "top10_concentration"]:
            rows.append(row("crossnet", f"{name} {k}", (oc[o_name][k + "_mean"], oc[o_name][k + "_std"]),
                            (nc[name][k + "_mean"], nc[name][k + "_std"]) if name in nc else None))
    n_diff = len([r for r in rows if r.get("std_rule") == "differs"])
    n_within = len([r for r in rows if r.get("std_rule") == "within std"])
    n_notrun = len([r for r in rows if r.get("rebuilt") == "not run"])
    out = dict(part="N13 Step 8: old vs rebuilt, unpaired, std rule", n_rows=len(rows), n_differs=n_diff, n_within_std=n_within,
               n_not_run=n_notrun, rows=rows, std_rule="differs only if |rebuilt - old| > max(old std, rebuilt std); numbers without a std (std 0) compare exactly",
               wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, default=float)
    ins = [p for p in ["data/sts_n5_gate_094.json", "data/sts_n13_gate_D94.json", "data/sts_n10_illinois.json", "data/sts_n11_smallnets.json",
                       "data/sts_n11_dose_response.json", "data/sts_n13_floor.json", "data/sts_n9_budget_curve.json", "data/sts_n13_budget.json",
                       "data/sts_n11_n2.json", "data/sts_n13_n2.json", "data/sts_n11_mondrian.json", "data/sts_n13_mondrian.json",
                       "data/sts_n12_condhist.json", "data/sts_n13_condhist.json", "data/sts_n12_guarantee.json", "data/sts_n13_guarantee.json",
                       "data/sts_n12_crossnet.json", "data/sts_n13_crossnet.json", "data/dataset.parquet", "data/sts_n13_D94.parquet"] if os.path.exists(p)]
    man = sm.build_manifest([OUT], "scratch/n13_compare.py", [".venv/bin/python", "scratch/n13_compare.py"], ins,
                            dict(model_hyperparameters="none fitted here except persistence/train-mean baselines (no hyperparameters)"), "")
    sm.write_manifest(man, OUT)
    print(f"compare: {len(rows)} rows; differs {n_diff}; within std {n_within}; not run {n_notrun}")


if __name__ == "__main__":
    main()
