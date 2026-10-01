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

# N11 relabel driver for the floor builds: scratch/n9_relabel.py with the generator voltage floor as a fifth
# argument (N9 hardcoded 0.95). Otherwise unchanged.
# (N9 header follows) N9 relabel driver: the scratch/n5_relabel095.py procedure with the dataset, shard seeds and output as
# arguments. PV/PQ switch-back relabel (scripts/sts_n2_label_audit.py replay_shard + audit_scenario,
# imported unchanged). Scenarios are replayed with GEN_VM_LO = 0.95 set inside each worker. 4 workers,
# one parquet per shard seed in the shard directory, finished shards skipped on restart.
#
# argv: dataset_path  shard_seeds(comma)  output_parquet  shard_dir  gen_vm_lo
# example: data/sts_n11_floor093.parquet 100,101,102,103 data/sts_n11_floor093_relabel.parquet scratch/n11_relabel_floor093_shards 0.93

FLOOR = float(sys.argv[5]) if len(sys.argv) > 5 else 0.95
NPROC = 4
LIMIT = 0.94
FAIL_CEIL = 0.005


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


def deepest_row(res):
    n1 = res[res["outaged_type"] != "none"]
    i = n1["stored_min_vm"].idxmin()
    r = n1.loc[i]
    return dict(scenario_id=int(r["scenario_id"]), outaged_type=str(r["outaged_type"]),
                outaged_idx=int(r["outaged_idx"]), stored_min_vm=float(r["stored_min_vm"]),
                corrected_status=str(r["corrected_status"]), corrected_min_vm=float(r["corrected_min_vm"]),
                corrected_violation=bool(r["corrected_min_vm"] < LIMIT),
                n_inconsistent_absorbing=int(r["n_inconsistent_absorbing"]),
                n_inconsistent_injecting=int(r["n_inconsistent_injecting"]),
                n_outer_iter=int(r["n_outer_iter"]))


def main():
    data_path = sys.argv[1]
    seeds = [int(s) for s in sys.argv[2].split(",")]
    out = sys.argv[3]
    shard_dir = sys.argv[4]
    out_json = out.replace(".parquet", ".json")
    t0 = time.time()
    os.makedirs(shard_dir, exist_ok=True)
    df = pd.read_parquet(data_path, columns=["scenario_id", "outaged_type", "outaged_idx", "converged",
                                             "min_vm", "n0_min_vm"])
    per = n2.N_TOTAL // len(seeds)
    ml = n2.mode_lists()
    tasks = []
    for w, s in enumerate(seeds):
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
    if n0_diffs.max() != 0.0 or len(n0_diffs) != stored_n0.shape[0]:
        raise ValueError("replay does not reproduce the stored N-0 minima; stop")

    conv = df[df["converged"]]
    by_scen = {}
    for sid, ot, oi, mv in zip(conv["scenario_id"].to_numpy(), conv["outaged_type"].to_numpy(),
                               conv["outaged_idx"].to_numpy(), conv["min_vm"].to_numpy(np.float64)):
        by_scen.setdefault(int(sid), []).append((str(ot), int(oi), float(mv)))

    shard_files = []
    shard_walls = {}
    for sh in shards:
        path = os.path.join(shard_dir, f"shard_{sh['seed0']}.parquet")
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
    res.to_parquet(out, index=False)
    summ = summarize(res)
    checks = dict(replay_n0_exact=bool(n0_diffs.max() == 0.0),
                  resolve_min_vm_exact=bool(summ["max_repro_abs_diff"] == 0.0),
                  failed_share_le_0p5pct=bool(summ["n1_failed_share"] <= FAIL_CEIL))
    wall = time.time() - t0
    result = dict(question=f"N11 switch-back relabel of {data_path} (N2 method), GEN_VM_LO={FLOOR}",
                  method="scripts/sts_n2_label_audit.py replay_shard + audit_scenario, unchanged; replay with GEN_VM_LO set to the build floor",
                  shard_seeds=seeds, replay_n0_max_abs_diff=float(n0_diffs.max()), replay_n_scenarios=int(len(n0_diffs)),
                  rejects_per_shard=n_reject, shard_wall_s=shard_walls, wall_s=wall, checks=checks,
                  summary=summ, deepest_stored_row=deepest_row(res))
    with open(out_json, "w") as f:
        json.dump(result, f, indent=2)
    params = dict(gen_vm_lo=FLOOR, nproc=NPROC, limit=LIMIT, shard_seeds=seeds, n_total=n2.N_TOTAL,
                  switchback_tol_q=n2.TOL_Q, switchback_tol_v=n2.TOL_V, switchback_max_outer=n2.MAX_OUTER,
                  solver="pandapower runpp enforce_q_lims=True init=dc numba=True (pinned)",
                  model_hyperparameters="none (no model fit)")
    man = sm.build_manifest([out, out_json], "scratch/n11_relabel_floor.py", [".venv/bin/python", "scratch/n11_relabel_floor.py"] + sys.argv[1:],
                            [data_path, "scripts/sts_n2_label_audit.py", "feasibility/generate_dataset.py"], params, "")
    man["no_new_solves"] = "FALSE: this run re-solves every converged row with the pinned solver and runs the switch-back loop"
    sm.write_manifest(man, out)
    print(json.dumps(dict(checks=checks, summary=summ, deepest=result["deepest_stored_row"]), indent=1))
    if not checks["failed_share_le_0p5pct"]:
        print("STOP: failed share above 0.5%", flush=True)


if __name__ == "__main__":
    main()
