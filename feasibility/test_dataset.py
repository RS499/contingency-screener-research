import sys
import numpy as np
import pandas as pd

VMIN = 0.94
COLLAPSE_FLOOR = 0.80

FEATURE_PREFIXES = ("pload_", "qload_", "genvm_", "genp_", "genqmin_", "genqmax_",
                    "genon_", "vm0_")
LEAK_SUBSTRINGS = ("res_", "post", "_pc", "result", "min_vm", "max_vm",
                   "argmin", "violation", "straddle")


def load(path):
    return pd.read_parquet(path)


def test_T1_n0_feasible(df):
    n0 = df[df.outaged_type == "none"]
    bad = n0[(~n0.n0_converged) | (n0.n0_min_vm < VMIN)]
    assert len(bad) == 0, f"T1 FAIL: {len(bad)} accepted scenarios have infeasible/nonconv N-0 base"
    return f"T1 PASS: all {len(n0)} scenarios have feasible N-0 base (min_vm >= {VMIN})"


def test_T2_violation_band(df):
    n1 = df[(df.outaged_type != "none") & (df.converged)]
    vr = n1.violation.mean() * 100
    assert 10.0 <= vr <= 60.0, f"T2 FAIL: N-1 violation rate {vr:.1f}% outside [10, 60]%"
    return f"T2 PASS: N-1 violation rate {vr:.1f}% within [10, 60]%"


def test_T3_straddle_floor(df):
    n1 = df[(df.outaged_type != "none") & (df.converged)]
    ss = n1.straddle.mean() * 100
    assert ss >= 3.0, f"T3 FAIL: straddle share {ss:.1f}% below 3% floor"
    return f"T3 PASS: straddle share {ss:.1f}% >= 3%"


def test_T4_collapse_bounded(df):
    n1 = df[(df.outaged_type != "none") & (df.converged)]
    cs = (n1.min_vm < COLLAPSE_FLOOR).mean() * 100
    assert cs <= 0.5, f"T4 FAIL: {cs:.2f}% of converged N-1 below collapse floor {COLLAPSE_FLOOR} (>0.5%)"
    return f"T4 PASS: {cs:.2f}% below collapse floor {COLLAPSE_FLOOR} (<= 0.5%)"


def test_T5_float64_targets(df):
    need64 = ["min_vm", "max_vm", "n0_min_vm"] + [c for c in df.columns if c.startswith("vm0_")]
    bad = [c for c in need64 if c in df.columns and df[c].dtype != np.float64]
    assert not bad, f"T5 FAIL: these must be float64 but aren't: {bad[:8]}{'...' if len(bad)>8 else ''}"
    return f"T5 PASS: min_vm/max_vm/n0_min_vm/vm0_* all float64 ({len(need64)} cols)"


def test_T6_no_leakage(df):
    feats = [c for c in df.columns if c.startswith(FEATURE_PREFIXES)]
    leaked = [c for c in feats if any(s in c.lower() for s in LEAK_SUBSTRINGS if s not in ("vm0_",))]
    assert not leaked, f"T6 FAIL: feature columns look post-contingency: {leaked[:8]}"
    return f"T6 PASS: {len(feats)} feature columns, none carry post-contingency data"


def test_T7_no_boundary_snap(df):
    conv = df[df.converged]
    snap_viol = conv[(conv.min_vm == VMIN) & (conv.violation)]
    label_ok = conv[(conv.violation) & (conv.min_vm >= VMIN)]
    assert len(snap_viol) == 0, f"T7 FAIL: {len(snap_viol)} cases at exactly 0.94 labeled violation (snap defect)"
    assert len(label_ok) == 0, f"T7 FAIL: {len(label_ok)} violation-labeled cases have min_vm >= 0.94"
    return "T7 PASS: no boundary-snap; violation label consistent with min_vm < 0.94"


def test_T8_no_allnan_n0(df):
    vm0 = [c for c in df.columns if c.startswith("vm0_")]
    conv = df[df.converged]
    allnan = conv[conv[vm0].isna().all(axis=1)]
    assert len(allnan) == 0, f"T8 FAIL: {len(allnan)} converged rows have all-NaN N-0 features"
    return f"T8 PASS: no converged row with all-NaN N-0 features"


def test_T9_no_min_vm_spike(df):
    n1 = df[(df.outaged_type != "none") & (df.converged)]
    vals, counts = np.unique(np.round(n1.min_vm.to_numpy(), 9), return_counts=True)
    order = np.argsort(counts)[::-1]
    top = [(float(vals[i]), round(100.0 * counts[i] / len(n1), 2)) for i in order[:3]]
    top_share = 100.0 * counts[order[0]] / len(n1)
    assert top_share <= 1.0, (
        f"T9 FAIL: min_vm={vals[order[0]]:.6f} is {top_share:.2f}% of converged N-1 rows (>1%); "
        f"a point mass at one value signals a setpoint clip (notes/artifact-clip-0.94.md); top3={top}")
    return f"T9 PASS: no single min_vm value exceeds 1% of converged N-1 rows; top3 (value, share%)={top}"


TESTS = [test_T1_n0_feasible, test_T2_violation_band, test_T3_straddle_floor,
         test_T4_collapse_bounded, test_T5_float64_targets, test_T6_no_leakage,
         test_T7_no_boundary_snap, test_T8_no_allnan_n0, test_T9_no_min_vm_spike]


def run_all(path):
    df = load(path)
    print(f"dataset: {path}  rows={len(df)} scenarios={df.scenario_id.nunique()} cols={df.shape[1]}")
    fails = 0
    for t in TESTS:
        try:
            print("  " + t(df))
        except AssertionError as e:
            print("  " + str(e)); fails += 1
    print(f"\n{'ALL TESTS PASS' if fails == 0 else f'{fails} TEST(S) FAILED'}")
    return fails


def _default_path():
    return "data/dataset.parquet"

def test_dataset_passes_all_guards():
    import os
    p = os.environ.get("DATASET_PATH", _default_path())
    assert run_all(p) == 0


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else _default_path()
    sys.exit(1 if run_all(path) else 0)
