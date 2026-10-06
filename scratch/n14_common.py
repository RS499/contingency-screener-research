import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd
import networkx as nx
import pandapower.networks as nw
import pandapower.topology as top

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import make_splits as ms
import n5_gate_eval as n5

# N14 shared helpers (scratch/n14_decision_rule.md §B).
# Islanding: an outage after which at least one bus is no longer connected to the reference (ext_grid) bus, from the
# base network's topology (scenario-independent: every branch is in service in every base).
# Exclusion (primary): the reference bus's island holds fewer than half of the network's buses.
# Sensitivity: every islanding outage removed.
# Rows of removed outages are dropped from the rebuilt N13 dataset (data/sts_n13_<name>.parquet) before the design
# matrix is built; splits are drawn by base case (scenario_id), so they do not change.

RULE = "scratch/n14_decision_rule.md"
RULE_SHA = "scratch/n14_decision_rule.sha256"
NETWORK = {"D94": "case118", "ILL": "case_illinois200", "C30": "case30", "C24": "case24_ieee_rts"}
N_LINE = {"D94": 173, "ILL": 179, "C30": 41, "C24": 33}
LIMIT = 0.94


def check_hash():
    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    return h


def topology(name):
    net = getattr(nw, NETWORK[name])()
    ref = set(net.ext_grid.bus.tolist())
    nb = len(net.bus)
    out = []
    branches = [("line", int(i)) for i in net.line.index if net.line.at[i, "in_service"]]
    branches += [("trafo", int(i)) for i in net.trafo.index if net.trafo.at[i, "in_service"]]
    for t, i in branches:
        net[t].at[i, "in_service"] = False
        g = top.create_nxgraph(net, respect_switches=True)
        net[t].at[i, "in_service"] = True
        rc = [cc for cc in nx.connected_components(g) if cc & ref][0]
        if len(rc) < nb:
            out.append(dict(outaged_type=t, outaged_idx=i, ref_island=len(rc), n_bus=nb))
    return out


def removed_outages(name, mode):
    isl = topology(name)
    if mode == "primary":
        return [(x["outaged_type"], x["outaged_idx"]) for x in isl if x["ref_island"] < x["n_bus"] / 2.0]
    if mode == "sensitivity":
        return [(x["outaged_type"], x["outaged_idx"]) for x in isl]
    return []


def load(name, mode):
    df, feature_cols, info = n5.load_relabeled(f"data/sts_n13_{name}.parquet", "")
    rem = removed_outages(name, mode)
    keys = set(rem)
    drop = np.array([(a, int(b)) in keys for a, b in zip(df["outaged_type"], df["outaged_idx"])], dtype=bool)
    df = df[~drop].reset_index(drop=True)
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    is_trafo = df["outaged_type"].to_numpy() == "trafo"
    ek = df["outaged_idx"].to_numpy(np.int64) + np.where(is_trafo, N_LINE[name], 0)
    info = dict(info)
    info.update(labels="the rebuilt N13 dataset's own min_vm (corrected solver)", mode=mode,
                removed_outages=[dict(outaged_type=a, outaged_idx=b) for a, b in rem], n_rows_removed=int(drop.sum()),
                n_rows_used=int(len(df)))
    return dict(name=name, df=df, X=X, y=y, groups=groups, elem_key=ek, info=info)


def islanding_mask(name, df):
    keys = set([(x["outaged_type"], x["outaged_idx"]) for x in topology(name)])
    return np.array([(a, int(b)) in keys for a, b in zip(df["outaged_type"], df["outaged_idx"])], dtype=bool)
