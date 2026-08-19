import os
import sys
import json
import time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import manifest as mf
import classical_manifest as cm
import tune_surrogates as T

TUNED = "data/tuned_metrics.json"
CURVE_V2 = "data/tradeoff_curve_v2.json"
SOLVE = "data/solve_time.json"
OUT = "data/sweep_results_long.parquet"
DATASET = "data/dataset.parquet"

L_LO, L_HI, L_STEP = 0.900, 0.955, 0.001
H_BW = 0.002
FAMILIES = ("ridge", "histgb")


def m2_config(tuned, family, seed):
    for r in tuned["records"]:
        if r["family"] == family and r["metric"] == "m2" and r["seed"] == seed:
            return r["config"]
    raise ValueError(f"no M2 config for {family} seed {seed}")


def ms_surrogate(tuned, family, seed):
    for r in tuned["records"]:
        if r["family"] == family and r["metric"] == "m2" and r["seed"] == seed:
            return float(r["ms_surrogate"])
    raise ValueError(f"no ms_surrogate for {family} seed {seed}")


def ecdf(sorted_values, x):
    return float(np.searchsorted(sorted_values, x, side="left")) / len(sorted_values)


def density(sorted_values, x, h):
    lo = np.searchsorted(sorted_values, x - h, side="left")
    hi = np.searchsorted(sorted_values, x + h, side="left")
    return float(hi - lo) / (len(sorted_values) * 2.0 * h)


def main():
    t0 = time.time()
    with open(TUNED) as f:
        tuned = json.load(f)
    with open(CURVE_V2) as f:
        curve = json.load(f)
    with open(SOLVE) as f:
        solve = json.load(f)
    targets = list(curve["coverage_levels"])
    ms_solver = float(solve["ms_solver"])
    n_seeds = int(tuned["seeds"])

    grid = np.round(np.arange(L_LO, L_HI + 1e-9, L_STEP), 3)
    print(f"grid: {len(grid)} limits, {len(targets)} targets, {len(FAMILIES)} models, "
          f"{n_seeds} seeds -> {len(grid)*len(targets)*len(FAMILIES)*n_seeds} rows", flush=True)

    df, feature_cols = ms.load_dataset(DATASET)
    X, y, groups, _b = ms.build_design_matrix(df, feature_cols)

    rows = []
    for seed in range(n_seeds):
        splits = ms.make_splits(groups, seed)
        kept = ms.select_features(X, splits["train"])
        Xk = X[kept]
        Xtr = Xk.iloc[splits["train"]].to_numpy(np.float32)
        Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
        Xte = Xk.iloc[splits["test"]].to_numpy(np.float32)
        ytr, yca, yte = y[splits["train"]], y[splits["cal"]], y[splits["test"]]

        for fam in FAMILIES:
            ts = time.time()
            cfg = m2_config(tuned, fam, seed)
            fitted = T.fit_one(fam, cfg, Xtr, ytr, seed)
            p_ca = np.asarray(T.predict(fitted, Xca), dtype=np.float64)
            p_te = np.asarray(T.predict(fitted, Xte), dtype=np.float64)
            msur = ms_surrogate(tuned, fam, seed)
            print(f"  seed={seed} {fam:6s} fit+predict {time.time()-ts:.1f}s", flush=True)

            p_ca_s = np.sort(p_ca)
            p_te_s = np.sort(p_te)
            y_te_s = np.sort(yte)
            n_te = len(yte)

            qs = {}
            for tgt in targets:
                qs[tgt] = ge.calibrate_qhat(p_ca, yca, tgt)

            for L in grid:
                viol = yte < L
                n_viol = int(viol.sum())
                violation_rate = float(viol.mean())
                rho_y = density(y_te_s, L, H_BW)
                rho_p = density(p_te_s, L, H_BW)
                for tgt in targets:
                    q = qs[tgt]
                    certify = (p_te - q) >= L
                    flag = p_te < L
                    escalate = ~(certify | flag)
                    n_esc = int(escalate.sum())
                    esc_observed = float(escalate.mean())
                    missed = certify & viol
                    missed_rate = float(missed.sum() / max(n_viol, 1))
                    boundary_mass = float(((yte >= L) & (yte < L + q)).mean())
                    speedup = float(n_te * ms_solver / (n_te * msur + n_esc * ms_solver))
                    rows.append(dict(
                        L=float(L), model=fam, target=float(tgt), seed=int(seed),
                        q_hat=float(q),
                        boundary_mass=boundary_mass,
                        violation_rate=violation_rate,
                        esc_observed=esc_observed,
                        esc_pred_cdf=ecdf(p_ca_s, L + q) - ecdf(p_ca_s, L),
                        esc_pred_cdf_test=ecdf(p_te_s, L + q) - ecdf(p_te_s, L),
                        esc_pred_rho_outcome=rho_y * q,
                        esc_pred_rho_local=rho_p * q,
                        missed_rate=missed_rate,
                        speedup=speedup,
                        n_test=n_te, n_escalated=n_esc, n_true_viol=n_viol,
                    ))
            print(f"  seed={seed} {fam:6s} rows so far {len(rows)}", flush=True)

    out = pd.DataFrame(rows)
    out.to_parquet(OUT, index=False)
    print(f"wrote {OUT} rows={len(out)} cols={out.shape[1]} in {time.time()-t0:.1f}s", flush=True)

    meta = dict(
        artifact="long-format limit sweep over the promoted M2 surrogates",
        limits=dict(lo=L_LO, hi=L_HI, step=L_STEP, n=int(len(grid))),
        coverage_targets_source=CURVE_V2, n_targets=len(targets),
        families=list(FAMILIES), seeds=n_seeds,
        n_rows=int(len(out)),
        ms_solver=ms_solver, ms_solver_source=SOLVE,
        density_bandwidth_pu=H_BW,
        density_estimator="symmetric empirical-CDF finite difference (F(x+h)-F(x-h))/(2h)",
        q_hat_note=("q_hat is calibrated from the calibration-split residuals and is "
                    "INDEPENDENT of L (gate_eval.calibrate_qhat takes no limit argument). "
                    "It varies only with (model, target, seed): 300 distinct values across "
                    "16800 rows. Recalibrating inside the L loop returns the same number."),
        esc_pred_cdf_note=("the request wrote F_phat(q_hat) - F_phat(L); implemented as "
                           "F_phat(L+q_hat) - F_phat(L), which is the escalation strip the "
                           "gate actually applies (escalate <=> L <= pred < L+q_hat). "
                           "esc_pred_cdf uses the CALIBRATION predictions (out-of-sample, a "
                           "genuine prediction); esc_pred_cdf_test uses the TEST predictions "
                           "and is an algebraic identity with esc_observed, retained as a check."),
        model_hyperparameters={fam: {str(s): m2_config(tuned, fam, s) for s in range(n_seeds)}
                               for fam in FAMILIES},
    )
    settings = dict(task="limit sweep L=0.900..0.955 over M2 refits", source=DATASET,
                    tuned_source=TUNED)
    man = cm.build_manifest(OUT, meta, settings)
    with open(mf.manifest_path(OUT), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {mf.manifest_path(OUT)} (sha256 {man['content_sha256'][:12]}...)", flush=True)


if __name__ == "__main__":
    main()
