import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pandapower.networks as pn
import pandapower.topology as top
import networkx as nx

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import manifest as mf
import classical_manifest as cm
import tune_surrogates as T

# STAGE 2F. Is there an identifiable class of deep misses with a PRE-OUTAGE signature?
#
# THE KEY IDEA. The manuscript attributes the worst miss to a generator hitting its reactive
# limit and losing voltage control. A generator that has hit its Q limit is no longer holding
# its setpoint -- so its bus voltage departs from genvm. Both quantities are already in the
# committed feature block: genvm_g is the commanded setpoint and vm0_b is the SOLVED
# pre-outage voltage at bus b. So "generator g is at a reactive limit pre-outage" is
# computable as |vm0_[bus(g)] - genvm_g| > tol, from features the surrogate already sees.
#
# That matters for the collision this stage has to report: the manuscript says a model
# trained only on pre-outage features CANNOT predict such a discontinuity. If the signature
# is present in the pre-outage features, that claim is about statistics (these events are too
# rare to learn) rather than about information (the signal is absent). This script reports
# which; it does NOT decide which claim to keep.

DATASET = "data/dataset.parquet"
TUNED = "data/tuned_metrics.json"
OUT = "data/qlimit_class.json"
LIMIT = 0.94
SEEDS = 5
OPS = {"ridge": 0.94, "histgb": 0.97}
SETPOINT_TOL = 1e-4


def m2_config(tuned, fam, seed):
    for r in tuned["records"]:
        if r["family"] == fam and r["metric"] == "m2" and r["seed"] == seed:
            return r["config"]
    raise ValueError("missing config")


def network_maps():
    net = pn.case118()
    gen_bus = net.gen.bus.to_numpy()
    g = top.create_nxgraph(net, respect_switches=False)
    return net, gen_bus, g


def hops_from(graph, source, targets):
    try:
        lengths = nx.single_source_shortest_path_length(graph, source)
    except Exception:
        return {}
    return {t: lengths.get(t, None) for t in targets}


def main():
    t0 = time.time()
    tuned = json.load(open(TUNED))
    ms_solver = mf.load_solve_time()["ms_solver"]
    df, feat = ms.load_dataset(DATASET)
    X, y, groups, _b = ms.build_design_matrix(df, feat)

    net, gen_bus, graph = network_maps()
    n_gen = len(gen_bus)
    genvm_cols = [f"genvm_{i}" for i in range(n_gen)]
    vm0_at_gen = [f"vm0_{int(b)}" for b in gen_bus]
    genon_cols = [f"genon_{i}" for i in range(n_gen)]

    # pre-outage off-setpoint indicator, per row, per generator
    gv = df[genvm_cols].to_numpy(dtype=np.float64)
    v0 = df[vm0_at_gen].to_numpy(dtype=np.float64)
    on = df[genon_cols].to_numpy(dtype=np.float64)
    off_setpoint = (np.abs(v0 - gv) > SETPOINT_TOL) & (on > 0.5)
    n_off = off_setpoint.sum(axis=1)

    argmin_bus = df.argmin_bus.to_numpy()
    outaged_type = df.outaged_type.to_numpy()
    outaged_idx = df.outaged_idx.to_numpy()
    scen = df.scenario_id.to_numpy()

    print(f"pre-outage off-setpoint generators per row: mean={n_off.mean():.3f} "
          f"min={n_off.min()} max={n_off.max()}", flush=True)

    # min hops from the argmin bus to any off-setpoint generator, computed lazily per bus
    hop_cache = {}

    def min_hops(row):
        b = int(argmin_bus[row])
        if b < 0:
            return None
        if b not in hop_cache:
            hop_cache[b] = nx.single_source_shortest_path_length(graph, b)
        lens = hop_cache[b]
        idxs = np.flatnonzero(off_setpoint[row])
        if len(idxs) == 0:
            return None
        vals = [lens.get(int(gen_bus[i]), None) for i in idxs]
        vals = [v for v in vals if v is not None]
        return int(min(vals)) if vals else None

    deep, shallow, cert_all = [], [], []
    per_op = {}

    for fam, target in OPS.items():
        rows_deep = []
        depth_stats = []
        for seed in range(SEEDS):
            splits = ms.make_splits(groups, seed)
            kept = ms.select_features(X, splits["train"])
            Xk = X[kept]
            Xtr = Xk.iloc[splits["train"]].to_numpy(np.float32)
            fitted = T.fit_one(fam, m2_config(tuned, fam, seed), Xtr, y[splits["train"]], seed)
            p_ca = T.predict(fitted, Xk.iloc[splits["cal"]].to_numpy(np.float32))
            p_te = np.asarray(T.predict(fitted, Xk.iloc[splits["test"]].to_numpy(np.float32)),
                              dtype=np.float64)
            q = ge.calibrate_qhat(p_ca, y[splits["cal"]], target)
            gate = ge.run_gate(p_te, q, LIMIT)
            ti = splits["test"]
            yte = y[ti]
            missed = gate["certify"] & (yte < LIMIT)
            depth = LIMIT - yte
            deep_mask = missed & (depth > q)

            depth_stats.append(dict(seed=seed, q_hat=float(q),
                                    n_missed=int(missed.sum()),
                                    n_deep=int(deep_mask.sum()),
                                    max_depth=float(depth[missed].max()) if missed.any() else None,
                                    median_depth=float(np.median(depth[missed])) if missed.any() else None))

            for pos in np.flatnonzero(deep_mask):
                row = int(ti[pos])
                rows_deep.append(dict(
                    seed=seed, row=row, scenario_id=int(scen[row]),
                    outaged_type=str(outaged_type[row]), outaged_idx=int(outaged_idx[row]),
                    argmin_bus_idx=int(argmin_bus[row]),
                    argmin_bus_ieee=int(argmin_bus[row]) + 1,
                    # depth/yte are TEST-LOCAL (indexed by pos); scen/argmin_bus/off_setpoint
                    # are GLOBAL (indexed by row). Mixing the two index spaces is what the
                    # first run did, and it raised IndexError rather than silently
                    # mislabelling -- the loud failure was the lucky outcome.
                    depth=float(depth[pos]), q_hat=float(q),
                    n_offsetpoint_gens=int(n_off[row]),
                    min_hops_to_offsetpoint_gen=min_hops(row)))
            print(f"  {fam} seed {seed}: q={q:.6f} missed={int(missed.sum())} "
                  f"deep={int(deep_mask.sum())}", flush=True)

        dd = pd.DataFrame(rows_deep)
        entry = dict(target=target, per_seed_depth=depth_stats, n_deep_total=len(dd))
        if len(dd):
            elem = (dd.outaged_type + "_" + dd.outaged_idx.astype(str)).value_counts()
            bus = dd.argmin_bus_ieee.value_counts()
            entry.update(
                deep_elements=[dict(element=k, count=int(v), share=float(v) / len(dd))
                               for k, v in elem.head(10).items()],
                n_distinct_elements=int(elem.size),
                top_element_share=float(elem.iloc[0] / len(dd)),
                deep_argmin_buses_ieee=[dict(bus=int(k), count=int(v), share=float(v) / len(dd))
                                        for k, v in bus.head(10).items()],
                n_distinct_argmin_buses=int(bus.size),
                top_bus_share=float(bus.iloc[0] / len(dd)),
                offsetpoint_gens=dict(
                    mean=float(dd.n_offsetpoint_gens.mean()),
                    median=float(dd.n_offsetpoint_gens.median()),
                    min=int(dd.n_offsetpoint_gens.min()),
                    max=int(dd.n_offsetpoint_gens.max()),
                    share_with_any=float((dd.n_offsetpoint_gens > 0).mean())),
                min_hops=dict(
                    mean=float(dd.min_hops_to_offsetpoint_gen.dropna().mean())
                    if dd.min_hops_to_offsetpoint_gen.notna().any() else None,
                    median=float(dd.min_hops_to_offsetpoint_gen.dropna().median())
                    if dd.min_hops_to_offsetpoint_gen.notna().any() else None,
                    share_within_2=float((dd.min_hops_to_offsetpoint_gen.dropna() <= 2).mean())
                    if dd.min_hops_to_offsetpoint_gen.notna().any() else None),
                max_depth=float(dd.depth.max()),
                deepest=dd.loc[dd.depth.idxmax()].to_dict(),
            )
        per_op[fam] = entry

    # baseline: the same statistics over ALL converged N-1 rows, for contrast
    baseline = dict(
        n_rows=int(len(df)),
        offsetpoint_gens_mean=float(n_off.mean()),
        offsetpoint_gens_share_with_any=float((n_off > 0).mean()),
        violation_rate=float((df.min_vm < LIMIT).mean()),
    )

    out = dict(
        question=("Stage 2F: do deep misses at the recommended operating points form an "
                  "identifiable class with a PRE-OUTAGE signature?"),
        operating_points=OPS,
        limit=LIMIT,
        deep_definition="missed violation whose depth (0.94 - y) exceeds one band width q_hat",
        offsetpoint_definition=(
            "generator g counts as off-setpoint pre-outage when |vm0_[bus(g)] - genvm_g| > "
            f"{SETPOINT_TOL} and genon_g is 1. A generator holding its setpoint is regulating; "
            "one that has departed from it has hit a reactive limit."),
        baseline_all_n1_rows=baseline,
        per_operating_point=per_op,
    )

    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, default=str)
    man = cm.build_manifest(OUT, out, dict(task="Stage 2F q-limit class", source=DATASET))
    json.dump(man, open(mf.manifest_path(OUT), "w"), indent=2)
    print(f"\nwrote {OUT}  [{time.time()-t0:.0f}s]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
