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
STRIP = 0.005
COVERAGE_TARGETS = [round(0.90 + 0.01 * i, 2) for i in range(9)]


def m2_configs():
    tm = json.load(open("data/tuned_metrics.json"))
    cfg = {}
    for r in tm["records"]:
        if r["metric"] == "m2":
            cfg[(r["family"], r["seed"])] = r["config"]
    return cfg


def depth_stats(depths, qhats):
    n = int(len(depths))
    if n == 0:
        return dict(count=0, mean=None, median=None, p90=None, p99=None, max=None,
                    share_below_qhat=None, share_below_strip=None)
    d = np.asarray(depths, dtype=np.float64)
    q = np.asarray(qhats, dtype=np.float64)
    return dict(
        count=n,
        mean=float(d.mean()),
        median=float(np.median(d)),
        p90=float(np.percentile(d, 90)),
        p99=float(np.percentile(d, 99)),
        max=float(d.max()),
        share_below_qhat=float((d < q).mean()),
        share_below_strip=float((d < STRIP).mean()))


def main():
    cfg = m2_configs()
    df, feature_cols = ms.load_dataset("data/dataset.parquet")
    X, y, groups, _b = ms.build_design_matrix(df, feature_cols)

    families = {}
    for family in ("ridge", "histgb"):
        all_rows = []
        per_seed = {}
        pool = {cov: {"depths": [], "qhats": []} for cov in COVERAGE_TARGETS}

        for seed in range(SEEDS):
            splits = ms.make_splits(groups, seed)
            kept = ms.select_features(X, splits["train"])
            Xk = X[kept]
            Xtr = Xk.iloc[splits["train"]].to_numpy(np.float32)
            Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
            Xte = Xk.iloc[splits["test"]].to_numpy(np.float32)
            ytr, yca, yte = y[splits["train"]], y[splits["cal"]], y[splits["test"]]

            fitted = T.fit_one(family, cfg[(family, seed)], Xtr, ytr, seed)
            p_ca = T.predict(fitted, Xca)
            p_te = T.predict(fitted, Xte)
            true_viol = yte < LIMIT

            seed_cov = {}
            for cov in COVERAGE_TARGETS:
                q_hat = ge.calibrate_qhat(p_ca, yca, cov)
                gate = ge.run_gate(p_te, q_hat, LIMIT)
                missed = gate["certify"] & true_viol
                d = LIMIT - yte[missed]
                qrow = np.full(len(d), q_hat)
                seed_cov[f"{cov:.2f}"] = dict(q_hat=float(q_hat),
                                              n_true_viol=int(true_viol.sum()),
                                              **depth_stats(d, qrow))
                pool[cov]["depths"].extend(list(d))
                pool[cov]["qhats"].extend(list(qrow))
                for yi in yte[missed]:
                    all_rows.append(dict(depth=float(LIMIT - yi), y_true=float(yi),
                                         seed=seed, coverage=cov, q_hat=float(q_hat)))
                print(f"{family:6s} seed={seed} cov={cov:.2f} "
                      f"missed={seed_cov[f'{cov:.2f}']['count']:3d} "
                      f"maxdepth={seed_cov[f'{cov:.2f}']['max']}", flush=True)
            per_seed[str(seed)] = seed_cov

        pooled = {}
        for cov in COVERAGE_TARGETS:
            pooled[f"{cov:.2f}"] = depth_stats(pool[cov]["depths"], pool[cov]["qhats"])

        deepest = None
        if all_rows:
            deepest = max(all_rows, key=lambda r: r["depth"])
        families[family] = dict(per_seed=per_seed, pooled=pooled, deepest_missed=deepest,
                                n_missed_rows_total=len(all_rows))

    out = dict(
        question="depth-stratify the missed violations of the promoted v2 M2 surrogates",
        limit=LIMIT, boundary_strip_width=STRIP, seeds=SEEDS,
        coverage_targets=COVERAGE_TARGETS,
        definitions=dict(
            missed_violation="certified (lower band >= 0.94) AND true min_vm < 0.94",
            depth="d = 0.94 - Y (pu below the floor); larger d = deeper, more dangerous miss",
            share_below_qhat="fraction of misses with d < the model's own q_hat at that coverage",
            share_below_strip=f"fraction of misses with d < {STRIP} pu (boundary strip width)",
            pooled="misses concatenated across all 5 seeds at each coverage target",
            m2_selection="the seed's gate-aware (M2) config from tuned_metrics.json, refit on full train"),
        no_new_solves="surrogates refit deterministically; no AC power-flow solve rerun",
        families=families)
    settings = dict(task="depth-stratification of v2 M2 missed violations",
                    source="data/dataset.parquet, data/tuned_metrics.json (M2 configs)",
                    m2_configs={f"{f}_seed{s}": cfg[(f, s)]
                                for (f, s) in sorted(cfg, key=lambda k: (k[0], k[1]))})
    cm.write_with_manifest("data/missed_depth.json", out, settings)
    print("\nwrote data/missed_depth.json")


if __name__ == "__main__":
    main()
