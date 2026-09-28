import os
import sys
import json
import time
import hashlib
import argparse
import subprocess
import multiprocessing
import numpy as np
import pandas as pd
import pandapower as pp

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
import generate_dataset as gd
import manifest as mf

# N2: Q-limit label audit. Replays the committed generator RNG exactly (seeds 100-103, 375 accepted
# scenarios each, mixed modes, committed invocation flags), re-solves every converged row with the
# pinned solver, and flags generators whose Q-limit state contradicts their voltage:
#   at Qmin (absorbing) while bus voltage is BELOW setpoint, or at Qmax (injecting) while ABOVE.
# pandapower's enforce_q_lims loop (pf/run_newton_raphson_pf.py) converts PV->PQ and never back.
# Rows with an inconsistent generator are re-solved with a PV/PQ switch-back outer loop.

DATASET = "data/dataset.parquet"
OUT_PARQUET = "data/sts_n2_label_audit.parquet"
LIMIT = 0.94

# committed invocation (data/dataset.manifest.json run_settings.invocation); stress defaults to "fixed"
CFG = dict(mult_lo=1.0, mult_hi=1.12, reg_lo=1.0, reg_hi=1.12, pf_lo=0.9, pf_hi=1.15, dvm=0.025,
           network="case118")
SHARD_SEEDS = [100, 101, 102, 103]
N_TOTAL = 1500
STRESS = "fixed"

TOL_Q = 1e-3
TOL_V = 1e-3
MAX_OUTER = 30
NPROC = 10


def mode_lists():
    modes = np.array(["independent", "regional"])
    full = list(modes[(np.arange(N_TOTAL) % 2)])
    per = N_TOTAL // len(SHARD_SEEDS)
    out = []
    for w in range(len(SHARD_SEEDS)):
        out.append(full[w * per:(w + 1) * per])
    return out


def replay_shard(task):
    seed0, n_scen, mlist = task
    gd.apply_config(CFG)
    net = gd.build_net("case118")
    load_region, n_regions = gd.region_of_load(net)
    rng = np.random.default_rng(seed0)
    out = []
    n_reject = 0
    accepted = 0
    while accepted < n_scen:
        params = gd.sample_scenario(rng, net, mlist[accepted], load_region, n_regions, stress=STRESS)
        n0_conv, vm0, n0_min_vm = gd.solve_n0(net, params)
        if gd.GATE_N0 and (not n0_conv or n0_min_vm < gd.VMIN_LIMIT):
            n_reject += 1
            continue
        scen_id = seed0 * 1_000_000 + accepted
        out.append(dict(scenario_id=scen_id, params=params, n0_min_vm=n0_min_vm))
        accepted += 1
    return dict(seed0=seed0, scenarios=out, n_reject=n_reject)


def pinned_solve(net):
    try:
        pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)
        return True
    except Exception:
        return False


def gen_check(net, fixed, gen_on):
    # per generator: Q, V, setpoint, and whether its limit state contradicts its voltage.
    # fixed: dict gen -> "min"/"max" for gens held as PQ by the switch-back loop (modelled as sgens);
    # gen_on: scenario in-service mask (a gen out for the scenario is never checked)
    qmin = net.gen.min_q_mvar.values
    qmax = net.gen.max_q_mvar.values
    vset = net.gen.vm_pu.values
    q = net.res_gen.q_mvar.values.copy()
    for gi in fixed:
        if fixed[gi] == "min":
            q[gi] = qmin[gi]
        else:
            q[gi] = qmax[gi]
    v = net.res_bus.vm_pu.values[net.gen.bus.values]
    at_min = gen_on & (q <= qmin + TOL_Q)
    at_max = gen_on & (q >= qmax - TOL_Q)
    bad_abs = at_min & (v < vset - TOL_V)
    bad_inj = at_max & (v > vset + TOL_V)
    return dict(at_min=at_min, at_max=at_max, bad_abs=bad_abs, bad_inj=bad_inj)


def add_pq_sgens(net):
    # one out-of-service sgen per generator, used to hold a gen as PQ at a fixed Q limit
    sgen_of = {}
    for gi in net.gen.index:
        s = pp.create_sgen(net, bus=int(net.gen.at[gi, "bus"]), p_mw=float(net.gen.at[gi, "p_mw"]),
                           q_mvar=0.0, in_service=False)
        sgen_of[int(gi)] = s
    net["_sgen_of"] = sgen_of


def apply_fixed(net, fixed, gen_on):
    gen_in = gen_on.copy()
    sg_in = np.zeros(len(net.sgen), dtype=bool)
    sg_q = np.zeros(len(net.sgen))
    for gi in fixed:
        s = net["_sgen_of"][gi]
        gen_in[gi] = False
        sg_in[s] = True
        if fixed[gi] == "min":
            sg_q[s] = float(net.gen.at[gi, "min_q_mvar"])
        else:
            sg_q[s] = float(net.gen.at[gi, "max_q_mvar"])
    net.gen["in_service"] = gen_in
    net.sgen["in_service"] = sg_in
    net.sgen["q_mvar"] = sg_q


def fixed_from_check(chk):
    # hold every consistent limited gen as PQ at its limit; inconsistent gens go back to PV
    fixed = {}
    keep_min = chk["at_min"] & (~chk["bad_abs"]) & (~chk["bad_inj"])
    keep_max = chk["at_max"] & (~chk["bad_abs"]) & (~chk["bad_inj"]) & (~chk["at_min"])
    for gi in np.flatnonzero(keep_min):
        fixed[int(gi)] = "min"
    for gi in np.flatnonzero(keep_max):
        fixed[int(gi)] = "max"
    return fixed


def corrected_solve(net, first_check, gen_on):
    # PV/PQ switch-back outer loop. Start from the pinned solution's limit set with every
    # inconsistent gen returned to PV. Each pass: pandapower enforces PV->PQ on the free gens;
    # this loop holds consistent limited gens as PQ and returns inconsistent ones to PV.
    # The caller restores the scenario gen/sgen state afterwards.
    fixed = fixed_from_check(first_check)
    history = []
    for it in range(1, MAX_OUTER + 1):
        apply_fixed(net, fixed, gen_on)
        if not pinned_solve(net):
            return dict(status="nonconverged", n_outer=it, min_vm=np.nan, argmin=-1, history=history)
        chk = gen_check(net, fixed, gen_on)
        n_bad = int((chk["bad_abs"] | chk["bad_inj"]).sum())
        history.append(n_bad)
        vm = net.res_bus.vm_pu.values
        if n_bad == 0:
            return dict(status="converged", n_outer=it, min_vm=float(np.nanmin(vm)),
                        argmin=int(np.nanargmin(vm)), history=history)
        fixed = fixed_from_check(chk)
    vm = net.res_bus.vm_pu.values
    return dict(status="iteration_cap", n_outer=MAX_OUTER, min_vm=float(np.nanmin(vm)),
                argmin=int(np.nanargmin(vm)), history=history)


def audit_scenario(task):
    scen, rows = task
    gd.apply_config(CFG)
    net = gd.build_net("case118")
    gd.apply_scenario(net, scen["params"])
    add_pq_sgens(net)
    gen_on = net.gen.in_service.values.copy()
    out = []
    for otype, oidx, stored in rows:
        if otype != "none":
            net[otype].at[oidx, "in_service"] = False
        ok = pinned_solve(net)
        rec = dict(scenario_id=scen["scenario_id"], outaged_type=otype, outaged_idx=oidx,
                   stored_min_vm=stored, resolved_converged=ok)
        if ok:
            vm = net.res_bus.vm_pu.values
            rec["resolved_min_vm"] = float(np.nanmin(vm))
            rec["resolved_argmin"] = int(np.nanargmin(vm))
            chk = gen_check(net, {}, gen_on)
            bad_abs = [int(g) for g in np.flatnonzero(chk["bad_abs"])]
            bad_inj = [int(g) for g in np.flatnonzero(chk["bad_inj"])]
            rec["n_at_qmin"] = int(chk["at_min"].sum())
            rec["n_at_qmax"] = int(chk["at_max"].sum())
            rec["n_inconsistent_absorbing"] = len(bad_abs)
            rec["n_inconsistent_injecting"] = len(bad_inj)
            rec["inconsistent_absorbing_gens"] = ",".join(str(g) for g in bad_abs)
            rec["inconsistent_injecting_gens"] = ",".join(str(g) for g in bad_inj)
            if len(bad_abs) + len(bad_inj) > 0:
                cs = corrected_solve(net, chk, gen_on)
                apply_fixed(net, {}, gen_on)
                rec["corrected_status"] = cs["status"]
                rec["corrected_min_vm"] = cs["min_vm"]
                rec["corrected_argmin"] = cs["argmin"]
                rec["n_outer_iter"] = cs["n_outer"]
                rec["outer_history"] = ",".join(str(h) for h in cs["history"])
            else:
                rec["corrected_status"] = "not_needed"
                rec["corrected_min_vm"] = rec["resolved_min_vm"]
                rec["corrected_argmin"] = rec["resolved_argmin"]
                rec["n_outer_iter"] = 0
                rec["outer_history"] = ""
        else:
            rec["resolved_min_vm"] = np.nan
            rec["resolved_argmin"] = -1
            rec["n_at_qmin"] = -1
            rec["n_at_qmax"] = -1
            rec["n_inconsistent_absorbing"] = -1
            rec["n_inconsistent_injecting"] = -1
            rec["inconsistent_absorbing_gens"] = ""
            rec["inconsistent_injecting_gens"] = ""
            rec["corrected_status"] = "pinned_nonconverged"
            rec["corrected_min_vm"] = np.nan
            rec["corrected_argmin"] = -1
            rec["n_outer_iter"] = 0
            rec["outer_history"] = ""
        if otype != "none":
            net[otype].at[oidx, "in_service"] = True
        out.append(rec)
    return out


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-scen", type=int, default=0, help="pilot: audit only the first K scenarios per shard")
    ap.add_argument("--out", type=str, default=OUT_PARQUET)
    args = ap.parse_args()
    t0 = time.time()

    df = pd.read_parquet(DATASET, columns=["scenario_id", "outaged_type", "outaged_idx", "converged",
                                           "min_vm", "n0_min_vm"])
    per = N_TOTAL // len(SHARD_SEEDS)
    tasks = []
    ml = mode_lists()
    for w, s in enumerate(SHARD_SEEDS):
        tasks.append((s, per, ml[w]))
    with multiprocessing.Pool(len(SHARD_SEEDS)) as pool:
        shards = pool.map(replay_shard, tasks)
    t_replay = time.time() - t0

    stored_n0 = df.drop_duplicates("scenario_id").set_index("scenario_id")["n0_min_vm"]
    scen_list = []
    n0_diffs = []
    n_reject = {}
    for sh in shards:
        n_reject[str(sh["seed0"])] = sh["n_reject"]
        for k, sc in enumerate(sh["scenarios"]):
            n0_diffs.append(abs(sc["n0_min_vm"] - float(stored_n0.loc[sc["scenario_id"]])))
            if args.max_scen and k >= args.max_scen:
                continue
            scen_list.append(sc)
    n0_diffs = np.array(n0_diffs)
    print(f"replay {t_replay:.1f}s; scenarios {len(n0_diffs)}; max |n0_min_vm diff| {n0_diffs.max():.3e}; "
          f"rejects {n_reject}", flush=True)

    conv = df[df["converged"]]
    by_scen = {}
    for sid, ot, oi, mv in zip(conv["scenario_id"].to_numpy(), conv["outaged_type"].to_numpy(),
                               conv["outaged_idx"].to_numpy(), conv["min_vm"].to_numpy(np.float64)):
        by_scen.setdefault(int(sid), []).append((str(ot), int(oi), float(mv)))
    atasks = [(sc, by_scen[sc["scenario_id"]]) for sc in scen_list]
    with multiprocessing.Pool(NPROC) as pool:
        parts = pool.map(audit_scenario, atasks, chunksize=4)
    recs = []
    for p in parts:
        recs.extend(p)
    res = pd.DataFrame(recs)
    res["repro_abs_diff"] = (res["resolved_min_vm"] - res["stored_min_vm"]).abs()
    res["stored_violation"] = res["stored_min_vm"] < LIMIT
    res["corrected_violation"] = res["corrected_min_vm"] < LIMIT
    ok = res["corrected_status"].isin(["converged", "not_needed"])
    res["flip_viol_to_safe"] = ok & res["stored_violation"] & (~res["corrected_violation"])
    res["flip_safe_to_viol"] = ok & (~res["stored_violation"]) & res["corrected_violation"]
    res.to_parquet(args.out, index=False)
    wall = time.time() - t0
    print(f"audited rows {len(res)} in {wall:.1f}s; max repro diff {res['repro_abs_diff'].max():.3e}", flush=True)
    print(res["corrected_status"].value_counts().to_string(), flush=True)

    side = dict(script="scripts/sts_n2_label_audit.py", argv=sys.argv, wall_time_s=wall,
                replay_wall_s=t_replay, replay_n0_max_abs_diff=float(n0_diffs.max()),
                replay_n0_n_exact=int((n0_diffs == 0).sum()), replay_n_scenarios=int(len(n0_diffs)),
                rejects_per_shard=n_reject, max_scen=args.max_scen)
    with open(args.out + ".run.json", "w") as f:
        json.dump(side, f, indent=2)


if __name__ == "__main__":
    main()
