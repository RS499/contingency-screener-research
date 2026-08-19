import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pandapower as pp
import pandapower.networks as pn

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manifest as mf
import classical_manifest as cm

# STAGE 2A. Two questions, deliberately kept apart.
#
# 1. THERMAL. Are line and transformer ratings present, and if so are they MEANINGFUL?
#    The plan asks for "violations are ZERO, or UNDEFINED (no rating)". A third case
#    exists and is the one that actually occurs: ratings are POPULATED BUT PLACEHOLDER.
#    A populated placeholder yields "zero violations" from any naive check, which would
#    be the most misleading possible answer. So the rating audit is reported separately
#    from any violation count, and a placeholder verdict blocks the violation count
#    rather than producing a comforting zero.
#
# 2. OVER-VOLTAGE. Recomputed from scratch here so the result stops living only in a
#    chat transcript. Nothing is copied from any prior report.
#
# NO SOLVES ARE RUN for a network whose ratings are placeholders: a loading sweep against
# a fictitious rating measures nothing.

OUT = "data/thermal_check.json"
LIMIT = 0.94
OVER_V = 1.05
SOLVER = dict(enforce_q_lims=True, numba=True, init="dc", algorithm="nr")

NETWORKS = {
    "case118": dict(builder=pn.case118, dataset="data/dataset.parquet"),
    "case30": dict(builder=pn.case30, dataset="data/case30_dataset.parquet"),
}

# A rating is judged placeholder if the base case loads it to a share this small: a real
# thermal rating on a stressed test system does not sit at a fraction of a percent.
PLACEHOLDER_BASE_LOADING_PCT = 25.0


def rating_audit(net, name):
    line_r = net.line["max_i_ka"]
    trafo_r = net.trafo["sn_mva"]

    pp.runpp(net, **SOLVER)
    base_line = net.res_line["loading_percent"]
    base_trafo = net.res_trafo["loading_percent"]

    # implied MVA of each line rating, to expose placeholder magnitudes
    vn = net.bus.loc[net.line["from_bus"].values, "vn_kv"].to_numpy()
    implied_mva = np.sqrt(3.0) * vn * line_r.to_numpy()

    out = dict(
        n_lines=int(len(net.line)),
        n_trafos=int(len(net.trafo)),
        line_max_i_ka=dict(
            n_nan=int(line_r.isna().sum()),
            n_distinct=int(line_r.nunique()),
            min=float(line_r.min()) if line_r.notna().any() else None,
            max=float(line_r.max()) if line_r.notna().any() else None,
            implied_mva_min=float(np.nanmin(implied_mva)) if len(implied_mva) else None,
            implied_mva_max=float(np.nanmax(implied_mva)) if len(implied_mva) else None,
        ),
        trafo_sn_mva=dict(
            n_nan=int(trafo_r.isna().sum()),
            n_distinct=int(trafo_r.nunique()),
            min=float(trafo_r.min()) if trafo_r.notna().any() else None,
            max=float(trafo_r.max()) if trafo_r.notna().any() else None,
        ),
        base_case_loading_pct=dict(
            line_max=float(base_line.max()) if base_line.notna().any() else None,
            line_median=float(base_line.median()) if base_line.notna().any() else None,
            trafo_max=float(base_trafo.max()) if base_trafo.notna().any() else None,
        ),
    )

    # verdicts, stated per constraint
    if line_r.isna().all() or len(net.line) == 0:
        out["line_verdict"] = "UNDEFINED (no rating)"
    elif out["base_case_loading_pct"]["line_max"] is not None and \
            out["base_case_loading_pct"]["line_max"] < PLACEHOLDER_BASE_LOADING_PCT and \
            out["line_max_i_ka"]["n_distinct"] <= 3:
        out["line_verdict"] = "UNDEFINED (rating populated but PLACEHOLDER)"
    else:
        out["line_verdict"] = "RATED (rating appears meaningful)"

    if len(net.trafo) == 0:
        out["trafo_verdict"] = "N/A (network has no transformers)"
    elif trafo_r.isna().all():
        out["trafo_verdict"] = "UNDEFINED (no rating)"
    elif out["trafo_sn_mva"]["n_distinct"] == 1 and out["trafo_sn_mva"]["max"] >= 1000.0:
        out["trafo_verdict"] = "UNDEFINED (rating populated but PLACEHOLDER)"
    else:
        out["trafo_verdict"] = "RATED (rating appears meaningful)"

    return out


def overvoltage_from_dataset(path):
    """Recomputed from the committed dataset. Nothing copied from any prior report."""
    if not os.path.exists(path):
        return dict(status="ABSENT", dataset=path)
    d = pd.read_parquet(path, columns=["outaged_type", "converged", "max_vm", "min_vm"])
    conv = d[d.converged]
    base = conv[conv.outaged_type == "none"]
    n1 = conv[conv.outaged_type != "none"]

    def block(frame):
        if len(frame) == 0:
            return dict(n=0)
        mv = frame.max_vm
        return dict(
            n=int(len(frame)),
            share_above_1p05=float((mv > OVER_V).mean()),
            share_above_1p06=float((mv > 1.06).mean()),
            share_above_1p10=float((mv > 1.10).mean()),
            max_vm_max=float(mv.max()),
            max_vm_median=float(mv.median()),
            max_vm_min=float(mv.min()),
        )

    return dict(status="OK", dataset=path, n0_base=block(base), n1=block(n1))


def thermal_sweep(builder, dataset_path, name, max_scenarios=None):
    """Re-solve every N-1 contingency and record loading. Only for RATED networks."""
    d = pd.read_parquet(dataset_path,
                        columns=["scenario_id", "outaged_type", "outaged_idx",
                                 "converged", "gen_out"])
    base_rows = d[d.outaged_type == "none"]
    scen_ids = base_rows.scenario_id.to_numpy()
    if max_scenarios is not None:
        scen_ids = scen_ids[:max_scenarios]

    feat_cols = None
    full = pd.read_parquet(dataset_path)
    load_p = [c for c in full.columns if c.startswith("pload_")]
    load_q = [c for c in full.columns if c.startswith("qload_")]
    gen_vm = [c for c in full.columns if c.startswith("genvm_")]
    gen_qmin = [c for c in full.columns if c.startswith("genqmin_")]
    gen_qmax = [c for c in full.columns if c.startswith("genqmax_")]

    by_scen = full[full.outaged_type == "none"].set_index("scenario_id")
    n1 = full[full.outaged_type != "none"]

    t0 = time.time()
    line_max, trafo_max, solved, failed = [], [], 0, 0
    for si in scen_ids:
        row = by_scen.loc[si]
        rows = n1[n1.scenario_id == si]
        for _, r in rows.iterrows():
            net = builder()
            # pload_i / qload_i are PER-BUS aggregates: generate_dataset.py:158-166 sums
            # p_new into pbus[net["_load_bus"]], indexed 0..n_bus-1. net.load rows are NOT
            # indexed by bus -- on case30, net.load.bus is
            # [1,2,3,6,7,9,11,13,14,15,16,17,18,19,20,22,23,25,28,29].
            #
            # The previous code took the first len(net.load) bus columns positionally, which
            # gave every load a different bus's demand and dropped the remainder (case30:
            # 154.48 MW assigned against 203.95 MW correct; case118 would be 118 columns
            # against 99 load rows, latent because that sweep is skipped as PLACEHOLDER).
            #
            # Index by bus instead, the idiom used at scripts/classical_screen.py:18-29.
            # ACCEPTANCE TEST: bus-mapped reproduces the dataset's stored min_vm to <=1e-7;
            # positional does not. See --self-test.
            load_bus = net.load.bus.to_numpy()
            net.load["p_mw"] = row[load_p].to_numpy(dtype=float)[load_bus]
            net.load["q_mvar"] = row[load_q].to_numpy(dtype=float)[load_bus]
            net.gen["vm_pu"] = row[gen_vm].to_numpy(dtype=float)[:len(net.gen)]
            net.gen["min_q_mvar"] = row[gen_qmin].to_numpy(dtype=float)[:len(net.gen)]
            net.gen["max_q_mvar"] = row[gen_qmax].to_numpy(dtype=float)[:len(net.gen)]
            go = int(row["gen_out"])
            if go >= 0:
                net.gen.iat[go, net.gen.columns.get_loc("in_service")] = False
            if r["outaged_type"] == "line":
                net.line.iat[int(r["outaged_idx"]),
                             net.line.columns.get_loc("in_service")] = False
            else:
                net.trafo.iat[int(r["outaged_idx"]),
                              net.trafo.columns.get_loc("in_service")] = False
            try:
                pp.runpp(net, **SOLVER)
            except Exception:
                failed += 1
                continue
            solved += 1
            lm = net.res_line["loading_percent"]
            line_max.append(float(lm.max()) if lm.notna().any() else np.nan)
            if len(net.trafo):
                tm = net.res_trafo["loading_percent"]
                trafo_max.append(float(tm.max()) if tm.notna().any() else np.nan)

    lm = np.array(line_max, dtype=float)
    lm = lm[~np.isnan(lm)]
    n_base_total = int(len(base_rows))
    is_sample = max_scenarios is not None and len(scen_ids) < n_base_total
    res = dict(
        coverage=("SAMPLE - NOT a full sweep" if is_sample else "FULL SWEEP"),
        n_base_scenarios_in_dataset=n_base_total,
        sample_note=(
            f"first {len(scen_ids)} of {n_base_total} base scenarios in dataset order, "
            f"not a random sample; shares below are estimates over that prefix"
            if is_sample else "every base scenario in the dataset"),
        n_scenarios_swept=int(len(scen_ids)),
        n_contingencies_solved=int(solved),
        n_solver_failures=int(failed),
        elapsed_s=round(time.time() - t0, 1),
        line_loading=dict(
            n=int(len(lm)),
            share_above_100=float((lm > 100.0).mean()) if len(lm) else None,
            share_above_95=float((lm > 95.0).mean()) if len(lm) else None,
            max=float(lm.max()) if len(lm) else None,
            median=float(np.median(lm)) if len(lm) else None,
            p90=float(np.percentile(lm, 90)) if len(lm) else None,
        ),
    )
    tm = np.array(trafo_max, dtype=float)
    tm = tm[~np.isnan(tm)]
    res["trafo_loading"] = (
        dict(n=int(len(tm)), share_above_100=float((tm > 100.0).mean()),
             max=float(tm.max()), median=float(np.median(tm)))
        if len(tm) else dict(n=0, note="no transformers or no trafo results")
    )
    return res


def main():
    max_scen = None
    if "--max-scenarios" in sys.argv:
        max_scen = int(sys.argv[sys.argv.index("--max-scenarios") + 1])

    out = dict(
        question=("Stage 2A: are thermal ratings present and meaningful, and what is the "
                  "over-voltage picture? Reported separately per constraint."),
        limit_under_voltage=LIMIT,
        over_voltage_threshold=OVER_V,
        solver=SOLVER,
        placeholder_rule=(f"a rating is judged PLACEHOLDER if base-case max loading is "
                          f"below {PLACEHOLDER_BASE_LOADING_PCT}% AND the rating takes at "
                          f"most 3 distinct values (lines), or is a single value at or "
                          f"above 1000 MVA (transformers)"),
        networks={},
    )

    for name, cfg in NETWORKS.items():
        print(f"--- {name} ---", flush=True)
        net = cfg["builder"]()
        audit = rating_audit(net, name)
        ov = overvoltage_from_dataset(cfg["dataset"])
        entry = dict(rating_audit=audit, overvoltage=ov)

        rated = audit["line_verdict"].startswith("RATED")
        if rated and os.path.exists(cfg["dataset"]):
            print(f"    lines RATED -> running loading sweep", flush=True)
            entry["thermal_sweep"] = thermal_sweep(cfg["builder"], cfg["dataset"], name,
                                                   max_scen)
        else:
            entry["thermal_sweep"] = dict(
                skipped=True,
                reason=(f"line_verdict={audit['line_verdict']!r}; a loading sweep against "
                        f"a placeholder or absent rating measures nothing and would "
                        f"report a misleading zero"))
        out["networks"][name] = entry
        print(f"    line_verdict : {audit['line_verdict']}", flush=True)
        print(f"    trafo_verdict: {audit['trafo_verdict']}", flush=True)

    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {OUT}")

    meta = dict(artifact="thermal rating audit, thermal loading sweep, and over-voltage "
                         "shares for case118 and case30",
                over_voltage_threshold=OVER_V,
                caveat=("Thermal verdicts are per constraint and per network. A populated "
                        "rating is NOT evidence of a meaningful rating; see "
                        "placeholder_rule."),
                model_hyperparameters=None)
    man = cm.build_manifest(OUT, out, dict(task="Stage 2A thermal and over-voltage check",
                                           sources=[c["dataset"] for c in NETWORKS.values()]))
    man["run_meta"] = meta
    with open(mf.manifest_path(OUT), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {mf.manifest_path(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
