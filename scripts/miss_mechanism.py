import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import classical_manifest as cm

import pandapower as pp
import pandapower.networks as nw
import pandapower.topology as top
import networkx as nx

SCEN = 101000025
OUT_LINE = 78
WEAK_IDX = 53
LIMIT = 0.94
SEEDS = 5


def bus_label(net, i):
    return f"{i} (IEEE {net.bus.at[i, 'name']})"


def incident_branches(net, bus_idx):
    out = []
    for i in net.line.index:
        if not net.line.at[i, "in_service"]:
            continue
        fb, tb = int(net.line.at[i, "from_bus"]), int(net.line.at[i, "to_bus"])
        if bus_idx == fb:
            out.append(("line", int(i), tb))
        elif bus_idx == tb:
            out.append(("line", int(i), fb))
    for i in net.trafo.index:
        if not net.trafo.at[i, "in_service"]:
            continue
        hv, lv = int(net.trafo.at[i, "hv_bus"]), int(net.trafo.at[i, "lv_bus"])
        if bus_idx == hv:
            out.append(("trafo", int(i), lv))
        elif bus_idx == lv:
            out.append(("trafo", int(i), hv))
    return out


def rebuild_scenario(row):
    net = nw.case118()
    nbus = len(net.bus)
    net.load = net.load.iloc[0:0].copy()
    for i in range(nbus):
        p = float(row[f"pload_{i}"]); q = float(row[f"qload_{i}"])
        if abs(p) > 0 or abs(q) > 0:
            pp.create_load(net, bus=i, p_mw=p, q_mvar=q)
    for gi in net.gen.index:
        net.gen.at[gi, "vm_pu"] = float(row[f"genvm_{gi}"])
        net.gen.at[gi, "min_q_mvar"] = float(row[f"genqmin_{gi}"])
        net.gen.at[gi, "max_q_mvar"] = float(row[f"genqmax_{gi}"])
        net.gen.at[gi, "in_service"] = bool(int(row[f"genon_{gi}"]) == 1)
    return net


def solve_min(net):
    try:
        pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)
        return True, net.res_bus.vm_pu.values.copy()
    except Exception as e:
        print("  solve failed:", e)
        return False, None


def paths_to_generation(net, src_idx, drop_line=None):
    g = top.create_nxgraph(net, respect_switches=False, include_trafos=True)
    if drop_line is not None:
        fb, tb = int(net.line.at[drop_line, "from_bus"]), int(net.line.at[drop_line, "to_bus"])
        if g.has_edge(fb, tb):
            g.remove_edge(fb, tb)
    gen_buses = set(int(b) for b in net.gen.bus.values) | set(int(b) for b in net.ext_grid.bus.values)
    g.add_node("GEN")
    for b in gen_buses:
        if b in g:
            g.add_edge(b, "GEN")
    deg = int(g.degree(src_idx)) if src_idx in g else 0
    if src_idx in gen_buses:
        conn = "src_is_generator"
    else:
        conn = int(nx.node_connectivity(g, src_idx, "GEN"))
    return deg, conn


def main():
    df = pd.read_parquet("data/dataset.parquet")
    srow = df[df["scenario_id"] == SCEN].iloc[0]

    net0 = nw.case118()

    fb = int(net0.line.at[OUT_LINE, "from_bus"]); tb = int(net0.line.at[OUT_LINE, "to_bus"])
    adjacency = {}
    for b in sorted({fb, tb, WEAK_IDX, 54}):
        adjacency[str(b)] = dict(label=bus_label(net0, b),
                                 neighbors=[dict(kind=k, idx=ix, other=bus_label(net0, ob))
                                            for (k, ix, ob) in incident_branches(net0, b)])

    gen_buses = set(int(b) for b in net0.gen.bus.values)
    slack_buses = set(int(b) for b in net0.ext_grid.bus.values)
    weak_type = ("PV (has generator)" if WEAK_IDX in gen_buses else
                 "slack" if WEAK_IDX in slack_buses else "PQ (load/no local voltage control)")

    deg_in, conn_in = paths_to_generation(net0, WEAK_IDX, drop_line=None)
    deg_out, conn_out = paths_to_generation(net0, WEAK_IDX, drop_line=OUT_LINE)
    endpoint_deg_after = {}
    g_after = top.create_nxgraph(net0, respect_switches=False, include_trafos=True)
    if g_after.has_edge(fb, tb):
        g_after.remove_edge(fb, tb)
    for b in (fb, tb, WEAK_IDX):
        endpoint_deg_after[str(b)] = int(g_after.degree(b)) if b in g_after else 0

    g_hops = top.create_nxgraph(net0, respect_switches=False, include_trafos=True)
    near = set([WEAK_IDX])
    if WEAK_IDX in g_hops:
        near |= set(nx.single_source_shortest_path_length(g_hops, WEAK_IDX, cutoff=2).keys())
    gens_near = []
    for gi in net0.gen.index:
        gb = int(net0.gen.at[gi, "bus"])
        if gb in near:
            hop = nx.shortest_path_length(g_hops, WEAK_IDX, gb) if gb in g_hops else None
            gens_near.append(dict(gen=int(gi), bus=bus_label(net0, gb), hops=hop,
                                  qmin_scn=float(srow[f"genqmin_{gi}"]),
                                  qmax_scn=float(srow[f"genqmax_{gi}"]),
                                  on=int(srow[f"genon_{gi}"])))
    shunts_near = []
    if hasattr(net0, "shunt") and len(net0.shunt):
        for si in net0.shunt.index:
            sb = int(net0.shunt.at[si, "bus"])
            if sb in near:
                shunts_near.append(dict(shunt=int(si), bus=bus_label(net0, sb),
                                        q_mvar=float(net0.shunt.at[si, "q_mvar"])))

    net = rebuild_scenario(srow)
    n0_conv, vm0 = solve_min(net)
    base_min = float(np.nanmin(vm0)) if n0_conv else None
    base_argmin = int(np.nanargmin(vm0)) if n0_conv else None
    base_gen_q = net.res_gen.q_mvar.values.copy() if n0_conv else None

    net.line.at[OUT_LINE, "in_service"] = False
    n1_conv, vm1 = solve_min(net)
    n1_min = float(np.nanmin(vm1)) if n1_conv else None
    n1_argmin = int(np.nanargmin(vm1)) if n1_conv else None

    recorded_min = float(srow_min(df))
    reproduced = (n1_conv and abs(n1_min - recorded_min) < 1e-4 and n1_argmin == WEAK_IDX)
    print(f"[reproduce] recorded min_vm={recorded_min:.5f}@bus{WEAK_IDX} | "
          f"solved N-1 min_vm={n1_min:.5f}@bus{n1_argmin} | match={reproduced}", flush=True)
    print(f"[base]  N-0 min_vm={base_min:.5f}@bus{base_argmin} (dataset n0_min_vm={float(srow['n0_min_vm']):.5f})", flush=True)

    sat = []
    if n1_conv:
        qn1 = net.res_gen.q_mvar.values
        for gi in net.gen.index:
            if not bool(net.gen.at[gi, "in_service"]):
                continue
            qmax = float(net.gen.at[gi, "max_q_mvar"]); qmin = float(net.gen.at[gi, "min_q_mvar"])
            q = float(qn1[net.gen.index.get_loc(gi)])
            at_max = q >= qmax - 1e-3
            at_min = q <= qmin + 1e-3
            gb = int(net.gen.at[gi, "bus"])
            if (at_max or at_min) and gb in near:
                q0 = float(base_gen_q[net.gen.index.get_loc(gi)]) if base_gen_q is not None else None
                sat.append(dict(gen=int(gi), bus=bus_label(net0, gb), q_n1=q, qmax=qmax, qmin=qmin,
                                q_n0=q0, at_max=at_max, at_min=at_min,
                                hops=(nx.shortest_path_length(g_hops, WEAK_IDX, gb) if gb in g_hops else None)))
    key_v = {}
    for b in sorted({fb, tb, WEAK_IDX}):
        key_v[str(b)] = dict(label=bus_label(net0, b),
                             vm_n0=(float(vm0[b]) if n0_conv else None),
                             vm_n1=(float(vm1[b]) if n1_conv else None))

    _dfg, fc = ms.load_dataset("data/dataset.parquet")
    _X, _y, groups, _b = ms.build_design_matrix(_dfg, fc)
    all_scen = np.array(sorted(set(int(s) for s in groups)))
    idx_of = {s: k for k, s in enumerate(all_scen)}
    counts = np.zeros(len(all_scen), dtype=int)
    scen_seeds = {SCEN: []}
    for seed in range(SEEDS):
        sp = ms.make_splits(groups, seed)
        test_scen = set(int(s) for s in groups[sp["test"]])
        for s in test_scen:
            counts[idx_of[s]] += 1
        if SCEN in test_scen:
            scen_seeds[SCEN].append(seed)
    hist = {str(k): int((counts == k).sum()) for k in range(SEEDS + 1)}
    from math import comb
    p = 0.2
    n_scen = len(all_scen)
    expected = {str(k): float(n_scen * comb(SEEDS, k) * p**k * (1 - p)**(SEEDS - k)) for k in range(SEEDS + 1)}
    mean_count = float(counts.mean())
    chi2 = float(sum((hist[str(k)] - expected[str(k)])**2 / expected[str(k)]
                     for k in range(SEEDS + 1) if expected[str(k)] > 0))
    binom_ok = abs(mean_count - 1.0) < 0.05
    print(f"[split] scenario {SCEN} test-seeds={scen_seeds[SCEN]} (count {len(scen_seeds[SCEN])})", flush=True)
    print(f"[split] membership counts obs={hist} mean={mean_count:.4f} chi2={chi2:.2f} "
          f"(expected Binomial(5,0.2) mean 1.0)", flush=True)

    out = dict(
        scenario_id=SCEN, outaged_line=OUT_LINE, weak_bus_index=WEAK_IDX,
        weak_bus_ieee_name=int(net0.bus.at[WEAK_IDX, "name"]),
        note_index_vs_name="pandapower bus INDEX != IEEE bus NAME; both are reported everywhere",
        part1_mechanism=dict(
            line78_endpoints=dict(from_bus=bus_label(net0, fb), to_bus=bus_label(net0, tb)),
            adjacency=adjacency,
            weak_bus_type=weak_type,
            paths_to_generation=dict(
                weak_bus_degree_intact=deg_in, indep_paths_to_gen_intact=conn_in,
                weak_bus_degree_line78_out=deg_out, indep_paths_to_gen_line78_out=conn_out,
                endpoint_degree_after_outage=endpoint_deg_after,
                radial_after_outage=any(d == 1 for d in endpoint_deg_after.values())),
            reactive_support_near_weak_bus=dict(generators_within_2_hops=gens_near,
                                                shunts_within_2_hops=shunts_near),
            reconstruction=dict(reproduced=bool(reproduced), recorded_min_vm=recorded_min,
                                solved_n1_min_vm=n1_min, solved_n1_argmin=n1_argmin,
                                solved_n0_min_vm=base_min, solved_n0_argmin=base_argmin,
                                dataset_n0_min_vm=float(srow["n0_min_vm"])),
            key_bus_voltages_n0_vs_n1=key_v,
            saturated_gens_near_weak_bus_post_outage=sat),
        part2_split_independence=dict(
            scenario_test_seeds=scen_seeds[SCEN], scenario_test_count=len(scen_seeds[SCEN]),
            n_scenarios=n_scen, test_frac_per_seed=0.2, seeds=SEEDS,
            observed_membership_counts=hist, expected_binomial_5_0p2=expected,
            mean_membership_count=mean_count, chi_square=chi2,
            independent_ok=bool(binom_ok),
            interpretation=("mean ~1.0 and observed ~ expected Binomial(5,0.2) => per-seed test sets "
                            "are independent draws; a large chi-square or mean far from 1.0 would flag "
                            "correlated splits")),
        solver="enforce_q_lims=True, init=dc, numba=True (pinned)",
        solves_run=2)
    settings = dict(task="deepest-miss physical mechanism + split independence",
                    source="data/dataset.parquet (scenario 101000025 features)",
                    solves="2 AC solves: reconstructed N-0 base and N-1 (line 78 out)")
    cm.write_with_manifest("data/miss_mechanism.json", out, settings)
    print("\nwrote data/miss_mechanism.json")


def srow_min(df):
    r = df[(df["scenario_id"] == SCEN) & (df["outaged_type"] == "line") & (df["outaged_idx"] == OUT_LINE)]
    return float(r["min_vm"].iloc[0])


if __name__ == "__main__":
    main()
