import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import manifest as mf
import classical_manifest as cm
import tune_surrogates as T

CASE30_PATH = "data/case30_dataset.parquet"
CASE118_PATH = "data/dataset.parquet"
SEEDS = 5
LIMIT = 0.94
STRIP_HI = 0.945
STRIP_W = 0.005
COVERAGE_LEVELS = [round(0.90 + 0.01 * i, 2) for i in range(9)]


def main():
    t0 = time.time()
    assert CASE30_PATH != CASE118_PATH
    ms_solver = mf.load_solve_time()["ms_solver"]

    df, feature_cols = ms.load_dataset(CASE30_PATH)
    assert (df["outaged_type"] != "none").all() and df["converged"].all()
    print(f"ASSERT: loaded ONLY {CASE30_PATH}; {CASE118_PATH} never opened this run. "
          f"rows={len(df)} scenarios={df.scenario_id.nunique()}", flush=True)

    X, y, groups, _b = ms.build_design_matrix(df, feature_cols)
    r_cands = T.ridge_candidates()
    h_cands = T.histgb_candidates()
    print(f"candidates: ridge={len(r_cands)} histgb={len(h_cands)}", flush=True)

    phase_a = {}
    split_info = {}

    for seed in range(SEEDS):
        splits = ms.make_splits(groups, seed)
        split_info[seed] = splits
        kept = ms.select_features(X, splits["train"])
        Xk = X[kept]
        tr, cal = splits["train"], splits["cal"]

        g_tr = groups[tr]
        inner = ms.make_splits(g_tr, T.INNER_SEED_OFFSET + seed)
        i_fit, i_cal, i_score = tr[inner["train"]], tr[inner["cal"]], tr[inner["test"]]
        Xfit = Xk.iloc[i_fit].to_numpy(np.float32); yfit = y[i_fit]
        Xic = Xk.iloc[i_cal].to_numpy(np.float32); yic = y[i_cal]
        Xis = Xk.iloc[i_score].to_numpy(np.float32); yis = y[i_score]

        Xtr = Xk.iloc[tr].to_numpy(np.float32); ytr = y[tr]
        Xca = Xk.iloc[cal].to_numpy(np.float32); yca = y[cal]

        for family, cands in (("ridge", r_cands), ("histgb", h_cands)):
            rows = T.search_one_family(family, cands, Xfit, yfit, Xic, yic, Xis, yis, seed, ms_solver)
            _m1_tag, m2_tag = T.select_best(rows)
            cfg = T.find_config(cands, m2_tag)

            fitted = T.fit_one(family, cfg, Xtr, ytr, seed)
            pred_cal = T.predict(fitted, Xca)
            q90 = ge.calibrate_qhat(pred_cal, yca, 0.90)

            boundary_mask = (yca >= LIMIT) & (yca < STRIP_HI)
            rho_cal = float(boundary_mask.mean()) / STRIP_W
            predicted_esc = rho_cal * q90

            phase_a[(family, seed)] = dict(
                tag=m2_tag, config=cfg, kept_cols=kept, fitted=fitted,
                pred_cal=pred_cal, yca=yca,
                q_hat_90=q90, rho_cal=rho_cal, predicted_esc=predicted_esc,
                n_cal=int(len(cal)), cal_boundary_rows=int(boundary_mask.sum()),
            )
            print(f"  [cal-only] seed={seed} {family:6s} M2={m2_tag:16s} q_hat90={q90:.6f} "
                  f"rho_cal={rho_cal:.4f} predicted_esc={predicted_esc:.6f} "
                  f"(n_cal={len(cal)}, boundary_rows={int(boundary_mask.sum())})", flush=True)

    pred_records = []
    for family in ("ridge", "histgb"):
        for seed in range(SEEDS):
            e = phase_a[(family, seed)]
            pred_records.append(dict(
                family=family, seed=seed, m2_tag=e["tag"],
                n_cal=e["n_cal"], cal_boundary_rows=e["cal_boundary_rows"],
                rho_cal=e["rho_cal"], q_hat_90=e["q_hat_90"], predicted_esc=e["predicted_esc"]))
    pred_out = dict(
        network="case30", limit=LIMIT, boundary_strip=[LIMIT, STRIP_HI], strip_width=STRIP_W,
        coverage_target_for_prediction=0.90,
        definition="rho_cal = (share of CALIBRATION rows with true min_vm in [0.94,0.945)) / 0.005; "
                   "predicted_esc = rho_cal * q_hat_90. Computed from calibration TRUE OUTCOMES "
                   "only (y_cal), never from predictions and never from test.",
        written_before_test_access=True,
        records=pred_records)
    pred_settings = dict(task="STAGE 3 case30 gate: prediction file (calibration-only)",
                         source=CASE30_PATH, stage="written before any test-split computation")
    cm.write_with_manifest("data/case30_prediction.json", pred_out, pred_settings)
    with open("data/case30_prediction.json", "rb") as f:
        import hashlib
        sha = hashlib.sha256(f.read()).hexdigest()
    print(f"\n*** WROTE data/case30_prediction.json  sha256={sha} ***", flush=True)
    print("*** PHASE A COMPLETE. No test-split row or label has been read. "
          "Proceeding to PHASE B (test). ***\n", flush=True)

    tradeoff_records = []
    frozen_per_seed_090 = {"ridge": [], "histgb": []}
    crossings = {}
    for family in ("ridge", "histgb"):
        for seed in range(SEEDS):
            splits = split_info[seed]
            e = phase_a[(family, seed)]
            kept = e["kept_cols"]
            Xte = X[kept].iloc[splits["test"]].to_numpy(np.float32)
            yte = y[splits["test"]]
            pred_te = T.predict(e["fitted"], Xte)
            n_test = int(len(yte))
            n_viol_test = int((yte < LIMIT).sum())

            for cov in COVERAGE_LEVELS:
                q_hat = ge.calibrate_qhat(e["pred_cal"], e["yca"], cov)
                gate = ge.run_gate(pred_te, q_hat, LIMIT)
                s = ge.score(gate, yte, 1e-6, ms_solver, LIMIT)
                n_missed = int((gate["certify"] & (yte < LIMIT)).sum())
                rec = dict(family=family, seed=seed, coverage_target=cov, q_hat=q_hat,
                          escalation=s["escalation"], coverage_emp=s["coverage"],
                          missed_viol=s["missed_viol"], net_speedup=s["net_speedup"],
                          n_test=n_test, n_true_viol=n_viol_test,
                          n_escalated=s["n_escalated"], n_missed=n_missed)
                tradeoff_records.append(rec)
                if abs(cov - 0.90) < 1e-9:
                    frozen_per_seed_090[family].append(rec)
            print(f"  [test] seed={seed} {family:6s} n_test={n_test} n_true_viol={n_viol_test} "
                  f"esc@0.90={frozen_per_seed_090[family][-1]['escalation']*100:.2f}% "
                  f"missed@0.90={frozen_per_seed_090[family][-1]['n_missed']}/{n_viol_test}", flush=True)

    tradeoff_out = dict(network="case30", seeds=SEEDS, limit=LIMIT, ms_solver=ms_solver,
                        coverage_levels=COVERAGE_LEVELS,
                        std_convention="population std (ddof=0) over the five held-out splits",
                        records=tradeoff_records)
    cm.write_with_manifest("data/case30_tradeoff_curve.json", tradeoff_out,
                           dict(task="STAGE 3 case30 gate: test-split coverage sweep",
                                source=CASE30_PATH))

    summary = {}
    for family in ("ridge", "histgb"):
        recs = frozen_per_seed_090[family]
        esc = np.array([r["escalation"] for r in recs])
        cov_emp = np.array([r["coverage_emp"] for r in recs])
        missed = np.array([r["missed_viol"] for r in recs])
        speedup = np.array([r["net_speedup"] for r in recs])
        n_missed_raw = [r["n_missed"] for r in recs]
        n_viol_raw = [r["n_true_viol"] for r in recs]
        predicted = np.array([phase_a[(family, s)]["predicted_esc"] for s in range(SEEDS)])
        pct_err = float((esc.mean() - predicted.mean()) / predicted.mean() * 100.0)
        summary[family] = dict(
            escalation_mean=float(esc.mean()), escalation_std=float(esc.std()),
            coverage_emp_mean=float(cov_emp.mean()), coverage_emp_std=float(cov_emp.std()),
            missed_viol_mean=float(missed.mean()), missed_viol_std=float(missed.std()),
            net_speedup_mean=float(speedup.mean()), net_speedup_std=float(speedup.std()),
            n_missed_per_seed=n_missed_raw, n_true_viol_per_seed=n_viol_raw,
            n_test_per_seed=[r["n_test"] for r in recs],
            predicted_esc_mean=float(predicted.mean()), predicted_esc_std=float(predicted.std()),
            predicted_vs_measured_pct_error=pct_err)
        print(f"\n{family}: measured esc@0.90={esc.mean()*100:.2f}%+-{esc.std()*100:.2f}  "
              f"predicted={predicted.mean()*100:.2f}%  pct_error={pct_err:+.1f}%", flush=True)

    for family in ("ridge", "histgb"):
        by_cov = {}
        for r in tradeoff_records:
            if r["family"] != family:
                continue
            by_cov.setdefault(r["coverage_target"], []).append(r)
        crossing = None
        for cov in COVERAGE_LEVELS:
            rs = by_cov[cov]
            mean_missed = np.mean([r["missed_viol"] for r in rs])
            if mean_missed < 0.01:
                crossing = dict(coverage_target=cov, missed_viol=float(mean_missed),
                                escalation=float(np.mean([r["escalation"] for r in rs])),
                                net_speedup=float(np.mean([r["net_speedup"] for r in rs])))
                break
        crossings[family] = crossing

    n1 = df
    violation_rate = float((n1.min_vm < LIMIT).mean())
    saturation_point = 100.0 * (1.0 - violation_rate)
    boundary_mass = float(((n1.min_vm >= LIMIT) & (n1.min_vm < STRIP_HI)).mean())

    frozen_out = dict(
        network="case30", source_dataset=CASE30_PATH,
        violation_rate_pct=round(100 * violation_rate, 4),
        saturation_point_pct=round(saturation_point, 4),
        boundary_mass_pct=round(100 * boundary_mass, 4),
        case118_comparators=dict(
            violation_rate_pct=17.48, saturation_point_pct=82.52, boundary_mass_pct=56.86,
            source="data/frozen_poster_numbers_v2.json"),
        four_metrics_at_90pct_coverage=summary,
        crossings_first_below_1pct_missed=crossings,
    )
    cm.write_with_manifest("data/case30_frozen.json", frozen_out,
                           dict(task="STAGE 3 case30 gate: headline summary", source=CASE30_PATH))

    print(f"\ntime_s={time.time()-t0:.1f}")


if __name__ == "__main__":
    main()
