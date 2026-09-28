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

# Conditional strip share P(0.94 <= min_vm < 0.945 | min_vm >= 0.94) recounted from row counts,
# for the ungated build (data/unconditioned_base.parquet) and the committed N-0-gated build
# (data/dataset.parquet), with the unconditional strip share and violation rate beside it.
#
# usage: .venv/bin/python scripts/sts_dataset_facts_c.py OUT_DIR [REF_DIR]

BUILDS = [("ungated", "data/unconditioned_base.parquet"),
          ("committed_gated", "data/dataset.parquet")]
UNCOND_JSON = "data/unconditioned_base.json"
SCRIPT = "scripts/sts_dataset_facts_c.py"
OUT_NAME = "sts_dataset_facts_c.json"
LIMIT = 0.94
STRIP_HI = 0.945


def counts(path):
    df = pd.read_parquet(path, columns=["outaged_type", "converged", "min_vm"])
    n1 = df[(df["outaged_type"] != "none") & (df["converged"])]
    y = n1["min_vm"].to_numpy(np.float64)
    n = len(y)
    n_nonfinite = int((~np.isfinite(y)).sum())
    n_viol = int((y < LIMIT).sum())
    n_at_or_above = int((y >= LIMIT).sum())
    n_strip = int(((y >= LIMIT) & (y < STRIP_HI)).sum())
    return {
        "source": path,
        "population": "converged N-1 rows (outaged_type != 'none' and converged)",
        "n_rows": n,
        "n_nonfinite_min_vm": n_nonfinite,
        "violation_rate": {"numerator": n_viol, "denominator": n, "pct": 100.0 * n_viol / n},
        "strip_share_unconditional": {"numerator": n_strip, "denominator": n,
                                      "pct": 100.0 * n_strip / n},
        "strip_share_conditional_on_safe": {"numerator": n_strip, "denominator": n_at_or_above,
                                            "pct": 100.0 * n_strip / n_at_or_above},
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

    out = {
        "definition": f"conditional strip share = P({LIMIT} <= min_vm < {STRIP_HI} | min_vm >= {LIMIT}) "
                      f"= #strip rows / #rows with min_vm >= {LIMIT}, from row counts",
        "builds": {},
    }
    for name, path in BUILDS:
        out["builds"][name] = counts(path)
    with open(UNCOND_JSON) as f:
        uj = json.load(f)
    out["comparison_with_unconditioned_base_json"] = {
        "ungated_conditional_boundary_pct_in_json": uj["unconditioned"]["conditional_boundary_pct"],
        "committed_conditional_boundary_pct_in_json": uj["committed_gated"]["conditional_boundary_pct"],
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {out_path}")
    for name, path in BUILDS:
        c = out["builds"][name]["strip_share_conditional_on_safe"]
        print(f"  {name}: {c['numerator']} / {c['denominator']} = {c['pct']:.4f}%")

    inputs = [{"path": UNCOND_JSON, "sha256": cm.content_hash(UNCOND_JSON)}]
    for name, path in BUILDS:
        inputs.append({"path": path, "sha256": cm.content_hash(path)})
    settings = {
        "task": "conditional strip-share recount from row counts",
        "generating_script": SCRIPT,
        "regeneration_argv": [SCRIPT, "data"],
        "inputs": inputs,
        "outputs": [{"path": out_path, "sha256": cm.content_hash(out_path),
                     "repro": repro(out_path, ref_dir)}],
        "limit": LIMIT, "strip_hi": STRIP_HI,
        "rounding_note": "data/unconditioned_base.json conditional_boundary_pct (ungated 65.5823, "
                         "committed 68.9045) was computed by scripts/uncond_analysis.py "
                         "conditional_boundary() as 100 * b / (100 - v) from the 2-dp-rounded "
                         "percentages boundary_0p94_to_0p945_pct and violation_rate_pct. The values "
                         "here are exact row-count ratios and supersede them for printing.",
        "no_new_solves": "counted from the two parquet builds; no fit or AC solve",
    }
    man = cm.build_manifest(out_path, out, settings)
    with open(mf.manifest_path(out_path), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {mf.manifest_path(out_path)}")


if __name__ == "__main__":
    main()
