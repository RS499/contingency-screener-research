import os
import sys
import json
import time
import multiprocessing
import numpy as np
import pandas as pd
import pandapower as pp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import generate_dataset as G
import case30_thermal as H
import sts_n2_label_audit as n2
import sts_manifest as sm

# N11 Part 2 relabel driver: scratch/n10_relabel_illinois.py with the network as a parameter (argv[1] = one of
# NETS below). Everything else is the N10 logic unchanged (helper-only switch-back, 4 workers, chunk files).
# case30_thermal replays scripts/case30_thermal_build.py (same draw loop and thermal N-0 gate; its equivalence
# checks and rating assertion solve only and consume no RNG); case39 and case24_ieee_rts replay netstudy.py phase 1a.
#
# (N10 header follows)
# N10 Part B relabel: case_illinois200 with the N2 PV/PQ switch-back method.
# (1) Replay the scripts/netstudy.py phase-1a build exactly: one RNG stream (seed 100), load window from
#     data/netstudy/case_illinois200/build_stats.json, voltage AND thermal N-0 gate (case30_thermal.n0_feasible),
#     mode alternation modes[accepted % 2]. Stored N-0 minima must be reproduced exactly.
# (2) Re-solve every converged N-1 row with the pinned solver and run the N2 switch-back loop.
#     The N2 logic is copied with the network as a parameter. gen_check, fixed_from_check, pinned_solve and
#     the tolerances are imported unchanged from scripts/sts_n2_label_audit.py.
#     ONE necessary change: N2's add_pq_sgens / apply_fixed switch EVERY sgen of the network. case118 has none,
#     case_illinois200 has 11, so here only the helper sgens added by this script are switched; the network's
#     own sgens are never touched.
# 4 workers; progress saved as one parquet per chunk of scenarios; finished chunks skipped on restart.

NETS = {
    "case30_thermal": ("case30", "data/case30_thermal/dataset.parquet", "data/case30_thermal/h3_build_stats.json"),
    "case39": ("case39", "data/netstudy/case39/dataset.parquet", "data/netstudy/case39/build_stats.json"),
    "case24_ieee_rts": ("case24_ieee_rts", "data/netstudy/case24_ieee_rts/dataset.parquet",
                        "data/netstudy/case24_ieee_rts/build_stats.json"),
}
NAME = sys.argv[1] if len(sys.argv) > 1 else "case39"
NETWORK, DATASET, BUILD_STATS = NETS[NAME]
OUT = f"data/sts_n11_relabel_{NAME}.parquet"
OUT_JSON = f"data/sts_n11_relabel_{NAME}.json"
CHUNK_DIR = f"scratch/n11_relabel_{NAME}_chunks"
BUILD_SEED = 100
N_SCENARIOS = 1500
CHUNK = 50
NPROC = 4
LIMIT = 0.94
FAIL_CEIL = 0.005


def build_stats():
    bs = json.load(open(BUILD_STATS))
    return bs.get("stats", bs)


def build_cfg():
    bs = build_stats()
    lo = bs["range"]["lo"]
    hi = bs["range"]["hi"]
    return dict(network=NETWORK, stress="fixed", mult_lo=lo, mult_hi=hi,
                reg_lo=lo, reg_hi=hi, pf_lo=0.9, pf_hi=1.15, dvm=0.025)


def replay():
    # netstudy.py phase_1a build loop, without the N-1 solves
    cfg = build_cfg()
    H.NETWORK = NETWORK
    G.apply_config(cfg)
    net = G.build_net(NETWORK)
    load_region, n_regions = G.region_of_load(net)
    rng = np.random.default_rng(BUILD_SEED)
    modes = ("independent", "regional")
    scenarios = []
    accepted = 0
    draws = 0
    rejected = dict(nonconvergence=0, voltage=0, thermal=0)
    max_draws = N_SCENARIOS * G.MAX_REJECT_FACTOR
    while accepted < N_SCENARIOS and draws < max_draws:
        draws += 1
        this_mode = modes[accepted % 2]
        params = G.sample_scenario(rng, net, this_mode, load_region, n_regions, stress="fixed")
        n0_conv, vm0, n0_min_vm = G.solve_n0(net, params)
        load_pct = H.max_loading_pct(net) if n0_conv else np.nan
        ok, reason = H.n0_feasible(n0_conv, n0_min_vm, load_pct, thermal=True)
        if not ok:
            rejected[reason] += 1
            continue
        scenarios.append(dict(scenario_id=BUILD_SEED * 1_000_000 + accepted, params=params, n0_min_vm=n0_min_vm))
        accepted += 1
    return scenarios, draws, rejected, cfg


def add_helper_sgens(net):
    # one out-of-service helper sgen per generator, used to hold that gen as PQ at a fixed Q limit
    helper = {}
    for gi in net.gen.index:
        s = pp.create_sgen(net, bus=int(net.gen.at[gi, "bus"]), p_mw=float(net.gen.at[gi, "p_mw"]),
                           q_mvar=0.0, in_service=False)
        helper[int(gi)] = s
    net["_helper_sgen"] = helper


def apply_fixed(net, fixed, gen_on):
    # N2 apply_fixed, restricted to the helper sgens
    gen_in = gen_on.copy()
    for gi in net["_helper_sgen"]:
        s = net["_helper_sgen"][gi]
        net.sgen.at[s, "in_service"] = False
        net.sgen.at[s, "q_mvar"] = 0.0
    for gi in fixed:
        s = net["_helper_sgen"][gi]
        gen_in[gi] = False
        net.sgen.at[s, "in_service"] = True
        if fixed[gi] == "min":
            net.sgen.at[s, "q_mvar"] = float(net.gen.at[gi, "min_q_mvar"])
        else:
            net.sgen.at[s, "q_mvar"] = float(net.gen.at[gi, "max_q_mvar"])
    net.gen["in_service"] = gen_in


def corrected_solve(net, first_check, gen_on):
    # N2 corrected_solve with the helper-only apply_fixed
    fixed = n2.fixed_from_check(first_check)
    history = []
    for it in range(1, n2.MAX_OUTER + 1):
        apply_fixed(net, fixed, gen_on)
        if not n2.pinned_solve(net):
            return dict(status="nonconverged", n_outer=it, min_vm=np.nan, argmin=-1, history=history)
        chk = n2.gen_check(net, fixed, gen_on)
        n_bad = int((chk["bad_abs"] | chk["bad_inj"]).sum())
        history.append(n_bad)
        vm = net.res_bus.vm_pu.values
        if n_bad == 0:
            return dict(status="converged", n_outer=it, min_vm=float(np.nanmin(vm)),
                        argmin=int(np.nanargmin(vm)), history=history)
        fixed = n2.fixed_from_check(chk)
    vm = net.res_bus.vm_pu.values
    return dict(status="iteration_cap", n_outer=n2.MAX_OUTER, min_vm=float(np.nanmin(vm)),
                argmin=int(np.nanargmin(vm)), history=history)


def audit_chunk(task):
    # N2 audit_scenario, network as a parameter, for a chunk of scenarios; writes one parquet
    path, cfg, chunk = task
    network = cfg["network"]
    if os.path.exists(path):
        return path
    G.apply_config(cfg)
    recs = []
    for scen, rows in chunk:
        net = G.build_net(network)
        G.apply_scenario(net, scen["params"])
        add_helper_sgens(net)
        gen_on = net.gen.in_service.values.copy()
        for otype, oidx, stored in rows:
            net[otype].at[oidx, "in_service"] = False
            ok = n2.pinned_solve(net)
            rec = dict(scenario_id=scen["scenario_id"], outaged_type=otype, outaged_idx=oidx,
                       stored_min_vm=stored, resolved_converged=ok)
            if ok:
                vm = net.res_bus.vm_pu.values
                rec["resolved_min_vm"] = float(np.nanmin(vm))
                rec["resolved_argmin"] = int(np.nanargmin(vm))
                chk = n2.gen_check(net, {}, gen_on)
                n_bad = int((chk["bad_abs"] | chk["bad_inj"]).sum())
                rec["n_at_qmin"] = int(chk["at_min"].sum())
                rec["n_at_qmax"] = int(chk["at_max"].sum())
                rec["n_inconsistent_absorbing"] = int(chk["bad_abs"].sum())
                rec["n_inconsistent_injecting"] = int(chk["bad_inj"].sum())
                if n_bad > 0:
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
                rec["corrected_status"] = "pinned_nonconverged"
                rec["corrected_min_vm"] = np.nan
                rec["corrected_argmin"] = -1
                rec["n_outer_iter"] = 0
                rec["outer_history"] = ""
            net[otype].at[oidx, "in_service"] = True
            recs.append(rec)
    pd.DataFrame(recs).to_parquet(path, index=False)
    return path


def main():
    t0 = time.time()
    os.makedirs(CHUNK_DIR, exist_ok=True)
    df = pd.read_parquet(DATASET, columns=["scenario_id", "outaged_type", "outaged_idx", "converged",
                                           "min_vm", "n0_min_vm"])
    bs = build_stats()
    scenarios, draws, rejected, cfg = replay()
    t_replay = time.time() - t0
    stored_n0 = df[df["outaged_type"] == "none"].set_index("scenario_id")["n0_min_vm"]
    diffs = np.array([abs(sc["n0_min_vm"] - float(stored_n0.loc[sc["scenario_id"]])) for sc in scenarios])
    replay_ok = bool(len(scenarios) == len(stored_n0) and diffs.max() == 0.0 and draws == bs["n_draws"]
                     and rejected == bs["rejected_by"])
    print(f"replay {t_replay:.1f}s; scenarios {len(scenarios)}; draws {draws} (stored {bs['n_draws']}); "
          f"rejected {rejected} (stored {bs['rejected_by']}); max |n0 diff| {diffs.max():.3e}", flush=True)
    if not replay_ok:
        raise ValueError("replay does not reproduce the stored build; stop")

    n1 = df[(df["outaged_type"] != "none") & (df["converged"])]
    by_scen = {}
    for sid, ot, oi, mv in zip(n1["scenario_id"].to_numpy(), n1["outaged_type"].to_numpy(),
                               n1["outaged_idx"].to_numpy(), n1["min_vm"].to_numpy(np.float64)):
        by_scen.setdefault(int(sid), []).append((str(ot), int(oi), float(mv)))
    tasks = []
    for c0 in range(0, len(scenarios), CHUNK):
        chunk = [(sc, by_scen.get(sc["scenario_id"], [])) for sc in scenarios[c0:c0 + CHUNK]]
        tasks.append((os.path.join(CHUNK_DIR, f"chunk_{c0:04d}.parquet"), cfg, chunk))
    n_done = len([t for t in tasks if os.path.exists(t[0])])
    print(f"chunks {len(tasks)} ({n_done} already done)", flush=True)
    paths = []
    with multiprocessing.Pool(NPROC) as pool:
        for i, p in enumerate(pool.imap(audit_chunk, tasks)):
            paths.append(p)
            print(f"chunk {i + 1}/{len(tasks)} done [{time.time() - t0:.0f}s]", flush=True)

    res = pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True)
    res["repro_abs_diff"] = (res["resolved_min_vm"] - res["stored_min_vm"]).abs()
    res["stored_violation"] = res["stored_min_vm"] < LIMIT
    res["corrected_violation"] = res["corrected_min_vm"] < LIMIT
    ok = res["corrected_status"].isin(["converged", "not_needed"])
    res["flip_viol_to_safe"] = ok & res["stored_violation"] & (~res["corrected_violation"])
    res["flip_safe_to_viol"] = ok & (~res["stored_violation"]) & res["corrected_violation"]
    res.to_parquet(OUT, index=False)
    v_c = res.loc[ok, "corrected_min_vm"].to_numpy()
    v_s = res["stored_min_vm"].to_numpy()
    counts = res["corrected_status"].value_counts()
    summ = dict(n1_converged_rows=int(len(res)), rows_expected=int(len(n1)),
                status_counts={str(k): int(counts[k]) for k in counts.index},
                n1_failed=int((~ok).sum()), n1_failed_share=float((~ok).mean()),
                n_needing_switchback=int((res["n_inconsistent_absorbing"] + res["n_inconsistent_injecting"] > 0).sum()),
                max_repro_abs_diff=float(res["repro_abs_diff"].max()),
                flip_viol_to_safe=int(res["flip_viol_to_safe"].sum()),
                flip_safe_to_viol=int(res["flip_safe_to_viol"].sum()),
                stored_violation_rate=float((v_s < LIMIT).mean()),
                stored_boundary_mass=float(((v_s >= 0.94) & (v_s < 0.945)).mean()),
                corrected_violation_rate=float((v_c < LIMIT).mean()),
                corrected_boundary_mass=float(((v_c >= 0.94) & (v_c < 0.945)).mean()))
    checks = dict(replay_exact=replay_ok, resolve_min_vm_exact=bool(summ["max_repro_abs_diff"] == 0.0),
                  all_rows_audited=bool(summ["n1_converged_rows"] == summ["rows_expected"]),
                  failed_share_le_0p5pct=bool(summ["n1_failed_share"] <= FAIL_CEIL))
    out = dict(question=f"N11 Part 2: switch-back relabel of {NAME} (N2 method, network-parameterized)",
               build_config=cfg, build_seed=BUILD_SEED, replay_draws=draws, replay_rejected=rejected,
               replay_n0_max_abs_diff=float(diffs.max()), checks=checks, summary=summ,
               sgen_note="helper-only apply_fixed (as N10): the network's own sgens are never switched",
               wall_s=time.time() - t0)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    params = dict(name=NAME, network=NETWORK, build_config=cfg, build_seed=BUILD_SEED, n_scenarios=N_SCENARIOS, chunk=CHUNK,
                  nproc=NPROC, limit=LIMIT, switchback_tol_q=n2.TOL_Q, switchback_tol_v=n2.TOL_V,
                  switchback_max_outer=n2.MAX_OUTER, n0_gate="voltage AND thermal (case30_thermal.n0_feasible)",
                  solver="pandapower runpp enforce_q_lims=True init=dc numba=True (pinned)",
                  model_hyperparameters="none (no model fit)")
    man = sm.build_manifest([OUT, OUT_JSON], "scratch/n11_relabel_net.py", [".venv/bin/python", "scratch/n11_relabel_net.py", NAME],
                            [DATASET, BUILD_STATS, "scripts/sts_n2_label_audit.py", "feasibility/generate_dataset.py",
                             "scripts/case30_thermal.py"], params, "")
    man["no_new_solves"] = "FALSE: replays the N-0 build and re-solves every converged N-1 row with the switch-back loop"
    sm.write_manifest(man, OUT)
    print(json.dumps(dict(checks=checks, summary=summ), indent=1))
    if not checks["failed_share_le_0p5pct"]:
        print("STOP: failed share above 0.5%", flush=True)


if __name__ == "__main__":
    main()
