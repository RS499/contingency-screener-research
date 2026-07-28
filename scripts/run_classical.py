import os
import sys
import time
import argparse
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import classical_screen as cs
import classical_manifest as cm

DATASET = "data/dataset.parquet"
OUT = "data/classical_predictions.parquet"
VM0_TOL = 1e-5


def scenario_rows(df):
    out = []
    for sid, sdf in df.groupby("scenario_id", sort=True):
        n0 = sdf[sdf["outaged_type"] == "none"]
        if len(n0) == 0:
            continue
        out.append((int(sid), n0.iloc[0], sdf[sdf["outaged_type"] != "none"]))
    return out


def run_one(sid, n0_row, cont_df):
    net = cs.rebuild_net(n0_row)
    t0 = time.perf_counter()
    ok = cs.solve_base(net)
    t_base = time.perf_counter() - t0
    if not ok:
        return None, None, None, None

    vm0 = net.res_bus.vm_pu.values.astype(np.float64)
    stored = np.array([float(n0_row[f"vm0_{i}"]) for i in range(cs.N_BUS)])
    vm0_err = float(np.nanmax(np.abs(vm0 - stored)))

    t0 = time.perf_counter()
    setup = cs.sensitivity_setup(net)
    t_setup = time.perf_counter() - t0

    bus_types = cs.base_bus_types(net)
    diag = cs.base_diagnostics(net)

    truth = {}
    for r in cont_df.itertuples():
        truth[(r.outaged_type, int(r.outaged_idx))] = (float(r.min_vm), bool(r.converged),
                                                       int(r.argmin_bus))

    rows = []
    t_apply = 0.0
    for br in cs.branch_terminals(net):
        t0 = time.perf_counter()
        dV = cs.inject_dv(setup, br["terminals"])
        pred_vm = vm0 + dV
        pred_min = float(pred_vm.min())
        pi = cs.voltage_pi(pred_vm)
        t_apply += time.perf_counter() - t0
        pred_bus = int(np.argmin(pred_vm))
        key = (br["type"], br["idx"])
        true_min, converged, argmin_bus = truth.get(key, (np.nan, False, -1))
        rows.append(dict(scenario_id=sid, outaged_type=br["type"], outaged_idx=br["idx"],
                         pred_min_vm=pred_min, pi=pi,
                         pred_argmin_bus=pred_bus,
                         true_min_vm=true_min, converged=converged, argmin_bus=argmin_bus,
                         true_weakest_type=int(bus_types[argmin_bus]) if argmin_bus >= 0 else -1,
                         n0_min_vm=float(n0_row["n0_min_vm"])))
    timing = dict(t_base=t_base, t_setup=t_setup, t_apply=t_apply, n_cont=len(rows))
    return rows, vm0_err, timing, dict(diag=diag, bus_types=bus_types)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="only screen the first N scenarios")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    t_start = time.time()
    df = pd.read_parquet(DATASET)
    groups = scenario_rows(df)
    if args.limit is not None:
        groups = groups[:args.limit]
    print(f"screening {len(groups)} scenarios")

    all_rows = []
    vm0_errs = []
    t_base_tot = t_setup_tot = t_apply_tot = 0.0
    n_apply = 0
    n_failed = 0
    type_counts = np.zeros((cs.N_BUS, 3), dtype=np.int64)
    qlim_counts = []

    for k, (sid, n0_row, cont_df) in enumerate(groups):
        rows, vm0_err, timing, info = run_one(sid, n0_row, cont_df)
        if rows is None:
            n_failed += 1
            continue
        if vm0_err > VM0_TOL:
            raise RuntimeError(
                f"scenario {sid}: reconstructed vm0 differs from stored by {vm0_err:.2e} "
                f"(tolerance {VM0_TOL:.0e}). The screen would be reading a different operating "
                f"point than the dataset recorded. Stopping rather than reporting a wrong number.")
        all_rows.extend(rows)
        vm0_errs.append(vm0_err)
        t_base_tot += timing["t_base"]
        t_setup_tot += timing["t_setup"]
        t_apply_tot += timing["t_apply"]
        n_apply += timing["n_cont"]
        for b in range(cs.N_BUS):
            type_counts[b, int(info["bus_types"][b])] += 1
        qlim_counts.append(info["diag"]["n_gen_at_qlim"])
        if (k + 1) % 250 == 0:
            print(f"  {k+1}/{len(groups)} scenarios  ({time.time()-t_start:.0f}s)")

    out = pd.DataFrame(all_rows)
    out.to_parquet(args.out, index=False)

    n_scen = len(vm0_errs)
    ms_apply = t_apply_tot / n_apply * 1000.0
    ms_factor = t_setup_tot / n_apply * 1000.0
    ms_basesolve = t_base_tot / n_apply * 1000.0
    timing = dict(ms_apply_only=round(ms_apply, 6),
                  ms_apply_plus_factor=round(ms_apply + ms_factor, 6),
                  ms_apply_plus_factor_plus_basesolve=round(ms_apply + ms_factor + ms_basesolve, 6),
                  headline="ms_apply_plus_factor",
                  note=("per-contingency cost; Jacobian factorization and base solve are amortized "
                        "over the 186 contingencies of their scenario. Headline charges apply + "
                        "factorization (parity with the surrogate, which is charged predict time "
                        "but not fit time); the strictest accounting also charges the base solve."))
    print(f"\nvm0 reproduction: max over {n_scen} scenarios = {max(vm0_errs):.2e} (tol {VM0_TOL:.0e})")
    print(f"failed base solves: {n_failed}")
    print(f"rows written: {len(out)}  -> {args.out}")
    print(f"timing ms/contingency: apply={ms_apply:.5f} +factor={ms_apply+ms_factor:.5f} "
          f"+basesolve={ms_apply+ms_factor+ms_basesolve:.5f}")

    bus_type_dist = {}
    for b in range(cs.N_BUS):
        pq, pv, ref = (int(type_counts[b, 0]), int(type_counts[b, 1]), int(type_counts[b, 2]))
        if pv > 0 or ref > 0:
            bus_type_dist[str(b)] = dict(PQ=pq, PV=pv, ref=ref)
    meta = dict(n_scenarios=n_scen, n_failed_base=n_failed, n_rows=len(out),
                vm0_max_err=max(vm0_errs), vm0_tol=VM0_TOL,
                timing_ms_per_contingency=timing,
                gens_at_qlim_base=dict(mean=float(np.mean(qlim_counts)),
                                       min=int(np.min(qlim_counts)),
                                       max=int(np.max(qlim_counts)),
                                       n_gen=53),
                bus_base_type_counts=bus_type_dist)
    run_settings = dict(task="classical baseline: sensitivity screen prediction pass",
                        dataset=DATASET, n_scenarios_screened=n_scen,
                        limit=args.limit, nproc=1, seed="n/a (no RNG; deterministic reconstruction)",
                        sampling_flags="n/a (reads the committed dataset; no scenario sampling)",
                        solver=dict(enforce_q_lims=True, init="dc", numba=True, algorithm="nr"),
                        pi_exponent_2n=cs.PI_EXPONENT_2N, comp_sign=cs.COMP_SIGN,
                        vm0_guard_tol=VM0_TOL, output_parquet=args.out)
    cm.write_with_manifest(args.out.replace(".parquet", "_meta.json"), meta, run_settings)
    print(f"time_s={time.time()-t_start:.1f}")


if __name__ == "__main__":
    main()
