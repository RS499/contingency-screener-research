import json
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

# STAGE 2H / H3b. The gate on the thermal-feasible case30 dataset.
#
# This mirrors scripts/case30_gate.py step for step. Every protocol constant is taken from
# that file unchanged: 5 seeds, limit 0.94, boundary strip [0.94, 0.945), coverage grid
# 0.90..0.98, the same ridge/histgb candidate sets, the same inner-split M2 selection, the
# same population std convention. The ONLY differences are the input dataset and the output
# paths. "Nothing about the method changes" is the whole point of the comparison, so the
# constants are asserted against case30_gate at import rather than retyped.

DATASET = "data/case30_thermal/dataset.parquet"
OUTDIR = "data/case30_thermal"
PUBLISHED = "data/case30_dataset.parquet"

SEEDS = 5
LIMIT = 0.94
STRIP_HI = 0.945
STRIP_W = 0.005
COVERAGE_LEVELS = [round(0.90 + 0.01 * i, 2) for i in range(9)]


def assert_protocol_matches_published():
    """Fail loudly if this script has drifted from the committed case30 protocol."""
    import case30_gate as P
    checks = {
        "SEEDS": (SEEDS, P.SEEDS),
        "LIMIT": (LIMIT, P.LIMIT),
        "STRIP_HI": (STRIP_HI, P.STRIP_HI),
        "STRIP_W": (STRIP_W, P.STRIP_W),
        "COVERAGE_LEVELS": (COVERAGE_LEVELS, P.COVERAGE_LEVELS),
    }
    bad = {k: v for k, v in checks.items() if v[0] != v[1]}
    if bad:
        raise ValueError(f"protocol drift vs scripts/case30_gate.py: {bad}")
    return {k: v[0] for k, v in checks.items()}


def main():
    t0 = time.time()
    protocol = assert_protocol_matches_published()
    print(f"protocol matches scripts/case30_gate.py: {protocol}", flush=True)

    ms_solver = mf.load_solve_time()["ms_solver"]
    df, feature_cols = ms.load_dataset(DATASET)
    assert (df["outaged_type"] != "none").all() and df["converged"].all()

    leaked = [c for c in feature_cols if "load" in c.lower() and c.startswith("max_")]
    if leaked:
        raise ValueError(f"post-outage loading leaked into features: {leaked}")
    print(f"loaded {DATASET}: rows={len(df)} scenarios={df.scenario_id.nunique()} "
          f"features={len(feature_cols)}", flush=True)

    X, y, groups, _b = ms.build_design_matrix(df, feature_cols)
    r_cands = T.ridge_candidates()
    h_cands = T.histgb_candidates()

    phase_a, split_info = {}, {}
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
            rows = T.search_one_family(family, cands, Xfit, yfit, Xic, yic, Xis, yis,
                                       seed, ms_solver)
            _m1_tag, m2_tag = T.select_best(rows)
            cfg = T.find_config(cands, m2_tag)
            fitted = T.fit_one(family, cfg, Xtr, ytr, seed)
            pred_cal = T.predict(fitted, Xca)
            q90 = ge.calibrate_qhat(pred_cal, yca, 0.90)
            boundary_mask = (yca >= LIMIT) & (yca < STRIP_HI)
            rho_cal = float(boundary_mask.mean()) / STRIP_W
            phase_a[(family, seed)] = dict(
                tag=m2_tag, config=cfg, kept_cols=kept, fitted=fitted,
                pred_cal=pred_cal, yca=yca, q_hat_90=q90, rho_cal=rho_cal,
                predicted_esc=rho_cal * q90, n_cal=int(len(cal)))
            print(f"  [cal] seed={seed} {family:6s} M2={m2_tag:16s} q90={q90:.6f} "
                  f"rho={rho_cal:.4f} pred_esc={rho_cal*q90:.6f}", flush=True)

    records, frozen090 = [], {"ridge": [], "histgb": []}
    for family in ("ridge", "histgb"):
        for seed in range(SEEDS):
            splits = split_info[seed]
            e = phase_a[(family, seed)]
            Xte = X[e["kept_cols"]].iloc[splits["test"]].to_numpy(np.float32)
            yte = y[splits["test"]]
            pred_te = T.predict(e["fitted"], Xte)
            n_test, n_viol = int(len(yte)), int((yte < LIMIT).sum())
            for cov in COVERAGE_LEVELS:
                q_hat = ge.calibrate_qhat(e["pred_cal"], e["yca"], cov)
                gate = ge.run_gate(pred_te, q_hat, LIMIT)
                s = ge.score(gate, yte, 1e-6, ms_solver, LIMIT)
                rec = dict(family=family, seed=seed, coverage_target=cov, q_hat=q_hat,
                           escalation=s["escalation"], coverage_emp=s["coverage"],
                           missed_viol=s["missed_viol"], net_speedup=s["net_speedup"],
                           n_test=n_test, n_true_viol=n_viol,
                           n_escalated=s["n_escalated"],
                           n_missed=int((gate["certify"] & (yte < LIMIT)).sum()))
                records.append(rec)
                if abs(cov - 0.90) < 1e-9:
                    frozen090[family].append(rec)
            print(f"  [test] seed={seed} {family:6s} n_test={n_test} n_viol={n_viol} "
                  f"esc@0.90={frozen090[family][-1]['escalation']*100:.2f}%", flush=True)

    summary = {}
    for family in ("ridge", "histgb"):
        recs = frozen090[family]
        esc = np.array([r["escalation"] for r in recs])
        cov_emp = np.array([r["coverage_emp"] for r in recs])
        missed = np.array([r["missed_viol"] for r in recs])
        speed = np.array([r["net_speedup"] for r in recs])
        summary[family] = dict(
            escalation_mean=float(esc.mean()), escalation_std=float(esc.std()),
            coverage_emp_mean=float(cov_emp.mean()), coverage_emp_std=float(cov_emp.std()),
            missed_viol_mean=float(missed.mean()), missed_viol_std=float(missed.std()),
            net_speedup_mean=float(speed.mean()), net_speedup_std=float(speed.std()),
            n_test_per_seed=[r["n_test"] for r in recs],
            n_true_viol_per_seed=[r["n_true_viol"] for r in recs])

    crossings = {}
    for family in ("ridge", "histgb"):
        by_cov = {}
        for r in records:
            if r["family"] == family:
                by_cov.setdefault(r["coverage_target"], []).append(r)
        crossing = None
        for cov in COVERAGE_LEVELS:
            mm = float(np.mean([r["missed_viol"] for r in by_cov[cov]]))
            if mm < 0.01:
                crossing = dict(coverage_target=cov, missed_viol=mm,
                                escalation=float(np.mean([r["escalation"] for r in by_cov[cov]])),
                                net_speedup=float(np.mean([r["net_speedup"] for r in by_cov[cov]])))
                break
        crossings[family] = crossing

    violation_rate = float((df.min_vm < LIMIT).mean())
    boundary_mass = float(((df.min_vm >= LIMIT) & (df.min_vm < STRIP_HI)).mean())

    out = dict(
        network="case30_thermal_feasible", source_dataset=DATASET,
        protocol_source="scripts/case30_gate.py (constants asserted equal at runtime)",
        seeds=SEEDS, limit=LIMIT, ms_solver=ms_solver, coverage_levels=COVERAGE_LEVELS,
        std_convention="population std (ddof=0) over the five held-out splits",
        violation_rate_pct=round(100 * violation_rate, 4),
        saturation_point_pct=round(100 * (1 - violation_rate), 4),
        boundary_mass_pct=round(100 * boundary_mass, 4),
        four_metrics_at_90pct_coverage=summary,
        crossings_first_below_1pct_missed=crossings,
        records=records)

    path = os.path.join(OUTDIR, "case30_thermal_frozen.json")
    cm.write_with_manifest(path, out,
                           dict(task="Stage 2H H3b: gate on the thermal-feasible case30",
                                source=DATASET, protocol="mirrors scripts/case30_gate.py"))
    print(f"\nwrote {path}")
    print(f"  violation rate {out['violation_rate_pct']}%  boundary mass {out['boundary_mass_pct']}%")
    for f in ("ridge", "histgb"):
        s = summary[f]
        c = crossings[f]
        print(f"  {f:6s} esc@0.90={s['escalation_mean']*100:.2f}+-{s['escalation_std']*100:.2f}%  "
              f"speedup={s['net_speedup_mean']:.2f}  missed={s['missed_viol_mean']*100:.3f}%  "
              f"crossing={c}")
    print(f"time_s={time.time()-t0:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
