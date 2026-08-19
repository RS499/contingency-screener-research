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

DATASET = "data/dataset.parquet"
TUNED = "data/tuned_metrics.json"
CURVE_V2 = "data/tradeoff_curve_v2.json"
OUT = "data/flag_confusion_long.parquet"
LIMIT = 0.94
OPS = {"ridge": 0.94, "histgb": 0.97}
NEAR = [0.001, 0.005, 0.010, 0.020]


def m2_config(tuned, fam, seed):
    for r in tuned["records"]:
        if r["family"] == fam and r["metric"] == "m2" and r["seed"] == seed:
            return r["config"]
    raise ValueError("missing config")


def main():
    t0 = time.time()
    tuned = json.load(open(TUNED))
    targets = list(json.load(open(CURVE_V2))["coverage_levels"])
    n_seeds = int(tuned["seeds"])

    df, feat = ms.load_dataset(DATASET)
    X, y, groups, _b = ms.build_design_matrix(df, feat)

    rows = []
    for seed in range(n_seeds):
        splits = ms.make_splits(groups, seed)
        kept = ms.select_features(X, splits["train"])
        Xk = X[kept]
        Xtr = Xk.iloc[splits["train"]].to_numpy(np.float32)
        Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
        Xte = Xk.iloc[splits["test"]].to_numpy(np.float32)
        ytr, yca, yte = y[splits["train"]], y[splits["cal"]], y[splits["test"]]
        viol = yte < LIMIT
        safe = ~viol

        for fam in ("ridge", "histgb"):
            fitted = T.fit_one(fam, m2_config(tuned, fam, seed), Xtr, ytr, seed)
            p_ca = T.predict(fitted, Xca)
            p_te = np.asarray(T.predict(fitted, Xte), dtype=np.float64)
            for tgt in targets:
                q = ge.calibrate_qhat(p_ca, yca, tgt)
                g = ge.run_gate(p_te, q, LIMIT)
                cert, flag, esc = g["certify"], g["flag"], g["escalate"]

                cert_safe = int((cert & safe).sum())
                cert_viol = int((cert & viol).sum())     # missed violations
                flag_viol = int((flag & viol).sum())     # correct flags
                flag_safe = int((flag & safe).sum())     # FALSE FLAGS
                esc_safe = int((esc & safe).sum())
                esc_viol = int((esc & viol).sum())
                n = int(len(yte))

                n_flag = flag_viol + flag_safe
                prec = flag_viol / n_flag if n_flag else float("nan")
                rec = flag_viol / int(viol.sum()) if int(viol.sum()) else float("nan")
                if np.isnan(prec) or np.isnan(rec) or (4 * prec + rec) == 0:
                    f2 = float("nan")
                else:
                    f2 = 5 * prec * rec / (4 * prec + rec)

                ff_y = yte[flag & safe]
                margin = ff_y - LIMIT if len(ff_y) else np.array([])
                rec_row = dict(
                    model=fam, target=float(tgt), seed=int(seed), q_hat=float(q),
                    n_test=n, n_viol=int(viol.sum()), n_safe=int(safe.sum()),
                    cert_safe=cert_safe, cert_viol=cert_viol,
                    flag_viol=flag_viol, flag_safe=flag_safe,
                    esc_safe=esc_safe, esc_viol=esc_viol,
                    certified_frac=float((cert_safe + cert_viol) / n),
                    flagged_frac=float(n_flag / n),
                    escalated_frac=float((esc_safe + esc_viol) / n),
                    flag_precision=float(prec), flag_recall=float(rec), flag_f2=float(f2),
                    false_flag_rate_of_all=float(flag_safe / n),
                    false_flag_rate_of_safe=float(flag_safe / int(safe.sum())),
                    missed_viol_rate=float(cert_viol / max(int(viol.sum()), 1)),
                )
                if len(margin):
                    rec_row.update(
                        ff_margin_mean=float(margin.mean()),
                        ff_margin_p50=float(np.percentile(margin, 50)),
                        ff_margin_p90=float(np.percentile(margin, 90)),
                        ff_margin_max=float(margin.max()),
                        ff_minvm_mean=float(ff_y.mean()),
                        ff_minvm_max=float(ff_y.max()),
                    )
                    for nz in NEAR:
                        rec_row[f"ff_share_within_{str(nz).replace('.','p')}"] = \
                            float((margin < nz).mean())
                else:
                    rec_row.update(ff_margin_mean=np.nan, ff_margin_p50=np.nan,
                                   ff_margin_p90=np.nan, ff_margin_max=np.nan,
                                   ff_minvm_mean=np.nan, ff_minvm_max=np.nan)
                    for nz in NEAR:
                        rec_row[f"ff_share_within_{str(nz).replace('.','p')}"] = np.nan
                rows.append(rec_row)
        print(f"  seed {seed} done {time.time()-t0:.0f}s", flush=True)

    out = pd.DataFrame(rows)
    out.to_parquet(OUT, index=False)
    print(f"wrote {OUT} rows={len(out)} cols={out.shape[1]} in {time.time()-t0:.0f}s")

    meta = dict(
        artifact="three-way gate confusion matrix and FLAG-decision metrics across the coverage sweep",
        limit=LIMIT, operating_points=OPS, n_targets=len(targets), seeds=n_seeds,
        columns_note=("cert_viol are the missed violations the paper reports; flag_safe are the "
                      "FALSE FLAGS, which the paper does not report. flag decision metrics treat "
                      "'violating' as the positive class."),
        f2_note="F2 = 5*P*R/(4P+R), weighting recall over precision.",
        false_flag_margin_note=("ff_margin_* are true min_vm minus the 0.94 limit for falsely "
                                "flagged cases; ff_share_within_X is the share of false flags whose "
                                "true outcome sat within X pu above the limit."),
        cost_note=("a FLAG skips the solver, so a false flag is never corrected downstream; its "
                   "cost is unnecessary redispatch, not solver time."),
        model_hyperparameters={f: {str(s): m2_config(tuned, f, s) for s in range(n_seeds)}
                               for f in ("ridge", "histgb")},
    )
    man = cm.build_manifest(OUT, meta, dict(task="flag confusion sweep", source=DATASET))
    json.dump(man, open(mf.manifest_path(OUT), "w"), indent=2)
    print(f"wrote {mf.manifest_path(OUT)}")


if __name__ == "__main__":
    main()
