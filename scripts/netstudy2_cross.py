"""Cross-network escalation prediction: 2a record, 2b predict a NEW network from PRIOR ones.

2a  For every already-run network, record (boundary density, q_hat, measured escalation)
    per model per coverage target. Nothing is fitted.
2b  For a network whose gate has NOT run, predict its escalation from its boundary mass and
    its calibration-split q_hat, using ONLY the relationship observed on prior networks.
    Sealed before the gate. This is out-of-sample ACROSS networks, not within one.

Two predictors, both sealed:
  A  parameter-free density model:  esc = (boundary_mass / STRIP_W) * q_hat
  B  prior-fitted slope through the origin: esc = a * (boundary_mass / STRIP_W) * q_hat,
     a = sum(x*y)/sum(x*x) over prior-network points only.
"""

import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import netstudy as V1
import netstudy2 as V2

ROOT = "data/netstudy2"
PREREG = V2.PREREG
STRIP_W = V2.STRIP_W


def points_case118():
    fz = json.load(open("data/frozen_poster_numbers.json"))
    bm = fz["dataset_facts"]["boundary_0p94_to_0p945_pct"] / 100.0
    tc = json.load(open("data/tradeoff_curve_v2.json"))
    return [dict(network="case118", family=r["model"], coverage_target=r["coverage_target"],
                 boundary_mass=bm, q_hat=r["q_hat"], escalation=r["escalation"],
                 source="data/tradeoff_curve_v2.json + data/frozen_poster_numbers.json")
            for r in tc["records"]]


def points_case30_thermal():
    fz = json.load(open("data/case30_thermal/case30_thermal_frozen.json"))
    bm = fz["boundary_mass_pct"] / 100.0
    by = {}
    for r in fz["records"]:
        by.setdefault((r["family"], r["coverage_target"]), []).append(r)
    return [dict(network="case30_thermal", family=k[0], coverage_target=k[1],
                 boundary_mass=bm,
                 q_hat=float(np.mean([x["q_hat"] for x in v])),
                 escalation=float(np.mean([x["escalation"] for x in v])),
                 source="data/case30_thermal/case30_thermal_frozen.json")
            for k, v in by.items()]


def points_netstudy2(network):
    p = os.path.join(ROOT, network, "frozen.json")
    if not os.path.exists(p):
        return []
    fz = json.load(open(p))
    bm = fz["boundary_mass_pct"] / 100.0
    by = {}
    for r in fz["records"]:
        by.setdefault((r["family"], r["coverage_target"]), []).append(r)
    return [dict(network=network, family=k[0], coverage_target=k[1], boundary_mass=bm,
                 q_hat=float(np.mean([x["q_hat"] for x in v])),
                 escalation=float(np.mean([x["escalation"] for x in v])), source=p)
            for k, v in by.items()]


def phase_2a(done_networks):
    pts = points_case118() + points_case30_thermal()
    for n in done_networks:
        pts += points_netstudy2(n)
    for p in pts:
        p["rho_times_qhat"] = (p["boundary_mass"] / STRIP_W) * p["q_hat"]
    doc = dict(phase="2a record (nothing fitted)",
               strip_width=STRIP_W,
               density_definition="rho = boundary_mass / strip_width, strip = [0.94, 0.945)",
               n_points=len(pts),
               networks=sorted({p["network"] for p in pts}),
               points=pts)
    path = os.path.join(ROOT, "cross_2a_points.json")
    os.makedirs(ROOT, exist_ok=True)
    V1.write_json(path, doc, dict(seed=None, input_file=None,
                                  run_settings=dict(phase="2a")))
    return doc


def fit_slope(points):
    x = np.array([p["rho_times_qhat"] for p in points], dtype=float)
    y = np.array([p["escalation"] for p in points], dtype=float)
    a = float((x * y).sum() / (x * x).sum())
    resid = y - a * x
    return dict(slope_through_origin=a, n_points=len(points),
                residual_std=float(resid.std(ddof=0)),
                residual_mean_abs=float(np.abs(resid).mean()),
                fitted_on=sorted({p["network"] for p in points}))


def phase_2b_seal(network, prior_networks):
    """Predict this network's escalation from PRIOR networks only. Gate must not have run."""
    fz_path = os.path.join(ROOT, network, "frozen.json")
    if os.path.exists(fz_path):
        raise RuntimeError(f"{network}: frozen.json already exists. 2b must seal BEFORE 1d.")
    a2 = phase_2a(prior_networks)
    prior = [p for p in a2["points"] if p["network"] != network]
    fit = fit_slope(prior)

    pi = json.load(open(os.path.join(ROOT, network, "prediction_inputs.json")))
    bm = pi["dataset_boundary_mass"]
    rho = bm / STRIP_W
    preds = []
    for p in pi["predictions"]:
        x = rho * p["mean_q_hat"]
        preds.append(dict(family=p["family"], coverage_target=p["coverage_target"],
                          boundary_mass=bm, rho=rho, mean_q_hat=p["mean_q_hat"],
                          rho_times_qhat=x,
                          pred_A_density=x,
                          pred_B_prior_slope=fit["slope_through_origin"] * x,
                          pred_B_interval_lo=fit["slope_through_origin"] * x - fit["residual_std"],
                          pred_B_interval_hi=fit["slope_through_origin"] * x + fit["residual_std"]))

    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    head = V1.git_out(["rev-parse", "HEAD"])
    L = ["", "---", "",
         f"## SEALED CROSS-NETWORK PREDICTION (2b) — {network}", "",
         f"**Sealed:** {stamp}   **git HEAD:** `{head}`",
         f"**Prior networks used (this network EXCLUDED):** {', '.join(fit['fitted_on'])}",
         f"**Prior points:** {fit['n_points']}   "
         f"**Slope through origin:** {fit['slope_through_origin']!r}   "
         f"**Residual std:** {fit['residual_std']!r}",
         f"**This network's boundary mass:** {bm!r}   **rho:** {rho!r}", "",
         "| family | target | rho*q_hat | pred A (density) | pred B (prior slope) | B lo | B hi |",
         "|---|---|---|---|---|---|---|"]
    for p in preds:
        L.append(f"| {p['family']} | {p['coverage_target']} | {p['rho_times_qhat']!r} | "
                 f"{p['pred_A_density']!r} | {p['pred_B_prior_slope']!r} | "
                 f"{p['pred_B_interval_lo']!r} | {p['pred_B_interval_hi']!r} |")
    L += ["", "**This prediction can fail badly.** It uses no information from this network's "
              "own gate and only its true-min_vm boundary mass plus its calibration q_hat.", "",
          f"gate not yet run on {network} as of {stamp}", ""]
    with open(PREREG, "a", encoding="utf-8") as f:
        f.write("\n".join(L))
    sha = V1.sha256_of(PREREG)
    n_lines = sum(1 for _ in open(PREREG, "rb"))

    doc = dict(network=network, phase="2b sealed cross-network prediction",
               sealed_utc=stamp, git_head=head,
               preregistration_sha256=sha, sealed_prefix_lines=n_lines,
               prior_fit=fit, prior_networks=fit["fitted_on"],
               boundary_mass=bm, rho=rho, predictions=preds,
               gate_run_before_seal=False)
    path = os.path.join(ROOT, network, "cross_2b_seal.json")
    V1.write_json(path, doc, dict(seed=None, input_file=PREREG, input_sha256=sha,
                                  run_settings=dict(phase="2b-seal", network=network)))
    print(f"[{network}] 2b SEAL sha256={sha} prefix={n_lines} "
          f"slope={fit['slope_through_origin']:.6f} on {fit['n_points']} prior points",
          flush=True)
    return doc


def phase_2b_compare(network):
    seal = json.load(open(os.path.join(ROOT, network, "cross_2b_seal.json")))
    fz = json.load(open(os.path.join(ROOT, network, "frozen.json")))
    meas = {}
    for r in fz["records"]:
        meas.setdefault((r["family"], r["coverage_target"]), []).append(r["escalation"])
    rows = []
    for p in seal["predictions"]:
        v = np.array(meas[(p["family"], p["coverage_target"])], dtype=float)
        m = float(v.mean())
        rows.append(dict(
            family=p["family"], coverage_target=p["coverage_target"], measured=m,
            pred_A_density=p["pred_A_density"],
            err_A=m - p["pred_A_density"],
            abs_err_A=abs(m - p["pred_A_density"]),
            rel_err_A=(None if m == 0 else (m - p["pred_A_density"]) / m),
            pred_B_prior_slope=p["pred_B_prior_slope"],
            err_B=m - p["pred_B_prior_slope"],
            abs_err_B=abs(m - p["pred_B_prior_slope"]),
            rel_err_B=(None if m == 0 else (m - p["pred_B_prior_slope"]) / m),
            hit_B=bool(p["pred_B_interval_lo"] <= m <= p["pred_B_interval_hi"])))
    aA = np.array([r["abs_err_A"] for r in rows]); aB = np.array([r["abs_err_B"] for r in rows])
    lines = open(PREREG, "rb").readlines()[:seal["sealed_prefix_lines"]]
    sha_prefix = hashlib.sha256(b"".join(lines)).hexdigest()
    doc = dict(network=network, phase="2b comparison",
               seal=dict(sha256_at_seal=seal["preregistration_sha256"],
                         sha256_of_prefix_now=sha_prefix,
                         unchanged=bool(sha_prefix == seal["preregistration_sha256"]),
                         sealed_prefix_lines=seal["sealed_prefix_lines"]),
               prior_networks=seal["prior_networks"], prior_fit=seal["prior_fit"],
               n_predictions=len(rows),
               A_mean_abs_err=float(aA.mean()), A_max_abs_err=float(aA.max()),
               B_mean_abs_err=float(aB.mean()), B_max_abs_err=float(aB.max()),
               B_hits=int(sum(r["hit_B"] for r in rows)),
               A_mean_rel_err=float(np.mean([abs(r["rel_err_A"]) for r in rows
                                             if r["rel_err_A"] is not None])),
               B_mean_rel_err=float(np.mean([abs(r["rel_err_B"]) for r in rows
                                             if r["rel_err_B"] is not None])),
               comparisons=rows)
    path = os.path.join(ROOT, network, "cross_2b_comparison.json")
    V1.write_json(path, doc, dict(seed=None, input_file=os.path.join(ROOT, network, "frozen.json"),
                                  input_sha256=V1.sha256_of(os.path.join(ROOT, network,
                                                                         "frozen.json")),
                                  run_settings=dict(phase="2b-compare", network=network)))
    print(f"[{network}] 2b compare: A mean|err| {doc['A_mean_abs_err']:.4f} "
          f"(rel {doc['A_mean_rel_err']:.2%}), B mean|err| {doc['B_mean_abs_err']:.4f} "
          f"(rel {doc['B_mean_rel_err']:.2%}), B hits {doc['B_hits']}/{doc['n_predictions']}",
          flush=True)
    return doc
