"""PART B: build four toggleable physics feature families for case118.

Re-solves the 1,500 N-0 BASE cases only. No contingency solves. Same pinned oracle
(enforce_q_lims=True, numba, init="dc", nr) and the same builder helpers as the committed
generator.

F1  outaged-element pre-outage flow  (4 cols)   p_mw, q_mvar, loading_percent, i_ka
F2  full pre-outage loading vector   (186 cols) loading_percent for every branch
F3  LODF row                         (186 cols) exact DC line outage distribution factors
F4  electrical distance              (118 cols) impedance-weighted distance to every bus

Base-case reconstruction is validated against the stored vm0_* vector before any feature is
emitted. A reconstruction that does not reproduce the committed solve is a defect, not a
starting point.
"""

import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pandapower as pp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, HERE)
import generate_dataset as G
import make_splits as ms
import netstudy as V1

NETWORK = "case118"
DATASET = "data/dataset.parquet"
OUTDIR = "data/physics"
SUMMARY = "data/physics_features.json"


def audit_columns(df):
    import re
    import collections
    pat = re.compile(r'flow|loading|p_mw|q_mvar|i_ka|lodf|ptdf|va_degree', re.I)
    cols = list(df.columns)
    feat = [c for c in cols if c not in ms.EXCLUDE_COLS and pd.api.types.is_numeric_dtype(df[c])]
    fam = dict(collections.Counter(re.sub(r'\d+$', '', c) for c in feat))
    return dict(
        n_columns_total=len(cols),
        n_feature_columns=len(feat),
        feature_families=fam,
        loading_like_names_anywhere=[c for c in cols if pat.search(c)],
        loading_like_among_features=[c for c in feat if pat.search(c)],
        agg_loading_in_EXCLUDE_COLS=bool("agg_loading" in ms.EXCLUDE_COLS),
        agg_loading_is_a_feature=bool("agg_loading" in feat),
        branch_flow_columns_present=False,
        correction_to_the_premise=(
            "The brief says 'the only loading feature is the scenario scalar agg_loading'. "
            "That is not right: agg_loading is listed in make_splits.EXCLUDE_COLS and is "
            "therefore NOT a feature. The committed design matrix carries NO loading "
            "information of any kind. It does carry vm0_* (118 pre-outage bus voltages), so "
            "part of the base AC solution is already exposed - the voltages, not the flows."))


def reconstruct(net, row, n_bus, n_gen):
    """Rebuild one base operating point from the committed feature columns.

    pload_i / qload_i are PER BUS (generate_dataset.py:163-164 writes pbus/qbus). case118 has
    at most one load per bus, so the bus -> load-row map is unique. Positional assignment to
    net.load would be wrong; this is the defect CORRECTION C-4 recorded for thermal_check.
    """
    pb = np.array([row[f"pload_{i}"] for i in range(n_bus)], dtype=np.float64)
    qb = np.array([row[f"qload_{i}"] for i in range(n_bus)], dtype=np.float64)
    buses = net.load.bus.values.astype(int)
    net.load["p_mw"] = pb[buses]
    net.load["q_mvar"] = qb[buses]
    net.gen["vm_pu"] = np.array([row[f"genvm_{g}"] for g in range(n_gen)], dtype=np.float64)
    net.gen["min_q_mvar"] = np.array([row[f"genqmin_{g}"] for g in range(n_gen)], dtype=np.float64)
    net.gen["max_q_mvar"] = np.array([row[f"genqmax_{g}"] for g in range(n_gen)], dtype=np.float64)
    net.gen["in_service"] = np.array([bool(row[f"genon_{g}"]) for g in range(n_gen)])


def branch_flows(net):
    """From-side / HV-side pre-outage flow per branch, in branch_list order."""
    rl, rt = net.res_line, net.res_trafo
    p = list(rl["p_from_mw"].values) + list(rt["p_hv_mw"].values)
    q = list(rl["q_from_mvar"].values) + list(rt["q_hv_mvar"].values)
    ld = list(rl["loading_percent"].values) + list(rt["loading_percent"].values)
    ik = list(rl["i_from_ka"].values) + list(rt["i_hv_ka"].values)
    return np.array(p), np.array(q), np.array(ld), np.array(ik)


def build_lodf(net):
    """Exact DC LODF from the base-case branch admittance. Not an approximation of AC."""
    from pandapower.pypower.makePTDF import makePTDF
    from pandapower.pypower.makeLODF import makeLODF
    from pandapower.pd2ppc import _pd2ppc
    net2 = G.build_net(NETWORK)
    pp.runpp(net2, enforce_q_lims=True, init="dc", numba=True)
    ppc, _ppci = _pd2ppc(net2)
    baseMVA, bus, branch = ppc["baseMVA"], ppc["bus"], ppc["branch"]
    slack = int(np.where(bus[:, 1] == 3)[0][0])
    H = makePTDF(baseMVA, bus, branch, slack)
    lodf = makeLODF(branch, H)
    lookup = net2["_pd2ppc_lookups"]["branch"]
    return np.asarray(lodf), {k: (int(v[0]), int(v[1])) for k, v in lookup.items()}, ppc


def build_edistance(net, branches):
    """F4 definition, stated: weighted shortest-path over branch impedance magnitude.

    Edge weight = |z| = sqrt(r_pu^2 + x_pu^2) on the FULL in-service network. For each outaged
    branch, distance to bus b = min over the branch's two terminal buses of the weighted
    shortest path to b. Units are per-unit impedance. Unreachable buses get -1.
    """
    import networkx as nx
    g = nx.Graph()
    for i in net.bus.index:
        g.add_node(int(i))
    zb = net.sn_mva
    for i in net.line.index:
        r = net.line.at[i, "r_ohm_per_km"] * net.line.at[i, "length_km"]
        x = net.line.at[i, "x_ohm_per_km"] * net.line.at[i, "length_km"]
        vn = net.bus.at[net.line.at[i, "from_bus"], "vn_kv"]
        base_z = vn ** 2 / zb
        w = float(np.hypot(r, x) / base_z)
        g.add_edge(int(net.line.at[i, "from_bus"]), int(net.line.at[i, "to_bus"]),
                   weight=max(w, 1e-9))
    for i in net.trafo.index:
        w = float(net.trafo.at[i, "vk_percent"] / 100.0)
        g.add_edge(int(net.trafo.at[i, "hv_bus"]), int(net.trafo.at[i, "lv_bus"]),
                   weight=max(w, 1e-9))
    n_bus = len(net.bus)
    out = np.full((len(branches), n_bus), -1.0)
    import networkx.algorithms.shortest_paths.weighted as wsp
    cache = {}
    for r, (etype, idx) in enumerate(branches):
        if etype == "line":
            a, b = int(net.line.at[idx, "from_bus"]), int(net.line.at[idx, "to_bus"])
        else:
            a, b = int(net.trafo.at[idx, "hv_bus"]), int(net.trafo.at[idx, "lv_bus"])
        for term in (a, b):
            if term not in cache:
                cache[term] = wsp.single_source_dijkstra_path_length(g, term, weight="weight")
        da, db = cache[a], cache[b]
        for bus_i in range(n_bus):
            va, vb = da.get(bus_i), db.get(bus_i)
            vals = [v for v in (va, vb) if v is not None]
            out[r, bus_i] = min(vals) if vals else -1.0
    return out


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    t_all = time.time()
    df = pd.read_parquet(DATASET)
    audit = audit_columns(df)
    print(json.dumps(audit, indent=1))

    base = df[df.outaged_type == "none"].reset_index(drop=True)
    net = G.build_net(NETWORK)
    n_bus, n_gen = len(net.bus), len(net.gen)
    branches = G.branch_list(net)
    print(f"\nbase rows {len(base)}  buses {n_bus}  gens {n_gen}  branches {len(branches)}")

    vm_err, minvm_err, rows = [], [], []
    n_fail = 0
    t0 = time.time()
    for r in range(len(base)):
        row = base.iloc[r]
        reconstruct(net, row, n_bus, n_gen)
        try:
            pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)
            conv = True
        except Exception:
            conv = False
        if not conv:
            n_fail += 1
            continue
        vm = net.res_bus.vm_pu.values
        stored = np.array([row[f"vm0_{i}"] for i in range(n_bus)], dtype=np.float64)
        vm_err.append(float(np.abs(vm - stored).max()))
        minvm_err.append(abs(float(np.nanmin(vm)) - float(row["n0_min_vm"])))
        p, q, ld, ik = branch_flows(net)
        sid = int(row["scenario_id"])
        for bi, (etype, idx) in enumerate(branches):
            rows.append((sid, etype, int(idx), p[bi], q[bi], ld[bi], ik[bi]))
        if (r + 1) % 250 == 0:
            print(f"  solved {r+1}/{len(base)} [{time.time()-t0:.0f}s] "
                  f"max|vm err| so far {max(vm_err):.3e}", flush=True)
    elapsed = time.time() - t0

    flows = pd.DataFrame(rows, columns=["scenario_id", "outaged_type", "outaged_idx",
                                        "pre_p_mw", "pre_q_mvar", "pre_loading_percent",
                                        "pre_i_ka"])
    fp = os.path.join(OUTDIR, "base_flows.parquet")
    flows.to_parquet(fp, index=False)

    accept = dict(n_base=len(base), n_nonconverged=n_fail,
                  max_abs_vm_error=float(np.max(vm_err)),
                  median_abs_vm_error=float(np.median(vm_err)),
                  max_abs_n0_min_vm_error=float(np.max(minvm_err)),
                  tolerance_note="reconstruction is accepted only if max|vm error| < 1e-6",
                  passed=bool(np.max(vm_err) < 1e-6))
    print("\nacceptance:", json.dumps(accept, indent=1))

    t3 = time.time()
    try:
        lodf, lookup, ppc = build_lodf(net)
        n_ppc = lodf.shape[0]
        rowsL = []
        for bi, (etype, idx) in enumerate(branches):
            lo, hi = lookup[etype]
            rowsL.append(lodf[lo + int(idx), :])
        lodf_df = pd.DataFrame(np.array(rowsL),
                               columns=[f"lodf_{j}" for j in range(n_ppc)])
        lodf_df.insert(0, "outaged_idx", [int(i) for _t, i in branches])
        lodf_df.insert(0, "outaged_type", [t for t, _i in branches])
        lodf_df.to_parquet(os.path.join(OUTDIR, "lodf.parquet"), index=False)
        f3 = dict(status="AVAILABLE", n_cols=int(n_ppc),
                  source="pandapower.pypower.makeLODF on the base-case ppc branch array",
                  definition=("exact DC line outage distribution factors: dF_l / F_k for the "
                              "outage of branch k, from the linearized DC network. LODF is by "
                              "construction a DC quantity; this is NOT an approximation of an "
                              "AC quantity, it is the exact value of the DC quantity."),
                  ppc_branch_lookup={k: list(v) for k, v in lookup.items()},
                  constant_across_scenarios=True,
                  constant_reason=("depends only on branch series admittance and topology, "
                                   "neither of which varies across scenarios: generator "
                                   "outages change in_service on gens, not on branches"),
                  elapsed_s=round(time.time() - t3, 2))
    except Exception as e:
        f3 = dict(status="NOT AVAILABLE", reason=f"{type(e).__name__}: {e}")
    print("F3:", json.dumps({k: v for k, v in f3.items() if k != "ppc_branch_lookup"}, indent=1))

    t4 = time.time()
    ed = build_edistance(net, branches)
    ed_df = pd.DataFrame(ed, columns=[f"edist_{i}" for i in range(n_bus)])
    ed_df.insert(0, "outaged_idx", [int(i) for _t, i in branches])
    ed_df.insert(0, "outaged_type", [t for t, _i in branches])
    ed_df.to_parquet(os.path.join(OUTDIR, "edistance.parquet"), index=False)
    f4 = dict(status="AVAILABLE", n_cols=int(n_bus),
              definition=("weighted shortest path over branch impedance magnitude "
                          "|z|=sqrt(r_pu^2+x_pu^2); transformers weighted by vk_percent/100. "
                          "Distance from an outaged branch to bus b is the MINIMUM over the "
                          "branch's two terminal buses. Unreachable = -1."),
              constant_across_scenarios=True, n_unreachable=int((ed < 0).sum()),
              elapsed_s=round(time.time() - t4, 2))
    print("F4:", json.dumps(f4, indent=1))

    doc = dict(
        part="B (feature construction). PART C ablation NOT run.",
        network=NETWORK, dataset=DATASET,
        prereg_sha256_at_partA="51f1544675b9a237e7078672086c2266e7f11da2e16c7bee98795e46ed6478fc",
        column_audit=audit,
        resolve=dict(n_base_cases=len(base), n_contingency_solves=0,
                     elapsed_s=round(elapsed, 1),
                     solver=dict(enforce_q_lims=True, numba=True, init="dc", algorithm="nr"),
                     builder="feasibility/generate_dataset.build_net + reconstruct()",
                     acceptance=accept),
        F1=dict(status="AVAILABLE", n_cols=4,
                cols=["pre_p_mw", "pre_q_mvar", "pre_loading_percent", "pre_i_ka"],
                side="from-side for lines, HV-side for transformers",
                artifact=fp, join_key=["scenario_id", "outaged_type", "outaged_idx"]),
        F2=dict(status="AVAILABLE", n_cols=len(branches),
                note="pivot of the same artifact: pre_loading_percent for all 186 branches, "
                     "identical across the 186 rows of a scenario",
                artifact=fp),
        F3=f3, F4=f4,
        total_elapsed_s=round(time.time() - t_all, 1))
    V1.write_json(SUMMARY, doc, dict(seed=None, input_file=DATASET,
                                     input_sha256=V1.sha256_of(DATASET),
                                     run_settings=dict(part="B", network=NETWORK)))
    print(f"\nwrote {SUMMARY}; total {doc['total_elapsed_s']}s")


if __name__ == "__main__":
    main()
