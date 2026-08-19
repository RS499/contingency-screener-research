import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_dataset as G
import manifest as mf
import classical_manifest as cm
import case30_thermal as H

# STAGE 2H / H3. Regenerate case30 under the thermal-feasible N-0 criterion.
#
# LEAKAGE GUARD: per-contingency loading is a POST-OUTAGE OUTCOME. make_splits.load_dataset
# treats every numeric column not in EXCLUDE_COLS as a feature, so putting loading in the
# same parquet would feed the answer to the surrogate. It is written to a SEPARATE file,
# keyed by (scenario_id, outaged_type, outaged_idx), where it cannot reach the design matrix.
#
# EQUIVALENCE: the contingency loop here mirrors generate_dataset.run_scenario but also
# records loading. Because it is a copy, it is CHECKED against the original on the first
# few scenarios and the check result is written into the artifact. A copy that silently
# diverges is worse than no copy.

OUTDIR = "data/case30_thermal"
NETWORK = "case30"
N_SCENARIOS = 1500
SEED = 100
VMIN = 0.94
THERMAL_MAX_PCT = 100.0


def contingency_rows(net, branches, params, scen_id, mode, n0_conv, vm0, n0_min_vm):
    """Mirror of generate_dataset.run_scenario, plus per-contingency max loading.

    net must already carry the applied, solved scenario (call G.solve_n0 first).
    """
    feat = G.scenario_features(net, params, vm0, n0_conv)
    rows, loading = [], []

    def make_row(otype, oidx, conv, vm):
        r = dict(scenario_id=scen_id, sampling_mode=mode,
                 outaged_type=otype, outaged_idx=oidx,
                 gen_out=params["gen_out"], agg_loading=params["agg_loading"],
                 n0_converged=n0_conv, n0_min_vm=n0_min_vm, converged=conv)
        if conv and vm is not None:
            mn = float(np.nanmin(vm)); mx = float(np.nanmax(vm))
            r.update(min_vm=mn, max_vm=mx, argmin_bus=int(np.nanargmin(vm)),
                     violation=bool(mn < G.VMIN_LIMIT),
                     straddle=bool((not (mn < G.VMIN_LIMIT))
                                   and G.STRADDLE_BAND[0] <= mn <= G.STRADDLE_BAND[1]),
                     deep_collapse=bool(mn < G.COLLAPSE_FLOOR))
        else:
            r.update(min_vm=np.nan, max_vm=np.nan, argmin_bus=-1,
                     violation=False, straddle=False, deep_collapse=False)
        r.update(feat)
        return r

    rows.append(make_row("none", -1, n0_conv, vm0))
    for etype, idx in branches:
        tbl = net[etype]
        col = tbl.columns.get_loc("in_service")
        tbl.iat[tbl.index.get_loc(idx), col] = False
        conv, vm = G.solve(net, init="dc")
        load_pct = H.max_loading_pct(net) if conv else np.nan
        tbl.iat[tbl.index.get_loc(idx), col] = True
        rows.append(make_row(etype, idx, conv, vm))
        loading.append(dict(scenario_id=scen_id, outaged_type=etype, outaged_idx=idx,
                            converged=bool(conv), max_loading_pct=float(load_pct)))
    return rows, loading


def equivalence_check(net, branches, params, scen_id, n0_conv, vm0, n0_min_vm):
    """Run both the mirror and the committed original; compare the shared columns."""
    G.solve_n0(net, params)
    mine, _load = contingency_rows(net, branches, params, scen_id, "probe",
                                   n0_conv, vm0, n0_min_vm)
    G.solve_n0(net, params)
    theirs = G.run_scenario(net, branches, params, scen_id, "probe",
                            n0_conv, vm0, n0_min_vm)
    if len(mine) != len(theirs):
        return dict(match=False, reason=f"row count {len(mine)} vs {len(theirs)}")
    diffs = []
    for a, b in zip(mine, theirs):
        for k in ("outaged_type", "outaged_idx", "converged", "violation",
                  "straddle", "deep_collapse", "argmin_bus"):
            if a[k] != b[k]:
                diffs.append(f"{k}: {a[k]} vs {b[k]}")
        for k in ("min_vm", "max_vm"):
            av, bv = a[k], b[k]
            if np.isnan(av) and np.isnan(bv):
                continue
            if not np.isclose(av, bv, rtol=0, atol=0):
                diffs.append(f"{k}: {av!r} vs {bv!r}")
    return dict(match=len(diffs) == 0, n_rows=len(mine), diffs=diffs[:10])


def build(lo, hi, n_scenarios, seed, n_equiv):
    cfg = dict(network=NETWORK, stress="fixed", mult_lo=lo, mult_hi=hi,
               reg_lo=lo, reg_hi=hi, pf_lo=0.9, pf_hi=1.15, dvm=0.025)
    G.apply_config(cfg)
    net = G.build_net(NETWORK)
    H.assert_ratings_usable(net, NETWORK)
    load_region, n_regions = G.region_of_load(net)
    branches = G.branch_list(net)
    rng = np.random.default_rng(seed)
    modes = ("independent", "regional")

    all_rows, all_loading, equiv = [], [], []
    accepted, rejected = 0, dict(nonconvergence=0, voltage=0, thermal=0)
    base_loads = []
    t0 = time.time()
    max_draws = n_scenarios * G.MAX_REJECT_FACTOR

    draws = 0
    while accepted < n_scenarios and draws < max_draws:
        draws += 1
        this_mode = modes[accepted % 2]
        params = G.sample_scenario(rng, net, this_mode, load_region, n_regions, stress="fixed")
        n0_conv, vm0, n0_min_vm = G.solve_n0(net, params)
        load_pct = H.max_loading_pct(net) if n0_conv else np.nan
        ok, reason = H.n0_feasible(n0_conv, n0_min_vm, load_pct, thermal=True)
        if not ok:
            rejected[reason] += 1
            continue

        scen_id = seed * 1_000_000 + accepted
        if len(equiv) < n_equiv:
            equiv.append(equivalence_check(net, branches, params, scen_id,
                                           n0_conv, vm0, n0_min_vm))
            G.solve_n0(net, params)

        rows, loading = contingency_rows(net, branches, params, scen_id, this_mode,
                                         n0_conv, vm0, n0_min_vm)
        all_rows.extend(rows)
        all_loading.extend(loading)
        base_loads.append(load_pct)
        accepted += 1
        if accepted % 100 == 0:
            print(f"    accepted {accepted}/{n_scenarios}  draws={draws}  "
                  f"[{time.time()-t0:.0f}s]", flush=True)

    df = G.rows_to_frame(all_rows)
    load_df = pd.DataFrame(all_loading)
    stats = dict(
        n_accepted=accepted, n_draws=draws, acceptance_rate=accepted / draws,
        rejected_by=rejected,
        max_base_loading_pct=float(np.max(base_loads)),
        median_base_loading_pct=float(np.median(base_loads)),
        elapsed_s=round(time.time() - t0, 1),
        equivalence_checks=equiv,
        equivalence_all_match=bool(all(e["match"] for e in equiv)) if equiv else None,
    )
    return df, load_df, stats


def main():
    n_scen = N_SCENARIOS
    if "--n" in sys.argv:
        n_scen = int(sys.argv[sys.argv.index("--n") + 1])

    sweep_path = os.path.join(OUTDIR, "h2_range_sweep.json")
    with open(sweep_path) as f:
        chosen = json.load(f)["h2"]["chosen"]
    if chosen is None:
        print("NO FEASIBLE RANGE in H2 - H3 does not run.")
        return 2
    lo, hi = chosen["lo"], chosen["hi"]
    print(f"H3: regenerating {NETWORK} at [{lo}, {hi}] with the thermal N-0 gate, "
          f"n={n_scen}, seed={SEED}")

    df, load_df, stats = build(lo, hi, n_scen, SEED, n_equiv=5)

    os.makedirs(OUTDIR, exist_ok=True)
    ds_path = os.path.join(OUTDIR, "dataset.parquet")
    ld_path = os.path.join(OUTDIR, "n1_loading.parquet")
    df.to_parquet(ds_path, index=False)
    load_df.to_parquet(ld_path, index=False)

    n1 = load_df[load_df.converged]
    stats["n1_loading"] = dict(
        n=int(len(n1)),
        share_above_100=float((n1.max_loading_pct > 100.0).mean()),
        median=float(n1.max_loading_pct.median()),
        p90=float(np.percentile(n1.max_loading_pct, 90)),
        max=float(n1.max_loading_pct.max()),
    )
    stats["range"] = dict(lo=lo, hi=hi)
    stats["dataset_rows"] = int(len(df))
    stats["leakage_guard"] = ("per-contingency loading is written to n1_loading.parquet, "
                              "NOT to dataset.parquet: make_splits.load_dataset treats any "
                              "numeric column outside EXCLUDE_COLS as a feature, and "
                              "loading is a post-outage outcome")

    stats_path = os.path.join(OUTDIR, "h3_build_stats.json")
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    for path in (ds_path, ld_path, stats_path):
        man = cm.build_manifest(path, {}, dict(
            task="Stage 2H H3 build: thermal-feasible case30",
            network=NETWORK, range=[lo, hi], n_scenarios=n_scen, seed=SEED,
            n0_predicate=(f"n0_conv AND n0_min_vm >= {VMIN} AND max loading_percent "
                          f"<= {THERMAL_MAX_PCT}"),
            imported_from="feasibility/generate_dataset.py"))
        with open(mf.manifest_path(path), "w") as f:
            json.dump(man, f, indent=2)

    print(f"\nwrote {ds_path}  rows={len(df)}")
    print(f"wrote {ld_path}  rows={len(load_df)}")
    print(f"wrote {stats_path}")
    print(f"  acceptance {stats['acceptance_rate']:.4f} ({stats['n_accepted']}/{stats['n_draws']})")
    print(f"  equivalence vs run_scenario: {stats['equivalence_all_match']}")
    print(f"  max base loading {stats['max_base_loading_pct']:.2f}%")
    print(f"  N-1 loading > 100%: {stats['n1_loading']['share_above_100']:.6f}  "
          f"median {stats['n1_loading']['median']:.2f}  max {stats['n1_loading']['max']:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
