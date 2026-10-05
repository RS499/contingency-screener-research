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
import case30_thermal as H
import case30_thermal_build as c30b
import sts_n2_label_audit as n2
import sts_manifest as sm

# N13 Step 3 (scratch/n13_decision_rule.md §1): rebuild one dataset with the corrected solver.
# argv[1] = dataset name (n13_common.DATASETS). Every power-flow solve is the corrected solve (n13_common: pinned,
# then the N2 switch-back where needed), used for acceptance, inputs (vm0_*, n0_min_vm) and labels.
# Phase 1 (draws): the original accept loop, one process per RNG stream:
#   case118: generate_dataset.worker's loop (mode_list[accepted], GATE_N0 voltage check, max_rejects), GEN_VM_LO =
#            the build floor, committed invocation (scripts/sts_n2_label_audit.CFG), seeds as in the original build;
#   ILL, C24: scripts/netstudy.py phase 1a's loop (modes[accepted % 2], case30_thermal.n0_feasible, thermal on);
#   C30: scripts/case30_thermal_build.build's loop (same predicate, thermal on).
#   The loop glue is copied (as the N10/N11 replays did); every function it calls is imported unchanged.
#   An N-0 draw whose switch-back fails returns n0_conv = False and is rejected; its reason is recorded as
#   "N-0 correction failed" (pinned non-convergence stays "nonconvergence").
# Phase 2 (rows): per accepted base, generate_dataset.run_scenario (C30: case30_thermal_build.contingency_rows),
#   in parallel chunks of CHUNK bases; the base is re-applied with solve_n0 (checked equal to phase 1). Rows of a
#   failed outage switch-back keep converged = False. The dataset keeps exactly the original schema; audit columns
#   (pinned minima, status, outer iterations) go to data/sts_n13_audit_<name>.parquet.
# Restart: phase-1 files and phase-2 chunk files are skipped if present.

NAME = sys.argv[1] if len(sys.argv) > 1 else "D94"
WORK = f"scratch/n13_build/{NAME}"
CHUNK = 25
NPROC = 8
N_TOTAL = 1500
LIMIT = 0.94


def kind_of(spec):
    if spec["kind"] == "case118":
        return "case118"
    return "other"


def cfg_other(spec):
    bs = json.load(open(spec["stats"]))
    bs = bs.get("stats", bs)
    lo = bs["range"]["lo"]
    hi = bs["range"]["hi"]
    return dict(network=spec["network"], stress="fixed", mult_lo=lo, mult_hi=hi, reg_lo=lo, reg_hi=hi,
                pf_lo=0.9, pf_hi=1.15, dvm=0.025)


def reason_of(n0_conv, n0_info, ok_reason):
    if n0_conv:
        return ok_reason
    st = (n0_info or {}).get("status")
    if st == "pinned_nonconverged" or st is None:
        return "nonconvergence"
    return "n0_correction_failed"


def phase1_case118(task):
    name, seed = task
    spec = c.DATASETS[name]
    out = os.path.join(WORK, f"phase1_{seed}.json")
    if os.path.exists(out):
        return out
    c.install("corrected", "case118")
    gd.apply_config(n2.CFG)
    gd.GEN_VM_LO = spec["floor"]
    w = spec["seeds"].index(seed)
    n_scen = N_TOTAL // len(spec["seeds"])
    mode_list = n2.mode_lists()[w]
    net = gd.build_net("case118")
    load_region, n_regions = gd.region_of_load(net)
    rng = np.random.default_rng(seed)
    acc = []
    rejected = dict(nonconvergence=0, voltage=0, n0_correction_failed=0)
    accepted = 0
    n_reject = 0
    max_rejects = n_scen * gd.MAX_REJECT_FACTOR
    while accepted < n_scen and n_reject <= max_rejects:
        this_mode = mode_list[accepted]
        params = gd.sample_scenario(rng, net, this_mode, load_region, n_regions, stress="fixed")
        n0_conv, vm0, n0_min_vm = gd.solve_n0(net, params)
        if gd.GATE_N0 and (not n0_conv or n0_min_vm < gd.VMIN_LIMIT):
            n_reject += 1
            rejected[reason_of(n0_conv, c.STATE["n0_info"], "voltage")] += 1
            continue
        acc.append(dict(scenario_id=seed * 1_000_000 + accepted, mode=this_mode, draw=c.STATE["draw"],
                        params=c.params_jsonable(params), params_hash=c.params_hash(params), n0_min_vm=float(n0_min_vm),
                        n0_info=c.STATE["n0_info"]))
        accepted += 1
    pd.DataFrame(c.STATE["n0_log"]).assign(shard_seed=seed).to_parquet(os.path.join(WORK, f"n0log_{seed}.parquet"), index=False)
    with open(out, "w") as f:
        json.dump(dict(shard_seed=seed, accepted=acc, n_draws=len(c.STATE["n0_log"]), rejected=rejected,
                       n_reject=n_reject), f)
    return out


def phase1_other(name):
    spec = c.DATASETS[name]
    out = os.path.join(WORK, "phase1_100.json")
    if os.path.exists(out):
        return out
    c.install("corrected", "other")
    cfg = cfg_other(spec)
    H.NETWORK = spec["network"]
    gd.apply_config(cfg)
    net = gd.build_net(spec["network"])
    if spec["kind"] == "case30":
        H.assert_ratings_usable(net, spec["network"])
    load_region, n_regions = gd.region_of_load(net)
    rng = np.random.default_rng(100)
    modes = ("independent", "regional")
    acc = []
    rejected = dict(nonconvergence=0, voltage=0, thermal=0, n0_correction_failed=0)
    accepted = 0
    draws = 0
    max_draws = N_TOTAL * gd.MAX_REJECT_FACTOR
    while accepted < N_TOTAL and draws < max_draws:
        draws += 1
        this_mode = modes[accepted % 2]
        params = gd.sample_scenario(rng, net, this_mode, load_region, n_regions, stress="fixed")
        n0_conv, vm0, n0_min_vm = gd.solve_n0(net, params)
        load_pct = H.max_loading_pct(net) if n0_conv else np.nan
        ok, reason = H.n0_feasible(n0_conv, n0_min_vm, load_pct, thermal=True)
        if not ok:
            rejected[reason_of(n0_conv, c.STATE["n0_info"], reason)] += 1
            continue
        acc.append(dict(scenario_id=100 * 1_000_000 + accepted, mode=this_mode, draw=c.STATE["draw"],
                        params=c.params_jsonable(params), params_hash=c.params_hash(params), n0_min_vm=float(n0_min_vm),
                        n0_info=c.STATE["n0_info"], load_pct=float(load_pct)))
        accepted += 1
    pd.DataFrame(c.STATE["n0_log"]).assign(shard_seed=100).to_parquet(os.path.join(WORK, "n0log_100.parquet"), index=False)
    with open(out, "w") as f:
        json.dump(dict(shard_seed=100, accepted=acc, n_draws=draws, rejected=rejected, cfg=cfg), f)
    return out


def phase2_chunk(task):
    name, k, bases = task
    spec = c.DATASETS[name]
    path = os.path.join(WORK, f"rows_{k:04d}.parquet")
    apath = os.path.join(WORK, f"audit_{k:04d}.parquet")
    if os.path.exists(path) and os.path.exists(apath):
        return path
    if spec["kind"] == "case118":
        c.install("corrected", "case118")
        gd.apply_config(n2.CFG)
        gd.GEN_VM_LO = spec["floor"]
        network = "case118"
    else:
        c.install("corrected", "other")
        gd.apply_config(cfg_other(spec))
        network = spec["network"]
    net = gd.build_net(network)
    branches = gd.branch_list(net)
    rows = []
    n0_mismatch = 0
    for b in bases:
        params = c.params_from_json(b["params"])
        c.STATE["scen"] = -1
        n0_conv, vm0, n0_min_vm = gd.solve_n0(net, params)
        if (not n0_conv) or float(n0_min_vm) != b["n0_min_vm"]:
            n0_mismatch += 1
        c.STATE["scen"] = b["scenario_id"]
        if spec["kind"] == "case30":
            r, _loading = c30b.contingency_rows(net, branches, params, b["scenario_id"], b["mode"], n0_conv, vm0, n0_min_vm)
        else:
            r = gd.run_scenario(net, branches, params, b["scenario_id"], b["mode"], n0_conv, vm0, n0_min_vm)
        rows.extend(r)
    gd.rows_to_frame(rows).to_parquet(path, index=False)
    pd.DataFrame(c.STATE["audit"]).to_parquet(apath, index=False)
    with open(os.path.join(WORK, f"chunkinfo_{k:04d}.json"), "w") as f:
        json.dump(dict(chunk=k, n_bases=len(bases), n0_rebuild_mismatch=n0_mismatch), f)
    return path


def main():
    t0 = time.time()
    spec = c.DATASETS[NAME]
    os.makedirs(WORK, exist_ok=True)
    if spec["kind"] == "case118":
        tasks = [(NAME, s) for s in spec["seeds"]]
        with multiprocessing.Pool(len(tasks)) as pool:
            p1 = pool.map(phase1_case118, tasks)
    else:
        p1 = [phase1_other(NAME)]
    t1 = time.time() - t0
    phase1 = [json.load(open(p)) for p in p1]
    bases = []
    for ph in phase1:
        bases.extend(ph["accepted"])
    print(f"{NAME}: phase 1 done, {len(bases)} accepted, draws {sum([ph['n_draws'] for ph in phase1])} [{t1:.0f}s]", flush=True)
    chunks = []
    for k in range(0, len(bases), CHUNK):
        chunks.append((NAME, k // CHUNK, bases[k:k + CHUNK]))
    with multiprocessing.Pool(NPROC) as pool:
        done = 0
        for p in pool.imap(phase2_chunk, chunks):
            done += 1
            if done % 10 == 0 or done == len(chunks):
                print(f"{NAME}: chunk {done}/{len(chunks)} [{time.time() - t0:.0f}s]", flush=True)
    frames = [pd.read_parquet(os.path.join(WORK, f"rows_{k:04d}.parquet")) for k in range(len(chunks))]
    df = pd.concat(frames, ignore_index=True)
    audit = pd.concat([pd.read_parquet(os.path.join(WORK, f"audit_{k:04d}.parquet")) for k in range(len(chunks))],
                      ignore_index=True)
    orig = pd.read_parquet(spec["file"])
    same_cols = list(df.columns) == list(orig.columns)
    dtype_diff = [col for col in orig.columns if col in df.columns and df[col].dtype != orig[col].dtype]
    df.to_parquet(f"data/sts_n13_{NAME}.parquet", index=False)
    # audit: N-0 rows from phase 1, outage rows from phase 2
    n0a = []
    for b in bases:
        info = b["n0_info"] or {}
        n0a.append(dict(scenario_id=b["scenario_id"], outaged_type="none", outaged_idx=-1, status=info.get("status"),
                        pinned_min=info.get("pinned_min"), corrected_min=info.get("corrected_min"),
                        n_outer=info.get("n_outer", 0), params_hash=b["params_hash"], draw=b["draw"]))
    a1 = audit.rename(columns={"scen": "scenario_id"})[["scenario_id", "outaged_type", "outaged_idx", "status",
                                                        "pinned_min", "corrected_min", "n_outer"]]
    aud = pd.concat([pd.DataFrame(n0a), a1], ignore_index=True)
    aud.to_parquet(f"data/sts_n13_audit_{NAME}.parquet", index=False)
    n0log = pd.concat([pd.read_parquet(os.path.join(WORK, f"n0log_{ph['shard_seed']}.parquet")) for ph in phase1],
                      ignore_index=True)
    n0log.to_parquet(os.path.join(WORK, "n0log_all.parquet"), index=False)
    rej = {}
    for ph in phase1:
        for k in ph["rejected"]:
            rej[k] = rej.get(k, 0) + ph["rejected"][k]
    info = dict(name=NAME, n_accepted=len(bases), n_draws=sum([ph["n_draws"] for ph in phase1]), rejected=rej,
                schema_same_columns=same_cols, schema_dtype_differences=dtype_diff,
                n0_rebuild_mismatches=sum([json.load(open(os.path.join(WORK, f"chunkinfo_{k:04d}.json")))["n0_rebuild_mismatch"]
                                           for k in range(len(chunks))]),
                phase1_wall_s=t1, wall_s=time.time() - t0)
    with open(os.path.join(WORK, "build_info.json"), "w") as f:
        json.dump(info, f, indent=2)
    print(json.dumps(info, indent=1), flush=True)


if __name__ == "__main__":
    main()
