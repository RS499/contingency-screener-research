import os, json, sys, platform, subprocess
from importlib import metadata

SOLVER = dict(enforce_q_lims=True, numba=True, init="dc", algorithm="nr")

TUNED = dict(stress="fixed", mult_lo=1.00, mult_hi=1.12)

SOLVE_TIME_PATH = "data/solve_time.json"

PACKAGES = ("pandapower", "numpy", "pandas", "scikit-learn", "pyarrow", "numba")


def pkg_version(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "not installed"


def numba_state():
    version = pkg_version("numba")
    available = version != "not installed"
    if available:
        return dict(available=True, version=version)
    return dict(available=False, version=None)


def cpu_brand():
    try:
        result = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                capture_output=True, text=True, timeout=5)
        brand = result.stdout.strip()
        if brand:
            return brand
        return "unknown"
    except Exception:
        return "unknown"


def hardware():
    return dict(machine=platform.machine(), processor=platform.processor(),
                system=platform.system(), release=platform.release(), cpu=cpu_brand())


def load_solve_time():
    if not os.path.exists(SOLVE_TIME_PATH):
        raise FileNotFoundError(
            f"{SOLVE_TIME_PATH} is missing. Run 'python feasibility/measure_solve.py' first "
            f"to measure and pin the per-case solve time.")
    with open(SOLVE_TIME_PATH) as f:
        return json.load(f)


def build_manifest():
    versions = {}
    for name in PACKAGES:
        versions[name] = pkg_version(name)
    out = dict(python=sys.version.split()[0], packages=versions,
               solver=SOLVER, numba=numba_state(), tuned_generator_settings=TUNED,
               hardware=hardware(), measurement=load_solve_time())
    return out


def manifest_path(results_path):
    root = os.path.splitext(results_path)[0]
    return root + ".manifest.json"


def write_with_manifest(results_path, out):
    with open(results_path, "w") as f:
        json.dump(out, f, indent=2)
    with open(manifest_path(results_path), "w") as f:
        json.dump(build_manifest(), f, indent=2)
