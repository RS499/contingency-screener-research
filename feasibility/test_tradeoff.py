import sys, os, json
import numpy as np

DEFAULT_PATH = "data/tradeoff_curve.json"
COV_TOL = 0.03
MODELS = ("persistence", "ridge", "histgb")


def load(path):
    with open(path) as f:
        return json.load(f)


def test_T1_coverage_tracks_target(d):
    worst = 0.0
    for r in d["records"]:
        worst = max(worst, abs(r["coverage_emp"] - r["coverage_target"]))
    assert worst <= COV_TOL, f"T1 FAIL: max |empirical - target| coverage = {worst:.3f} > {COV_TOL}"
    return f"T1 PASS: empirical coverage tracks target within {worst:.3f} (<= {COV_TOL})"


def test_T2_qhat_monotone(d):
    for model in MODELS:
        rows = sorted([r for r in d["records"] if r["model"] == model],
                      key=lambda r: r["coverage_target"])
        q = [r["q_hat"] for r in rows]
        for i in range(1, len(q)):
            assert q[i] >= q[i - 1] - 1e-9, \
                f"T2 FAIL: {model} q_hat rose as coverage fell (level {rows[i]['coverage_target']})"
    return "T2 PASS: mean q_hat monotonically non-increasing as target coverage decreases (all models)"


def test_T3_quantile_index_valid(d):
    n = int(d["n_cal"])
    k = int(np.ceil((n + 1) * 0.99))
    assert k <= n, f"T3 FAIL: ceil((n_cal+1)*0.99)={k} > n_cal={n} (quantile index would clip)"
    return f"T3 PASS: n_cal={n}, ceil((n_cal+1)*0.99)={k} <= {n} (index valid at coverage 0.99)"


TESTS = [test_T1_coverage_tracks_target, test_T2_qhat_monotone, test_T3_quantile_index_valid]


def run_all(path):
    print(f"tradeoff guards on {path}")
    d = load(path)
    n_fail = 0
    for t in TESTS:
        try:
            print("  " + t(d))
        except AssertionError as e:
            print("  " + str(e)); n_fail += 1
    print("ALL TESTS PASS" if n_fail == 0 else f"{n_fail} TEST(S) FAILED")
    return n_fail


def test_tradeoff_passes_all_guards():
    p = os.environ.get("TRADEOFF_PATH", DEFAULT_PATH)
    assert run_all(p) == 0


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    sys.exit(1 if run_all(path) else 0)
