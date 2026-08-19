import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pandapower as pp

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_dataset as G
import manifest as mf
import classical_manifest as cm

# STAGE 2H. Thermal-feasible regeneration of case30.
#
# H1 EXTENDS the N-0 acceptance criterion. The committed predicate is voltage-only:
#
#     feasibility/generate_dataset.py:256
#     if GATE_N0 and (not n0_conv or n0_min_vm < VMIN_LIMIT):
#         n_reject += 1 ; continue
#
# i.e. accept iff  n0_conv AND n0_min_vm >= 0.94.  Thermal loading is never consulted,
# which is why data/case30_dataset.parquet contains base cases loaded to 111.83%.
#
# WHY THIS SCRIPT RATHER THAN AN EDIT TO generate_dataset.py: the committed generator
# produced the frozen case118 artifacts. Editing its accept/reject loop risks changing a
# reproduction path that every headline number depends on. Instead the sampling and row
# construction are IMPORTED from it unchanged -- sample_scenario, solve_n0, run_scenario,
# rows_to_frame, build_net, branch_list, region_of_load, apply_config -- and only the
# accept/reject predicate, the one thing H1 asks to change, lives here.
#
# PLACEHOLDER GUARD: the thermal predicate is UNDEFINED on a network whose ratings are
# placeholders. case118 carries a uniform 9,900 MVA on every line and transformer. This
# script RAISES on such a network rather than silently accepting everything.

OUTDIR = "data/case30_thermal"
NETWORK = "case30"
VMIN = 0.94
THERMAL_MAX_PCT = 100.0
WINDOW = 0.12

PLACEHOLDER_MAX_DISTINCT = 3
PLACEHOLDER_BASE_LOADING_PCT = 25.0
PLACEHOLDER_TRAFO_MVA = 1000.0


def assert_ratings_usable(net, network_name):
    """Raise unless the network carries ratings that can support a thermal predicate."""
    line_r = net.line["max_i_ka"]
    if len(net.line) == 0 or line_r.isna().all():
        raise ValueError(
            f"{network_name}: no line ratings (max_i_ka all NaN or no lines). The thermal "
            f"N-0 predicate is UNDEFINED here and must not be applied.")

    probe = G.build_net(network_name)
    pp.runpp(probe, enforce_q_lims=True, init="dc", numba=True)
    base_max = float(probe.res_line["loading_percent"].max())

    if line_r.nunique() <= PLACEHOLDER_MAX_DISTINCT and base_max < PLACEHOLDER_BASE_LOADING_PCT:
        raise ValueError(
            f"{network_name}: line ratings look like PLACEHOLDERS "
            f"({line_r.nunique()} distinct values, base-case max loading {base_max:.3f}%). "
            f"A thermal N-0 predicate against a placeholder accepts everything and reports "
            f"a misleading zero. Refusing to run.")

    trafo_r = net.trafo["sn_mva"]
    if len(net.trafo) > 0 and trafo_r.nunique() == 1 and float(trafo_r.max()) >= PLACEHOLDER_TRAFO_MVA:
        raise ValueError(
            f"{network_name}: transformer sn_mva is a single value >= "
            f"{PLACEHOLDER_TRAFO_MVA} MVA ({float(trafo_r.max())}). PLACEHOLDER. Refusing.")

    return dict(n_lines=int(len(net.line)), n_trafos=int(len(net.trafo)),
                line_rating_distinct=int(line_r.nunique()),
                base_case_max_loading_pct=base_max)


def max_loading_pct(net):
    """Max loading over lines and transformers of the CURRENT solved state."""
    vals = []
    lp = net.res_line["loading_percent"]
    if len(lp) and lp.notna().any():
        vals.append(float(lp.max()))
    if len(net.trafo):
        tp = net.res_trafo["loading_percent"]
        if len(tp) and tp.notna().any():
            vals.append(float(tp.max()))
    return max(vals) if vals else np.nan


def n0_feasible(n0_conv, n0_min_vm, load_pct, thermal):
    """H1's extended predicate. thermal=False reproduces the committed voltage-only gate."""
    if not n0_conv:
        return False, "nonconvergence"
    if n0_min_vm < VMIN:
        return False, "voltage"
    if thermal and (np.isnan(load_pct) or load_pct > THERMAL_MAX_PCT):
        return False, "thermal"
    return True, "accepted"


def base_config(lo, hi):
    return dict(network=NETWORK, stress="fixed", mult_lo=lo, mult_hi=hi,
                reg_lo=lo, reg_hi=hi, pf_lo=0.9, pf_hi=1.15, dvm=0.025)


def probe_range(lo, hi, n_draws, seed, thermal, n_contingency_bases=0):
    """Draw n_draws base scenarios at [lo, hi]; report acceptance and base statistics.

    Optionally run full N-1 contingency sets on the first n_contingency_bases accepted
    scenarios to estimate the violation rate at this range.
    """
    cfg = base_config(lo, hi)
    G.apply_config(cfg)
    net = G.build_net(NETWORK)
    load_region, n_regions = G.region_of_load(net)
    branches = G.branch_list(net)
    rng = np.random.default_rng(seed)

    accepted, rejected = 0, dict(nonconvergence=0, voltage=0, thermal=0)
    base_loads, base_vms = [], []
    kept_params = []

    # "mixed" is expanded in generate_dataset.main() as mode_list[accepted], alternating
    # independent/regional by ACCEPTED index (generate_dataset.py:316-318, :253).
    # Replicated exactly rather than passed through: sample_scenario raises on "mixed".
    modes = ("independent", "regional")

    for _ in range(n_draws):
        this_mode = modes[accepted % 2]
        params = G.sample_scenario(rng, net, this_mode, load_region, n_regions, stress="fixed")
        n0_conv, vm0, n0_min_vm = G.solve_n0(net, params)
        load_pct = max_loading_pct(net) if n0_conv else np.nan
        ok, reason = n0_feasible(n0_conv, n0_min_vm, load_pct, thermal)
        if not ok:
            rejected[reason] += 1
            continue
        accepted += 1
        base_loads.append(load_pct)
        base_vms.append(n0_min_vm)
        if len(kept_params) < n_contingency_bases:
            kept_params.append((params, n0_conv, vm0, n0_min_vm))

    out = dict(
        lo=round(lo, 4), hi=round(hi, 4), n_draws=n_draws,
        n_accepted=accepted,
        acceptance_rate=accepted / n_draws,
        rejected_by=rejected,
        max_base_loading_pct=(float(np.max(base_loads)) if base_loads else None),
        median_base_loading_pct=(float(np.median(base_loads)) if base_loads else None),
        min_base_vm_pu=(float(np.min(base_vms)) if base_vms else None),
    )

    if kept_params:
        mins, loads = [], []
        for params, n0_conv, vm0, n0_min_vm in kept_params:
            # MUST re-apply before running contingencies. run_scenario toggles in_service
            # and re-solves the CURRENT net state (generate_dataset.py:210-216); it does
            # not re-apply params itself. The committed worker() calls it immediately
            # after solve_n0, so net is already correct there. Here the probe is deferred
            # to after the draw loop, at which point net holds the LAST DRAWN scenario --
            # usually a rejected one. Without this line the probe silently measured
            # contingencies against the wrong base case, which produced impossible
            # violation rates of exactly 1.0 next to neighbours at 0.12.
            G.solve_n0(net, params)
            rows = G.run_scenario(net, branches, params, 0, "probe", n0_conv, vm0, n0_min_vm)
            for r in rows:
                if r["outaged_type"] == "none":
                    continue
                if r["converged"] and not np.isnan(r["min_vm"]):
                    mins.append(float(r["min_vm"]))
        mins = np.array(mins, dtype=float)
        out["n1_probe"] = dict(
            n_bases=len(kept_params), n_contingencies=int(len(mins)),
            violation_rate=(float((mins < VMIN).mean()) if len(mins) else None),
            boundary_mass=(float(((mins >= VMIN) & (mins < 0.945)).mean()) if len(mins) else None),
            min_vm_min=(float(mins.min()) if len(mins) else None),
            min_vm_median=(float(np.median(mins)) if len(mins) else None),
        )
    else:
        out["n1_probe"] = None
    return out


def h2_sweep(n_draws, seed, lo_floor, n_contingency_bases):
    net = G.build_net(NETWORK)
    ratings = assert_ratings_usable(net, NETWORK)
    print(f"ratings usable: {ratings}", flush=True)

    rows = []
    lo = 1.00
    t0 = time.time()
    while lo >= lo_floor - 1e-9:
        r = probe_range(lo, lo + WINDOW, n_draws, seed, thermal=True,
                        n_contingency_bases=n_contingency_bases)
        rows.append(r)
        vp = r["n1_probe"]
        print(f"  lo={r['lo']:.2f} hi={r['hi']:.2f}  acc={r['acceptance_rate']:.3f} "
              f"({r['n_accepted']}/{r['n_draws']})  "
              f"maxload={r['max_base_loading_pct'] if r['max_base_loading_pct'] is None else round(r['max_base_loading_pct'],2)}  "
              f"minvm={r['min_base_vm_pu'] if r['min_base_vm_pu'] is None else round(r['min_base_vm_pu'],5)}  "
              f"viol={vp['violation_rate'] if vp and vp['violation_rate'] is not None else 'n/a'}  "
              f"[{time.time()-t0:.0f}s]", flush=True)
        lo = round(lo - 0.01, 4)

    return ratings, rows


def choose_range(rows, min_acceptance=0.20):
    """Highest range with acceptance >= min_acceptance AND max base loading <= 100."""
    for r in rows:                      # rows are in descending lo order already
        if r["max_base_loading_pct"] is None:
            continue
        if r["acceptance_rate"] >= min_acceptance and r["max_base_loading_pct"] <= THERMAL_MAX_PCT:
            return r
    return None


def main():
    n_draws = 200
    seed = 100
    lo_floor = 0.70
    n_cont = 6
    if "--n-draws" in sys.argv:
        n_draws = int(sys.argv[sys.argv.index("--n-draws") + 1])
    if "--lo-floor" in sys.argv:
        lo_floor = float(sys.argv[sys.argv.index("--lo-floor") + 1])
    if "--n-contingency-bases" in sys.argv:
        n_cont = int(sys.argv[sys.argv.index("--n-contingency-bases") + 1])

    os.makedirs(OUTDIR, exist_ok=True)

    print("H1: committed predicate is feasibility/generate_dataset.py:256")
    print("    if GATE_N0 and (not n0_conv or n0_min_vm < VMIN_LIMIT): reject")
    print("    accept iff n0_conv AND n0_min_vm >= 0.94  (VOLTAGE ONLY)")
    print(f"H1 extended: accept iff n0_conv AND n0_min_vm >= {VMIN} AND "
          f"max loading_percent <= {THERMAL_MAX_PCT}")
    print()
    print(f"H2: sweeping lo from 1.00 down to {lo_floor} in 0.01 steps, window {WINDOW}, "
          f"{n_draws} draws each, {n_cont} bases for the N-1 probe")

    ratings, rows = h2_sweep(n_draws, seed, lo_floor, n_cont)
    chosen = choose_range(rows)

    out = dict(
        stage="2H",
        network=NETWORK,
        h1=dict(
            committed_predicate_site="feasibility/generate_dataset.py:256",
            committed_predicate="accept iff n0_conv AND n0_min_vm >= 0.94",
            committed_is_voltage_only=True,
            extended_predicate=(f"accept iff n0_conv AND n0_min_vm >= {VMIN} AND "
                                f"max(line,trafo) loading_percent <= {THERMAL_MAX_PCT}"),
            applied_to=[NETWORK],
            refused_for=["case118"],
            refusal_reason=("case118 line and transformer ratings are uniform 9,900 MVA "
                            "placeholders; assert_ratings_usable raises rather than "
                            "silently accepting everything"),
            ratings_check=ratings,
        ),
        h2=dict(
            window_width=WINDOW,
            step=0.01,
            n_draws_per_candidate=n_draws,
            seed=seed,
            selection_rule=("highest lo whose acceptance rate >= 0.20 AND whose max base "
                            "loading_percent <= 100"),
            sweep=rows,
            chosen=chosen,
            verdict=("FEASIBLE RANGE FOUND" if chosen else "NO FEASIBLE RANGE"),
        ),
    )

    path = os.path.join(OUTDIR, "h2_range_sweep.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {path}")

    man = cm.build_manifest(path, out,
                            dict(task="Stage 2H H1+H2: thermal N-0 predicate and range sweep",
                                 network=NETWORK, imported_from="feasibility/generate_dataset.py"))
    with open(mf.manifest_path(path), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {mf.manifest_path(path)}")

    if chosen is None:
        print("\nNO FEASIBLE RANGE - H3 does not run.")
        return 2
    print(f"\nCHOSEN RANGE: [{chosen['lo']}, {chosen['hi']}]  "
          f"acceptance {chosen['acceptance_rate']:.3f}  "
          f"max base loading {chosen['max_base_loading_pct']:.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
