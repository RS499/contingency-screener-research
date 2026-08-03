import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import tune_surrogates as T
import classical_manifest as cm

LIMIT = 0.94
SEEDS = 5
COV = 0.90
THRESH = [0.01, 0.02, 0.05]


def m2_configs():
    tm = json.load(open("data/tuned_metrics.json"))
    return {(r["family"], r["seed"]): r["config"] for r in tm["records"] if r["metric"] == "m2"}


def main():
    cfg = m2_configs()
    df, fc = ms.load_dataset("data/dataset.parquet")
    X, y, groups, _b = ms.build_design_matrix(df, fc)

    per_seed = {f: [] for f in ("ridge", "histgb")}
    pooled_depths = {f: [] for f in ("ridge", "histgb")}
    for seed in range(SEEDS):
        sp = ms.make_splits(groups, seed)
        kept = ms.select_features(X, sp["train"]); Xk = X[kept]
        Xtr = Xk.iloc[sp["train"]].to_numpy(np.float32); ytr = y[sp["train"]]
        Xca = Xk.iloc[sp["cal"]].to_numpy(np.float32); yca = y[sp["cal"]]
        Xte = Xk.iloc[sp["test"]].to_numpy(np.float32); yte = y[sp["test"]]
        tv = yte < LIMIT
        for fam in ("ridge", "histgb"):
            fit = T.fit_one(fam, cfg[(fam, seed)], Xtr, ytr, seed)
            q = ge.calibrate_qhat(T.predict(fit, Xca), yca, COV)
            g = ge.run_gate(T.predict(fit, Xte), q, LIMIT)
            d = LIMIT - yte[g["certify"] & tv]
            pooled_depths[fam].extend(list(d))
            rec = dict(seed=seed, n_miss=int(len(d)),
                       shortfall_mean_depth=(float(np.mean(d)) if len(d) else None))
            for t in THRESH:
                rec[f"n_gt_{t}"] = int((d > t).sum())
            per_seed[fam].append(rec)
            print(f"{fam:7s} seed={seed} n_miss={rec['n_miss']:4d} "
                  f">0.01={rec['n_gt_0.01']:3d} >0.02={rec['n_gt_0.02']:3d} >0.05={rec['n_gt_0.05']:2d}", flush=True)

    out = dict(coverage_target=COV, thresholds_pu=THRESH,
               shortfall_def="E[depth | certified miss] = mean(0.94 - Y over certified true violations)",
               std_convention="population std ddof=0 across 5 seeds", families={})
    for fam in ("ridge", "histgb"):
        rows = per_seed[fam]
        dp = np.asarray(pooled_depths[fam], dtype=np.float64)
        agg = dict(per_seed=rows)
        for key in ["n_miss", "shortfall_mean_depth"] + [f"n_gt_{t}" for t in THRESH]:
            vals = [r[key] for r in rows if r[key] is not None]
            agg[f"{key}_seedmean"] = float(np.mean(vals)) if vals else None
            agg[f"{key}_seedstd"] = float(np.std(vals)) if vals else None
        pooled = dict(n_miss=int(len(dp)),
                      shortfall_mean_depth=(float(dp.mean()) if len(dp) else None))
        for t in THRESH:
            pooled[f"n_gt_{t}"] = int((dp > t).sum())
        agg["pooled"] = pooled
        out["families"][fam] = agg

    settings = dict(task="STEP 0 tail-miss counts (per seed + pooled) at coverage 0.90",
                    source="data/dataset.parquet, data/tuned_metrics.json")
    cm.write_with_manifest("data/miss_tail_counts.json", out, settings)
    print("\nwrote data/miss_tail_counts.json")


if __name__ == "__main__":
    main()
