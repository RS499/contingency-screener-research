"""Read-only: seed-mean +- population std of the three committed drift tests at 0.90 target.
Sources: data/drift_n0_stratum_long.parquet (2C), data/drift_element_type_long.parquet (2D),
data/drift_loading_tilt_long.parquet (2E). Writes nothing.

Usage: .venv/bin/python scratch/drift_summary.py
"""

import numpy as np
import pandas as pd


def summarize(df, keys):
    sub = df[np.isclose(df["coverage_target"], 0.9)]
    rows = []
    for name, grp in sub.groupby(keys):
        rows.append({"cell": name, "n_seeds": grp["seed"].nunique(),
                     "cov": f"{100*grp['coverage_emp'].mean():.1f}+-{100*grp['coverage_emp'].std(ddof=0):.1f}",
                     "esc": f"{100*grp['escalation'].mean():.1f}+-{100*grp['escalation'].std(ddof=0):.1f}",
                     "miss": f"{100*grp['missed_viol'].mean():.2f}+-{100*grp['missed_viol'].std(ddof=0):.2f}"})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("2C  N-0 stratum (median split on n0_min_vm)")
    print(summarize(pd.read_parquet("data/drift_n0_stratum_long.parquet"),
                    ["model", "cal_stratum", "test_stratum"]).to_string(index=False))
    print("\n2D  element type (line vs trafo)")
    print(summarize(pd.read_parquet("data/drift_element_type_long.parquet"),
                    ["model", "cal_stratum", "test_stratum"]).to_string(index=False))
    print("\n2E  loading soft tilt (lambda = 3)")
    print(summarize(pd.read_parquet("data/drift_loading_tilt_long.parquet"),
                    ["model", "cell"]).to_string(index=False))
