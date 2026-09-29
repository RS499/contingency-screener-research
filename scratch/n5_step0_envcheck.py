import os
import sys
import json
import time
import hashlib
import platform
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
import generate_dataset as gd
import manifest as mf

# N5 Step 0: environment check. Rebuild the first RNG shard (seed 100 of 100-103) of the committed
# 0.94-floor build with the committed invocation, and compare it column by column, byte for byte,
# with the seed-100 rows of data/dataset.parquet (scenario_id // 1_000_000 == 100).

DATASET = "data/dataset.parquet"
CFG = dict(mult_lo=1.0, mult_hi=1.12, reg_lo=1.0, reg_hi=1.12, pf_lo=0.9, pf_hi=1.15, dvm=0.025,
           network="case118")
N_TOTAL = 1500
SEED = 100
PER_SHARD = 375
OUT_JSON = "scratch/n5_step0_envcheck.json"


def col_sha(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def main():
    shard_path = sys.argv[1]
    t0 = time.time()
    modes = np.array(["independent", "regional"])
    mode_list = list(modes[(np.arange(N_TOTAL) % 2)])
    gd.worker((SEED, PER_SHARD, "mixed", mode_list[0:PER_SHARD], "fixed", shard_path, CFG))
    wall = time.time() - t0

    new = pd.read_parquet(shard_path)
    old = pd.read_parquet(DATASET)
    old = old[(old["scenario_id"] // 1_000_000) == SEED].reset_index(drop=True)

    diffs = []
    same_cols = list(new.columns) == list(old.columns)
    if same_cols and len(new) == len(old):
        for c in new.columns:
            a = new[c].to_numpy()
            b = old[c].to_numpy()
            if a.dtype != b.dtype:
                diffs.append(dict(column=c, why=f"dtype {a.dtype} vs {b.dtype}"))
            elif a.dtype == object:
                if not np.array_equal(a, b):
                    diffs.append(dict(column=c, why="object values differ"))
            elif col_sha(a) != col_sha(b):
                d = np.abs(a.astype(np.float64) - b.astype(np.float64))
                diffs.append(dict(column=c, why="bytes differ", n_rows_diff=int(np.sum(~(d == 0))),
                                  max_abs_diff=float(np.nanmax(d)) if np.any(~np.isnan(d)) else None))
    out = dict(step="N5 step 0 environment check", shard_seed=SEED, scenarios=PER_SHARD,
               rows_new=int(len(new)), rows_old=int(len(old)), columns_match=same_cols,
               frame_equals=bool(new.equals(old)), n_columns_differing=len(diffs), differing=diffs[:50],
               byte_identical=bool(same_cols and len(new) == len(old) and len(diffs) == 0),
               reject_file=open(shard_path + ".reject").read(),
               wall_s=wall, python=platform.python_version(),
               packages={p: mf.pkg_version(p) for p in mf.PACKAGES},
               dataset_sha256=mf_sha(DATASET),
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: out[k] for k in ["rows_new", "rows_old", "columns_match", "frame_equals",
                                          "n_columns_differing", "byte_identical", "wall_s"]}, indent=1))


def mf_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


if __name__ == "__main__":
    main()
