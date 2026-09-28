import os
import sys
import json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, HERE)
import manifest as mf
import classical_manifest as cm

# Boundary-proximity facts printed in the STS report without a JSON key (ledger P-008):
# the [0.94, 0.945) strip share, the candidate readings of "most contingencies lie within
# 0.005 pu of the boundary", and the tallest 0.001 pu histogram bin.
#
# usage: .venv/bin/python scripts/sts_dataset_facts_b.py OUT_DIR [REF_DIR]

DATA = "data/dataset.parquet"
FROZEN_V2 = "data/frozen_poster_numbers_v2.json"
SCRIPT = "scripts/sts_dataset_facts_b.py"
OUT_NAME = "sts_dataset_facts_b.json"

LIMIT = 0.94
WIDTH = 0.005
# histogram edges exactly as feasibility/boundary_mass_hist.py builds them (Fig. 4)
LO, HI, BINW = 0.715, 0.965, 0.001


def load_min_vm():
    df = pd.read_parquet(DATA, columns=["min_vm", "converged", "outaged_type"])
    n1 = df[(df["outaged_type"] != "none") & (df["converged"])]
    return n1["min_vm"].to_numpy(np.float64)


def share(mask):
    return {"n_rows": int(mask.sum()), "share_pct": 100.0 * float(mask.mean())}


def proximity(v):
    out = {}
    one = share((v >= LIMIT) & (v < LIMIT + WIDTH))
    one["definition"] = f"{LIMIT} <= min_vm < {LIMIT + WIDTH} (one-sided, above the limit)"
    out["above_only"] = one
    two = share(np.abs(v - LIMIT) < WIDTH)
    two["definition"] = f"|min_vm - {LIMIT}| < {WIDTH} (two-sided, open)"
    out["two_sided_open"] = two
    two_c = share(np.abs(v - LIMIT) <= WIDTH)
    two_c["definition"] = f"|min_vm - {LIMIT}| <= {WIDTH} (two-sided, closed)"
    out["two_sided_closed"] = two_c
    below = share((v >= LIMIT - WIDTH) & (v < LIMIT))
    below["definition"] = f"{LIMIT - WIDTH:.3f} <= min_vm < {LIMIT} (one-sided, below the limit)"
    out["below_only"] = below
    return out


def tallest_bin(v):
    # the figure's own binning (float edges from np.arange), then an integer-index binning as a
    # check that the tallest bin does not depend on floating-point edge placement
    edges = np.arange(LO, HI + BINW / 2, BINW)
    counts, _ = np.histogram(v, bins=edges)
    i = int(np.argmax(counts))
    k = np.floor((v - LIMIT) / BINW + 1e-9).astype(np.int64)
    ks, kc = np.unique(k, return_counts=True)
    j = int(np.argmax(kc))
    return {
        "figure_binning": {
            "edges": f"np.arange({LO}, {HI} + {BINW}/2, {BINW}) as in feasibility/boundary_mass_hist.py",
            "bin_lo": float(edges[i]), "bin_hi": float(edges[i + 1]),
            "n_rows": int(counts[i]), "share_pct": 100.0 * float(counts[i]) / len(v),
            "rows_outside_histogram_range": int(len(v) - counts.sum()),
        },
        "integer_binning_check": {
            "rule": f"bin k = floor((min_vm - {LIMIT}) / {BINW}); bin k covers [{LIMIT} + k*{BINW}, {LIMIT} + (k+1)*{BINW})",
            "bin_lo": LIMIT + int(ks[j]) * BINW, "bin_hi": LIMIT + (int(ks[j]) + 1) * BINW,
            "n_rows": int(kc[j]), "share_pct": 100.0 * float(kc[j]) / len(v),
        },
    }


def repro(path, ref_dir):
    if ref_dir == "":
        return "not checked in this run"
    ref = os.path.join(ref_dir, os.path.basename(path))
    return {"compared_with": ref, "same_sha256": cm.content_hash(ref) == cm.content_hash(path)}


def main():
    out_dir = sys.argv[1]
    ref_dir = ""
    if len(sys.argv) > 2:
        ref_dir = sys.argv[2]
    out_path = os.path.join(out_dir, OUT_NAME)

    v = load_min_vm()
    with open(FROZEN_V2) as f:
        facts = json.load(f)["dataset_facts"]
    prox = proximity(v)
    out = {
        "source": DATA,
        "population": "converged N-1 rows (outaged_type != 'none' and converged)",
        "n_rows": int(len(v)),
        "strip_0p94_to_0p945": prox["above_only"],
        "strip_crosscheck_frozen_v2_pct": facts["boundary_0p94_to_0p945_pct"],
        "within_0p005_of_limit": prox,
        "tallest_0p001_bin": tallest_bin(v),
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {out_path}")

    settings = {
        "task": "boundary-proximity facts without a JSON key (ledger P-008)",
        "generating_script": SCRIPT,
        "regeneration_argv": [SCRIPT, "data"],
        "inputs": [{"path": DATA, "sha256": cm.content_hash(DATA)},
                   {"path": FROZEN_V2, "sha256": cm.content_hash(FROZEN_V2)}],
        "outputs": [{"path": out_path, "sha256": cm.content_hash(out_path),
                     "repro": repro(out_path, ref_dir)}],
        "limit": LIMIT, "width_pu": WIDTH, "hist_lo": LO, "hist_hi": HI, "bin_width": BINW,
        "no_new_solves": "computed from data/dataset.parquet; no fit or AC solve",
    }
    man = cm.build_manifest(out_path, out, settings)
    with open(mf.manifest_path(out_path), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {mf.manifest_path(out_path)}")


if __name__ == "__main__":
    main()
