import os
import sys

import numpy as np
import pandas as pd
import pandapower as pp
import pandapower.networks as pn

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))

# ACCEPTANCE TEST for the scripts/thermal_check.py load-mapping fix.
#
# Runs BOTH mappings against the committed case30 dataset and reports, for each, the maximum
# absolute difference between the recomputed N-1 min_vm and the value stored in the parquet.
#
# PASS CRITERION, both directions:
#   bus-mapped  ->  max abs diff <= 1e-7   (reproduces the dataset)
#   positional  ->  max abs diff  > 1e-7   (does NOT reproduce it)
#
# A fix that only satisfies the first half is not verified: if positional ALSO reproduced the
# stored values, the two mappings would be equivalent and the defect would not be a defect.

DATASET = "data/case30_dataset.parquet"
SOLVER = dict(enforce_q_lims=True, init="dc", numba=True, algorithm="nr")
TOL = 1e-7


def solve_one(builder, row, r, mapping):
    net = builder()
    n_bus = len(net.bus)
    load_p = [f"pload_{i}" for i in range(n_bus)]
    load_q = [f"qload_{i}" for i in range(n_bus)]
    gen_vm = [f"genvm_{i}" for i in range(len(net.gen))]
    gen_qmin = [f"genqmin_{i}" for i in range(len(net.gen))]
    gen_qmax = [f"genqmax_{i}" for i in range(len(net.gen))]

    p = row[load_p].to_numpy(dtype=float)
    q = row[load_q].to_numpy(dtype=float)
    if mapping == "bus":
        bus = net.load.bus.to_numpy()
        net.load["p_mw"] = p[bus]
        net.load["q_mvar"] = q[bus]
    else:
        net.load["p_mw"] = p[:len(net.load)]
        net.load["q_mvar"] = q[:len(net.load)]

    net.gen["vm_pu"] = row[gen_vm].to_numpy(dtype=float)
    net.gen["min_q_mvar"] = row[gen_qmin].to_numpy(dtype=float)
    net.gen["max_q_mvar"] = row[gen_qmax].to_numpy(dtype=float)
    go = int(row["gen_out"])
    if go >= 0:
        net.gen.iat[go, net.gen.columns.get_loc("in_service")] = False
    tbl = net.line if r["outaged_type"] == "line" else net.trafo
    col = tbl.columns.get_loc("in_service")
    tbl.iat[int(r["outaged_idx"]), col] = False
    try:
        pp.runpp(net, **SOLVER)
    except Exception:
        return np.nan, np.nan
    lp = net.res_line["loading_percent"]
    return (float(np.nanmin(net.res_bus.vm_pu.values)),
            float(lp.max()) if lp.notna().any() else np.nan)


def main():
    n_scen = 40
    if "--n" in sys.argv:
        n_scen = int(sys.argv[sys.argv.index("--n") + 1])

    df = pd.read_parquet(DATASET)
    base = df[df.outaged_type == "none"].set_index("scenario_id")
    n1 = df[df.outaged_type != "none"]
    scen_ids = list(base.index[:n_scen])

    out = {}
    for mapping in ("bus", "positional"):
        diffs, loads = [], []
        for si in scen_ids:
            row = base.loc[si]
            for _, r in n1[n1.scenario_id == si].iterrows():
                mn, lp = solve_one(pn.case30, row, r, mapping)
                if not np.isnan(mn):
                    diffs.append(abs(mn - float(r["min_vm"])))
                    loads.append(lp)
        d = np.array(diffs)
        l = np.array(loads, dtype=float)
        l = l[~np.isnan(l)]
        out[mapping] = dict(
            n=len(d), max_abs_diff=float(d.max()), median_abs_diff=float(np.median(d)),
            share_above_100=float((l > 100).mean()), median_load=float(np.median(l)),
            p90_load=float(np.percentile(l, 90)), max_load=float(l.max()))

    print(f"acceptance test on {DATASET}, {n_scen} scenarios, {out['bus']['n']} contingencies")
    print(f"  tolerance: {TOL}")
    print()
    for m in ("bus", "positional"):
        o = out[m]
        print(f"  {m:11s} max|recomputed - stored min_vm| = {o['max_abs_diff']:.6e}   "
              f"median {o['median_abs_diff']:.6e}")
    print()
    bus_ok = out["bus"]["max_abs_diff"] <= TOL
    pos_ok = out["positional"]["max_abs_diff"] > TOL
    print(f"  bus-mapped reproduces stored min_vm (<= {TOL}) : {'PASS' if bus_ok else 'FAIL'}")
    print(f"  positional does NOT reproduce it   (>  {TOL}) : {'PASS' if pos_ok else 'FAIL'}")
    print()
    print("  loading under each mapping, same contingencies:")
    for m in ("bus", "positional"):
        o = out[m]
        print(f"    {m:11s} share>100 {o['share_above_100']:.6f}  median {o['median_load']:.4f}  "
              f"p90 {o['p90_load']:.4f}  max {o['max_load']:.4f}")
    return 0 if (bus_ok and pos_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
