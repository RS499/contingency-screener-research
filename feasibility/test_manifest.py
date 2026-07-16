import os, sys, json

DATA_DIR = "data"
RESULTS_FILES = ("splits.json", "screener_metrics.json", "solve_time.json")
REQUIRED_KEYS = ("python", "packages", "solver", "numba", "tuned_generator_settings",
                 "hardware", "measurement")
REQUIRED_PACKAGES = ("pandapower", "numpy", "pandas", "scikit-learn")
REQUIRED_HARDWARE_KEYS = ("machine", "processor", "system", "release", "cpu")


def manifest_for(results_path):
    root = os.path.splitext(results_path)[0]
    return root + ".manifest.json"


def test_T1_manifest_exists(data_dir):
    missing = []
    for name in RESULTS_FILES:
        results_path = os.path.join(data_dir, name)
        if os.path.exists(results_path) and not os.path.exists(manifest_for(results_path)):
            missing.append(name)
    assert len(missing) == 0, f"T1 FAIL: results files written without a matching manifest: {missing}"
    return "T1 PASS: every results file has a matching manifest"


def test_T2_manifest_fields(data_dir):
    for name in RESULTS_FILES:
        manifest_path = manifest_for(os.path.join(data_dir, name))
        if not os.path.exists(manifest_path):
            continue
        m = json.load(open(manifest_path))
        for key in REQUIRED_KEYS:
            assert key in m, f"T2 FAIL: {name} manifest missing key '{key}'"
        assert m["solver"]["enforce_q_lims"] is True, \
            f"T2 FAIL: {name} manifest does not pin enforce_q_lims=True"
        for pkg in REQUIRED_PACKAGES:
            assert pkg in m["packages"], f"T2 FAIL: {name} manifest missing version for {pkg}"
        for hk in REQUIRED_HARDWARE_KEYS:
            assert hk in m["hardware"], f"T2 FAIL: {name} manifest missing hardware key '{hk}'"
    return "T2 PASS: manifests pin the solver config, package versions, and hardware"


def test_T3_ms_solver_single_source(data_dir):
    solve_path = os.path.join(data_dir, "solve_time.json")
    screener_path = os.path.join(data_dir, "screener_metrics.json")
    if not (os.path.exists(solve_path) and os.path.exists(screener_path)):
        return "T3 SKIP: solve_time.json or screener_metrics.json not present"
    measured = json.load(open(solve_path))["ms_solver"]
    used = json.load(open(screener_path))["ms_solver"]
    assert used == measured, \
        f"T3 FAIL: screener_metrics ms_solver {used} != measured {measured} - stale, re-run run_all.py"
    return f"T3 PASS: screener ms_solver matches the measured {measured} ms/case"


TESTS = [test_T1_manifest_exists, test_T2_manifest_fields, test_T3_ms_solver_single_source]


def run_all(data_dir):
    fails = 0
    for t in TESTS:
        try:
            print(t(data_dir))
        except AssertionError as e:
            print(e)
            fails += 1
    return fails


def test_manifest_passes_all_guards():
    d = os.environ.get("DATA_DIR", DATA_DIR)
    assert run_all(d) == 0


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else DATA_DIR
    sys.exit(1 if run_all(d) else 0)
