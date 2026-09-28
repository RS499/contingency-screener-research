import os
import sys
import json
import time
import hashlib
import argparse
import subprocess
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import manifest as mf
import tune_surrogates as T

# N1: class-conditional calibration of the certify threshold.
# Step 1 refits the committed M2 (gate-aware) surrogates on the committed splits (5 seeds) and checks
# the refit against data/tuned_metrics.json. The cal/test predictions are saved as a long parquet so
# the E12/E13 and N2 scripts reuse the same refit without fitting again.
# Step 2 calibrates the certify threshold on calibration VIOLATION rows only, so that
# P(certify | violation) <= alpha; the flag rule (point prediction < 0.94) is unchanged.

DATASET = "data/dataset.parquet"
TUNED = "data/tuned_metrics.json"
OUT_JSON = "data/sts_n1_class_conditional.json"
OUT_PRED = "data/sts_n1_predictions_long.parquet"
SEEDS = 5
LIMIT = 0.94
ALPHAS = [0.10, 0.05, 0.02, 0.01]
FAMILIES = ["ridge", "histgb"]
CHECK_COVERAGES = [0.90, 0.94, 0.97]
GROUP_DRAW_SEED_OFFSET = 7000
GLOBAL_GRID = [round(0.70 + 0.001 * i, 3) for i in range(300)]


def m2_records():
    tm = json.load(open(TUNED))
    out = {}
    for r in tm["records"]:
        if r["metric"] == "m2":
            out[(r["family"], r["seed"])] = r
    return out


def sweep_point(rec, cov):
    for p in rec["sweep"]:
        if abs(p["coverage_target"] - cov) < 1e-9:
            return p
    return None


def rank_threshold(scores, alpha):
    # finite-sample one-sided rank: the ceil((n+1)(1-alpha))-th smallest score; +inf if the rank exceeds n
    s = np.sort(np.asarray(scores, dtype=np.float64))
    n = len(s)
    k = int(np.ceil((n + 1) * (1.0 - alpha)))
    if k > n:
        return float("inf")
    return float(s[k - 1])


def gate_with_threshold(pred, q):
    # same three-way gate as gate_eval.run_gate, with flag taking priority so that a negative
    # threshold can never certify a case whose point prediction is already below the limit
    flag = pred < LIMIT
    certify = (~flag) & (pred - q >= LIMIT)
    escalate = ~(certify | flag)
    return certify, flag, escalate


def gate_metrics(pred, y, sid, q, ms_surr, ms_solver):
    certify, flag, escalate = gate_with_threshold(pred, q)
    viol = y < LIMIT
    n = len(y)
    missed = certify & viol
    n_esc = int(escalate.sum())
    n_flag = int(flag.sum())
    # group-weighted missed rate: mean over test scenarios having >= 1 violation of the
    # per-scenario share of violations certified
    d = pd.DataFrame(dict(sid=sid, viol=viol, missed=missed))
    g = d[d["viol"]].groupby("sid")["missed"].mean()
    return dict(
        missed_viol=float(missed.sum() / max(int(viol.sum()), 1)),
        missed_viol_group_weighted=float(g.mean()),
        n_missed=int(missed.sum()),
        escalation=float(escalate.mean()),
        certified_frac=float(certify.mean()),
        flagged_frac=float(flag.mean()),
        coverage_emp=float((y >= pred - q).mean()),
        full_speedup=float(n * ms_solver / (n * ms_surr + n_esc * ms_solver)),
        certify_only_speedup=float(n * ms_solver / (n * ms_surr + (n_esc + n_flag) * ms_solver)))


def one_row_per_group(scores, sid, seed):
    # one violation row drawn at random from each calibration scenario that has any violation
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(scores))
    seen = set()
    keep = []
    for i in order:
        s = int(sid[i])
        if s not in seen:
            seen.add(s)
            keep.append(i)
    keep = np.array(sorted(keep))
    return scores[keep]


def equivalent_global_coverage(pred_cal, y_cal, q):
    # share of ALL calibration rows whose score pred - y is <= q: the global coverage target whose
    # q_hat would equal this threshold
    return float(np.mean((pred_cal - y_cal) <= q))


def mean_std(vals):
    a = np.array(vals, dtype=np.float64)
    finite = a[np.isfinite(a)]
    if len(finite) < len(a):
        return dict(mean=None, std=None, n_infinite=int(len(a) - len(finite)), per_seed=[float(v) for v in a])
    return dict(mean=float(a.mean()), std=float(a.std()), per_seed=[float(v) for v in a])


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def git_head():
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip()


def refit_all(X, y, groups, df, recs):
    rows = []
    fit_info = []
    for seed in range(SEEDS):
        sp = ms.make_splits(groups, seed)
        kept = ms.select_features(X, sp["train"])
        Xk = X[kept]
        Xtr = Xk.iloc[sp["train"]].to_numpy(np.float32)
        Xca = Xk.iloc[sp["cal"]].to_numpy(np.float32)
        Xte = Xk.iloc[sp["test"]].to_numpy(np.float32)
        ytr = y[sp["train"]]
        for fam in FAMILIES:
            rec = recs[(fam, seed)]
            t0 = time.time()
            fitted = T.fit_one(fam, rec["config"], Xtr, ytr, seed)
            fit_s = time.time() - t0
            p_ca = T.predict(fitted, Xca)
            t1 = time.time()
            p_te = T.predict(fitted, Xte)
            ms_surr = (time.time() - t1) / len(p_te) * 1000.0
            n_iter = int(fitted["model"].n_iter_) if fam == "histgb" else None
            fit_info.append(dict(seed=seed, family=fam, tag=rec["tag"], config=rec["config"],
                                 n_iter=n_iter, n_iter_committed=rec["n_iter"], fit_s=fit_s,
                                 ms_surrogate=ms_surr, n_features=int(len(kept))))
            for split, idx, p in (("cal", sp["cal"], p_ca), ("test", sp["test"], p_te)):
                rows.append(pd.DataFrame(dict(
                    seed=seed, family=fam, split=split, row_pos=idx.astype(np.int64),
                    scenario_id=groups[idx].astype(np.int64),
                    outaged_type=df["outaged_type"].to_numpy()[idx],
                    outaged_idx=df["outaged_idx"].to_numpy()[idx].astype(np.int64),
                    y=y[idx], pred=np.asarray(p, dtype=np.float64))))
            print(f"  seed {seed} {fam:6s} {rec['tag']:12s} fit {fit_s:.1f}s n_iter={n_iter} "
                  f"(committed {rec['n_iter']})", flush=True)
    return pd.concat(rows, ignore_index=True), fit_info


def reproduction_check(pl, recs, ms_solver):
    out = []
    worst = 0.0
    for seed in range(SEEDS):
        for fam in FAMILIES:
            sub = pl[(pl["seed"] == seed) & (pl["family"] == fam)]
            ca = sub[sub["split"] == "cal"]
            te = sub[sub["split"] == "test"]
            rec = recs[(fam, seed)]
            mae = float(np.mean(np.abs(te["pred"].to_numpy() - te["y"].to_numpy())))
            r = dict(seed=seed, family=fam, mae_refit=mae, mae_committed=rec["mae"])
            worst = max(worst, abs(mae - rec["mae"]))
            for cov in CHECK_COVERAGES:
                q = ge.calibrate_qhat(ca["pred"].to_numpy(), ca["y"].to_numpy(), cov)
                g = ge.run_gate(te["pred"].to_numpy(), q, LIMIT)
                s = ge.score(g, te["y"].to_numpy(), 1e-6, ms_solver, LIMIT)
                p = sweep_point(rec, cov)
                r[f"{cov}"] = dict(q_hat_refit=q, q_hat_committed=p["q_hat"],
                                   escalation_refit=s["escalation"], escalation_committed=p["escalation"],
                                   missed_refit=s["missed_viol"], missed_committed=p["missed_viol"])
                worst = max(worst, abs(q - p["q_hat"]), abs(s["escalation"] - p["escalation"]),
                            abs(s["missed_viol"] - p["missed_viol"]))
            out.append(r)
    return out, worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-predictions", action="store_true",
                    help="skip the refit; reuse data/sts_n1_predictions_long.parquet and the fit_info of the previous JSON")
    args = ap.parse_args()
    t0 = time.time()
    ms_solver = mf.load_solve_time()["ms_solver"]
    recs = m2_records()
    if args.from_predictions:
        pl = pd.read_parquet(OUT_PRED)
        prev = json.load(open(OUT_JSON))
        fit_info = prev["fit_info"]
        t_fit = prev["refit_wall_time_s"]
    else:
        df, feature_cols = ms.load_dataset(DATASET)
        X, y, groups, _b = ms.build_design_matrix(df, feature_cols)
        pl, fit_info = refit_all(X, y, groups, df, recs)
        pl.to_parquet(OUT_PRED, index=False)
        t_fit = time.time() - t0
    repro, worst = reproduction_check(pl, recs, ms_solver)
    print(f"reproduction: worst abs diff vs tuned_metrics (q_hat/escalation/missed/MAE) = {worst:.3e}", flush=True)

    ms_by = {}
    for fi in fit_info:
        ms_by[(fi["family"], fi["seed"])] = fi["ms_surrogate"]

    per_seed = []
    for seed in range(SEEDS):
        for fam in FAMILIES:
            sub = pl[(pl["seed"] == seed) & (pl["family"] == fam)]
            ca = sub[sub["split"] == "cal"]
            te = sub[sub["split"] == "test"]
            pc = ca["pred"].to_numpy(); yc = ca["y"].to_numpy(); sc = ca["scenario_id"].to_numpy()
            pt = te["pred"].to_numpy(); yt = te["y"].to_numpy(); st = te["scenario_id"].to_numpy()
            vmask = yc < LIMIT
            s_viol = pc[vmask] - yc[vmask]
            s_viol_sid = sc[vmask]
            p_viol = pc[vmask]
            n_v = int(vmask.sum())
            n_g = int(len(set(int(s) for s in s_viol_sid)))
            s_group = one_row_per_group(s_viol, s_viol_sid, GROUP_DRAW_SEED_OFFSET + seed)
            p_group = one_row_per_group(p_viol, s_viol_sid, GROUP_DRAW_SEED_OFFSET + seed)
            ms_surr = ms_by[(fam, seed)]
            for alpha in ALPHAS:
                # (a) band form: q_v on residual scores pred - y of calibration violations
                q_band = rank_threshold(s_viol, alpha)
                # (b) threshold form: tau on predictions of calibration violations; certify iff
                #     pred > tau (strict), i.e. q = tau - LIMIT with a strict inequality
                tau = rank_threshold(p_viol, alpha)
                q_thr = tau - LIMIT + 1e-12
                # (c) group-level band: one violation row per calibration scenario
                q_group = rank_threshold(s_group, alpha)
                tau_g = rank_threshold(p_group, alpha)
                q_thr_g = tau_g - LIMIT + 1e-12
                for form, q in (("band_rows", q_band), ("threshold_rows", q_thr),
                                ("band_groups", q_group), ("threshold_groups", q_thr_g)):
                    rec = dict(seed=seed, family=fam, alpha=alpha, form=form,
                               q=(q if np.isfinite(q) else None),
                               n_cal_violation_rows=n_v, n_cal_violation_groups=n_g)
                    if np.isfinite(q):
                        rec.update(gate_metrics(pt, yt, st, q, ms_surr, ms_solver))
                        rec["equivalent_global_coverage"] = equivalent_global_coverage(pc, yc, q)
                    else:
                        rec.update(gate_metrics(pt, yt, st, 1e9, ms_surr, ms_solver))
                        rec["equivalent_global_coverage"] = 1.0
                    per_seed.append(rec)
            # committed global q_hat reference points
            for cov in CHECK_COVERAGES:
                q = ge.calibrate_qhat(pc, yc, cov)
                rec = dict(seed=seed, family=fam, alpha=None, form=f"global_{cov}", q=q,
                           n_cal_violation_rows=n_v, n_cal_violation_groups=n_g)
                rec.update(gate_metrics(pt, yt, st, q, ms_surr, ms_solver))
                rec["equivalent_global_coverage"] = cov
                per_seed.append(rec)

    # matched-missed comparison: the global gate traced on a fine coverage grid; for each seed, the
    # smallest global coverage target whose TEST missed rate is <= the class-conditional missed rate
    matched = []
    for seed in range(SEEDS):
        for fam in FAMILIES:
            sub = pl[(pl["seed"] == seed) & (pl["family"] == fam)]
            ca = sub[sub["split"] == "cal"]
            te = sub[sub["split"] == "test"]
            pc = ca["pred"].to_numpy(); yc = ca["y"].to_numpy()
            pt = te["pred"].to_numpy(); yt = te["y"].to_numpy(); st = te["scenario_id"].to_numpy()
            curve = []
            for cov in GLOBAL_GRID:
                q = ge.calibrate_qhat(pc, yc, cov)
                m = gate_metrics(pt, yt, st, q, ms_by[(fam, seed)], ms_solver)
                curve.append((cov, q, m["missed_viol"], m["escalation"]))
            for r in per_seed:
                if r["seed"] != seed or r["family"] != fam or r["form"] not in ("band_rows", "threshold_rows"):
                    continue
                hit = None
                for cov, q, mv, esc in curve:
                    if mv <= r["missed_viol"]:
                        hit = (cov, q, mv, esc)
                        break
                matched.append(dict(seed=seed, family=fam, form=r["form"], alpha=r["alpha"],
                                    cc_missed=r["missed_viol"], cc_escalation=r["escalation"],
                                    global_cov=(hit[0] if hit else None),
                                    global_q=(hit[1] if hit else None),
                                    global_missed=(hit[2] if hit else None),
                                    global_escalation=(hit[3] if hit else None)))

    summary = {}
    for fam in FAMILIES:
        summary[fam] = {}
        forms = ["band_rows", "threshold_rows", "band_groups", "threshold_groups"]
        for form in forms:
            summary[fam][form] = {}
            for alpha in ALPHAS:
                rs = [r for r in per_seed if r["family"] == fam and r["form"] == form and r["alpha"] == alpha]
                block = {}
                for key in ("q", "missed_viol", "missed_viol_group_weighted", "escalation", "certified_frac",
                            "flagged_frac", "coverage_emp", "full_speedup", "certify_only_speedup",
                            "equivalent_global_coverage"):
                    block[key] = mean_std([r[key] for r in rs])
                block["missed_viol_max_over_seeds"] = float(max(r["missed_viol"] for r in rs))
                block["n_seeds_missed_le_alpha"] = int(sum(1 for r in rs if r["missed_viol"] <= alpha))
                summary[fam][form][str(alpha)] = block
        summary[fam]["global_reference"] = {}
        for cov in CHECK_COVERAGES:
            rs = [r for r in per_seed if r["family"] == fam and r["form"] == f"global_{cov}"]
            block = {}
            for key in ("q", "missed_viol", "missed_viol_group_weighted", "escalation", "certified_frac",
                        "flagged_frac", "coverage_emp", "full_speedup", "certify_only_speedup"):
                block[key] = mean_std([r[key] for r in rs])
            summary[fam]["global_reference"][str(cov)] = block
        summary[fam]["matched_missed_vs_global"] = {}
        for form in ("band_rows", "threshold_rows"):
            summary[fam]["matched_missed_vs_global"][form] = {}
            for alpha in ALPHAS:
                ms_rows = [m for m in matched if m["family"] == fam and m["alpha"] == alpha and m["form"] == form]
                diffs = [m["cc_escalation"] - m["global_escalation"] for m in ms_rows
                         if m["global_escalation"] is not None]
                complete = len(diffs) == len(ms_rows)
                summary[fam]["matched_missed_vs_global"][form][str(alpha)] = dict(
                    cc_missed=mean_std([m["cc_missed"] for m in ms_rows]),
                    cc_escalation=mean_std([m["cc_escalation"] for m in ms_rows]),
                    global_escalation_at_matched_missed=(mean_std([m["global_escalation"] for m in ms_rows])
                                                         if complete else None),
                    global_cov_at_matched_missed=[m["global_cov"] for m in ms_rows],
                    paired_diff_cc_minus_global=(mean_std(diffs) if complete else None))

    wall = time.time() - t0
    out = dict(
        question=("class-conditional calibration: certify threshold calibrated on calibration-split "
                  "violation rows only so that P(certify | violation) <= alpha; flag rule unchanged"),
        limit=LIMIT, alphas=ALPHAS, seeds=SEEDS, families=FAMILIES,
        forms=dict(
            band_rows=("q_v = ceil((n_v+1)(1-alpha))-th smallest of pred - y over the n_v calibration "
                       "violation ROWS; certify iff pred - q_v >= 0.94 and pred >= 0.94. A certified "
                       "violation needs pred - y > q_v, so P(certify|violation) <= alpha if violation "
                       "rows were exchangeable."),
            threshold_rows=("tau = ceil((n_v+1)(1-alpha))-th smallest PREDICTION over calibration "
                            "violation rows; certify iff pred > tau and pred >= 0.94. Directly bounds "
                            "P(pred > tau | violation); less conservative than band_rows."),
            band_groups=("band_rows computed on ONE randomly drawn violation row per calibration "
                         "scenario (seed 7000+split seed); n = number of calibration scenarios with a violation."),
            threshold_groups="threshold_rows on the same one-row-per-scenario draw.",
            global_reference="committed global q_hat (all calibration rows) at coverage 0.90/0.94/0.97"),
        exchangeability=(
            "Splits are GroupShuffleSplit on scenario_id (the base case). The exchangeable unit is the "
            "base case: calibration and test base cases are i.i.d. draws from the same accepted-scenario "
            "distribution. Rows within one base case share its load/generator draw and are NOT "
            "independent, and the number of violation rows per base case varies, so the pooled-row forms "
            "(band_rows, threshold_rows) do not carry the textbook finite-sample row-level guarantee; "
            "they are pooled-row calibrations whose rank uses n_v rows as if exchangeable. The "
            "group forms (one violation row per calibration base case) carry the finite-sample marginal "
            "guarantee for ONE randomly chosen violation row of a NEW base case that has at least one "
            "violation; the matching test metric is missed_viol_group_weighted (mean over test base "
            "cases with a violation of the per-base share certified)."),
        speedup_definitions=dict(
            full_speedup="committed formula: n*t_solve / (n*t_surr + n_esc*t_solve); certify and flag both skip the solver",
            certify_only_speedup=("n*t_solve / (n*t_surr + (n_esc + n_flag)*t_solve): only certified "
                                  "cases skip the solver; flagged cases are also solved"),
            t_solve_ms=ms_solver, t_surr="batch test prediction time / n, measured in this refit"),
        matched_missed_note=(
            "Every gate here has the form certify iff pred >= 0.94 + q (flag iff pred < 0.94), so for "
            "a given model and split the class-conditional gate lies on the SAME one-parameter "
            "(missed, escalation) curve as the committed global gate; it selects a different threshold "
            "q and attaches a bound to the missed rate, it does not move the frontier. The matched "
            "comparison uses the smallest global coverage target on a 0.001 grid whose TEST missed "
            "rate is <= the class-conditional test missed rate (test-informed; for comparison only)."),
        reproduction_check=dict(worst_abs_diff=worst, per_seed=repro,
                                compared_against=TUNED + " (M2 records, sweep points 0.90/0.94/0.97, MAE)"),
        fit_info=fit_info,
        summary=summary,
        per_seed=per_seed,
        matched_per_seed=matched,
        predictions_parquet=OUT_PRED,
        predictions_reused_from_earlier_refit=bool(args.from_predictions),
        std_convention="population std (ddof=0) over the five held-out splits",
        wall_time_s=wall, refit_wall_time_s=t_fit)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)

    hyper = {}
    for fi in fit_info:
        hyper[f"{fi['family']}_seed{fi['seed']}"] = dict(tag=fi["tag"], config=fi["config"])
    man = dict(
        schema="sts-new-analysis",
        artifacts=[OUT_JSON, OUT_PRED],
        generating_script="scripts/sts_n1_class_conditional.py",
        regeneration_argv=[".venv/bin/python", "scripts/sts_n1_class_conditional.py"],
        script_sha256=sha256_of("scripts/sts_n1_class_conditional.py"),
        repo_head_commit=git_head(),
        inputs=[dict(path=DATASET, sha256=sha256_of(DATASET)),
                dict(path=TUNED, sha256=sha256_of(TUNED)),
                dict(path="data/solve_time.json", sha256=sha256_of("data/solve_time.json"))],
        output_sha256={OUT_JSON: sha256_of(OUT_JSON), OUT_PRED: sha256_of(OUT_PRED)},
        run_mode=("--from-predictions: summary recomputed from the saved refit predictions (refit wall time "
                  "carried from the refit run)" if args.from_predictions else "full refit"),
        model_hyperparameters=hyper,
        selection="M2 (gate-aware) committed selections from data/tuned_metrics.json, refit on the full train split",
        seeds=list(range(SEEDS)), split_protocol="make_splits(groups, seed): GroupShuffleSplit 60/20/20 on scenario_id",
        group_draw_seeds=[GROUP_DRAW_SEED_OFFSET + s for s in range(SEEDS)],
        alphas=ALPHAS, limit=LIMIT,
        solver=dict(note="no AC solves in this script", pinned=mf.SOLVER),
        environment=mf.build_manifest(),
        wall_time_s=wall,
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(mf.manifest_path(OUT_JSON), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {OUT_JSON}, {OUT_PRED} + manifest; wall {wall:.0f}s", flush=True)
    for fam in FAMILIES:
        for alpha in ALPHAS:
            b = summary[fam]["band_rows"][str(alpha)]
            g = summary[fam]["band_groups"][str(alpha)]
            print(f"  {fam:6s} a={alpha:.2f} band_rows missed={b['missed_viol']['mean']} esc={b['escalation']['mean']} "
                  f"| band_groups missed_gw={g['missed_viol_group_weighted']['mean']} esc={g['escalation']['mean']}", flush=True)


if __name__ == "__main__":
    main()
