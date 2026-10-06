import os
import sys
import json
import time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import manifest as mf
import tune_surrogates as tu
import sts_manifest as sm
import n5_gate_eval as n5
import n10_gate_illinois as il
import n14_common as cm

# N14 gate (scratch/n14_decision_rule.md §A, §B): the N13 arm-S gate procedure (full M2 re-search, held-out target,
# outer splits seeds 0-4, rule-B accounting) on a rebuilt N13 dataset with outages removed per the mode.
# argv: name (D94 | ILL | C30 | C24)  mode (primary | sensitivity)
#   D94: scratch/n5_gate_eval.py run_seed; others: scratch/n10_gate_illinois.py run_seed (as N13 / N10 / N11).
# Output: data/sts_n14_gate_<name>.json (primary) or data/sts_n14_gate_<name>_sens.json (sensitivity), + manifest.

NAME = sys.argv[1] if len(sys.argv) > 1 else "C24"
MODE = sys.argv[2] if len(sys.argv) > 2 else "primary"
SEEDS = [0, 1, 2, 3, 4]


def main():
    t0 = time.time()
    h = cm.check_hash()
    ms_solver = mf.load_solve_time()["ms_solver"]
    r_cands = tu.ridge_candidates()
    h_cands = tu.histgb_candidates()
    d = cm.load(NAME, MODE)
    print(json.dumps(d["info"]), flush=True)
    search, sel, fits, points, curves, conc = [], {}, [], [], [], []
    for seed in SEEDS:
        if NAME == "D94":
            s, se, f, p = n5.run_seed(d["df"], d["X"], d["y"], d["groups"], seed, ms_solver, r_cands, h_cands, d["elem_key"])
        else:
            s, se, f, p, cv, co = il.run_seed(d["df"], d["X"], d["y"], d["groups"], seed, ms_solver, r_cands, h_cands, d["elem_key"])
            curves.extend(cv)
            co["seed"] = seed
            conc.append(co)
        search.extend(s)
        sel[str(seed)] = se
        fits.extend(f)
        points.extend(p)
        hp = [q for q in p if q["family"] == "histgb" and q["point"] == "held_out"]
        if hp:
            print(f"{NAME} {MODE} seed {seed}: histgb held-out {hp[0]['target']:.2f} esc {100 * hp[0]['escalation']:.1f}% missed "
                  f"{100 * hp[0]['missed']:.2f}% catch {100 * hp[0]['gate_catch']:.2f} static_B {100 * hp[0]['static_catch_B']:.2f}", flush=True)
    op = f"data/sts_n14_gate_{NAME}.json" if MODE == "primary" else f"data/sts_n14_gate_{NAME}_sens.json"
    out = dict(run=f"N14 gate, {NAME}, {MODE}", decision_rule_sha256=h, dataset=f"data/sts_n13_{NAME}.parquet", labels=d["info"],
               seeds=SEEDS, limit=0.94, ms_solver=ms_solver, selections=sel, fits=fits, points=points,
               curves_at_declared_k=curves, concentration=conc, search=search, wall_s=time.time() - t0)
    with open(op, "w") as f:
        json.dump(out, f, indent=2)
    params = dict(seeds=SEEDS, mode=MODE, excluded_outages=d["info"]["removed_outages"], invocation=f"scratch/n14_gate.py {NAME} {MODE}",
                  candidate_grids=dict(ridge_alphas=[float(a) for a in tu.RIDGE_ALPHAS], histgb_space=dict(
                      learning_rate=tu.HISTGB_LR, max_iter=tu.HISTGB_MAX_ITER, max_leaf_nodes=tu.HISTGB_LEAVES,
                      min_samples_leaf=tu.HISTGB_MIN_LEAF, l2_regularization=tu.HISTGB_L2, n_random=tu.N_RANDOM_HISTGB,
                      search_seed=tu.SEARCH_SEED)),
                  model_hyperparameters=[dict(seed=f["seed"], family=f["family"], tag=f["tag"], config=f["config"]) for f in fits],
                  omp_num_threads=os.environ.get("OMP_NUM_THREADS", "unset"))
    man = sm.build_manifest([op], "scratch/n14_gate.py", [".venv/bin/python", "scratch/n14_gate.py", NAME, MODE],
                            [f"data/sts_n13_{NAME}.parquet", "data/solve_time.json", cm.RULE], params, "")
    man["no_new_solves"] = "No AC solve. Model fits: full tune_surrogates search + M2 refits per seed."
    sm.write_manifest(man, op)
    print(f"wrote {op}; wall {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
