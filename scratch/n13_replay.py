import os
import sys
import json
import time
import multiprocessing
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import n13_common as c
import generate_dataset as gd
import sts_n2_label_audit as n2
import n10_relabel_illinois as n10r
import n11_relabel_net as n11r
import sts_manifest as sm

# N13 Step 2, check 1 (scratch/n13_decision_rule.md §2): replay each original build N-0 only with its original
# pinned acceptance and confirm every stored n0_min_vm reproduces exactly. Replays use the existing functions:
# case118 builds: scripts/sts_n2_label_audit.py replay_shard (GEN_VM_LO = the build's floor, shard seeds);
# ILL: scratch/n10_relabel_illinois.py replay; C30, C24: scratch/n11_relabel_net.py replay (network set by module
# attributes, no file edited). generate_dataset.solve_n0 is wrapped (n13_common, mode "pinned") only to log each
# draw's parameter hash and N-0 result. N2R uses the D94 base cases, so its check 1 is D94's.
# Outputs: data/sts_n13_replaycheck.json (+ manifest); per-shard draw logs scratch/n13_drawlog_old_<name>_<shard>.parquet
# (used later for the shared-prefix and base-set comparisons).

OUT = "data/sts_n13_replaycheck.json"
LOG_DIR = "scratch/n13_drawlogs"
NPROC = 8


def replay_task(task):
    name, seed = task
    spec = c.DATASETS[name]
    path = os.path.join(LOG_DIR, f"old_{name}_{seed}.parquet")
    t0 = time.time()
    if spec["kind"] == "case118":
        c.install("pinned", "case118")
        gd.GEN_VM_LO = spec["floor"]
        w = spec["seeds"].index(seed)
        rep = n2.replay_shard((seed, n2.N_TOTAL // len(n2.SHARD_SEEDS), n2.mode_lists()[w]))
        scenarios = rep["scenarios"]
        extra = dict(n_reject=rep["n_reject"])
    elif name == "ILL":
        c.install("pinned", "other")
        scenarios, draws, rejected, cfg = n10r.replay()
        extra = dict(draws=draws, rejected=rejected, cfg=cfg)
    else:
        c.install("pinned", "other")
        n11r.NETWORK = spec["network"]
        n11r.DATASET = spec["file"]
        n11r.BUILD_STATS = spec["stats"]
        scenarios, draws, rejected, cfg = n11r.replay()
        extra = dict(draws=draws, rejected=rejected, cfg=cfg)
    log = pd.DataFrame(c.STATE["n0_log"])
    acc_hash = [c.params_hash(sc["params"]) for sc in scenarios]
    acc_sid = {}
    for h, sc in zip(acc_hash, scenarios):
        acc_sid[h] = int(sc["scenario_id"])
    log["accepted"] = log["params_hash"].isin(set(acc_hash))
    log["scenario_id"] = log["params_hash"].map(acc_sid).fillna(-1).astype(np.int64)
    log["shard_seed"] = seed
    log.to_parquet(path, index=False)
    stored = c.stored_n0(spec["file"])
    rep_n0 = np.array([sc["n0_min_vm"] for sc in scenarios], dtype=np.float64)
    st = stored.reindex([int(sc["scenario_id"]) for sc in scenarios]).to_numpy(np.float64)
    diffs = np.abs(rep_n0 - st)
    return dict(name=name, shard_seed=seed, n_draws=int(len(log)), n_accepted=int(len(scenarios)),
                n_accepted_flagged=int(log["accepted"].sum()), max_abs_n0_diff=float(np.nanmax(diffs)),
                n_nan=int(np.isnan(diffs).sum()), exact=bool(np.nanmax(diffs) == 0.0 and not np.isnan(diffs).any()),
                wall_s=time.time() - t0, extra=extra, draw_log=path)


def main():
    t0 = time.time()
    os.makedirs(LOG_DIR, exist_ok=True)
    tasks = []
    for name in c.DATASETS:
        spec = c.DATASETS[name]
        if spec["kind"] == "case118":
            for s in spec["seeds"]:
                tasks.append((name, s))
        else:
            tasks.append((name, 100))
    with multiprocessing.Pool(NPROC) as pool:
        res = pool.map(replay_task, tasks)
    per = {}
    for r in res:
        per.setdefault(r["name"], []).append(r)
    summary = {}
    for name in c.DATASETS:
        rows = per[name]
        stored = c.stored_n0(c.DATASETS[name]["file"])
        n_acc = sum([r["n_accepted"] for r in rows])
        ok = bool(all([r["exact"] for r in rows]) and n_acc == len(stored))
        summary[name] = dict(check1_passed=ok, n_accepted_total=n_acc, n_stored_bases=int(len(stored)),
                             max_abs_n0_diff=max([r["max_abs_n0_diff"] for r in rows]),
                             n_draws_total=sum([r["n_draws"] for r in rows]))
        print(f"{name}: check 1 {'PASS' if ok else 'FAIL'} | accepted {n_acc} / stored {len(stored)} | draws "
              f"{summary[name]['n_draws_total']} | max |n0 diff| {summary[name]['max_abs_n0_diff']:.3e}", flush=True)
    summary["N2R"] = dict(check1_passed=summary["D94"]["check1_passed"], note="N2R uses the D94 base cases; check 1 is D94's")
    out = dict(check="N13 check 1: original pinned acceptance replay, N-0 only; stored n0_min_vm reproduced exactly",
               summary=summary, per_shard=res, wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, default=str)
    inputs = ["scratch/n13_decision_rule.md"]
    for name in c.DATASETS:
        inputs.append(c.DATASETS[name]["file"])
        if "stats" in c.DATASETS[name]:
            inputs.append(c.DATASETS[name]["stats"])
    man = sm.build_manifest([OUT], "scratch/n13_replay.py", [".venv/bin/python", "scratch/n13_replay.py"], inputs,
                            dict(datasets=c.DATASETS, seeds="per dataset (see datasets)", nproc=NPROC,
                                 solver="pandapower runpp enforce_q_lims=True init=dc numba=True (pinned, original acceptance)",
                                 model_hyperparameters="none (no model fit)"), "")
    man["no_new_solves"] = "FALSE: N-0 pinned solves of every original draw (replay)"
    sm.write_manifest(man, OUT)


if __name__ == "__main__":
    main()
