import os, time, argparse
import numpy as np

import make_splits as ms
import surrogate as sg
import gate_eval as ge
import manifest as mf

COVERAGE = 0.90
LIMIT = 0.94
MODELS = ("persistence", "train_mean", "ridge", "histgb")


def fit_model(kind, X_train, y_train, seed):
    if kind == "ridge":
        return sg.train_ridge(X_train, y_train)
    return sg.train_histgb(X_train, y_train, seed=seed)


def mae_r2(pred, ytrue):
    pred = np.asarray(pred, dtype=np.float64)
    ytrue = np.asarray(ytrue, dtype=np.float64)
    mae = float(np.mean(np.abs(pred - ytrue)))
    ss_res = float(np.sum((ytrue - pred) ** 2))
    ss_tot = float(np.sum((ytrue - ytrue.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return mae, r2


def evaluate_seed(X, y, n0, groups, seed, ms_solver, ms_surrogate_arg):
    splits = ms.make_splits(groups, seed)
    kept = ms.select_features(X, splits["train"])
    Xk = X[kept]
    Xtr = Xk.iloc[splits["train"]].to_numpy(np.float32)
    Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
    Xte = Xk.iloc[splits["test"]].to_numpy(np.float32)
    ytr, yca, yte = y[splits["train"]], y[splits["cal"]], y[splits["test"]]
    n0ca, n0te = n0[splits["cal"]], n0[splits["test"]]

    records = []
    for kind in MODELS:
        if kind == "persistence":
            pred_ca = sg.predict_persistence(n0ca)
            t0 = time.time(); pred_te = sg.predict_persistence(n0te); dt = time.time() - t0
        elif kind == "train_mean":
            pred_ca = sg.predict_mean(ytr, len(yca))
            t0 = time.time(); pred_te = sg.predict_mean(ytr, len(yte)); dt = time.time() - t0
        else:
            fitted = fit_model(kind, Xtr, ytr, seed)
            pred_ca = sg.predict(fitted, Xca)
            t0 = time.time(); pred_te = sg.predict(fitted, Xte); dt = time.time() - t0
        ms_surrogate = ms_surrogate_arg if ms_surrogate_arg is not None else dt / len(yte) * 1000.0

        q_hat = ge.calibrate_qhat(pred_ca, yca, COVERAGE)
        gate = ge.run_gate(pred_te, q_hat, LIMIT)
        s = ge.score(gate, yte, ms_surrogate, ms_solver, LIMIT)
        mae, r2 = mae_r2(pred_te, yte)
        s.update(seed=seed, model=kind, q_hat=q_hat, ms_surrogate=ms_surrogate, mae=mae, r2=r2)
        records.append(s)
        print(f"  seed={seed} {kind:12s} q_hat={q_hat:.5f} esc={s['escalation']*100:5.1f}% "
              f"cov={s['coverage']*100:5.1f}% missed={s['missed_viol']*100:5.2f}% "
              f"speedup={s['net_speedup']:.2f}x MAE={mae:.4f} R2={r2:.3f}")
    return records


def mean_std(values):
    a = np.asarray(values, dtype=np.float64)
    return float(a.mean()), float(a.std(ddof=0))


def print_table(records, ms_solver, ms_std):
    print("\ngate metrics + fit quality (mean +/- std across seeds; baselines first)")
    print(f"{'model':12s} {'esc%':>11s} {'cov%':>11s} {'missed%':>11s} "
          f"{'speedup':>11s} {'MAE':>8s} {'R2':>8s}")
    for kind in MODELS:
        rows = [r for r in records if r["model"] == kind]
        em, es = mean_std([r["escalation"] * 100 for r in rows])
        cm, cs = mean_std([r["coverage"] * 100 for r in rows])
        mm, mstd = mean_std([r["missed_viol"] * 100 for r in rows])
        sm, ss = mean_std([r["net_speedup"] for r in rows])
        am, _ = mean_std([r["mae"] for r in rows])
        rm, _ = mean_std([r["r2"] for r in rows])
        print(f"{kind:12s} {em:5.1f}+/-{es:3.1f} {cm:5.1f}+/-{cs:3.1f} {mm:5.2f}+/-{mstd:3.2f} "
              f"{sm:4.2f}x+/-{ss:4.2f} {am:8.4f} {rm:8.3f}")
    std_txt = f"solver std={ms_std:.2f} ms; " if ms_std is not None else ""
    print(f"* net_speedup PINNED: ms_solver={ms_solver:.2f} ms/case (MINIMUM over timed solves; "
          f"{std_txt}numba-on, enforce_q_lims=True); numba version + hardware in the manifest. "
          f"MAE/R2 on the TEST split.")
    print(f"  baselines: persistence = predict n0_min_vm (min of the vm0_* inputs); "
          f"train_mean = predict the train mean of min_vm.")


def write_metrics_json(records, path, ms_solver, n_seeds):
    clean = []
    for r in records:
        clean.append(dict(seed=int(r["seed"]), model=r["model"], q_hat=r["q_hat"],
                          escalation=r["escalation"], coverage=r["coverage"],
                          missed_viol=r["missed_viol"], net_speedup=r["net_speedup"],
                          mae=r["mae"], r2=r["r2"],
                          ms_surrogate=r["ms_surrogate"], n=r["n"],
                          n_escalated=r["n_escalated"], n_true_viol=r["n_true_viol"]))
    out = dict(n_seeds=n_seeds, coverage_target=COVERAGE, limit=LIMIT,
               ms_solver=ms_solver, speedup_note="pinned: ms_solver measured (numba-on, enforce_q_lims=True); config + hardware in the manifest",
               records=clean)
    mf.write_with_manifest(path, out)
    print(f"wrote {path} ({len(clean)} records)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="data/dataset.parquet")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--ms-solver", type=float, default=None,
                    help="per-case AC solve time in ms; default reads data/solve_time.json")
    ap.add_argument("--ms-surrogate", type=float, default=None,
                    help="override per-case surrogate ms; default measures it in-process")
    ap.add_argument("--out", default="data/screener_metrics.json")
    args = ap.parse_args()
    ms_std = None
    if args.ms_solver is None:
        solve = mf.load_solve_time()
        args.ms_solver = solve["ms_solver"]
        ms_std = solve.get("std_ms")

    t0 = time.time()
    df, feature_cols = ms.load_dataset(args.path)
    X, y, groups, _branch_cols = ms.build_design_matrix(df, feature_cols)
    n0 = df["n0_min_vm"].to_numpy(np.float64)

    all_records = []
    for seed in range(args.seeds):
        all_records.extend(evaluate_seed(X, y, n0, groups, seed, args.ms_solver, args.ms_surrogate))

    write_splits_json_ref(groups)

    print_table(all_records, args.ms_solver, ms_std)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    write_metrics_json(all_records, args.out, args.ms_solver, args.seeds)
    print(f"time_s={time.time() - t0:.1f} seeds={args.seeds} models={len(MODELS)}")


def write_splits_json_ref(groups):
    splits0 = ms.make_splits(groups, seed=0)
    ms.write_splits_json(splits0, groups, seed=0)


if __name__ == "__main__":
    main()
