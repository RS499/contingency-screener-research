"""v2 cross-network summary: within-network (1e) and across-network (2b) results."""

import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import netstudy as V1
import netstudy2 as V2

ROOT = V2.ROOT
OUT = os.path.join(ROOT, "summary.json")


def main():
    st = json.load(open(os.path.join(ROOT, "run_status.json")))
    rows, within, cross = [], [], []
    for net in st["networks"]:
        res = st["results"].get(net, {})
        cp = os.path.join(ROOT, net, "comparison.json")
        xp = os.path.join(ROOT, net, "cross_2b_comparison.json")
        if not os.path.exists(cp):
            rows.append(dict(network=net, status=res.get("status", "not reached"),
                             note=res.get("abandon_reason")))
            continue
        c = json.load(open(cp))
        bm = json.load(open(os.path.join(ROOT, net, "prediction_inputs.json"))
                       )["dataset_boundary_mass"]
        for r in c["comparisons"]:
            within.append(dict(network=net, boundary_mass=bm, **r))
        x = json.load(open(xp)) if os.path.exists(xp) else None
        if x:
            for r in x["comparisons"]:
                cross.append(dict(network=net, prior=",".join(x["prior_networks"]), **r))
        at90 = [r for r in c["comparisons"] if abs(r["coverage_target"] - 0.90) < 1e-9]
        for r in at90:
            xr = next((q for q in (x["comparisons"] if x else [])
                       if q["family"] == r["family"]
                       and abs(q["coverage_target"] - 0.90) < 1e-9), None)
            rows.append(dict(
                network=net, status=res.get("status"), family=r["family"],
                boundary_mass=bm, predicted=r["predicted"], measured=r["measured"],
                abs_error=r["abs_error"], error_in_std_units=r["error_in_std_units"],
                hit=("HIT" if r["hit"] else "MISS"),
                cross_pred_A=(xr["pred_A_density"] if xr else None),
                cross_pred_B=(xr["pred_B_prior_slope"] if xr else None),
                cross_abs_err_A=(xr["abs_err_A"] if xr else None),
                cross_abs_err_B=(xr["abs_err_B"] if xr else None),
                seal=c["seal"]["verdict"], alarm=c["epsilon_alarm"]))

    we = np.array([r["abs_error"] for r in within]) if within else np.array([])
    by_fam = {}
    for fam in ("ridge", "histgb"):
        f = [r for r in within if r["family"] == fam]
        if f:
            se = np.array([r["signed_error"] for r in f])
            by_fam[fam] = dict(n=len(f), hits=int(sum(r["hit"] for r in f)),
                               mean_signed_error=float(se.mean()),
                               mean_abs_error=float(np.abs(se).mean()),
                               max_abs_error=float(np.abs(se).max()),
                               all_same_sign=bool((se > 0).all() or (se < 0).all()))
    doc = dict(
        phase="v2 summary",
        supersedes="data/netstudy/ (v1, VOID as validation: same rows both sides)",
        design=("1b measures the predictive CDF on the CALIBRATION split; 1d gates the "
                "DISJOINT TEST split. The error is sampling error and can be non-zero."),
        table_at_090=rows,
        within_network=dict(
            n=len(within), hits=int(sum(r["hit"] for r in within)),
            n_bitwise_identical=int(sum(r["bitwise_identical"] for r in within)),
            mean_abs_error=(float(we.mean()) if len(we) else None),
            max_abs_error=(float(we.max()) if len(we) else None),
            by_family=by_fam,
            epsilon_alarm_any=bool(any(r["network"] and False for r in within))),
        cross_network=dict(
            n=len(cross),
            A_mean_abs_error=(float(np.mean([r["abs_err_A"] for r in cross])) if cross else None),
            A_mean_rel_error=(float(np.mean([abs(r["rel_err_A"]) for r in cross
                                             if r["rel_err_A"] is not None])) if cross else None),
            B_mean_abs_error=(float(np.mean([r["abs_err_B"] for r in cross])) if cross else None),
            B_mean_rel_error=(float(np.mean([abs(r["rel_err_B"]) for r in cross
                                             if r["rel_err_B"] is not None])) if cross else None),
            B_hits=(int(sum(r["hit_B"] for r in cross)) if cross else None),
            verdict=("the cross-network prediction from boundary mass alone is the genuine "
                     "out-of-sample test; read its relative error, not the within-network one")),
        within_comparisons=within, cross_comparisons=cross)
    V1.write_json(OUT, doc, dict(seed=None, input_file=os.path.join(ROOT, "run_status.json"),
                                 input_sha256=V1.sha256_of(os.path.join(ROOT, "run_status.json")),
                                 run_settings=dict(phase="v2-summary")))
    print(json.dumps({k: doc[k] for k in ("within_network", "cross_network")},
                     indent=1, default=str))


if __name__ == "__main__":
    main()
