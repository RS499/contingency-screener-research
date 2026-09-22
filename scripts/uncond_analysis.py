# Unconditioned-build analysis: is the boundary mass a property of case118, or an
# artifact of the N-0 acceptance gate? Reads the ungated parquet, recomputes the
# committed pipeline's own dataset_facts on BOTH datasets (two-key), and writes
# data/unconditioned_base.json.
import sys, os, json, hashlib, platform, subprocess
import numpy as np
import pandas as pd

sys.path.insert(0, "feasibility")
from freeze_poster_numbers import dataset_facts   # the committed definition, reused verbatim

UNCOND = "data/unconditioned_base.parquet"
COMMITTED = "data/dataset.parquet"
OUT = "data/unconditioned_base.json"
LIMIT = 0.94
STRIP_HI = 0.945


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def n0_stats(path):
    df = pd.read_parquet(path, columns=["scenario_id", "outaged_type", "n0_min_vm", "n0_converged"])
    base = df[df["outaged_type"] == "none"]
    v = base["n0_min_vm"].to_numpy()
    finite = v[np.isfinite(v)]
    return dict(
        n_scenarios=int(len(base)),
        n0_converged=int(base["n0_converged"].sum()),
        n0_nonconverged=int((~base["n0_converged"]).sum()),
        n0_min_vm_min=round(float(finite.min()), 6),
        n0_min_vm_median=round(float(np.median(finite)), 6),
        n0_min_vm_max=round(float(finite.max()), 6),
        n0_share_below_0p94_pct=round(100.0 * float(np.mean(finite < LIMIT)), 4),
        n0_nonfinite=int(len(v) - len(finite)),
    )


def largest_bin(path):
    df = pd.read_parquet(path, columns=["min_vm", "converged", "outaged_type"])
    n1 = df[(df["outaged_type"] != "none") & (df["converged"])]
    y = n1["min_vm"].to_numpy()
    lo, hi = 0.80, 1.10
    edges = np.arange(lo, hi + 0.001, 0.001)
    counts, _ = np.histogram(y, bins=edges)
    i = int(np.argmax(counts))
    return dict(
        largest_bin_lo=round(float(edges[i]), 4),
        largest_bin_hi=round(float(edges[i + 1]), 4),
        largest_bin_share_pct=round(100.0 * float(counts[i]) / len(y), 4),
        n1_rows=int(len(y)),
    )


def conditional_boundary(facts):
    # P(0.94 <= min_vm < 0.945 | min_vm >= 0.94), the pre-registered decisive quantity
    b = facts["boundary_0p94_to_0p945_pct"]
    v = facts["violation_rate_pct"]
    return round(100.0 * b / (100.0 - v), 4) if v < 100.0 else float("nan")


def main():
    out = {}
    out["definition_source"] = "feasibility/freeze_poster_numbers.py:dataset_facts (imported, not reimplemented)"
    out["limit"] = LIMIT
    out["strip_hi"] = STRIP_HI

    for label, path in [("committed_gated", COMMITTED), ("unconditioned", UNCOND)]:
        if not os.path.exists(path):
            out[label] = {"error": f"missing {path}"}
            continue
        facts = dataset_facts(path)
        facts["source"] = path   # dataset_facts hardcodes data/dataset.parquet; record the file actually read
        facts["conditional_boundary_pct"] = conditional_boundary(facts)
        facts.update(n0_stats(path))
        facts.update(largest_bin(path))
        facts["input_sha256"] = sha256_of(path)
        out[label] = facts

    # two-key check: the committed numbers must reproduce from the committed parquet
    _fz = json.load(open("data/frozen_poster_numbers.json"))
    frozen = _fz["dataset_facts"]
    c = out.get("committed_gated", {})
    out["two_key_check"] = dict(
        frozen_boundary_pct=frozen["boundary_0p94_to_0p945_pct"],
        recomputed_boundary_pct=c.get("boundary_0p94_to_0p945_pct"),
        boundary_matches=bool(abs(frozen["boundary_0p94_to_0p945_pct"] - c.get("boundary_0p94_to_0p945_pct", -1)) < 0.01),
        frozen_violation_pct=frozen["violation_rate_pct"],
        recomputed_violation_pct=c.get("violation_rate_pct"),
        violation_matches=bool(abs(frozen["violation_rate_pct"] - c.get("violation_rate_pct", -1)) < 0.01),
    )

    out["case30_reference"] = dict(
        case30_thermal_boundary_pct=7.0862,
        case30_voltage_boundary_pct=20.0146,
        source="data/case30_thermal/case30_thermal_frozen.json, data/case30_frozen.json",
    )
    out["committed_n0_gate_pass_rate_pct"] = _fz.get("n0_gate_pass_rate_pct")

    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)

    u = out["unconditioned"]; g = out["committed_gated"]
    print(f"two-key: boundary {out['two_key_check']['boundary_matches']} violation {out['two_key_check']['violation_matches']}")
    print(f"{'':<28}{'GATED':>12}{'UNGATED':>12}")
    for k in ["boundary_0p94_to_0p945_pct", "violation_rate_pct", "conditional_boundary_pct",
              "largest_bin_share_pct", "n0_share_below_0p94_pct", "converged_n1_rows", "n_scenarios"]:
        print(f"{k:<28}{g.get(k, float('nan')):>12}{u.get(k, float('nan')):>12}")
    print(f"largest bin ungated: [{u['largest_bin_lo']}, {u['largest_bin_hi']})")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
