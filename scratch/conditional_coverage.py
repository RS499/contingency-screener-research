"""Read-only: conditional-coverage views that already exist in data/ (no refit, no solve).

- per-ELEMENT coverage under the global quantile: data/mondrian_element_long.parquet
- per-N-0-stratum coverage: data/drift_n0_stratum_long.parquet
Writes nothing.

Usage: .venv/bin/python scratch/conditional_coverage.py
"""

import numpy as np
import pandas as pd

if __name__ == "__main__":
    me = pd.read_parquet("data/mondrian_element_long.parquet")
    print("mondrian_element_long calibration kinds:", me["calibration"].unique().tolist())
    print("targets:", sorted(me["target"].unique().tolist()))
    for cal in me["calibration"].unique():
        for model in ["ridge", "histgb"]:
            sub = me[(me["calibration"] == cal) & (me["model"] == model) & (np.isclose(me["target"], 0.9))]
            if len(sub) == 0:
                continue
            per_el = sub.groupby("element")["coverage_emp"].mean()
            print(f"  {cal:10s} {model:6s} @0.90: elements={len(per_el)}  "
                  f"share of elements below 0.85 = {100*(per_el < 0.85).mean():.1f}%  "
                  f"below 0.80 = {100*(per_el < 0.80).mean():.1f}%  min = {per_el.min():.3f}  "
                  f"p10 = {per_el.quantile(0.1):.3f}  median = {per_el.median():.3f}")

    ds = pd.read_parquet("data/drift_n0_stratum_long.parquet")
    print("\ndrift_n0_stratum_long 'test' strata:", ds["test"].unique().tolist())
    sub = ds[np.isclose(ds["coverage_target"], 0.9)]
    agg = sub.groupby(["model", "test"]).agg(cov=("coverage_emp", "mean"), cov_sd=("coverage_emp", "std"),
                                             esc=("escalation", "mean"), miss=("missed_viol", "mean"))
    print(agg.round(4).to_string())
