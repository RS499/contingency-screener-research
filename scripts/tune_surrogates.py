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

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor

SEEDS = 5
LIMIT = 0.94
INNER_SEED_OFFSET = 1000
INNER_MISSED_CEIL = 0.01
N_RANDOM_HISTGB = 24
SEARCH_SEED = 0
COVERAGE_LEVELS = [round(0.70 + 0.01 * i, 2) for i in range(30)]

RIDGE_ALPHAS = list(np.logspace(-3, 4, 15))
HISTGB_LR = [0.03, 0.05, 0.08, 0.1, 0.2]
HISTGB_MAX_ITER = [100, 300, 600, 1000]
HISTGB_LEAVES = [31, 63, 127, 255]
HISTGB_MIN_LEAF = [20, 50, 200]
HISTGB_L2 = [0.0, 0.1, 1.0, 10.0]


def histgb_candidates():
    cands = []
    cands.append(dict(tag="committed", learning_rate=0.08, max_iter=300, max_depth=8,
                      max_leaf_nodes=31, min_samples_leaf=20, l2_regularization=0.0))
    cands.append(dict(tag="sklearn_default", learning_rate=0.1, max_iter=100, max_depth=None,
                      max_leaf_nodes=31, min_samples_leaf=20, l2_regularization=0.0))
    rng = np.random.RandomState(SEARCH_SEED)
    for i in range(N_RANDOM_HISTGB):
        cands.append(dict(tag=f"rand{i:02d}",
                          learning_rate=float(rng.choice(HISTGB_LR)),
                          max_iter=int(rng.choice(HISTGB_MAX_ITER)),
                          max_depth=None,
                          max_leaf_nodes=int(rng.choice(HISTGB_LEAVES)),
                          min_samples_leaf=int(rng.choice(HISTGB_MIN_LEAF)),
                          l2_regularization=float(rng.choice(HISTGB_L2))))
    return cands


def ridge_candidates():
    cands = []
    for a in RIDGE_ALPHAS:
        cands.append(dict(tag=f"alpha{a:.4g}", alpha=float(a)))
    return cands


def fit_ridge(cfg, X, y):
    scaler = StandardScaler().fit(X)
    model = Ridge(alpha=cfg["alpha"]).fit(scaler.transform(X), y)
    return dict(kind="ridge", scaler=scaler, model=model)


def fit_histgb(cfg, X, y, seed):
    model = HistGradientBoostingRegressor(
        learning_rate=cfg["learning_rate"], max_iter=cfg["max_iter"],
        max_depth=cfg["max_depth"], max_leaf_nodes=cfg["max_leaf_nodes"],
        min_samples_leaf=cfg["min_samples_leaf"],
        l2_regularization=cfg["l2_regularization"], random_state=seed).fit(X, y)
    return dict(kind="histgb", model=model)


def fit_one(family, cfg, X, y, seed):
    if family == "ridge":
        return fit_ridge(cfg, X, y)
    return fit_histgb(cfg, X, y, seed)


def predict(fitted, X):
    if fitted["kind"] == "ridge":
        return fitted["model"].predict(fitted["scaler"].transform(X))
    return fitted["model"].predict(X)


def mae_r2(pred, ytrue):
    pred = np.asarray(pred, dtype=np.float64)
    ytrue = np.asarray(ytrue, dtype=np.float64)
    mae = float(np.mean(np.abs(pred - ytrue)))
    ss_res = float(np.sum((ytrue - pred) ** 2))
    ss_tot = float(np.sum((ytrue - ytrue.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return mae, r2


def gate_aware_score(pred_cal, y_cal, pred_score, y_score, ms_solver):
    best_avoided = 0.0
    best_cov = None
    for cov in COVERAGE_LEVELS:
        q_hat = ge.calibrate_qhat(pred_cal, y_cal, cov)
        gate = ge.run_gate(pred_score, q_hat, LIMIT)
        s = ge.score(gate, y_score, 1e-6, ms_solver, LIMIT)
        if s["missed_viol"] <= INNER_MISSED_CEIL:
            avoided = 1.0 - s["escalation"]
            if avoided > best_avoided:
                best_avoided = avoided
                best_cov = cov
    return best_avoided, best_cov


def select_best(rows):
    m1 = rows[0]
    for r in rows:
        if r["inner_mae"] < m1["inner_mae"]:
            m1 = r
    m2 = rows[0]
    for r in rows:
        better = r["inner_avoided"] > m2["inner_avoided"]
        tied = r["inner_avoided"] == m2["inner_avoided"] and r["inner_mae"] < m2["inner_mae"]
        if better or tied:
            m2 = r
    return m1["tag"], m2["tag"]


def search_one_family(family, cands, Xfit, yfit, Xic, yic, Xis, yis, seed, ms_solver):
    rows = []
    for cfg in cands:
        t0 = time.time()
        fitted = fit_one(family, cfg, Xfit, yfit, seed)
        p_ic = predict(fitted, Xic)
        p_is = predict(fitted, Xis)
        mae, r2 = mae_r2(p_is, yis)
        avoided, cov_at = gate_aware_score(p_ic, yic, p_is, yis, ms_solver)
        n_iter = None
        if family == "histgb":
            n_iter = int(fitted["model"].n_iter_)
        rows.append(dict(family=family, seed=seed, tag=cfg["tag"], config=dict(cfg),
                         inner_mae=mae, inner_r2=r2, inner_avoided=avoided,
                         inner_cov_at=cov_at, n_iter=n_iter, fit_s=round(time.time() - t0, 2)))
        print(f"    {family:6s} seed={seed} {cfg['tag']:16s} MAE={mae:.5f} R2={r2:.4f} "
              f"avoided@<=1%={avoided*100:5.1f}% (cov {cov_at}) n_iter={n_iter} "
              f"{rows[-1]['fit_s']:.1f}s", flush=True)
    return rows


def find_config(cands, tag):
    for c in cands:
        if c["tag"] == tag:
            return c
    return None


def coverage_sweep(pred_cal, y_cal, pred_test, y_test, ms_surrogate, ms_solver):
    out = []
    for cov in COVERAGE_LEVELS:
        q_hat = ge.calibrate_qhat(pred_cal, y_cal, cov)
        gate = ge.run_gate(pred_test, q_hat, LIMIT)
        s = ge.score(gate, y_test, ms_surrogate, ms_solver, LIMIT)
        out.append(dict(coverage_target=cov, q_hat=q_hat, escalation=s["escalation"],
                        coverage_emp=s["coverage"], missed_viol=s["missed_viol"],
                        net_speedup=s["net_speedup"]))
    return out


def run_seed(X, y, groups, seed, ms_solver, r_cands, h_cands):
    print(f"\n=== seed {seed} ===", flush=True)
    splits = ms.make_splits(groups, seed)
    kept = ms.select_features(X, splits["train"])
    Xk = X[kept]

    tr = splits["train"]
    g_tr = groups[tr]
    inner = ms.make_splits(g_tr, INNER_SEED_OFFSET + seed)
    i_fit, i_cal, i_score = tr[inner["train"]], tr[inner["cal"]], tr[inner["test"]]
    print(f"  inner split scenarios: fit={len(set(groups[i_fit]))} "
          f"inner_cal={len(set(groups[i_cal]))} inner_score={len(set(groups[i_score]))} "
          f"| rows {len(i_fit)}/{len(i_cal)}/{len(i_score)}", flush=True)

    Xfit = Xk.iloc[i_fit].to_numpy(np.float32)
    Xic = Xk.iloc[i_cal].to_numpy(np.float32)
    Xis = Xk.iloc[i_score].to_numpy(np.float32)
    yfit, yic, yis = y[i_fit], y[i_cal], y[i_score]

    search_rows = []
    selections = {}
    for family, cands in (("ridge", r_cands), ("histgb", h_cands)):
        rows = search_one_family(family, cands, Xfit, yfit, Xic, yic, Xis, yis, seed, ms_solver)
        search_rows.extend(rows)
        m1_tag, m2_tag = select_best(rows)
        selections[family] = dict(m1=m1_tag, m2=m2_tag)
        print(f"  -> {family}: M1 picks {m1_tag}, M2 picks {m2_tag}", flush=True)

    Xtr = Xk.iloc[splits["train"]].to_numpy(np.float32)
    Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
    Xte = Xk.iloc[splits["test"]].to_numpy(np.float32)
    ytr, yca, yte = y[splits["train"]], y[splits["cal"]], y[splits["test"]]

    test_rows = []
    refit_cache = {}
    for family, cands in (("ridge", r_cands), ("histgb", h_cands)):
        for metric in ("m1", "m2"):
            tag = selections[family][metric]
            cfg = find_config(cands, tag)
            key = f"{family}:{tag}"
            if key not in refit_cache:
                fitted = fit_one(family, cfg, Xtr, ytr, seed)
                p_ca = predict(fitted, Xca)
                t0 = time.time()
                p_te = predict(fitted, Xte)
                dt = time.time() - t0
                n_iter = int(fitted["model"].n_iter_) if family == "histgb" else None
                refit_cache[key] = dict(pred_cal=p_ca, pred_test=p_te,
                                        ms_surrogate=dt / len(yte) * 1000.0, n_iter=n_iter)
            c = refit_cache[key]
            mae, r2 = mae_r2(c["pred_test"], yte)
            q90 = ge.calibrate_qhat(c["pred_cal"], yca, 0.90)
            p_below = float(np.mean(c["pred_test"] < LIMIT))
            sweep = coverage_sweep(c["pred_cal"], yca, c["pred_test"], yte,
                                   c["ms_surrogate"], ms_solver)
            test_rows.append(dict(seed=seed, family=family, metric=metric, tag=tag,
                                  config=dict(cfg), mae=mae, r2=r2, q_hat_90=q90,
                                  p_pred_below_limit=p_below, n_iter=c["n_iter"],
                                  ms_surrogate=c["ms_surrogate"], n_test=int(len(yte)),
                                  sweep=sweep))
            print(f"  TEST {family:6s} {metric.upper()} {tag:16s} MAE={mae:.5f} R2={r2:.4f} "
                  f"q90={q90:.5f} P(pred<0.94)={p_below*100:.1f}% n_iter={c['n_iter']}", flush=True)
    return search_rows, test_rows, selections


def main():
    t0 = time.time()
    ms_solver = mf.load_solve_time()["ms_solver"]
    df, feature_cols = ms.load_dataset("data/dataset.parquet")
    X, y, groups, _b = ms.build_design_matrix(df, feature_cols)

    r_cands = ridge_candidates()
    h_cands = histgb_candidates()
    print(f"candidates: ridge={len(r_cands)} histgb={len(h_cands)} "
          f"({len(r_cands) + len(h_cands)} fits per seed x {SEEDS} seeds)", flush=True)

    all_search, all_test, all_sel = [], [], {}
    for seed in range(SEEDS):
        s_rows, t_rows, sel = run_seed(X, y, groups, seed, ms_solver, r_cands, h_cands)
        all_search.extend(s_rows)
        all_test.extend(t_rows)
        all_sel[str(seed)] = sel

    protocol = ("per seed: (1) outer GroupShuffleSplit on scenario_id -> train/cal/test; "
                "(2) inner GroupShuffleSplit of TRAIN ONLY (random_state=1000+seed) -> "
                "fit/inner_cal/inner_score; (3) every candidate fit on `fit`, scored on inner_score; "
                "(4) M1 = lowest MAE, M2 = max avoided subject to inner missed <= 1%; "
                "(5) REFIT on the FULL train split with the selected config; "
                "(6) calibrate q_hat on the untouched cal split; (7) evaluate on the untouched test "
                "split. cal and test are never read during the search.")

    search_out = dict(seeds=SEEDS, limit=LIMIT, inner_missed_ceiling=INNER_MISSED_CEIL,
                      inner_seed_offset=INNER_SEED_OFFSET, search_seed=SEARCH_SEED,
                      coverage_levels=COVERAGE_LEVELS, protocol=protocol,
                      ridge_alpha_grid=[float(a) for a in RIDGE_ALPHAS],
                      histgb_space=dict(learning_rate=HISTGB_LR, max_iter=HISTGB_MAX_ITER,
                                        max_leaf_nodes=HISTGB_LEAVES,
                                        min_samples_leaf=HISTGB_MIN_LEAF,
                                        l2_regularization=HISTGB_L2,
                                        sampler=f"{N_RANDOM_HISTGB} random draws, "
                                                f"np.random.RandomState({SEARCH_SEED}), fixed "
                                                f"candidate set across seeds; plus 2 pinned "
                                                f"candidates (committed, sklearn_default)"),
                      selections=all_sel, records=all_search)
    settings = dict(task="hyperparameter tuning: inner search", ms_solver=ms_solver,
                    split_purity="tuning confined to the 60% train split; cal and test untouched",
                    committed_note=("surrogate.py is NOT at sklearn defaults: alpha=10.0, "
                                    "max_iter=300, learning_rate=0.08, max_depth=8. The committed "
                                    "config is carried as pinned candidate 'committed' and "
                                    "sklearn's real defaults as 'sklearn_default'."))
    cm.write_with_manifest("data/tuning_search.json", search_out, settings)

    test_out = dict(seeds=SEEDS, limit=LIMIT, ms_solver=ms_solver,
                    ms_solver_basis="minimum over 400 timed solves (data/solve_time.json)",
                    coverage_levels=COVERAGE_LEVELS, protocol=protocol,
                    std_convention="population std (ddof=0) over the five held-out splits",
                    selections=all_sel, records=all_test)
    settings2 = dict(settings)
    settings2["task"] = "hyperparameter tuning: test-split evaluation of the tuned models"
    cm.write_with_manifest("data/tuned_metrics.json", test_out, settings2)

    print(f"\ntime_s={time.time() - t0:.1f}")


if __name__ == "__main__":
    main()
