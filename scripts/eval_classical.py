import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import classical_manifest as cm

PREDS = "data/classical_predictions.parquet"
DATASET = "data/dataset.parquet"
OUT = "data/classical_screen_metrics.json"
SEEDS = [0, 1, 2, 3, 4]
LIMIT = 0.94
MS_SOLVER = 9.14
DELTAS = [round(0.001 * i, 4) for i in range(0, 31)]
COVERAGES = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98]
K_VALUES = [1, 2, 3, 5, 8, 10, 15, 20, 30, 40, 50, 65, 80, 100, 120, 150, 186]


def mean_std(values):
    a = np.asarray(values, dtype=np.float64)
    return float(a.mean()), float(a.std(ddof=0))


def load_joined():
    df, _feature_cols = ms.load_dataset(DATASET)
    preds = pd.read_parquet(PREDS)
    key = ["scenario_id", "outaged_type", "outaged_idx"]
    left = df[key + ["min_vm", "argmin_bus"]].copy()
    right = preds[key + ["pred_min_vm", "pi", "pred_argmin_bus", "true_weakest_type"]].copy()
    joined = left.merge(right, on=key, how="left", validate="one_to_one")
    n_missing = int(joined["pred_min_vm"].isna().sum())
    if n_missing:
        raise RuntimeError(f"{n_missing} converged rows have no classical prediction; stopping.")
    groups = df["scenario_id"].to_numpy()
    print(f"joined: {len(joined)} converged N-1 rows, {len(set(groups))} scenarios")
    return joined, groups


def delta_sweep(pred, y, deltas, ms_classical):
    out = []
    n = len(y)
    true_viol = y < LIMIT
    n_true = max(int(true_viol.sum()), 1)
    for d in deltas:
        certify = pred >= LIMIT + d
        flag = pred < LIMIT
        escalate = ~(certify | flag)
        n_esc = int(escalate.sum())
        missed = int((certify & true_viol).sum())
        out.append(dict(delta=d,
                        escalation=n_esc / n,
                        avoided=1.0 - n_esc / n,
                        missed_viol=missed / n_true,
                        net_speedup=n * MS_SOLVER / (n * ms_classical + n_esc * MS_SOLVER)))
    return out


def conformal_sweep(pred_cal, y_cal, pred_te, y_te, coverages, ms_classical):
    out = []
    for cov in coverages:
        q_hat = ge.calibrate_qhat(pred_cal, y_cal, cov)
        gate = ge.run_gate(pred_te, q_hat, LIMIT)
        s = ge.score(gate, y_te, ms_classical, MS_SOLVER, LIMIT)
        out.append(dict(coverage_target=cov, q_hat=q_hat,
                        escalation=s["escalation"], avoided=1.0 - s["escalation"],
                        coverage_emp=s["coverage"], missed_viol=s["missed_viol"],
                        net_speedup=s["net_speedup"]))
    return out


def pi_ranking(sub, k_values, ms_classical):
    out = []
    n_total = len(sub)
    n_true = max(int((sub["min_vm"].to_numpy() < LIMIT).sum()), 1)
    sub = sub.copy()
    sub["rank"] = sub.groupby("scenario_id")["pi"].rank(ascending=False, method="first")
    ranks = sub["rank"].to_numpy()
    viol = sub["min_vm"].to_numpy() < LIMIT
    for k in k_values:
        solved = ranks <= k
        skipped = ~solved
        n_solved = int(solved.sum())
        missed = int((skipped & viol).sum())
        out.append(dict(k=k,
                        escalation=n_solved / n_total,
                        avoided=1.0 - n_solved / n_total,
                        missed_viol=missed / n_true,
                        net_speedup=n_total * MS_SOLVER /
                        (n_total * ms_classical + n_solved * MS_SOLVER)))
    return out


def qlimit_analysis(joined):
    err = joined["pred_min_vm"].to_numpy() - joined["min_vm"].to_numpy()
    wtype = joined["true_weakest_type"].to_numpy()
    names = {0: "PQ", 1: "PV", 2: "ref"}
    table = {}
    for t in (0, 1, 2):
        m = wtype == t
        if not m.any():
            continue
        e = err[m]
        table[names[t]] = dict(n=int(m.sum()),
                               n_over=int((e > 0).sum()), n_under=int((e <= 0).sum()),
                               frac_over=float((e > 0).mean()),
                               mae=float(np.mean(np.abs(e))),
                               mean_signed_err=float(e.mean()),
                               p95_over=float(np.quantile(e, 0.95)))
    per_bus = {}
    for b in (75, 52, 106):
        m = joined["argmin_bus"].to_numpy() == b
        if not m.any():
            continue
        e = err[m]
        t = wtype[m]
        per_bus[str(b)] = dict(n=int(m.sum()),
                               share_of_all=float(m.mean()),
                               n_base_PV=int((t == 1).sum()), n_base_PQ=int((t == 0).sum()),
                               mae=float(np.mean(np.abs(e))),
                               mean_signed_err=float(e.mean()),
                               frac_over=float((e > 0).mean()))
        for t_val, t_name in ((1, "PV"), (0, "PQ")):
            mm = m & (wtype == t_val)
            if mm.any():
                ee = err[mm]
                per_bus[str(b)][f"when_base_{t_name}"] = dict(
                    n=int(mm.sum()), mae=float(np.mean(np.abs(ee))),
                    mean_signed_err=float(ee.mean()), frac_over=float((ee > 0).mean()))
    return dict(by_weakest_bus_type=table, per_bus=per_bus)


def main():
    joined, groups = load_joined()
    with open("data/classical_predictions_meta.json") as f:
        meta = json.load(f)
    timing = meta["timing_ms_per_contingency"]
    ms_classical = timing["ms_apply_plus_factor"]
    print(f"ms_classical (headline apply+factor) = {ms_classical:.5f} ms/contingency")

    pred_all = joined["pred_min_vm"].to_numpy(np.float64)
    y_all = joined["min_vm"].to_numpy(np.float64)

    per_seed = {"delta": [], "conformal": [], "pi": [], "fit": []}
    for seed in SEEDS:
        splits = ms.make_splits(groups, seed)
        cal, test = splits["cal"], splits["test"]
        pred_cal, y_cal = pred_all[cal], y_all[cal]
        pred_te, y_te = pred_all[test], y_all[test]
        per_seed["delta"].append(delta_sweep(pred_te, y_te, DELTAS, ms_classical))
        per_seed["conformal"].append(
            conformal_sweep(pred_cal, y_cal, pred_te, y_te, COVERAGES, ms_classical))
        per_seed["pi"].append(pi_ranking(joined.iloc[test], K_VALUES, ms_classical))
        e = pred_te - y_te
        per_seed["fit"].append(dict(mae=float(np.mean(np.abs(e))),
                                    mean_signed_err=float(e.mean()),
                                    frac_over=float((e > 0).mean()),
                                    r2=float(1 - np.sum(e ** 2) /
                                             np.sum((y_te - y_te.mean()) ** 2)),
                                    n_test=int(len(y_te))))
        print(f"  seed {seed}: n_test={len(y_te)} MAE={per_seed['fit'][-1]['mae']:.4f} "
              f"q_hat@0.90={per_seed['conformal'][-1][0]['q_hat']:.5f}")

    def agg(kind, keyfield, metrics):
        rows = []
        n_points = len(per_seed[kind][0])
        for i in range(n_points):
            rec = {keyfield: per_seed[kind][0][i][keyfield]}
            for m in metrics:
                mu, sd = mean_std([per_seed[kind][s][i][m] for s in range(len(SEEDS))])
                rec[m] = mu
                rec[m + "_std"] = sd
            rows.append(rec)
        return rows

    out = dict(
        n_seeds=len(SEEDS), seeds=SEEDS, limit=LIMIT, ms_solver=MS_SOLVER,
        ms_solver_basis=("MINIMUM over 400 timed solves after 30 warm-up (data/solve_time.json; "
                         "mean 9.561, median 9.512, std 0.256 ms). The minimum is the conservative "
                         "choice: a smaller t_solve yields a SMALLER speedup."),
        ms_classical_headline=ms_classical,
        ms_classical_accountings=timing,
        nonconverged_convention=("dropped, identically to the surrogate evaluation "
                                 "(make_splits.load_dataset keeps converged rows only); "
                                 "45 of 279,000 N-1 cases"),
        coverage_note=("The uncalibrated screens (delta sweep, PI ranking) have NO prediction "
                       "interval, so empirical coverage is NOT APPLICABLE for them. The "
                       "conformalized screen does have one and its coverage_emp is reported."),
        pi_definition=dict(
            source=("Ejebe, G.C. & Wollenberg, B.F., 'Automatic Contingency Selection', IEEE Trans. "
                    "Power Apparatus and Systems, PAS-98(1), 1979, pp. 97-109 (voltage PI, Eq. 4)"),
            formula="PI_V = sum_i (W_i / 2n) * ((|V_i| - V_sp) / dV_lim)^{2n}",
            exponent_2n=2, n=1, weights="unit (W_i = 1)",
            reference_point=("V_sp = 0.94, the SCREENING FLOOR. Ejebe-Wollenberg typically "
                             "reference NOMINAL voltage; using the floor targets the quantity "
                             "actually being screened."),
            normalizer=("dV_lim = 0.94 with unit weights is a CONSTANT SCALE FACTOR, so it does "
                        "not affect the RANKING at all (the PI is used only to order "
                        "contingencies within a scenario)."),
            under_voltage_only=("only buses below the floor contribute (max(0, .)), so "
                                "over-voltage cannot mask under-voltage"),
            known_limitation=("low order (2n=2) can mask one severe violation behind many mild "
                              "ones; n=2 is a separately reported tuning follow-up, not mixed "
                              "into this first honest result")),
        fit_quality=dict(
            mae=mean_std([f["mae"] for f in per_seed["fit"]])[0],
            mae_std=mean_std([f["mae"] for f in per_seed["fit"]])[1],
            mean_signed_err=mean_std([f["mean_signed_err"] for f in per_seed["fit"]])[0],
            mean_signed_err_std=mean_std([f["mean_signed_err"] for f in per_seed["fit"]])[1],
            frac_over=mean_std([f["frac_over"] for f in per_seed["fit"]])[0],
            r2=mean_std([f["r2"] for f in per_seed["fit"]])[0],
            r2_std=mean_std([f["r2"] for f in per_seed["fit"]])[1],
            n_test_per_seed=[f["n_test"] for f in per_seed["fit"]],
            comparability_note=("These are five full held-out splits, directly comparable to the "
                                "committed surrogate MAE/R2 in data/screener_metrics.json. The "
                                "12-scenario pilot number is NOT comparable and is not reported "
                                "here.")),
        delta_sweep=agg("delta", "delta", ["escalation", "avoided", "missed_viol", "net_speedup"]),
        conformalized=agg("conformal", "coverage_target",
                          ["q_hat", "escalation", "avoided", "coverage_emp", "missed_viol",
                           "net_speedup"]),
        pi_ranking=agg("pi", "k", ["escalation", "avoided", "missed_viol", "net_speedup"]),
        qlimit_analysis=qlimit_analysis(joined),
        bus_base_type_counts=meta["bus_base_type_counts"],
        gens_at_qlim_base=meta["gens_at_qlim_base"],
    )

    run_settings = dict(task="classical baseline: evaluation on the five held-out splits",
                        predictions=PREDS, dataset=DATASET, seeds=SEEDS,
                        split="GroupShuffleSplit by scenario_id, train 0.6 / cal 0.2 / test 0.2",
                        conformal_code="feasibility/gate_eval.py (REUSED unmodified)",
                        tuned_on="nothing yet - this is the first honest, untuned result",
                        ms_classical_accounting="apply + amortized Jacobian factorization",
                        nproc=1, seed="split seeds 0-4; no other RNG")
    cm.write_with_manifest(OUT, out, run_settings)

    print("\n=== fit quality (5 full test splits) ===")
    fq = out["fit_quality"]
    print(f"  MAE={fq['mae']:.4f}+/-{fq['mae_std']:.4f}  R2={fq['r2']:.3f}+/-{fq['r2_std']:.3f}  "
          f"mean_signed_err={fq['mean_signed_err']:+.4f} over-pred={fq['frac_over']*100:.1f}%")
    print("\n=== conformalized classical screen ===")
    for r in out["conformalized"]:
        print(f"  cov={r['coverage_target']:.2f} q_hat={r['q_hat']:.5f}+/-{r['q_hat_std']:.5f} "
              f"esc={r['escalation']*100:5.1f}% cov_emp={r['coverage_emp']*100:5.1f}% "
              f"missed={r['missed_viol']*100:5.2f}% speedup={r['net_speedup']:.2f}x")
    print("\n=== Q-limit analysis (weakest-bus base type x error sign) ===")
    for t, d in out["qlimit_analysis"]["by_weakest_bus_type"].items():
        print(f"  weakest={t:3s} n={d['n']:6d} over={d['n_over']:6d} under={d['n_under']:6d} "
              f"({d['frac_over']*100:5.1f}% over) MAE={d['mae']:.4f} "
              f"signed={d['mean_signed_err']:+.4f}")


if __name__ == "__main__":
    main()
