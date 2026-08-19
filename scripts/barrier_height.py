import json
import os
import sys
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

# BARRIER-HEIGHT RESOLUTION.
#
# Certify means pred - q_hat >= L, so pred >= L + q_hat. A miss is certify AND Y < L.
# With depth d = L - Y > 0 and overshoot o = pred - Y:
#
#     o = pred - Y >= (L + q_hat) - Y = q_hat + d
#
# So every miss REQUIRES o >= q_hat + d. That is algebra, not an empirical claim, and the
# measured share must be exactly 1.0. Likewise coverage = P(Y >= pred - q_hat) = P(o <= q_hat),
# so P(o > q_hat) must equal 1 - coverage exactly. Both are used here as two-key checks on the
# computation rather than as findings.
#
# The open question is why ridge misses LESS than histgb on case118 and MORE on case30-thermal
# while having the taller barrier on both. This script measures the overshoot distribution
# conditional on violations, relative to each model's own q_hat.

CASE118 = "data/dataset.parquet"
CASE30T = "data/case30_thermal/dataset.parquet"
TUNED = "data/tuned_metrics.json"
OUT = "data/barrier_height.json"
LIMIT = 0.94
SEEDS = 5


def m2_config(tuned, fam, seed):
    for r in tuned["records"]:
        if r["family"] == fam and r["metric"] == "m2" and r["seed"] == seed:
            return r["config"]
    raise ValueError("missing config")


def fit_predict(path, tuned_path, targets, use_stored_cfg):
    """Return per-seed (pred_cal, y_cal, pred_test, y_test) for both families."""
    df, feat = ms.load_dataset(path)
    X, y, groups, _b = ms.build_design_matrix(df, feat)
    tuned = json.load(open(tuned_path)) if use_stored_cfg else None
    r_c, h_c = T.ridge_candidates(), T.histgb_candidates()
    ms_solver = mf.load_solve_time()["ms_solver"]

    out = {}
    for seed in range(SEEDS):
        splits = ms.make_splits(groups, seed)
        kept = ms.select_features(X, splits["train"])
        Xk = X[kept]
        tr, ca, te = splits["train"], splits["cal"], splits["test"]
        Xtr = Xk.iloc[tr].to_numpy(np.float32)

        for fam, cands in (("ridge", r_c), ("histgb", h_c)):
            if use_stored_cfg:
                cfg = m2_config(tuned, fam, seed)
            else:
                g_tr = groups[tr]
                inner = ms.make_splits(g_tr, T.INNER_SEED_OFFSET + seed)
                i_f, i_c, i_s = tr[inner["train"]], tr[inner["cal"]], tr[inner["test"]]
                rows = T.search_one_family(
                    fam, cands,
                    Xk.iloc[i_f].to_numpy(np.float32), y[i_f],
                    Xk.iloc[i_c].to_numpy(np.float32), y[i_c],
                    Xk.iloc[i_s].to_numpy(np.float32), y[i_s], seed, ms_solver)
                _m1, m2 = T.select_best(rows)
                cfg = T.find_config(cands, m2)
            fitted = T.fit_one(fam, cfg, Xtr, y[tr], seed)
            out[(fam, seed)] = dict(
                pred_cal=np.asarray(T.predict(fitted, Xk.iloc[ca].to_numpy(np.float32)), float),
                y_cal=y[ca],
                pred_te=np.asarray(T.predict(fitted, Xk.iloc[te].to_numpy(np.float32)), float),
                y_te=y[te], cfg=cfg)
        print(f"    seed {seed} fitted", flush=True)
    return out


def analyse(store, targets, network):
    recs = []
    for fam in ("ridge", "histgb"):
        for seed in range(SEEDS):
            e = store[(fam, seed)]
            o = e["pred_te"] - e["y_te"]          # overshoot, signed
            viol = e["y_te"] < LIMIT
            d = LIMIT - e["y_te"]                  # depth, positive on violations
            for cov in targets:
                q = ge.calibrate_qhat(e["pred_cal"], e["y_cal"], cov)
                gate = ge.run_gate(e["pred_te"], q, LIMIT)
                missed = gate["certify"] & viol
                nm = int(missed.sum())

                # P-BH-1: algebraic identity, must be exactly 1.0 when any miss exists
                share_miss_over_q = float((o[missed] > q).mean()) if nm else None
                share_miss_over_qd = float((o[missed] >= q + d[missed] - 1e-12).mean()) if nm else None
                # P-BH-2: identity against coverage
                p_o_gt_q = float((o > q).mean())
                cov_emp = float((e["y_te"] >= e["pred_te"] - q).mean())

                ov = o[viol]
                recs.append(dict(
                    network=network, model=fam, seed=seed, coverage_target=cov,
                    q_hat=float(q),
                    n_test=int(len(o)), n_viol=int(viol.sum()), n_missed=nm,
                    missed_viol=float(nm / max(int(viol.sum()), 1)),
                    coverage_emp=cov_emp,
                    p_overshoot_gt_qhat=p_o_gt_q,
                    identity_gap=abs(p_o_gt_q - (1.0 - cov_emp)),
                    share_missed_overshoot_gt_qhat=share_miss_over_q,
                    share_missed_overshoot_ge_qhat_plus_depth=share_miss_over_qd,
                    # conditional-on-violation overshoot, relative to the model's own barrier
                    mean_overshoot_given_viol=float(ov.mean()),
                    p90_overshoot_given_viol=float(np.percentile(ov, 90)),
                    p99_overshoot_given_viol=float(np.percentile(ov, 99)),
                    max_overshoot_given_viol=float(ov.max()),
                    S_mean_over_qhat=float(ov.mean() / q),
                    S_p99_over_qhat=float(np.percentile(ov, 99) / q),
                    p_overshoot_gt_qhat_given_viol=float((ov > q).mean()),
                ))
    return recs


def main():
    t0 = time.time()
    targets = [round(0.90 + 0.01 * i, 2) for i in range(9)]

    print("case118 (stored M2 configs)", flush=True)
    s118 = fit_predict(CASE118, TUNED, targets, use_stored_cfg=True)
    r118 = analyse(s118, targets, "case118")

    print("case30_thermal (M2 search, no stored configs for this dataset)", flush=True)
    s30 = fit_predict(CASE30T, TUNED, targets, use_stored_cfg=False)
    r30 = analyse(s30, targets, "case30_thermal")

    df = pd.DataFrame(r118 + r30)
    path = "data/barrier_height_long.parquet"
    df.to_parquet(path, index=False)

    summ = {}
    for net in ("case118", "case30_thermal"):
        summ[net] = {}
        for fam in ("ridge", "histgb"):
            s = df[(df.network == net) & (df.model == fam)]
            at90 = s[np.isclose(s.coverage_target, 0.90)]
            summ[net][fam] = dict(
                q_hat_at_090_mean=float(at90.q_hat.mean()),
                q_hat_at_090_std=float(at90.q_hat.std(ddof=0)),
                missed_at_090_mean=float(at90.missed_viol.mean()),
                missed_at_090_std=float(at90.missed_viol.std(ddof=0)),
                mean_overshoot_given_viol_at_090=float(at90.mean_overshoot_given_viol.mean()),
                S_mean_over_qhat_at_090_mean=float(at90.S_mean_over_qhat.mean()),
                S_mean_over_qhat_at_090_std=float(at90.S_mean_over_qhat.std(ddof=0)),
                S_p99_over_qhat_at_090_mean=float(at90.S_p99_over_qhat.mean()),
                S_p99_over_qhat_at_090_std=float(at90.S_p99_over_qhat.std(ddof=0)),
                p_overshoot_gt_qhat_given_viol_at_090_mean=float(
                    at90.p_overshoot_gt_qhat_given_viol.mean()),
            )
    checks = dict(
        max_identity_gap=float(df.identity_gap.max()),
        min_share_missed_overshoot_gt_qhat=float(
            df.share_missed_overshoot_gt_qhat.dropna().min()),
        min_share_missed_overshoot_ge_qhat_plus_depth=float(
            df.share_missed_overshoot_ge_qhat_plus_depth.dropna().min()),
        n_rows_with_any_miss=int(df.share_missed_overshoot_gt_qhat.notna().sum()),
        n_rows=int(len(df)),
    )
    out = dict(
        question=("Does the barrier inequality hold within each model, and does ridge's "
                  "overshoot tail outgrow its own q_hat on case30-thermal in a way that "
                  "explains the model-ordering reversal?"),
        definitions=dict(
            overshoot="pred - Y, signed; positive means the model predicted above the truth",
            depth="0.94 - Y, positive on violations",
            inequality="a miss requires overshoot >= q_hat + depth",
            S_mean="E[overshoot | Y < L] / q_hat",
            S_p99="p99(overshoot | Y < L) / q_hat"),
        coverage_targets=targets, seeds=SEEDS, limit=LIMIT,
        identity_checks=checks, summary_at_090=summ)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    for p in (OUT, path):
        man = cm.build_manifest(p, out if p == OUT else {},
                                dict(task="barrier-height resolution",
                                     sources=[CASE118, CASE30T]))
        json.dump(man, open(mf.manifest_path(p), "w"), indent=2)
    print(f"\nwrote {OUT} and {path}  [{time.time()-t0:.0f}s]")
    print(json.dumps(checks, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
