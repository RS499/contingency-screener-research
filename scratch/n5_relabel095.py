import os
import sys
import json
import time
import multiprocessing
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import generate_dataset as gd
import sts_n2_label_audit as n2
import sts_manifest as sm

# N5 Step 2: relabel data/sts_n3_floor095.parquet with the PV/PQ switch-back method of
# scripts/sts_n2_label_audit.py (functions imported unchanged: replay_shard, audit_scenario).
# The only difference from N2 is the generator voltage floor used to replay the scenarios:
# GEN_VM_LO = 0.95, as in scratch/n3_floor_rebuild.py. Every converged row is re-solved with the
# pinned solver; rows with a generator whose Q-limit state contradicts its voltage get the
# switch-back outer loop. 4 workers. Progress: one parquet per RNG shard in SHARD_DIR, skipped
# on restart if already present.

DATASET = "data/sts_n3_floor095.parquet"
OUT = "data/sts_n5_relabel095.parquet"
OUT_JSON = "data/sts_n5_relabel095.json"
SHARD_DIR = "scratch/n5_relabel095_shards"
FLOOR = 0.95
NPROC = 4
LIMIT = 0.94


def replay_with_floor(task):
    gd.GEN_VM_LO = FLOOR
    return n2.replay_shard(task)


def summarize(res):
    n1 = res[res["outaged_type"] != "none"]
    ok = n1["corrected_status"].isin(["converged", "not_needed"])
    v = n1.loc[ok, "corrected_min_vm"].to_numpy()
    counts = n1["corrected_status"].value_counts()
    status = {}
    for k in counts.index:
        status[str(k)] = int(counts[k])
    return dict(
        n1_rows=int(len(n1)),
        status_counts=status,
        n1_failed=int((~ok).sum()),
        n1_failed_share=float((~ok).mean()),
        n1_needing_switchback=int((n1["n_inconsistent_absorbing"] + n1["n_inconsistent_injecting"] > 0).sum()),
        max_repro_abs_diff=float(n1["repro_abs_diff"].max()),
        flip_viol_to_safe=int(n1["flip_viol_to_safe"].sum()),
        flip_safe_to_viol=int(n1["flip_safe_to_viol"].sum()),
        stored_violation_rate=float(n1.loc[ok, "stored_violation"].mean()),
        corrected_violation_rate=float((v < LIMIT).mean()),
        corrected_boundary_mass=float(((v >= 0.94) & (v < 0.945)).mean()))


def main():
    t0 = time.time()
    os.makedirs(SHARD_DIR, exist_ok=True)
    df = pd.read_parquet(DATASET, columns=["scenario_id", "outaged_type", "outaged_idx", "converged",
                                           "min_vm", "n0_min_vm"])
    per = n2.N_TOTAL // len(n2.SHARD_SEEDS)
    ml = n2.mode_lists()
    tasks = []
    for w, s in enumerate(n2.SHARD_SEEDS):
        tasks.append((s, per, ml[w]))
    with multiprocessing.Pool(NPROC) as pool:
        shards = pool.map(replay_with_floor, tasks)
    t_replay = time.time() - t0

    stored_n0 = df.drop_duplicates("scenario_id").set_index("scenario_id")["n0_min_vm"]
    n0_diffs = []
    n_reject = {}
    for sh in shards:
        n_reject[str(sh["seed0"])] = sh["n_reject"]
        for sc in sh["scenarios"]:
            n0_diffs.append(abs(sc["n0_min_vm"] - float(stored_n0.loc[sc["scenario_id"]])))
    n0_diffs = np.array(n0_diffs)
    print(f"replay {t_replay:.1f}s; scenarios {len(n0_diffs)}; max |n0_min_vm diff| {n0_diffs.max():.3e}; "
          f"rejects {n_reject}", flush=True)
    if n0_diffs.max() != 0.0:
        raise ValueError("replay does not reproduce the stored N-0 minima; stop")

    conv = df[df["converged"]]
    by_scen = {}
    for sid, ot, oi, mv in zip(conv["scenario_id"].to_numpy(), conv["outaged_type"].to_numpy(),
                               conv["outaged_idx"].to_numpy(), conv["min_vm"].to_numpy(np.float64)):
        by_scen.setdefault(int(sid), []).append((str(ot), int(oi), float(mv)))

    shard_files = []
    shard_walls = {}
    for sh in shards:
        path = os.path.join(SHARD_DIR, f"shard_{sh['seed0']}.parquet")
        shard_files.append(path)
        if os.path.exists(path):
            print(f"shard {sh['seed0']}: already done, skipped", flush=True)
            continue
        ts = time.time()
        atasks = [(sc, by_scen[sc["scenario_id"]]) for sc in sh["scenarios"]]
        with multiprocessing.Pool(NPROC) as pool:
            parts = pool.map(n2.audit_scenario, atasks, chunksize=4)
        recs = []
        for p in parts:
            recs.extend(p)
        pd.DataFrame(recs).to_parquet(path, index=False)
        shard_walls[str(sh["seed0"])] = time.time() - ts
        print(f"shard {sh['seed0']}: {len(recs)} rows in {shard_walls[str(sh['seed0'])]:.1f}s", flush=True)

    res = pd.concat([pd.read_parquet(p) for p in shard_files], ignore_index=True)
    res["repro_abs_diff"] = (res["resolved_min_vm"] - res["stored_min_vm"]).abs()
    res["stored_violation"] = res["stored_min_vm"] < LIMIT
    res["corrected_violation"] = res["corrected_min_vm"] < LIMIT
    ok = res["corrected_status"].isin(["converged", "not_needed"])
    res["flip_viol_to_safe"] = ok & res["stored_violation"] & (~res["corrected_violation"])
    res["flip_safe_to_viol"] = ok & (~res["stored_violation"]) & res["corrected_violation"]
    res.to_parquet(OUT, index=False)
    summ = summarize(res)
    wall = time.time() - t0
    out = dict(question="N5 step 2: switch-back relabel of the 0.95-floor dataset (N2 method)",
               method="scripts/sts_n2_label_audit.py replay_shard + audit_scenario, unchanged; replay with GEN_VM_LO=0.95",
               replay_n0_max_abs_diff=float(n0_diffs.max()), replay_n_scenarios=int(len(n0_diffs)),
               rejects_per_shard=n_reject, shard_wall_s=shard_walls, wall_s=wall, summary=summ)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    params = dict(gen_vm_lo=FLOOR, nproc=NPROC, limit=LIMIT, shard_seeds=n2.SHARD_SEEDS, n_total=n2.N_TOTAL,
                  switchback_tol_q=n2.TOL_Q, switchback_tol_v=n2.TOL_V, switchback_max_outer=n2.MAX_OUTER,
                  solver="pandapower runpp enforce_q_lims=True init=dc numba=True (pinned)",
                  model_hyperparameters="none (no model fit)")
    man = sm.build_manifest([OUT, OUT_JSON], "scratch/n5_relabel095.py", [".venv/bin/python", "scratch/n5_relabel095.py"],
                            [DATASET, "scripts/sts_n2_label_audit.py", "feasibility/generate_dataset.py"], params, "")
    man["no_new_solves"] = "FALSE: this run re-solves every converged row with the pinned solver and runs the switch-back loop"
    sm.write_manifest(man, OUT)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
