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
import n10_gate_illinois as il

# N13 Step 4, arm S (scratch/n13_decision_rule.md §3): gate with full M2 re-search on a rebuilt dataset, through the
# original procedure with only the input path changed. argv[1] = dataset name.
#   D94 (and tier-B D95a): scratch/n5_gate_eval.py run_seed (5 outer splits, inner make_splits(train, 1000 + seed),
#        tune_surrogates candidates, M2, held-out target, targets 0.90-0.98, rules A/B, static at k_B);
#   ILL: scratch/n10_gate_illinois.py run_seed (same protocol plus budget-curve, concentration and any-miss columns);
#   C30, C24: scratch/n11_smallnets.py's per-network use of n10_gate_illinois.run_seed.
# Labels are the rebuilt dataset's own (corrected) min_vm; loading = n5_gate_eval.load_relabeled(path, "") ->
# make_splits.load_dataset (converged N-1 rows; failed switch-back rows have converged = False and are dropped).
# Output: data/sts_n13_gate_<name>.json + manifest (selected hyperparameters per split, candidate grids).

NAME = sys.argv[1] if len(sys.argv) > 1 else "D94"
N_LINE = {"D94": 173, "D95a": 173, "D95b": 173, "D95c": 173, "ILL": 179, "C30": 41, "C24": 33}
SEEDS = [0, 1, 2, 3, 4]


def main():
    t0 = time.time()
    path = f"data/sts_n13_{NAME}.parquet"
    ms_solver = mf.load_solve_time()["ms_solver"]
    r_cands = tu.ridge_candidates()
    h_cands = tu.histgb_candidates()
    df, feature_cols, info = n5.load_relabeled(path, "")
    info["labels"] = "the rebuilt dataset's own min_vm (corrected solver); failed switch-back rows dropped as converged = False"
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    is_trafo = df["outaged_type"].to_numpy() == "trafo"
    ek = df["outaged_idx"].to_numpy(np.int64) + np.where(is_trafo, N_LINE[NAME], 0)
    search, sel, fits, points, curves, conc = [], {}, [], [], [], []
    for seed in SEEDS:
        if NAME in ("D94", "D95a", "D95b", "D95c"):
            s, se, f, p = n5.run_seed(df, X, y, groups, seed, ms_solver, r_cands, h_cands, ek)
        else:
            s, se, f, p, cv, co = il.run_seed(df, X, y, groups, seed, ms_solver, r_cands, h_cands, ek)
            curves.extend(cv)
            co["seed"] = seed
            conc.append(co)
        search.extend(s)
        sel[str(seed)] = se
        fits.extend(f)
        points.extend(p)
        h = [q for q in p if q["family"] == "histgb" and q["point"] == "held_out"]
        if h:
            print(f"{NAME} seed {seed}: histgb held-out {h[0]['target']:.2f} esc {100 * h[0]['escalation']:.1f}% "
                  f"missed {100 * h[0]['missed']:.2f}% catch {100 * h[0]['gate_catch']:.2f} static_B {100 * h[0]['static_catch_B']:.2f}",
                  flush=True)
    out = dict(run=f"N13 arm S gate, {NAME} (rebuilt)", dataset=path, labels=info, seeds=SEEDS, limit=0.94,
               ms_solver=ms_solver, procedure=("scratch/n5_gate_eval.py run_seed" if NAME.startswith("D9") else
                                               "scratch/n10_gate_illinois.py run_seed"),
               selections=sel, fits=fits, points=points, curves_at_declared_k=curves, concentration=conc,
               search=search, wall_s=time.time() - t0)
    op = f"data/sts_n13_gate_{NAME}.json"
    with open(op, "w") as f:
        json.dump(out, f, indent=2)
    params = dict(seeds=SEEDS, invocation=f"scratch/n13_gate.py {NAME}",
                  candidate_grids=dict(ridge_alphas=[float(a) for a in tu.RIDGE_ALPHAS], histgb_space=dict(
                      learning_rate=tu.HISTGB_LR, max_iter=tu.HISTGB_MAX_ITER, max_leaf_nodes=tu.HISTGB_LEAVES,
                      min_samples_leaf=tu.HISTGB_MIN_LEAF, l2_regularization=tu.HISTGB_L2,
                      n_random=tu.N_RANDOM_HISTGB, search_seed=tu.SEARCH_SEED)),
                  inner_seed_offset=tu.INNER_SEED_OFFSET, inner_missed_ceiling=tu.INNER_MISSED_CEIL,
                  model_hyperparameters=[dict(seed=f["seed"], family=f["family"], tag=f["tag"], config=f["config"]) for f in fits],
                  omp_num_threads=os.environ.get("OMP_NUM_THREADS", "unset"))
    man = sm.build_manifest([op], "scratch/n13_gate.py", [".venv/bin/python", "scratch/n13_gate.py", NAME],
                            [path, "data/solve_time.json", "scripts/tune_surrogates.py", "scratch/n13_decision_rule.md"], params, "")
    man["no_new_solves"] = "No AC solve. Model fits: full tune_surrogates search + M2 refits per seed."
    sm.write_manifest(man, op)
    print(f"wrote {op}; wall {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
