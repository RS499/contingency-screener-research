"""netstudy v2: escalation prediction that CAN fail.

v1 was definitional: it computed the predictive CDF and the gate on the same rows, so the
two were one expression evaluated twice (scripts/netstudy.py:345 vs gate_eval.py:21).

v2 fixes the design:
  1b  the predictive CDF is measured on the CALIBRATION split ONLY. Test-split predictions
      are never computed in 1b.
  1c  the seal predicts TEST-split escalation from calibration-split CDF terms.
  1d  the gate scores the TEST split, refitting from the same seeds.
  1e  the error is sampling error between two DISJOINT row sets and can be non-zero.

Disjointness is asserted before sealing; a non-empty intersection voids the network.
"""

import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, HERE)
import generate_dataset as G
import make_splits as ms
import gate_eval as ge
import manifest as mf
import tune_surrogates as T
import netstudy as V1

PREREG = "notes/preregistration.md"
ROOT = "data/netstudy2"

SEEDS = V1.SEEDS
LIMIT = V1.LIMIT
STRIP_HI = V1.STRIP_HI
STRIP_W = V1.STRIP_W
COVERAGE_LEVELS = V1.COVERAGE_LEVELS
DAY_SECONDS = 24 * 3600


def outdir(network):
    d = os.path.join(ROOT, network)
    os.makedirs(d, exist_ok=True)
    return d


def idx_hash(a):
    a = np.ascontiguousarray(np.asarray(a).astype(np.int64))
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def dataset_path(network):
    """Reuse a v1 dataset when one exists: the build is unaffected by the v1 defect."""
    v1 = os.path.join("data/netstudy", network, "dataset.parquet")
    if os.path.exists(v1):
        return v1, "reused from netstudy v1 (build protocol identical; the v1 defect was in "
    return os.path.join(outdir(network), "dataset.parquet"), "built by netstudy2"


def ensure_dataset(network):
    p, _ = dataset_path(network)
    if os.path.exists(p):
        return p, os.path.join(os.path.dirname(p), "build_stats.json")
    r = V1.phase_1a(network)          # unchanged 1a: range sweep + build
    if r["status"] != "OK":
        return None, None
    return r["dataset"], r["stats"]


def splits_for(network):
    p, _ = dataset_path(network)
    df, feature_cols = ms.load_dataset(p)
    X, y, groups, _b = ms.build_design_matrix(df, feature_cols)
    return df, X, y, groups


def disjointness_report(groups):
    rows, ok = [], True
    for seed in range(SEEDS):
        sp = ms.make_splits(groups, seed)
        cal, te = np.asarray(sp["cal"]), np.asarray(sp["test"])
        inter = np.intersect1d(cal, te)
        rows.append(dict(seed=seed,
                         n_cal=int(len(cal)), n_test=int(len(te)),
                         cal_index_hash=idx_hash(cal), test_index_hash=idx_hash(te),
                         intersection_size=int(len(inter)),
                         disjoint=bool(len(inter) == 0)))
        ok = ok and len(inter) == 0
    return rows, ok


# ----------------------------------------------------------------- 1b + 1c


def phase_1bc(network):
    """Fit, calibrate, and measure the CDF on the CALIBRATION split. No test predictions."""
    t0 = time.time()
    d = outdir(network)
    V1.assert_protocol()
    ds, _ = dataset_path(network)
    df, X, y, groups = splits_for(network)

    dj, ok = disjointness_report(groups)
    if not ok:
        raise RuntimeError(f"{network}: cal/test intersection is non-empty. Network VOID.")
    print(f"[{network}] disjointness OK: "
          + ", ".join(f"s{r['seed']} cal={r['n_cal']} test={r['n_test']}" for r in dj),
          flush=True)

    ms_solver = mf.load_solve_time()["ms_solver"]
    r_cands, h_cands = T.ridge_candidates(), T.histgb_candidates()
    per_seed = []
    for seed in range(SEEDS):
        sp = ms.make_splits(groups, seed)
        kept = ms.select_features(X, sp["train"])
        Xk = X[kept]
        tr, cal = sp["train"], sp["cal"]
        g_tr = groups[tr]
        inner = ms.make_splits(g_tr, T.INNER_SEED_OFFSET + seed)
        i_fit, i_cal, i_score = tr[inner["train"]], tr[inner["cal"]], tr[inner["test"]]
        Xfit = Xk.iloc[i_fit].to_numpy(np.float32); yfit = y[i_fit]
        Xic = Xk.iloc[i_cal].to_numpy(np.float32); yic = y[i_cal]
        Xis = Xk.iloc[i_score].to_numpy(np.float32); yis = y[i_score]
        Xtr = Xk.iloc[tr].to_numpy(np.float32); ytr = y[tr]
        Xca = Xk.iloc[cal].to_numpy(np.float32); yca = y[cal]
        for family, cands in (("ridge", r_cands), ("histgb", h_cands)):
            rows = T.search_one_family(family, cands, Xfit, yfit, Xic, yic, Xis, yis,
                                       seed, ms_solver)
            _m1, m2 = T.select_best(rows)
            cfg = T.find_config(cands, m2)
            fitted = T.fit_one(family, cfg, Xtr, ytr, seed)
            pca = np.asarray(T.predict(fitted, Xca), dtype=np.float64)
            for cov in COVERAGE_LEVELS:
                q_hat = ge.calibrate_qhat(pca, yca, cov)
                F_L = float((pca < LIMIT).mean())
                F_Lq = float((pca < LIMIT + q_hat).mean())
                per_seed.append(dict(
                    family=family, seed=seed, coverage_target=cov, q_hat=q_hat,
                    split_used="cal",
                    F_at_L_cal=F_L, F_at_L_plus_qhat_cal=F_Lq,
                    identity_escalation_cal=F_Lq - F_L,
                    n_cal=int(len(pca)),
                    cal_index_hash=dj[seed]["cal_index_hash"],
                    cal_violation_rate=float((yca < LIMIT).mean())))
            print(f"  [cal-cdf] seed={seed} {family:6s} M2={m2}", flush=True)

    ps = pd.DataFrame(per_seed)
    pred = []
    for family in ("ridge", "histgb"):
        for cov in COVERAGE_LEVELS:
            g = ps[(ps.family == family) & (np.isclose(ps.coverage_target, cov))]
            ident = g["identity_escalation_cal"].to_numpy()
            p = float(ident.mean())
            n_cal_mean = float(g["n_cal"].mean())
            binom = float(np.sqrt(max(p * (1 - p), 0.0) / n_cal_mean))
            pred.append(dict(
                family=family, coverage_target=cov,
                predicted_escalation=p,
                predicted_std_seed=float(ident.std(ddof=0)),
                interval_lo=p - float(ident.std(ddof=0)),
                interval_hi=p + float(ident.std(ddof=0)),
                binomial_se_cal=binom,
                mean_q_hat=float(g["q_hat"].mean()),
                mean_F_at_L_cal=float(g["F_at_L_cal"].mean()),
                mean_F_at_L_plus_qhat_cal=float(g["F_at_L_plus_qhat_cal"].mean()),
                n_seeds=int(len(g))))

    doc = dict(
        network=network, phase="1b prediction inputs on the CALIBRATION split (gate NOT run)",
        design_note=("v2. The predictive CDF is measured on the CALIBRATION rows only. "
                     "Test-split predictions are NEVER computed in this phase, so the "
                     "predicted and measured quantities come from DISJOINT row sets and the "
                     "error is genuine sampling error that can be non-zero."),
        supersedes="data/netstudy/ (v1, definitional: same rows both sides)",
        identity="Esc_test_predicted = F_cal(L + q_hat) - F_cal(L)",
        interval_convention=("predicted +/- seed-to-seed population std (ddof=0). A binomial "
                             "standard error on the calibration share is reported separately "
                             "as binomial_se_cal and is NOT used for the hit test."),
        limit=LIMIT, seeds=SEEDS, coverage_levels=COVERAGE_LEVELS,
        source_dataset=ds,
        disjointness=dj, disjoint_all_seeds=ok,
        dataset_violation_rate=float((df.min_vm < LIMIT).mean()),
        dataset_boundary_mass=float(((df.min_vm >= LIMIT) & (df.min_vm < STRIP_HI)).mean()),
        predictions=pred, per_seed=per_seed)
    path = os.path.join(d, "prediction_inputs.json")
    V1.write_json(path, doc, dict(seed=None, input_file=ds, input_sha256=V1.sha256_of(ds),
                                  run_settings=dict(phase="1b-v2", network=network,
                                                    gate_run=False, cdf_split="cal")))
    print(f"[{network}] 1b done [{time.time()-t0:.0f}s]; sealing", flush=True)
    sha = seal(network, doc, pred, dj)
    return dict(status="OK", seal_sha256=sha, prediction_inputs=path)


def seal(network, doc, pred, dj):
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    head = V1.git_out(["rev-parse", "HEAD"])
    L = ["", "---", "",
         f"## SEALED PREDICTION v2 — escalation on {network} (cal-split CDF -> test-split gate)",
         "", f"**Sealed:** {stamp}   **git HEAD:** `{head}`",
         f"**Design:** {doc['design_note']}",
         f"**Identity:** `{doc['identity']}`",
         f"**Interval:** {doc['interval_convention']}", "",
         "**Disjointness, asserted before sealing:**", "",
         "| seed | n_cal | n_test | cal hash | test hash | intersection | disjoint |",
         "|---|---|---|---|---|---|---|"]
    for r in dj:
        L.append(f"| {r['seed']} | {r['n_cal']} | {r['n_test']} | `{r['cal_index_hash']}` | "
                 f"`{r['test_index_hash']}` | {r['intersection_size']} | {r['disjoint']} |")
    L += ["", f"**Dataset inputs.** violation rate `{doc['dataset_violation_rate']!r}`; "
              f"boundary mass `{doc['dataset_boundary_mass']!r}`.", "",
          "| family | target | predicted esc (from cal) | seed std | lo | hi | binom SE | "
          "mean q_hat | mean F_cal(L) | mean F_cal(L+q) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for p in pred:
        L.append(f"| {p['family']} | {p['coverage_target']} | {p['predicted_escalation']!r} | "
                 f"{p['predicted_std_seed']!r} | {p['interval_lo']!r} | {p['interval_hi']!r} | "
                 f"{p['binomial_se_cal']!r} | {p['mean_q_hat']!r} | "
                 f"{p['mean_F_at_L_cal']!r} | {p['mean_F_at_L_plus_qhat_cal']!r} |")
    L += ["", "**Confidence label:** this prediction CAN fail. Predicted and measured come "
              "from disjoint row sets; a machine-epsilon result would indicate the v1 defect "
              "has recurred and must be reported as a defect, not as agreement.", "",
          f"gate not yet run on {network} as of {stamp}", ""]
    with open(PREREG, "a", encoding="utf-8") as f:
        f.write("\n".join(L))
    sha = V1.sha256_of(PREREG)
    n_lines = sum(1 for _ in open(PREREG, "rb"))
    sp = os.path.join(outdir(network), "seal_1c.json")
    with open(sp, "w") as f:
        json.dump(dict(network=network, sealed_utc=stamp, git_head=head,
                       preregistration_file=PREREG,
                       preregistration_sha256_at_1c=sha,
                       sealed_prefix_lines=n_lines,
                       seal_recovery_recipe=("head -n <sealed_prefix_lines> "
                                             f"{PREREG} | shasum -a 256"),
                       gate_run_before_seal=False), f, indent=1)
    V1.write_manifest(sp, dict(seed=None, input_file=PREREG, input_sha256=sha,
                               run_settings=dict(phase="1c-v2", network=network)))
    print(f"[{network}] SEAL sha256({PREREG}) = {sha}  (prefix {n_lines} lines)", flush=True)
    return sha


# ----------------------------------------------------------------- 1d


def phase_1d(network):
    """Gate on the TEST split. Refits from the same seeds; 1b never saw these rows."""
    t0 = time.time()
    d = outdir(network)
    protocol = V1.assert_protocol()
    if not os.path.exists(os.path.join(d, "seal_1c.json")):
        raise RuntimeError(f"{network}: no v2 seal on disk. The gate must not run first.")
    ds, _ = dataset_path(network)
    df, X, y, groups = splits_for(network)
    ms_solver = mf.load_solve_time()["ms_solver"]
    r_cands, h_cands = T.ridge_candidates(), T.histgb_candidates()

    records, frozen090 = [], {"ridge": [], "histgb": []}
    for seed in range(SEEDS):
        sp = ms.make_splits(groups, seed)
        kept = ms.select_features(X, sp["train"])
        Xk = X[kept]
        tr, cal = sp["train"], sp["cal"]
        g_tr = groups[tr]
        inner = ms.make_splits(g_tr, T.INNER_SEED_OFFSET + seed)
        i_fit, i_cal, i_score = tr[inner["train"]], tr[inner["cal"]], tr[inner["test"]]
        Xfit = Xk.iloc[i_fit].to_numpy(np.float32); yfit = y[i_fit]
        Xic = Xk.iloc[i_cal].to_numpy(np.float32); yic = y[i_cal]
        Xis = Xk.iloc[i_score].to_numpy(np.float32); yis = y[i_score]
        Xtr = Xk.iloc[tr].to_numpy(np.float32); ytr = y[tr]
        Xca = Xk.iloc[cal].to_numpy(np.float32); yca = y[cal]
        Xte = Xk.iloc[sp["test"]].to_numpy(np.float32); yte = y[sp["test"]]
        for family, cands in (("ridge", r_cands), ("histgb", h_cands)):
            rows = T.search_one_family(family, cands, Xfit, yfit, Xic, yic, Xis, yis,
                                       seed, ms_solver)
            _m1, m2 = T.select_best(rows)
            cfg = T.find_config(cands, m2)
            fitted = T.fit_one(family, cfg, Xtr, ytr, seed)
            pca = T.predict(fitted, Xca)
            pte = T.predict(fitted, Xte)
            n_test, n_viol = int(len(yte)), int((yte < LIMIT).sum())
            for cov in COVERAGE_LEVELS:
                q_hat = ge.calibrate_qhat(pca, yca, cov)
                gate = ge.run_gate(pte, q_hat, LIMIT)
                s = ge.score(gate, yte, 1e-6, ms_solver, LIMIT)
                rec = dict(family=family, seed=seed, coverage_target=cov, q_hat=q_hat,
                           escalation=s["escalation"], coverage_emp=s["coverage"],
                           missed_viol=s["missed_viol"], net_speedup=s["net_speedup"],
                           n_test=n_test, n_true_viol=n_viol, n_escalated=s["n_escalated"],
                           n_missed=int((gate["certify"] & (yte < LIMIT)).sum()),
                           test_index_hash=idx_hash(np.asarray(sp["test"])))
                records.append(rec)
                if abs(cov - 0.90) < 1e-9:
                    frozen090[family].append(rec)
            print(f"  [test-gate] seed={seed} {family:6s} esc@0.90="
                  f"{frozen090[family][-1]['escalation']*100:.2f}%", flush=True)

    summary = {}
    for family in ("ridge", "histgb"):
        recs = frozen090[family]
        esc = np.array([r["escalation"] for r in recs])
        missed = np.array([r["missed_viol"] for r in recs])
        speed = np.array([r["net_speedup"] for r in recs])
        cov_emp = np.array([r["coverage_emp"] for r in recs])
        summary[family] = dict(
            escalation_mean=float(esc.mean()), escalation_std=float(esc.std()),
            coverage_emp_mean=float(cov_emp.mean()), coverage_emp_std=float(cov_emp.std()),
            missed_viol_mean=float(missed.mean()), missed_viol_std=float(missed.std()),
            net_speedup_mean=float(speed.mean()), net_speedup_std=float(speed.std()))

    crossings = {}
    for family in ("ridge", "histgb"):
        by = {}
        for r in records:
            if r["family"] == family:
                by.setdefault(r["coverage_target"], []).append(r)
        cr = None
        for cov in COVERAGE_LEVELS:
            mm = float(np.mean([r["missed_viol"] for r in by[cov]]))
            if mm < 0.01:
                cr = dict(coverage_target=cov, missed_viol=mm,
                          escalation=float(np.mean([r["escalation"] for r in by[cov]])),
                          net_speedup=float(np.mean([r["net_speedup"] for r in by[cov]])))
                break
        crossings[family] = cr

    violation_rate = float((df.min_vm < LIMIT).mean())
    boundary_mass = float(((df.min_vm >= LIMIT) & (df.min_vm < STRIP_HI)).mean())
    out = dict(network=network, source_dataset=ds, protocol=protocol,
               protocol_source="scripts/case30_gate.py (constants asserted equal at runtime)",
               seeds=SEEDS, limit=LIMIT, ms_solver=ms_solver,
               ms_solver_provenance="imported from data/solve_time.json (case118); NOT re-timed",
               coverage_levels=COVERAGE_LEVELS,
               std_convention="population std (ddof=0) over the five held-out splits",
               violation_rate_pct=round(100 * violation_rate, 4),
               boundary_mass_pct=round(100 * boundary_mass, 4),
               four_metrics_at_90pct_coverage=summary,
               crossings_first_below_1pct_missed=crossings, records=records)
    path = os.path.join(d, "frozen.json")
    V1.write_json(path, out, dict(seed=None, input_file=ds, input_sha256=V1.sha256_of(ds),
                                  run_settings=dict(phase="1d-v2", network=network)))
    print(f"[{network}] 1d done [{time.time()-t0:.0f}s]", flush=True)
    return dict(status="OK", frozen=path)


# ----------------------------------------------------------------- 1e


def phase_1e(network):
    d = outdir(network)
    seal_doc = json.load(open(os.path.join(d, "seal_1c.json")))
    import subprocess
    lines = open(PREREG, "rb").readlines()[:seal_doc["sealed_prefix_lines"]]
    sha_prefix = hashlib.sha256(b"".join(lines)).hexdigest()
    intact = bool(sha_prefix == seal_doc["preregistration_sha256_at_1c"])

    pi = json.load(open(os.path.join(d, "prediction_inputs.json")))
    fr = json.load(open(os.path.join(d, "frozen.json")))
    meas = {}
    for r in fr["records"]:
        meas.setdefault((r["family"], r["coverage_target"]), []).append(r["escalation"])

    comp = []
    for p in pi["predictions"]:
        vals = np.array(meas[(p["family"], p["coverage_target"])], dtype=np.float64)
        m = float(vals.mean())
        err = m - p["predicted_escalation"]
        std = p["predicted_std_seed"]
        comp.append(dict(
            family=p["family"], coverage_target=p["coverage_target"],
            predicted=p["predicted_escalation"], predicted_std_seed=std,
            binomial_se_cal=p["binomial_se_cal"],
            interval_lo=p["interval_lo"], interval_hi=p["interval_hi"],
            measured=m, measured_std=float(vals.std(ddof=0)),
            abs_error=abs(err), signed_error=err,
            relative_error=(None if m == 0 else float(err / m)),
            error_in_std_units=(None if std == 0 else float(err / std)),
            hit=bool(p["interval_lo"] - 1e-15 <= m <= p["interval_hi"] + 1e-15),
            bitwise_identical=bool(m == p["predicted_escalation"])))

    errs = np.array([c["abs_error"] for c in comp])
    n_bitwise = int(sum(c["bitwise_identical"] for c in comp))
    epsilon_alarm = bool(errs.max() < 1e-12)
    doc = dict(network=network, phase="1e comparison (v2, disjoint row sets)",
               seal=dict(preregistration_file=PREREG,
                         sealed_prefix_lines=seal_doc["sealed_prefix_lines"],
                         sha256_at_1c=seal_doc["preregistration_sha256_at_1c"],
                         sha256_of_prefix_at_1e=sha_prefix, unchanged=intact,
                         verdict=("SEAL INTACT" if intact else
                                  "SEAL BROKEN - THIS NETWORK'S RESULT IS VOID")),
               disjointness=pi["disjointness"], disjoint_all_seeds=pi["disjoint_all_seeds"],
               n_predictions=len(comp), n_hits=int(sum(c["hit"] for c in comp)),
               n_bitwise_identical=n_bitwise,
               mean_abs_error=float(errs.mean()), max_abs_error=float(errs.max()),
               median_abs_error=float(np.median(errs)),
               mean_relative_error=float(np.mean([abs(c["relative_error"]) for c in comp
                                                  if c["relative_error"] is not None])),
               epsilon_alarm=epsilon_alarm,
               epsilon_alarm_note=("DEFECT: max abs error is below 1e-12, which for DISJOINT "
                                   "row sets is not possible as sampling error. The v1 "
                                   "same-rows defect has recurred and this result must be "
                                   "reported as a defect, not as agreement."
                                   if epsilon_alarm else
                                   "errors are at a scale consistent with sampling error "
                                   "between disjoint row sets"),
               comparisons=comp)
    path = os.path.join(d, "comparison.json")
    V1.write_json(path, doc, dict(seed=None, input_file=os.path.join(d, "frozen.json"),
                                  input_sha256=V1.sha256_of(os.path.join(d, "frozen.json")),
                                  run_settings=dict(phase="1e-v2", network=network)))
    print(f"[{network}] seal {doc['seal']['verdict']}; hits {doc['n_hits']}/{doc['n_predictions']}"
          f"  mean|err| {doc['mean_abs_error']:.3e}  max|err| {doc['max_abs_error']:.3e}"
          f"  bitwise-identical {n_bitwise}  ALARM={epsilon_alarm}", flush=True)
    return doc


if __name__ == "__main__":
    net = sys.argv[sys.argv.index("--network") + 1]
    ph = sys.argv[sys.argv.index("--phase") + 1]
    print(json.dumps({"1bc": phase_1bc, "1d": phase_1d, "1e": phase_1e}[ph](net), default=str))
