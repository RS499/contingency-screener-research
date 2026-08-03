import sys, os, time, warnings
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_dataset as gd
import manifest as mf
import pandapower as pp
import pandapower.networks as nw

warnings.filterwarnings("ignore")

COMMITTED_CFG = dict(mult_lo=1.0, mult_hi=1.12, reg_lo=1.0, reg_hi=1.12,
                     pf_lo=0.9, pf_hi=1.15, dvm=0.025)
STRESS = "fixed"
SEED = 100
TARGET_ACCEPTED = 200
MAX_ATTEMPTS = 3000
NETWORK = "case57"
SCAN_NETWORKS = ["case30", "case57", "case118", "case300", "case89pegase"]

C118_ACCEPT_PCT = 53.82
C118_BOUNDARY_PCT = 56.86


def wilson_ci(k, n):
    if n == 0:
        return (float("nan"), float("nan"))
    z = 1.959963984540054
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def timed_min_ms(net, n_timed, warmup):
    times = []
    for i in range(n_timed + warmup):
        t = time.perf_counter()
        gd.solve(net, init="dc")
        dt = (time.perf_counter() - t) * 1000.0
        if i >= warmup:
            times.append(dt)
    times = np.array(times)
    return float(times.min()), float(times.mean()), float(times.std())


def run_case57():
    gd.apply_config(COMMITTED_CFG)
    net = gd.build_net(NETWORK)
    load_region, n_regions = gd.region_of_load(net)
    branches = gd.branch_list(net)
    n_branch = len(branches)
    rng = np.random.default_rng(SEED)

    t0 = time.time()
    accepted = 0
    attempts = 0
    n0_nonconv = 0
    n0_min_vms = []
    n1_minvm = []
    n1_attempted = 0
    n1_nonconv = 0

    while accepted < TARGET_ACCEPTED and attempts < MAX_ATTEMPTS:
        this_mode = "independent" if (attempts % 2 == 0) else "regional"
        params = gd.sample_scenario(rng, net, this_mode, load_region, n_regions, stress=STRESS)
        n0_conv, _vm0, n0_min_vm = gd.solve_n0(net, params)
        attempts += 1
        if not n0_conv:
            n0_nonconv += 1
            continue
        n0_min_vms.append(n0_min_vm)
        if n0_min_vm < gd.VMIN_LIMIT:
            continue
        accepted += 1
        for etype, idx in branches:
            tbl = net[etype]
            col = tbl.columns.get_loc("in_service")
            tbl.iat[tbl.index.get_loc(idx), col] = False
            conv, vm = gd.solve(net, init="dc")
            tbl.iat[tbl.index.get_loc(idx), col] = True
            n1_attempted += 1
            if conv and vm is not None:
                n1_minvm.append(float(np.nanmin(vm)))
            else:
                n1_nonconv += 1
    dt = time.time() - t0

    n0_min_vms = np.array(n0_min_vms)
    v = np.array(n1_minvm)
    lo, hi = wilson_ci(accepted, attempts)

    params = gd.sample_scenario(rng, net, "independent", load_region, n_regions, stress=STRESS)
    gd.apply_scenario(net, params)
    ms_min, ms_mean, ms_std = timed_min_ms(net, 200, 20)

    return {
        "network_facts": {"n_bus": int(len(net.bus)), "n_load": int(len(net.load)),
                          "n_gen": int(len(net.gen)), "n_line": int(len(net.line)),
                          "n_trafo": int(len(net.trafo)), "n_branch_n1": n_branch},
        "step1_n0": {
            "attempts": attempts, "accepted": accepted,
            "accept_rate_pct": 100.0 * accepted / attempts if attempts else float("nan"),
            "accept_rate_wilson95_pct": [100.0 * lo, 100.0 * hi],
            "case118_accept_rate_pct": C118_ACCEPT_PCT,
            "n0_nonconverged": n0_nonconv,
            "n0_nonconv_rate_pct": 100.0 * n0_nonconv / attempts if attempts else float("nan"),
            "n0_min_vm_over_converged_attempts": {
                "min": float(n0_min_vms.min()) if n0_min_vms.size else None,
                "median": float(np.median(n0_min_vms)) if n0_min_vms.size else None,
                "max": float(n0_min_vms.max()) if n0_min_vms.size else None,
                "share_ge_0p94_pct": float(100.0 * np.mean(n0_min_vms >= 0.94)) if n0_min_vms.size else None},
            "wall_clock_s": round(dt, 2)},
        "step2_n1": {
            "solves_attempted": n1_attempted, "converged": int(v.size),
            "nonconverged": n1_nonconv,
            "min_vm_distribution": {
                "min": float(v.min()) if v.size else None,
                "median": float(np.median(v)) if v.size else None,
                "max": float(v.max()) if v.size else None,
                "violation_rate_pct": float(100.0 * np.mean(v < 0.94)) if v.size else None}},
        "step3_boundary_mass": {
            "definition": "share of converged N-1 rows with min_vm in [0.94, 0.945)",
            "case57_boundary_pct": float(100.0 * np.mean((v >= 0.94) & (v < 0.945))) if v.size else None,
            "case118_boundary_pct": C118_BOUNDARY_PCT,
            "n_converged_n1_denominator": int(v.size)},
        "solve_time_case57": {"ms_min": round(ms_min, 3), "ms_mean": round(ms_mean, 3),
                              "ms_std": round(ms_std, 3), "basis": "min over 200 timed solves"},
    }


def scan_networks():
    rows = []
    for name in SCAN_NETWORKS:
        net = getattr(nw, name)()
        nbranch = int(net.line.in_service.sum() + net.trafo.in_service.sum())
        rec = {"network": name, "n_bus": int(len(net.bus)),
               "n_branch_n1": nbranch, "n_shunt": int(len(net.shunt)),
               "gen_qlims_present": bool(net.gen[["min_q_mvar", "max_q_mvar"]].notna().all().all())
                                    if len(net.gen) else True}
        try:
            pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)
            vm = net.res_bus.vm_pu.values
            rec["base_min_vm"] = round(float(vm.min()), 4)
            rec["base_argmin_bus"] = int(vm.argmin())
            rec["buses_below_0p94"] = int((vm < 0.94).sum())
            rec["base_clears_0p94"] = bool(vm.min() >= 0.94)
            rec["pinned_oracle_converges"] = True
            rec["ms_per_solve_min"] = round(timed_min_ms(net, 50, 10)[0], 3)
        except pp.LoadflowNotConverged:
            rec["pinned_oracle_converges"] = False
            rec["base_clears_0p94"] = None
            rec["ms_per_solve_min"] = None
            net2 = getattr(nw, name)()
            try:
                pp.runpp(net2, enforce_q_lims=False, init="dc", numba=True)
                rec["noenforce_base_min_vm"] = round(float(net2.res_bus.vm_pu.min()), 4)
            except pp.LoadflowNotConverged:
                rec["noenforce_base_min_vm"] = None
        rows.append(rec)
    return rows


def extrapolate(scan):
    ests = []
    for r in scan:
        e = {"network": r["network"], "runnable_as_is": bool(r.get("base_clears_0p94"))}
        if not r.get("base_clears_0p94"):
            e["reason_not_runnable"] = ("pinned oracle (enforce_q_lims=True) does not converge at nominal base"
                                        if not r.get("pinned_oracle_converges")
                                        else f"nominal base min_vm={r.get('base_min_vm')} < 0.94 "
                                             f"({r.get('buses_below_0p94')} buses under floor); "
                                             f"upward-only stress cannot lift it, N-0 accept ~0%")
            ests.append(e)
            continue
        ms = r["ms_per_solve_min"]
        nbr = r["n_branch_n1"]
        e["ms_per_solve"] = ms
        e["n_branch"] = nbr
        for rate in (0.50, 0.25):
            n0 = TARGET_ACCEPTED / rate
            n1 = TARGET_ACCEPTED * nbr
            single = (n0 + n1) * ms / 1000.0
            e[f"wall_s_at_accept_{int(rate*100)}pct_1proc"] = round(single, 1)
            e[f"wall_s_at_accept_{int(rate*100)}pct_5proc"] = round(single / 5.0, 1)
        ests.append(e)
    return ests


def main():
    c57 = run_case57()
    scan = scan_networks()
    step4 = extrapolate(scan)

    out = {
        "network": NETWORK,
        "purpose": "go/no-go second-network feasibility probe (NOT a training dataset; no frozen artifact)",
        "verdict_case57": ("NO-GO under pinned config: nominal base is 0.72 pu (39/57 buses under 0.94); "
                           "upward-only stress + N-0 gate accept 0/3000. The acceptance rule, not the "
                           "network, is decisive."),
        "config": {
            "mirrors_committed_case118": True,
            "solver": {"enforce_q_lims": True, "init": "dc", "numba": True, "algorithm": "nr"},
            "sampling_knobs": COMMITTED_CFG, "stress": STRESS, "mode": "mixed", "seed": SEED,
            "n0_gate": "accept iff N-0 converges and n0_min_vm >= 0.94",
            "target_accepted": TARGET_ACCEPTED, "max_attempts_guard": MAX_ATTEMPTS},
        **c57,
        "step4_network_transfer_scan": scan,
        "step4_wall_clock_extrapolation": step4,
        "step4_notes": [
            "The nominal-base check (base_clears_0p94) is the real gate: the pinned config stresses "
            "upward only, so a network is screenable as-is only if its shipped base already clears 0.94.",
            "case300: pinned oracle (enforce_q_lims=True) does NOT converge at nominal under init dc/flat/auto; "
            "with enforcement off the base is 0.889 pu (26 buses under floor). Double transfer failure.",
            "case89pegase: PEGASE per-unit conventions and native voltage band differ from the IEEE cases; "
            "base clears 0.94 but the 0.94 floor itself may not match PEGASE operating limits -- verify before use.",
            "Extrapolation assumes accept rate 50% (case118-like) and 25% (conservative); actual rate is "
            "network-specific and must be probed, as case57 (0%) shows."],
    }

    mf.write_with_manifest("data/case57_feasibility.json", out)
    import json
    print(json.dumps({k: out[k] for k in
                      ["verdict_case57", "step1_n0", "step3_boundary_mass",
                       "step4_network_transfer_scan", "step4_wall_clock_extrapolation"]}, indent=2))
    print("\nwrote data/case57_feasibility.json (+ .manifest.json)")


if __name__ == "__main__":
    main()
