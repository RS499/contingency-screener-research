import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

import manifest as mf

TARGET_COL = "min_vm"
GROUP_COL = "scenario_id"
BRANCH_TYPE_COL = "outaged_type"
BRANCH_IDX_COL = "outaged_idx"
LIMIT = 0.94

EXCLUDE_COLS = frozenset({
    "scenario_id", "sampling_mode", "outaged_type", "outaged_idx", "gen_out", "agg_loading",
    "n0_converged", "n0_min_vm", "converged", "min_vm", "max_vm", "argmin_bus",
    "violation", "straddle", "deep_collapse",
})


def load_dataset(path):
    df = pd.read_parquet(path)
    keep = (df[BRANCH_TYPE_COL] != "none") & (df["converged"])
    df = df[keep].reset_index(drop=True)
    feature_cols = []
    for c in df.columns:
        if c not in EXCLUDE_COLS and pd.api.types.is_numeric_dtype(df[c]):
            feature_cols.append(c)
    print(f"load_dataset: rows={len(df)} scenarios={df[GROUP_COL].nunique()} "
          f"scenario_features={len(feature_cols)}")
    return df, feature_cols


def build_design_matrix(df, feature_cols):
    scen = df[feature_cols].astype(np.float32)
    branch = df[BRANCH_TYPE_COL].astype(str) + "_" + df[BRANCH_IDX_COL].astype(str)
    branch_oh = pd.get_dummies(branch, prefix="br", dtype=np.float32)
    X = pd.concat([scen, branch_oh], axis=1)
    y = df[TARGET_COL].to_numpy(np.float64)
    groups = df[GROUP_COL].to_numpy()
    branch_cols = list(branch_oh.columns)
    print(f"build_design_matrix: X={X.shape} (scen {scen.shape[1]} + branch {len(branch_cols)})")
    return X, y, groups, branch_cols


def select_features(X, train_idx):
    std = X.iloc[train_idx].std(axis=0, ddof=0)
    kept = [c for c in X.columns if std[c] > 0.0]
    print(f"select_features: kept {len(kept)} of {X.shape[1]} columns "
          f"(dropped {X.shape[1] - len(kept)} zero-variance)")
    return kept


def make_splits(groups, seed, train_frac=0.6, cal_frac=0.2):
    n = len(groups)
    placeholder = np.zeros(n)
    gss1 = GroupShuffleSplit(n_splits=1, train_size=train_frac, random_state=seed)
    train_idx, rest_idx = next(gss1.split(placeholder, groups=groups))

    cal_share = cal_frac / (1.0 - train_frac)
    gss2 = GroupShuffleSplit(n_splits=1, train_size=cal_share, random_state=seed)
    cal_rel, test_rel = next(gss2.split(np.zeros(len(rest_idx)), groups=groups[rest_idx]))
    cal_idx = rest_idx[cal_rel]
    test_idx = rest_idx[test_rel]
    return {"train": train_idx, "cal": cal_idx, "test": test_idx}


def write_splits_json(splits, groups, seed, train_frac=0.6, cal_frac=0.2, path="data/splits.json"):
    ids = {}
    n_scen = {}
    n_rows = {}
    for name in ("train", "cal", "test"):
        sids = sorted([int(s) for s in set(groups[splits[name]])])
        ids[name] = sids
        n_scen[name] = len(sids)
        n_rows[name] = int(len(splits[name]))
    out = dict(seed=seed, train_frac=train_frac, cal_frac=cal_frac,
               test_frac=round(1.0 - train_frac - cal_frac, 6),
               group_col=GROUP_COL, n_scenarios=n_scen, n_rows=n_rows, scenario_ids=ids)
    mf.write_with_manifest(path, out)
    print(f"write_splits_json: wrote {path} "
          f"(train/cal/test scenarios {n_scen['train']}/{n_scen['cal']}/{n_scen['test']})")


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "data/dataset.parquet"
    df, feature_cols = load_dataset(p)
    X, y, groups, branch_cols = build_design_matrix(df, feature_cols)
    splits = make_splits(groups, seed=0)
    kept = select_features(X, splits["train"])
    write_splits_json(splits, groups, seed=0)
