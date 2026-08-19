import sys, os
import numpy as np

import make_splits as ms
import surrogate as sg
import gate_eval as ge

DEFAULT_PATH = "data/dataset.parquet"
SEED = 0
COVERAGE = 0.90
LIMIT = 0.94
MIN_CAL_SCENARIOS = 200


def build_context(path, seed):
    df, feat_cols = ms.load_dataset(path)
    X, y, groups, branch_cols = ms.build_design_matrix(df, feat_cols)
    splits = ms.make_splits(groups, seed)
    kept = ms.select_features(X, splits["train"])
    Xk = X[kept]

    Xtr = Xk.iloc[splits["train"]].to_numpy(np.float32)
    Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
    Xte = Xk.iloc[splits["test"]].to_numpy(np.float32)
    ytr = y[splits["train"]]
    yca = y[splits["cal"]]
    yte = y[splits["test"]]

    fitted = sg.train_ridge(Xtr, ytr)
    q_hat = ge.calibrate_qhat(sg.predict(fitted, Xca), yca, COVERAGE)
    gate = ge.run_gate(sg.predict(fitted, Xte), q_hat, LIMIT)
    coverage = float((yte >= gate["lower"]).mean())

    ctx = dict(path=path, seed=seed, X=X, y=y, groups=groups,
               splits=splits, kept=kept, q_hat=q_hat, coverage=coverage)
    return ctx


def test_T1_no_scenario_overlap(ctx):
    g = ctx["groups"]
    s_tr = set(g[ctx["splits"]["train"]])
    s_ca = set(g[ctx["splits"]["cal"]])
    s_te = set(g[ctx["splits"]["test"]])
    ov = (s_tr & s_ca) | (s_tr & s_te) | (s_ca & s_te)
    assert len(ov) == 0, f"T1 FAIL: {len(ov)} scenario_ids appear in more than one split"


def test_T2_calibration_size(ctx):
    n_cal = len(set(ctx["groups"][ctx["splits"]["cal"]]))
    assert n_cal >= MIN_CAL_SCENARIOS, \
        f"T2 FAIL: calibration set has {n_cal} scenarios, need >= {MIN_CAL_SCENARIOS}"


def test_T3_coverage_in_band(ctx):
    c = ctx["coverage"]
    assert 0.87 <= c <= 0.93, \
        f"T3 FAIL: empirical coverage {c*100:.1f}% outside [87, 93]% (target 90%)"


def test_T4_band_one_sided(ctx):
    q = ctx["q_hat"]
    assert q > 0, f"T4 FAIL: q_hat={q:.5f} is not positive"
    gate = ge.run_gate(np.array([2.0]), q, LIMIT)
    assert bool(gate["certify"][0]) and not bool(gate["flag"][0]), \
        "T4 FAIL: a prediction far above the limit was not certified (band is not one-sided)"


def test_T5_no_row_leakage(ctx):
    idx_all = np.concatenate([ctx["splits"]["train"], ctx["splits"]["cal"], ctx["splits"]["test"]])
    n_unique = len(set(idx_all.tolist()))
    assert n_unique == len(idx_all), \
        f"T5 FAIL: {len(idx_all) - n_unique} row indices appear in more than one split"


def test_T6_reproducible(ctx):
    splits2 = ms.make_splits(ctx["groups"], ctx["seed"])
    for name in ("train", "cal", "test"):
        a = np.sort(np.unique(ctx["groups"][ctx["splits"][name]]))
        b = np.sort(np.unique(ctx["groups"][splits2[name]]))
        assert np.array_equal(a, b), f"T6 FAIL: split '{name}' scenario ids differ on rerun"
    Xk = ctx["X"][ctx["kept"]]
    fitted = sg.train_ridge(Xk.iloc[splits2["train"]].to_numpy(np.float32), ctx["y"][splits2["train"]])
    q2 = ge.calibrate_qhat(sg.predict(fitted, Xk.iloc[splits2["cal"]].to_numpy(np.float32)),
                           ctx["y"][splits2["cal"]], COVERAGE)
    assert abs(q2 - ctx["q_hat"]) < 1e-9, f"T6 FAIL: q_hat not reproduced ({q2} vs {ctx['q_hat']})"


TESTS = [test_T1_no_scenario_overlap, test_T2_calibration_size, test_T3_coverage_in_band,
         test_T4_band_one_sided, test_T5_no_row_leakage, test_T6_reproducible]


def run_all(path):
    print(f"screener pipeline guards on {path}")
    ctx = build_context(path, SEED)
    n_fail = 0
    for t in TESTS:
        try:
            t(ctx)
            print(f"  {t.__name__} PASS")
        except AssertionError as e:
            print("  " + str(e))
            n_fail += 1
    print("ALL TESTS PASS" if n_fail == 0 else f"{n_fail} TEST(S) FAILED")
    return n_fail


def test_pipeline_passes_all_guards():
    p = os.environ.get("DATASET_PATH", DEFAULT_PATH)
    assert run_all(p) == 0


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    sys.exit(1 if run_all(path) else 0)
