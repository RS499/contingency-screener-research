import os
import sys
import json
import numpy as np
import pandas as pd
import pandapower.networks as pn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sts_manifest as sm

# Dataset facts the STS report prints that had no data/*.json key: persistence of the N-0
# minimum voltage under N-1, the make-up of the [0.94, 0.945) boundary strip, and the
# sampling ranges of the 1,500 base cases. Everything is read from data/dataset.parquet.
#
# usage: .venv/bin/python scripts/sts_dataset_facts.py OUT_DIR [REF_DIR]

DATA = "data/dataset.parquet"
FROZEN_V2 = "data/frozen_poster_numbers_v2.json"
SCRIPT = "scripts/sts_dataset_facts.py"
OUT_NAME = "sts_dataset_facts.json"

LIMIT = 0.94
STRIP_HI = 0.945
PERSIST_TOL = 0.001
MULT_LO = 1.0
MULT_HI = 1.12
RANGE_TOL = 1e-9
DEEP_VM = 0.87
BUS76_INDEX = 75


def load_rows():
    cols = pd.read_parquet(DATA).columns
    pcols = [c for c in cols if c.startswith("pload_")]
    qcols = [c for c in cols if c.startswith("qload_")]
    keep = ["scenario_id", "sampling_mode", "outaged_type", "converged", "n0_min_vm", "min_vm",
            "argmin_bus"]
    df = pd.read_parquet(DATA, columns=keep + pcols + qcols)
    return df, len(pcols)


def persistence(n1):
    d = (n1["min_vm"] - n1["n0_min_vm"]).abs().to_numpy()
    within = d <= PERSIST_TOL
    return {
        "definition": f"converged N-1 rows; d = |min_vm - n0_min_vm|; within means d <= {PERSIST_TOL} pu",
        "n_rows": int(len(d)),
        "n_within": int(within.sum()),
        "share_within_pct": 100.0 * float(within.mean()),
        "n_within_strict_lt": int((d < PERSIST_TOL).sum()),
        "median_abs_diff_pu": float(np.median(d)),
        "mean_abs_diff_pu": float(d.mean()),
    }


def strip_makeup(n1, base):
    in_strip = (n1["min_vm"] >= LIMIT) & (n1["min_vm"] < STRIP_HI)
    strip = n1[in_strip].merge(base, on="scenario_id", how="left")
    n = len(strip)
    base_in_strip = strip["n0_min_vm"] < STRIP_HI
    same_bus = strip["argmin_bus"] == strip["n0_argmin_bus"]
    at76 = strip["argmin_bus"] == BUS76_INDEX
    return {
        "definition": f"converged N-1 rows with {LIMIT} <= min_vm < {STRIP_HI}",
        "n_rows": int(n),
        "share_of_converged_n1_pct": 100.0 * float(in_strip.mean()),
        "n_base_n0_below_strip_hi": int(base_in_strip.sum()),
        "share_base_n0_below_strip_hi_pct": 100.0 * float(base_in_strip.mean()),
        "n_same_weakest_bus_as_n0": int(same_bus.sum()),
        "share_same_weakest_bus_as_n0_pct": 100.0 * float(same_bus.mean()),
        "n_at_bus_index_75": int(at76.sum()),
        "share_at_bus_index_75_pct": 100.0 * float(at76.mean()),
        "bus_convention": "argmin_bus is the pandapower 0-based index; index 75 is IEEE bus 76",
    }


def multipliers(base, n_bus):
    # pload_i / qload_i are summed per bus index i; case118 has 99 loads on 99 distinct buses,
    # so the per-bus ratio to the case118 base load is the per-load multiplier
    net = pn.case118()
    p0 = net.load.groupby("bus")["p_mw"].sum().reindex(range(n_bus), fill_value=0.0).to_numpy()
    q0 = net.load.groupby("bus")["q_mvar"].sum().reindex(range(n_bus), fill_value=0.0).to_numpy()
    pmask = np.abs(p0) > RANGE_TOL
    qmask = np.abs(q0) > RANGE_TOL
    pcols = [f"pload_{i}" for i in range(n_bus)]
    qcols = [f"qload_{i}" for i in range(n_bus)]
    pm = base[pcols].to_numpy()[:, pmask] / p0[pmask]
    qm = base[qcols].to_numpy()[:, qmask] / q0[qmask]
    reg = (base["sampling_mode"] == "regional").to_numpy()
    ind = (base["sampling_mode"] == "independent").to_numpy()
    reg_pm = pm[reg]
    outside = (reg_pm < MULT_LO - RANGE_TOL) | (reg_pm > MULT_HI + RANGE_TOL)
    return {
        "definition": "per-load multiplier = base-case load / pandapower case118 load at the same bus",
        "n_loaded_buses_p": int(pmask.sum()),
        "n_loaded_buses_q": int(qmask.sum()),
        "regional_p_mult_min": float(reg_pm.min()),
        "regional_p_mult_max": float(reg_pm.max()),
        "regional_p_mult_n_values": int(reg_pm.size),
        "regional_p_mult_share_outside_pct": 100.0 * float(outside.mean()),
        "outside_interval": [MULT_LO, MULT_HI],
        "outside_tolerance": RANGE_TOL,
        "independent_p_mult_min": float(pm[ind].min()),
        "independent_p_mult_max": float(pm[ind].max()),
        "q_mult_min_all_bases": float(qm.min()),
        "q_mult_max_all_bases": float(qm.max()),
    }


def frozen_crosscheck(n_n1, strip_pct):
    with open(FROZEN_V2) as f:
        facts = json.load(f)["dataset_facts"]
    return {
        "converged_n1_rows_frozen": facts["converged_n1_rows"],
        "converged_n1_rows_here": n_n1,
        "boundary_pct_frozen": facts["boundary_0p94_to_0p945_pct"],
        "boundary_pct_here": strip_pct,
        "agree": bool(facts["converged_n1_rows"] == n_n1
                      and abs(facts["boundary_0p94_to_0p945_pct"] - strip_pct) < 0.005),
    }


def main():
    out_dir = sys.argv[1]
    ref_dir = ""
    if len(sys.argv) > 2:
        ref_dir = sys.argv[2]
    out_path = os.path.join(out_dir, OUT_NAME)

    df, n_bus = load_rows()
    base_rows = df[df["outaged_type"] == "none"]
    n1 = df[(df["outaged_type"] != "none") & (df["converged"])]
    base = base_rows[["scenario_id", "argmin_bus"]].rename(columns={"argmin_bus": "n0_argmin_bus"})

    mode_counts = {}
    for mode in sorted(base_rows["sampling_mode"].unique()):
        mode_counts[mode] = int((base_rows["sampling_mode"] == mode).sum())

    deep = n1["min_vm"] < DEEP_VM
    strip = strip_makeup(n1, base)
    out = {
        "source": DATA,
        "population": "converged N-1 rows = outaged_type != 'none' and converged; base rows = "
                      "outaged_type == 'none' (one per scenario)",
        "n_base_cases": int(len(base_rows)),
        "n_converged_n1_rows": int(len(n1)),
        "base_cases_per_sampling_mode": mode_counts,
        "n0_persistence": persistence(n1),
        "boundary_strip": strip,
        "load_multipliers": multipliers(base_rows, n_bus),
        "below_0p87": {
            "definition": f"converged N-1 rows with min_vm < {DEEP_VM}",
            "n_rows": int(deep.sum()),
            "share_pct": 100.0 * float(deep.mean()),
        },
        "crosscheck_frozen_v2": frozen_crosscheck(int(len(n1)), round(strip["share_of_converged_n1_pct"], 2)),
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {out_path}")

    params = {
        "limit": LIMIT, "strip_hi": STRIP_HI, "persistence_tolerance_pu": PERSIST_TOL,
        "multiplier_interval": [MULT_LO, MULT_HI], "range_tolerance": RANGE_TOL,
        "deep_vm_threshold": DEEP_VM, "bus76_pandapower_index": BUS76_INDEX,
        "base_load_reference": "pandapower.networks.case118() load p_mw / q_mvar summed per bus",
        "std_convention": "no std: every value is a single count or share over the full dataset",
    }
    argv = [SCRIPT, "data"]
    man = sm.build_manifest([out_path], SCRIPT, argv, [DATA, FROZEN_V2], params, ref_dir)
    sm.write_manifest(man, out_path)


if __name__ == "__main__":
    main()
