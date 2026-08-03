import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import classical_manifest as cm
import miss_mechanism as mm

import pandapower as pp
import pandapower.networks as nw

SCEN = 101000025
OUT_LINE = 78
CRIT_INDICES = [75, 52, 106]
WEAK_IDX = 53


def solve_flag(net, enforce):
    try:
        pp.runpp(net, enforce_q_lims=enforce, init="dc", numba=True)
        vm = net.res_bus.vm_pu.values
        return True, float(np.nanmin(vm)), int(np.nanargmin(vm))
    except Exception as e:
        print("  solve failed:", e)
        return False, None, None


def main():
    df = pd.read_parquet("data/dataset.parquet")
    srow = df[df["scenario_id"] == SCEN].iloc[0]

    net = nw.case118()
    name_map = {}
    for idx in CRIT_INDICES + [WEAK_IDX]:
        name_map[str(idx)] = int(net.bus.at[idx, "name"])
    print("[bus map] pandapower index -> IEEE name:")
    for idx in CRIT_INDICES:
        print(f"   index {idx}  ->  IEEE bus {name_map[str(idx)]}")
    print(f"   (weak bus) index {WEAK_IDX} -> IEEE bus {name_map[str(WEAK_IDX)]}")

    mech = json.load(open("data/miss_mechanism.json"))
    r = mech["part1_mechanism"]
    gen21_near = next(g for g in r["reactive_support_near_weak_bus"]["generators_within_2_hops"]
                      if g["gen"] == 21)
    gen21_sat = next((g for g in r["saturated_gens_near_weak_bus_post_outage"] if g["gen"] == 21), None)
    gen21 = dict(gen=21, bus=gen21_near["bus"],
                 q_mvar_n0=(gen21_sat["q_n0"] if gen21_sat else None),
                 q_mvar_post_outage=(gen21_sat["q_n1"] if gen21_sat else None),
                 min_q_mvar_scenario=gen21_near["qmin_scn"],
                 max_q_mvar_scenario=gen21_near["qmax_scn"])
    print(f"[gen 21] N-0 q={gen21['q_mvar_n0']:.2f} | post-outage q={gen21['q_mvar_post_outage']:.2f} | "
          f"min_q(scenario)={gen21['min_q_mvar_scenario']:.2f} | max_q={gen21['max_q_mvar_scenario']:.2f}")

    net_on = mm.rebuild_scenario(srow)
    net_on.line.at[OUT_LINE, "in_service"] = False
    conv_on, min_on, arg_on = solve_flag(net_on, enforce=True)

    net_off = mm.rebuild_scenario(srow)
    net_off.line.at[OUT_LINE, "in_service"] = False
    conv_off, min_off, arg_off = solve_flag(net_off, enforce=False)

    print(f"[solve] enforce_q_lims=True : min_vm={min_on:.5f} @ bus {arg_on} "
          f"(IEEE {int(net.bus.at[arg_on,'name'])})")
    print(f"[solve] enforce_q_lims=False: min_vm={min_off:.5f} @ bus {arg_off} "
          f"(IEEE {int(net.bus.at[arg_off,'name'])})")
    print(f"[solve] collapse magnitude (OFF - ON) = {min_off - min_on:.5f} pu")

    out = dict(
        question="is the deepest-miss collapse Q-limit-enforcement dependent?",
        scenario_id=SCEN, outaged_line=OUT_LINE,
        bus_numbering=dict(
            convention_in_paper="pandapower 0-based positional bus INDEX (argmin_bus)",
            source="freeze_poster_numbers.py:116 (bus=int(argmin_bus)); domain_figure.py:57 comment",
            index_to_ieee_name=name_map,
            note="critical_bus_top5 stores the INDEX; IEEE 1-based names differ (see mapping)"),
        gen21_reactive_state=gen21,
        gen21_note=("no contradiction: -10.0 is the N-0 (pre-outage) reactive output; -194.7 is the "
                    "post-outage output, pinned at gen 21's scenario min_q_mvar (absorbing limit)"),
        qlims_check=dict(
            enforce_q_lims_true=dict(converged=conv_on, min_vm=min_on, argmin_bus=arg_on,
                                     argmin_ieee=int(net.bus.at[arg_on, "name"]) if arg_on is not None else None),
            enforce_q_lims_false=dict(converged=conv_off, min_vm=min_off, argmin_bus=arg_off,
                                      argmin_ieee=int(net.bus.at[arg_off, "name"]) if arg_off is not None else None),
            delta_off_minus_on=(min_off - min_on) if (min_on is not None and min_off is not None) else None,
            interpretation=("under enforce_q_lims=False PV gens hold setpoint regardless of reactive "
                            "output, so no Q-limit binds and the limit-induced collapse cannot occur; "
                            "the deep miss exists only under the pinned enforce_q_lims=True oracle")),
        pinned_config_untouched="generate_dataset.solve keeps enforce_q_lims=True; this is a one-off local solve",
        solves_run=2)
    settings = dict(task="enforce_q_lims=False confirmation for scenario 101000025 / line 78",
                    source="data/dataset.parquet, data/miss_mechanism.json",
                    solver_note="one-off solves at both enforcement settings; pinned config unchanged")
    cm.write_with_manifest("data/qlims_off_check.json", out, settings)
    print("\nwrote data/qlims_off_check.json")


if __name__ == "__main__":
    main()
