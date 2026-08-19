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

# STAGE 2C / 2D / 2E. Three drift tests, case118 only.
#
# SHARED DESIGN. The surrogate is fit once per (seed, family) on the STANDARD train split
# using the stored M2 config -- no re-search, so the model is identical to the one behind
# every published number. Only the CALIBRATION and TEST populations change. That isolates
# the distribution shift from any model difference.
#
# EVERY SHIFTED CELL IS PAIRED WITH A SAME-STRATUM CONTROL. Calibrating on A and evaluating
# on B tells you nothing on its own: B may simply be harder. The control (calibrate A,
# evaluate A) separates "the shift broke the guarantee" from "this stratum is harder".
# Without it the experiment is uninterpretable, so it is not optional.
#
# 2C  n0_min_vm stratum   -- benign vs marginal base cases. Split at the median.
# 2D  element type        -- 173 lines vs 13 transformers. The event space changes, so no
#                            likelihood ratio exists; this is the N-1 -> N-2 failure mode.
# 2E  loading             -- SOFT TILT ONLY. A median split on a deterministic function of
#                            the sample gives disjoint support and an infinite density
#                            ratio, which is outside the weighted-conformal framework, not
#                            a hard case within it. The tilt keeps supports identical.

DATASET = "data/dataset.parquet"
TUNED = "data/tuned_metrics.json"
CURVE_V2 = "data/tradeoff_curve_v2.json"
LIMIT = 0.94
SEEDS = 5
FAMILIES = ("ridge", "histgb")

TILT_LAMBDA = 3.0
ESS_FLOOR = 0.10


def m2_config(tuned, family, seed):
    for r in tuned["records"]:
        if r["family"] == family and r["metric"] == "m2" and r["seed"] == seed:
            return r["config"]
    raise ValueError(f"no m2 config for {family} seed {seed}")


def weighted_qhat(over, weights, coverage):
    """Weighted split-conformal quantile (Tibshirani et al. 2019).

    Normalised weights over calibration points plus a point mass at +inf; the quantile is
    the smallest score whose cumulative normalised weight reaches the coverage level.
    With uniform weights this reduces to the ordinary rank quantile.
    """
    order = np.argsort(over)
    s, w = over[order], weights[order]
    total = w.sum() + w.max()          # +inf atom carries max weight
    cum = np.cumsum(w) / total
    idx = np.searchsorted(cum, coverage)
    if idx >= len(s):
        return float(s[-1])
    return float(s[idx])


def evaluate(pred_cal, y_cal, pred_te, y_te, targets, ms_solver, w_cal=None):
    out = []
    over = np.asarray(pred_cal, dtype=np.float64) - np.asarray(y_cal, dtype=np.float64)
    for cov in targets:
        if w_cal is None:
            q = ge.calibrate_qhat(pred_cal, y_cal, cov)
        else:
            q = weighted_qhat(over, np.asarray(w_cal, dtype=np.float64), cov)
        gate = ge.run_gate(pred_te, q, LIMIT)
        s = ge.score(gate, y_te, 1e-6, ms_solver, LIMIT)
        out.append(dict(coverage_target=cov, q_hat=float(q),
                        escalation=s["escalation"], coverage_emp=s["coverage"],
                        missed_viol=s["missed_viol"], net_speedup=s["net_speedup"],
                        n_test=s["n"], n_true_viol=s["n_true_viol"],
                        n_escalated=s["n_escalated"],
                        n_certified=int(gate["certify"].sum()),
                        n_flagged=int(gate["flag"].sum())))
    return out


def prepare():
    tuned = json.load(open(TUNED))
    targets = list(json.load(open(CURVE_V2))["coverage_levels"])
    ms_solver = mf.load_solve_time()["ms_solver"]
    df, feat = ms.load_dataset(DATASET)
    X, y, groups, _b = ms.build_design_matrix(df, feat)
    return tuned, targets, ms_solver, df, X, y, groups


def fitted_models(tuned, X, y, groups, seed):
    splits = ms.make_splits(groups, seed)
    kept = ms.select_features(X, splits["train"])
    Xk = X[kept]
    Xtr = Xk.iloc[splits["train"]].to_numpy(np.float32)
    ytr = y[splits["train"]]
    models = {}
    for fam in FAMILIES:
        models[fam] = T.fit_one(fam, m2_config(tuned, fam, seed), Xtr, ytr, seed)
    return splits, Xk, models


def run_2c(tuned, targets, ms_solver, df, X, y, groups):
    """Benign vs marginal base cases, split at the median n0_min_vm."""
    base_vm = df.groupby("scenario_id")["n0_min_vm"].first()
    median_vm = float(base_vm.median())
    benign_scen = set(base_vm[base_vm >= median_vm].index)
    row_benign = df.scenario_id.isin(benign_scen).to_numpy()

    rows = []
    for seed in range(SEEDS):
        splits, Xk, models = fitted_models(tuned, X, y, groups, seed)
        for fam in FAMILIES:
            pred_all = {}
            for part in ("cal", "test"):
                idx = splits[part]
                pred_all[part] = np.asarray(
                    T.predict(models[fam], Xk.iloc[idx].to_numpy(np.float32)), dtype=np.float64)
            for cal_str in ("benign", "marginal"):
                for te_str in ("benign", "marginal"):
                    ci = splits["cal"]
                    ti = splits["test"]
                    cm_ = row_benign[ci] if cal_str == "benign" else ~row_benign[ci]
                    tm_ = row_benign[ti] if te_str == "benign" else ~row_benign[ti]
                    if cm_.sum() < 100 or tm_.sum() < 100:
                        continue
                    recs = evaluate(pred_all["cal"][cm_], y[ci][cm_],
                                    pred_all["test"][tm_], y[ti][tm_], targets, ms_solver)
                    shift = (float(df.n0_min_vm.to_numpy()[ti][tm_].mean())
                             - float(df.n0_min_vm.to_numpy()[ci][cm_].mean()))
                    for r in recs:
                        r.update(test="2C_n0_stratum", seed=seed, model=fam,
                                 cal_stratum=cal_str, test_stratum=te_str,
                                 is_control=(cal_str == te_str),
                                 median_n0_min_vm=median_vm,
                                 realized_shift_mean_n0_min_vm=shift,
                                 n_cal=int(cm_.sum()))
                    rows.extend(recs)
        print(f"  2C seed {seed} done", flush=True)
    return rows


def run_2d(tuned, targets, ms_solver, df, X, y, groups):
    """Line outages vs transformer outages."""
    is_line = (df.outaged_type == "line").to_numpy()
    rows = []
    for seed in range(SEEDS):
        splits, Xk, models = fitted_models(tuned, X, y, groups, seed)
        for fam in FAMILIES:
            pred = {p: np.asarray(T.predict(models[fam],
                                            Xk.iloc[splits[p]].to_numpy(np.float32)),
                                  dtype=np.float64) for p in ("cal", "test")}
            for cal_e in ("line", "trafo"):
                for te_e in ("line", "trafo"):
                    ci, ti = splits["cal"], splits["test"]
                    cm_ = is_line[ci] if cal_e == "line" else ~is_line[ci]
                    tm_ = is_line[ti] if te_e == "line" else ~is_line[ti]
                    if cm_.sum() < 100 or tm_.sum() < 100:
                        continue
                    recs = evaluate(pred["cal"][cm_], y[ci][cm_],
                                    pred["test"][tm_], y[ti][tm_], targets, ms_solver)
                    for r in recs:
                        r.update(test="2D_element_type", seed=seed, model=fam,
                                 cal_stratum=cal_e, test_stratum=te_e,
                                 is_control=(cal_e == te_e), n_cal=int(cm_.sum()))
                    rows.extend(recs)
        print(f"  2D seed {seed} done", flush=True)
    return rows


def tilt_weights(agg, lam):
    """w(a) proportional to exp(lam * normalised a). Finite and positive everywhere."""
    a = np.asarray(agg, dtype=np.float64)
    lo, hi = a.min(), a.max()
    z = (a - lo) / (hi - lo) if hi > lo else np.zeros_like(a)
    w = np.exp(lam * z)
    return w / w.mean()


def run_2e(tuned, targets, ms_solver, df, X, y, groups):
    """Soft tilt toward high load. NO median split."""
    agg = df.agg_loading.to_numpy(dtype=np.float64)
    rows, diagnostics = [], []
    for seed in range(SEEDS):
        splits, Xk, models = fitted_models(tuned, X, y, groups, seed)
        ci, ti = splits["cal"], splits["test"]
        w_cal = tilt_weights(agg[ci], TILT_LAMBDA)
        w_te = tilt_weights(agg[ti], TILT_LAMBDA)
        ess = float(w_te.sum() ** 2 / (w_te ** 2).sum() / len(w_te))
        diag = dict(seed=seed, lam=TILT_LAMBDA,
                    w_cal_min=float(w_cal.min()), w_cal_max=float(w_cal.max()),
                    w_test_min=float(w_te.min()), w_test_max=float(w_te.max()),
                    ratio_finite=bool(np.all(np.isfinite(w_cal)) and np.all(w_cal > 0)
                                      and np.all(np.isfinite(w_te)) and np.all(w_te > 0)),
                    ess_fraction=ess,
                    agg_min=float(agg[ti].min()), agg_max=float(agg[ti].max()))
        diagnostics.append(diag)
        if not diag["ratio_finite"]:
            print(f"  2E seed {seed}: LIKELIHOOD RATIO NOT FINITE - stopping", flush=True)
            break
        if ess < ESS_FLOOR:
            print(f"  2E seed {seed}: ESS fraction {ess:.4f} < {ESS_FLOOR} - degenerate tilt, "
                  f"stopping", flush=True)
            break

        rng = np.random.default_rng(1000 + seed)
        p = w_te / w_te.sum()
        pick = rng.choice(len(ti), size=len(ti), replace=True, p=p)

        for fam in FAMILIES:
            pc = np.asarray(T.predict(models[fam], Xk.iloc[ci].to_numpy(np.float32)),
                            dtype=np.float64)
            pt = np.asarray(T.predict(models[fam], Xk.iloc[ti].to_numpy(np.float32)),
                            dtype=np.float64)
            cells = [
                ("untilted_test_unweighted_cal", pt, y[ti], None),
                ("tilted_test_unweighted_cal", pt[pick], y[ti][pick], None),
                ("tilted_test_weighted_cal", pt[pick], y[ti][pick], w_cal),
            ]
            for label, ptest, ytest, wc in cells:
                recs = evaluate(pc, y[ci], ptest, ytest, targets, ms_solver, w_cal=wc)
                for r in recs:
                    r.update(test="2E_loading_tilt", seed=seed, model=fam, cell=label,
                             is_control=(label == "untilted_test_unweighted_cal"),
                             lam=TILT_LAMBDA, ess_fraction=ess,
                             realized_mean_agg_cal=float(agg[ci].mean()),
                             realized_mean_agg_test=float(agg[ti][pick].mean()))
                rows.extend(recs)
        print(f"  2E seed {seed} done (ESS {ess:.4f})", flush=True)
    return rows, diagnostics


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    t0 = time.time()
    tuned, targets, ms_solver, df, X, y, groups = prepare()
    print(f"prepared: rows={len(df)} targets={len(targets)} seeds={SEEDS}", flush=True)

    if which in ("all", "2c"):
        rows = run_2c(tuned, targets, ms_solver, df, X, y, groups)
        out = pd.DataFrame(rows)
        path = "data/drift_n0_stratum_long.parquet"
        out.to_parquet(path, index=False)
        man = cm.build_manifest(path, {}, dict(
            task="Stage 2C: n0_min_vm stratum drift (case118)", source=DATASET,
            design="fit on standard train with stored M2 config; vary calibration and test "
                   "strata only; every shifted cell paired with a same-stratum control"))
        json.dump(man, open(mf.manifest_path(path), "w"), indent=2)
        print(f"wrote {path} rows={len(out)}  [{time.time()-t0:.0f}s]", flush=True)

    if which in ("all", "2d"):
        rows = run_2d(tuned, targets, ms_solver, df, X, y, groups)
        out = pd.DataFrame(rows)
        path = "data/drift_element_type_long.parquet"
        out.to_parquet(path, index=False)
        man = cm.build_manifest(path, {}, dict(
            task="Stage 2D: element-type drift (case118)", source=DATASET,
            design="calibrate on one element population, evaluate on the other; controls included",
            note="the event space changes between strata, so no likelihood ratio exists and "
                 "weighted conformal does not apply -- structurally the N-1 to N-2 failure"))
        json.dump(man, open(mf.manifest_path(path), "w"), indent=2)
        print(f"wrote {path} rows={len(out)}  [{time.time()-t0:.0f}s]", flush=True)

    if which in ("all", "2e"):
        rows, diags = run_2e(tuned, targets, ms_solver, df, X, y, groups)
        out = pd.DataFrame(rows)
        path = "data/drift_loading_tilt_long.parquet"
        out.to_parquet(path, index=False)
        json.dump(dict(tilt_lambda=TILT_LAMBDA, ess_floor=ESS_FLOOR, diagnostics=diags),
                  open("data/drift_loading_tilt_diagnostics.json", "w"), indent=2)
        man = cm.build_manifest(path, {}, dict(
            task="Stage 2E: loading soft-tilt drift (case118)", source=DATASET,
            design="soft exponential tilt on agg_loading; supports identical, ratio finite; "
                   "NO median split",
            tilt_lambda=TILT_LAMBDA))
        json.dump(man, open(mf.manifest_path(path), "w"), indent=2)
        print(f"wrote {path} rows={len(out)}  [{time.time()-t0:.0f}s]", flush=True)

    print(f"done in {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
