"""Why case57 has NO FEASIBLE RANGE: is the under-voltage load-driven or structural?

Scales every load by a single multiplier and reports base min_vm. No sampling, no gate.
"""
import json, os, sys, time
import numpy as np
import pandapower as pp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
import netstudy as N
import generate_dataset as G

NETWORK = "case57"
OUT = "data/netstudy/case57/nofeasible_diagnostic.json"

if __name__ == "__main__":
    rows = []
    for mult in [1.12, 1.0, 0.9, 0.8, 0.7, 0.5, 0.3, 0.1, 0.01, 0.0]:
        net = G.build_net(NETWORK)
        net.load["p_mw"] = net["_p0"] * mult
        net.load["q_mvar"] = net["_q0"] * mult
        try:
            pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)
            vm = net.res_bus.vm_pu.values
            rows.append(dict(multiplier=mult, converged=True,
                             min_vm_pu=float(np.nanmin(vm)),
                             argmin_bus_0based=int(np.nanargmin(vm)),
                             argmin_bus_ieee=int(np.nanargmin(vm)) + 1,
                             n_bus_below_094=int((vm < 0.94).sum()),
                             max_vm_pu=float(np.nanmax(vm))))
        except Exception as e:
            rows.append(dict(multiplier=mult, converged=False, error=type(e).__name__))
        print(rows[-1], flush=True)

    net = G.build_net(NETWORK)
    pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)
    vm = net.res_bus.vm_pu.values
    order = np.argsort(vm)[:6]
    doc = dict(
        network=NETWORK,
        question=("case57 rejected 200/200 draws on the VOLTAGE clause at every one of the "
                  "71 sweep candidates from lo=1.00 to lo=0.30. Is the under-voltage driven "
                  "by load level, which the sweep can move, or structural, which it cannot?"),
        method="uniform scaling of every load's p_mw and q_mvar; pinned solver; no sampling",
        zero_load_included=True,
        scaling=rows,
        nominal_worst_buses=[dict(bus_0based=int(b), bus_ieee=int(b) + 1,
                                  vm_pu=float(vm[b])) for b in order],
        nominal_n_bus_below_094=int((vm < 0.94).sum()),
        gen_vm_setpoints=dict(min=float(net.gen.vm_pu.min()), max=float(net.gen.vm_pu.max()),
                              n_gen=int(len(net.gen))),
        ext_grid_vm=float(net.ext_grid.vm_pu.iloc[0]),
    )
    doc["verdict"] = ("STRUCTURAL: min_vm stays below the 0.94 floor even at zero load, so no "
                      "load-multiplier window can satisfy the voltage clause"
                      if (rows[-1].get("converged") and rows[-1].get("min_vm_pu", 0) < 0.94)
                      else "NOT STRUCTURAL by this test: some scaling clears 0.94")
    N.write_json(OUT, doc, dict(seed=None, input_file=None,
                                run_settings=dict(phase="1a diagnostic", network=NETWORK)))
    print("\nverdict:", doc["verdict"])
