# Clip-artifact numbers cited in the STS report (Method, Dataset): the size of the
# 0.94 pu point mass in the FIRST (clip-era) dataset build, and the [0.94, 0.945)
# boundary mass before and after the fix. Recomputed from the archived clip-era
# parquet with the committed dataset_facts definition, and written to
# data/clip_artifact.json so the numbers live in a tracked file.
import sys, json, hashlib
import numpy as np
import pandas as pd

sys.path.insert(0, "feasibility")
from freeze_poster_numbers import dataset_facts   # the committed definition, reused verbatim

CLIP = "data/archive_clip/dataset.parquet"
FIXED = "data/dataset.parquet"
OUT = "data/clip_artifact.json"
LIMIT = 0.94


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def atom_detail(path):
    # which buses hold the minimum voltage inside the 0.94 atom, plus the exact-match count
    df = pd.read_parquet(path, columns=["min_vm", "converged", "outaged_type", "argmin_bus"])
    n1 = df[(df["outaged_type"] != "none") & (df["converged"])]
    y = n1["min_vm"].to_numpy()
    in_atom = np.abs(np.round(y, 9) - LIMIT) < 1e-9
    exact = y == LIMIT
    buses, counts = np.unique(n1["argmin_bus"].to_numpy()[in_atom], return_counts=True)
    order = np.argsort(counts)[::-1][:3]
    top = []
    for i in order:
        top.append(dict(bus_index=int(buses[i]), ieee_bus=int(buses[i]) + 1,
                        share_of_atom_pct=round(float(100.0 * counts[i] / in_atom.sum()), 2)))
    return dict(atom_rows=int(in_atom.sum()),
                exact_0p94_rows=int(exact.sum()),
                exact_0p94_pct=round(100.0 * float(exact.mean()), 2),
                atom_top_buses=top)


def main():
    out = {}
    out["definition_source"] = "feasibility/freeze_poster_numbers.py:dataset_facts (imported, not reimplemented)"
    out["atom_definition"] = ("share of converged N-1 rows whose min_vm, rounded to 9 decimals, equals 0.94 "
                              "(merges the solver-rounding bit patterns around 0.94); dataset_facts.clip_atom_share_pct")
    out["boundary_definition"] = "share of converged N-1 rows with 0.94 <= min_vm < 0.945; dataset_facts.boundary_0p94_to_0p945_pct"

    for label, path in [("clip_era", CLIP), ("fixed_v2", FIXED)]:
        facts = dataset_facts(path)
        facts["source"] = path   # dataset_facts hardcodes data/dataset.parquet; record the file actually read
        facts.update(atom_detail(path))
        facts["input_sha256"] = sha256_of(path)
        out[label] = facts

    c = out["clip_era"]
    f = out["fixed_v2"]
    out["cited_in_sts"] = dict(
        clip_atom_pct=c["clip_atom_share_pct"],
        boundary_before_fix_pct=c["boundary_0p94_to_0p945_pct"],
        boundary_after_fix_pct=f["boundary_0p94_to_0p945_pct"],
    )

    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)

    print(f"{'':<30}{'CLIP-ERA':>12}{'FIXED v2':>12}")
    for k in ["clip_atom_share_pct", "exact_0p94_pct", "boundary_0p94_to_0p945_pct",
              "violation_rate_pct", "converged_n1_rows"]:
        print(f"{k:<30}{c[k]:>12}{f[k]:>12}")
    print(f"clip-era atom top buses: {c['atom_top_buses']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
