import sys, os, json
import numpy as np

DEFAULT_PATH = "data/tradeoff_curve.json"
SPLITS_PATH = "data/splits.json"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COV_TOL = 0.03

# Families the promoted curve must carry. persistence is an M1-only baseline and is
# absent from tradeoff_curve_v2.json, so it is NOT required here: T2 previously
# iterated a fixed tuple that included it, matched zero rows on the M2 curve, and
# passed vacuously. T2 now derives the model list from the artifact and asserts only
# that the promoted families are present.
REQUIRED_MODELS = ("ridge", "histgb")


def load(path):
    with open(path) as f:
        return json.load(f)


def test_T1_coverage_tracks_target(d):
    worst = 0.0
    for r in d["records"]:
        worst = max(worst, abs(r["coverage_emp"] - r["coverage_target"]))
    assert worst <= COV_TOL, f"T1 FAIL: max |empirical - target| coverage = {worst:.3f} > {COV_TOL}"


def test_T2_qhat_monotone(d):
    present = sorted({r["model"] for r in d["records"]})
    for model in REQUIRED_MODELS:
        assert model in present, \
            f"T2 FAIL: promoted model {model!r} absent from the curve; present={present}"
    for model in present:
        rows = sorted([r for r in d["records"] if r["model"] == model],
                      key=lambda r: r["coverage_target"])
        assert len(rows) >= 2, \
            f"T2 FAIL: {model} has {len(rows)} record(s); monotonicity is untestable"
        q = [r["q_hat"] for r in rows]
        for i in range(1, len(q)):
            assert q[i] >= q[i - 1] - 1e-9, \
                f"T2 FAIL: {model} q_hat rose as coverage fell (level {rows[i]['coverage_target']})"


def resolve_n_cal(d):
    if "n_cal" in d:
        return int(d["n_cal"]), "curve n_cal"
    with open(os.path.join(REPO_ROOT, SPLITS_PATH)) as f:
        splits = json.load(f)
    return int(splits["n_rows"]["cal"]), f"{SPLITS_PATH} n_rows.cal"


def test_T3_quantile_index_valid(d):
    n, source = resolve_n_cal(d)
    k = int(np.ceil((n + 1) * 0.99))
    assert k <= n, \
        f"T3 FAIL: ceil((n_cal+1)*0.99)={k} > n_cal={n} from {source} (quantile index would clip)"


TESTS = [test_T1_coverage_tracks_target, test_T2_qhat_monotone, test_T3_quantile_index_valid]


def run_all(path):
    print(f"tradeoff guards on {path}")
    d = load(path)
    n_fail = 0
    for t in TESTS:
        try:
            t(d)
            print(f"  {t.__name__} PASS")
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
