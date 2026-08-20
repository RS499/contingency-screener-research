"""Why case89pegase has NO FEASIBLE RANGE: which clause binds, and is it load-reachable?"""
import json, os, sys
import numpy as np
import pandapower as pp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
import netstudy as V1
import case30_thermal as H
import generate_dataset as G

NETWORK = "case89pegase"
OUT = "data/netstudy2/case89pegase_nofeasible_diagnostic.json"

if __name__ == "__main__":
    rows = []
    for mult in [1.12, 1.0, 0.8, 0.6, 0.4, 0.2, 0.1, 0.0]:
        net = G.build_net(NETWORK)
        net.load["p_mw"] = net["_p0"] * mult
        net.load["q_mvar"] = net["_q0"] * mult
        try:
            pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)
            vm = net.res_bus.vm_pu.values
            lp = float(net.res_line["loading_percent"].max())
            tp = float(net.res_trafo["loading_percent"].max()) if len(net.trafo) else float("nan")
            rows.append(dict(multiplier=mult, converged=True,
                             min_vm_pu=float(np.nanmin(vm)),
                             max_line_loading_pct=lp, max_trafo_loading_pct=tp,
                             max_loading_pct=float(H.max_loading_pct(net)),
                             meets_voltage=bool(np.nanmin(vm) >= 0.94),
                             meets_thermal=bool(H.max_loading_pct(net) <= 100.0)))
        except Exception as e:
            rows.append(dict(multiplier=mult, converged=False, error=type(e).__name__))
        print(rows[-1], flush=True)

    net = G.build_net(NETWORK)
    pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)
    tl = net.res_trafo["loading_percent"]
    worst = tl.sort_values(ascending=False).head(5)
    s = json.load(open("data/netstudy/case89pegase/range_sweep.json"))
    pooled = {}
    for r in s["sweep"]:
        for k, v in r["rejected_by"].items():
            pooled[k] = pooled.get(k, 0) + v
    doc = dict(network=NETWORK,
               question=("case89pegase accepted 0 of 200 draws at all 71 sweep candidates. "
                         "Which clause binds, and can load scaling reach feasibility?"),
               sweep_rejections_pooled=pooled,
               n_candidates=len(s["sweep"]),
               method="uniform load scaling; pinned solver; no sampling",
               scaling=rows,
               worst_trafos_at_nominal=[dict(trafo_idx=int(i), loading_pct=float(v))
                                        for i, v in worst.items()],
               n_trafo_over_100_at_nominal=int((tl > 100).sum()),
               n_trafo=int(len(net.trafo)))
    zero = [r for r in rows if r["multiplier"] == 0.0 and r.get("converged")]
    doc["verdict"] = (
        "STRUCTURAL, THERMAL CLAUSE: max loading stays above 100% even at zero load, so no "
        "load-multiplier window can satisfy the thermal clause"
        if zero and not zero[0]["meets_thermal"] else
        "NOT structural by this test: some scaling satisfies both clauses")
    V1.write_json(OUT, doc, dict(seed=None, input_file=None,
                                 run_settings=dict(phase="1a diagnostic", network=NETWORK)))
    print("\nverdict:", doc["verdict"])
