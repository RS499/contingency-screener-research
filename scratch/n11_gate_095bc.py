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
import manifest as mf
import tune_surrogates as tu
import sts_manifest as sm
import n5_gate_eval as n5

# N11 Part 5 (scratch/n11_decision_rule.md §4, descriptive): the N5 protocol (scratch/n5_gate_eval.py run_seed,
# unchanged: full tune_surrogates search, M2, held-out target, rules A/B, static at k_B) on D95b (seeds 200-203)
# and D95c (seeds 300-303) with their N9 switch-back relabels. Held-out histgb numbers per build, mean +- std
# across the three 0.95 builds (D95a from data/sts_n5_gate_095.json), and the N5 SAFER / FASTER rules re-applied
# per build, labelled "replication of N5 rule, not a new verdict" (FASTER compares with D94 from
# data/sts_n5_gate_094.json).

BUILDS = {
    "D95b": ("data/sts_n5_floor095_seed200.parquet", "data/sts_n9_relabel095_seed200.parquet"),
    "D95c": ("data/sts_n9_floor095_seed300.parquet", "data/sts_n9_relabel095_seed300.parquet"),
}
OUT = "data/sts_n11_gate_095bc.json"
SEEDS = [0, 1, 2, 3, 4]
N_LINE = 173


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def held(points, fam):
    h = [p for p in points if p["family"] == fam and p["point"] == "held_out"]
    return [h[i] for i in np.argsort([p["seed"] for p in h])]


def n5_rules(h95, h94):
    # N5 SAFER and FASTER (scratch/n5_decision_rule.md), histgb held-out, applied to one 0.95 build
    n_ok = len([p for p in h95 if p["missed"] <= 0.01])
    b95 = [p["speedup_B"] for p in h95]
    b94 = [p["speedup_B"] for p in h94]
    m95, s95 = ms_(b95)
    m94, s94 = ms_(b94)
    gm, gs = ms_([p["gate_catch"] for p in h95])
    sm_, ss = ms_([p["static_catch_B"] for p in h95])
    c1 = bool(m95 - m94 > max(s94, s95))
    c2 = bool(gm - sm_ > max(gs, ss))
    return dict(label="replication of N5 rule, not a new verdict", SAFER=bool(n_ok >= 4), splits_missed_le_1pct=n_ok,
                FASTER=bool(c1 and c2), clause1=dict(speedup_B=m95, speedup_B_std=s95, speedup_B_094=m94,
                                                     speedup_B_094_std=s94, holds=c1),
                clause2=dict(gate_catch=gm, gate_catch_std=gs, static_catch_B=sm_, static_catch_B_std=ss, holds=c2))


def main():
    t0 = time.time()
    ms_solver = mf.load_solve_time()["ms_solver"]
    r_cands = tu.ridge_candidates()
    h_cands = tu.histgb_candidates()
    h94 = held(json.load(open("data/sts_n5_gate_094.json"))["points"], "histgb")
    res = {}
    fits_all = {}
    for name in BUILDS:
        data_path, lab_path = BUILDS[name]
        df, feature_cols, info = n5.load_relabeled(data_path, lab_path)
        X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
        is_trafo = df["outaged_type"].to_numpy() == "trafo"
        ek = df["outaged_idx"].to_numpy(np.int64) + np.where(is_trafo, N_LINE, 0)
        points, fits, sel = [], [], {}
        for seed in SEEDS:
            _s, se, f, p = n5.run_seed(df, X, y, groups, seed, ms_solver, r_cands, h_cands, ek)
            sel[str(seed)] = se
            fits.extend(f)
            points.extend(p)
        h95 = held(points, "histgb")
        summ = {}
        for k in ["target", "escalation", "flag_share", "solve_share_B", "missed", "gate_catch", "speedup_A", "speedup_B",
                  "static_catch_B", "coverage_emp"]:
            summ[k] = dict(zip(["mean", "std"], ms_([p[k] for p in h95])))
        res[name] = dict(labels=info, histgb_held_out=summ, histgb_held_out_per_split=h95, n5_rules=n5_rules(h95, h94),
                         selections=sel, points=points)
        fits_all[name] = [dict(seed=f["seed"], family=f["family"], tag=f["tag"], config=f["config"]) for f in fits]
        print(f"{name}: histgb held-out esc {100 * summ['escalation']['mean']:.1f} missed {100 * summ['missed']['mean']:.2f} "
              f"spB {summ['speedup_B']['mean']:.3f} | N5 rules {res[name]['n5_rules']['SAFER']}/{res[name]['n5_rules']['FASTER']}",
              flush=True)
    h95a = held(json.load(open("data/sts_n5_gate_095.json"))["points"], "histgb")
    across = {}
    for k in ["escalation", "missed", "gate_catch", "speedup_B", "static_catch_B"]:
        vals = [float(np.mean([p[k] for p in h95a]))] + [res[n]["histgb_held_out"][k]["mean"] for n in BUILDS]
        across[k] = dict(build_means=dict(zip(["D95a", "D95b", "D95c"], vals)), mean=float(np.mean(vals)),
                         std_ddof0=float(np.std(vals)), std_ddof1=float(np.std(vals, ddof=1)))
    out = dict(part="N11 Part 5: the gate on D95b and D95c (descriptive)", builds=res, across_three_095_builds=across,
               std_convention="population std (ddof=0) over 5 splits; across builds ddof=0 and ddof=1 over 3 build means",
               ms_solver=ms_solver, wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    inputs = ["data/sts_n5_gate_094.json", "data/sts_n5_gate_095.json"]
    for n in BUILDS:
        inputs += list(BUILDS[n])
    man = sm.build_manifest([OUT], "scratch/n11_gate_095bc.py", [".venv/bin/python", "scratch/n11_gate_095bc.py"], inputs,
                            dict(seeds=SEEDS, model_hyperparameters=fits_all,
                                 search="scripts/tune_surrogates.py candidates (15 ridge, 26 histgb)",
                                 solver_settings="labels: pinned pandapower + N2 switch-back (N9 relabels)"), "")
    man["no_new_solves"] = "No AC solve. Model fits: full tune_surrogates search + M2 refits per build and seed."
    sm.write_manifest(man, OUT)
    print(json.dumps(across, indent=1))


if __name__ == "__main__":
    main()
