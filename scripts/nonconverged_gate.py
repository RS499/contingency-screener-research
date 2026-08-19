import os
import sys
import json
import time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import manifest as mf
import classical_manifest as cm
import tune_surrogates as T

DATASET = "data/dataset.parquet"
TUNED = "data/tuned_metrics.json"
OUT = "data/nonconverged_gate.json"
LIMIT = 0.94
OPS = {"ridge": [0.90, 0.94], "histgb": [0.90, 0.97]}


def m2_config(tuned, family, seed):
    for r in tuned["records"]:
        if r["family"] == family and r["metric"] == "m2" and r["seed"] == seed:
            return r["config"]
    raise ValueError("missing config")


def main():
    t0 = time.time()
    with open(TUNED) as f:
        tuned = json.load(f)
    n_seeds = int(tuned["seeds"])

    raw = pd.read_parquet(DATASET)
    n1 = raw[raw.outaged_type != "none"].reset_index(drop=True)
    conv_mask = n1["converged"].to_numpy()
    nc_idx = np.flatnonzero(~conv_mask)
    print(f"N-1 rows {len(n1)}  converged {int(conv_mask.sum())}  NON-CONVERGED {len(nc_idx)}", flush=True)

    feature_cols = [c for c in n1.columns
                    if c not in ms.EXCLUDE_COLS and pd.api.types.is_numeric_dtype(n1[c])]
    X_all, _y_all, groups_all, _b = ms.build_design_matrix(n1, feature_cols)

    # the published pipeline sees only converged rows, in this same order
    df_c, fc_c = ms.load_dataset(DATASET)
    X_c, y_c, groups_c, _b2 = ms.build_design_matrix(df_c, fc_c)
    assert list(X_all.columns) == list(X_c.columns), "design-matrix columns diverge"
    assert np.array_equal(groups_all[conv_mask], groups_c), "converged row order diverges"
    print("alignment check passed: converged subset of X_all == published X", flush=True)

    nc = n1.iloc[nc_idx]
    out = dict(
        n_nonconverged=int(len(nc_idx)),
        n_n1_rows=int(len(n1)),
        n_converged=int(conv_mask.sum()),
        n_base_rows_excluded_by_design=int((raw.outaged_type == "none").sum()),
        note_1545=("1545 = 280500 total - 278955 converged N-1 = 1500 N-0 base rows "
                   "(all converged, excluded because they are base cases not contingencies) "
                   "+ 45 genuine non-convergences. Only the 45 are solver failures."),
        min_vm_all_nan=bool(nc.min_vm.isna().all()),
    )

    # Q3 concentration
    elem = (nc.outaged_type.astype(str) + "_" + nc.outaged_idx.astype(str)).value_counts()
    out["q3_top_elements"] = [dict(element=k, count=int(v), share_of_45=float(v) / len(nc_idx))
                              for k, v in elem.head(10).items()]
    out["q3_n_distinct_elements"] = int(elem.size)
    out["q3_n_distinct_scenarios"] = int(nc.scenario_id.nunique())
    sc = nc.scenario_id.value_counts()
    out["q3_max_per_scenario"] = int(sc.max())

    # Q4 base voltage of affected scenarios
    base = raw[raw.outaged_type == "none"][["scenario_id", "n0_min_vm"]]
    aff = set(nc.scenario_id.unique())
    a = base[base.scenario_id.isin(aff)].n0_min_vm.to_numpy()
    b = base[~base.scenario_id.isin(aff)].n0_min_vm.to_numpy()
    out["q4"] = dict(n_affected_scenarios=int(len(a)), n_other_scenarios=int(len(b)),
                     mean_n0_min_vm_affected=float(a.mean()),
                     mean_n0_min_vm_other=float(b.mean()),
                     difference=float(a.mean() - b.mean()),
                     std_affected=float(a.std(ddof=0)), std_other=float(b.std(ddof=0)),
                     median_affected=float(np.median(a)), median_other=float(np.median(b)))

    per_seed = {}
    pred_stats = {}
    for fam in ("ridge", "histgb"):
        per_seed[fam] = []
        pred_stats[fam] = []
    for seed in range(n_seeds):
        splits = ms.make_splits(groups_c, seed)
        kept = ms.select_features(X_c, splits["train"])
        Xk_c = X_c[kept]
        Xk_nc = X_all[kept].iloc[nc_idx]
        Xtr = Xk_c.iloc[splits["train"]].to_numpy(np.float32)
        Xte = Xk_c.iloc[splits["test"]].to_numpy(np.float32)
        Xca = Xk_c.iloc[splits["cal"]].to_numpy(np.float32)
        ytr, yca, yte = y_c[splits["train"]], y_c[splits["cal"]], y_c[splits["test"]]
        test_scen = set(np.unique(groups_c[splits["test"]]).tolist())
        nc_in_test = nc.scenario_id.isin(test_scen).to_numpy()

        for fam in ("ridge", "histgb"):
            fitted = T.fit_one(fam, m2_config(tuned, fam, seed), Xtr, ytr, seed)
            p_ca = T.predict(fitted, Xca)
            p_te = np.asarray(T.predict(fitted, Xte), dtype=np.float64)
            p_nc = np.asarray(T.predict(fitted, Xk_nc.to_numpy(np.float32)), dtype=np.float64)
            pred_stats[fam].append(dict(
                seed=seed,
                nonconv=dict(n=int(len(p_nc)), mean=float(p_nc.mean()), std=float(p_nc.std(ddof=0)),
                             min=float(p_nc.min()), p25=float(np.percentile(p_nc, 25)),
                             median=float(np.median(p_nc)), p75=float(np.percentile(p_nc, 75)),
                             max=float(p_nc.max()),
                             share_below_limit=float((p_nc < LIMIT).mean())),
                converged_test=dict(n=int(len(p_te)), mean=float(p_te.mean()),
                                    std=float(p_te.std(ddof=0)), min=float(p_te.min()),
                                    p25=float(np.percentile(p_te, 25)),
                                    median=float(np.median(p_te)),
                                    p75=float(np.percentile(p_te, 75)), max=float(p_te.max()),
                                    share_below_limit=float((p_te < LIMIT).mean()))))
            rec = dict(seed=seed, n_nc_in_test_split=int(nc_in_test.sum()))
            for tgt in OPS[fam]:
                q = ge.calibrate_qhat(p_ca, yca, tgt)
                g_nc = ge.run_gate(p_nc, q, LIMIT)
                g_te = ge.run_gate(p_te, q, LIMIT)
                viol_te = yte < LIMIT
                missed_pub = int((g_te["certify"] & viol_te).sum())
                nviol_pub = int(viol_te.sum())
                cert_nc_test = int((g_nc["certify"] & nc_in_test).sum())
                n_nc_test = int(nc_in_test.sum())
                rec[f"target_{tgt}"] = dict(
                    q_hat=float(q),
                    all45=dict(certified=int(g_nc["certify"].sum()),
                               flagged=int(g_nc["flag"].sum()),
                               escalated=int(g_nc["escalate"].sum())),
                    test_split_only=dict(n=n_nc_test,
                                         certified=cert_nc_test,
                                         flagged=int((g_nc["flag"] & nc_in_test).sum()),
                                         escalated=int((g_nc["escalate"] & nc_in_test).sum())),
                    published_missed_rate=float(missed_pub / max(nviol_pub, 1)),
                    missed_rate_if_nc_are_violations=float(
                        (missed_pub + cert_nc_test) / max(nviol_pub + n_nc_test, 1)),
                    n_true_viol_test=nviol_pub, n_missed_test=missed_pub)
            per_seed[fam].append(rec)
            print(f"  seed={seed} {fam:6s} done", flush=True)

    out["q1_q2_per_seed"] = per_seed
    out["q5_prediction_stats_per_seed"] = pred_stats

    summ = {}
    for fam in ("ridge", "histgb"):
        summ[fam] = {}
        for tgt in OPS[fam]:
            k = f"target_{tgt}"
            rows = [r[k] for r in per_seed[fam]]
            summ[fam][k] = dict(
                certified_all45_mean=float(np.mean([r["all45"]["certified"] for r in rows])),
                certified_all45_by_seed=[r["all45"]["certified"] for r in rows],
                flagged_all45_by_seed=[r["all45"]["flagged"] for r in rows],
                escalated_all45_by_seed=[r["all45"]["escalated"] for r in rows],
                certified_test_by_seed=[r["test_split_only"]["certified"] for r in rows],
                n_test_by_seed=[r["test_split_only"]["n"] for r in rows],
                published_missed_mean=float(np.mean([r["published_missed_rate"] for r in rows])),
                adjusted_missed_mean=float(np.mean([r["missed_rate_if_nc_are_violations"] for r in rows])),
            )
            summ[fam][k]["delta_missed"] = (summ[fam][k]["adjusted_missed_mean"]
                                            - summ[fam][k]["published_missed_mean"])
    out["summary"] = summ

    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {OUT} in {time.time()-t0:.1f}s", flush=True)

    meta = dict(artifact="gate behaviour on the non-converged N-1 rows",
                n_nonconverged=int(len(nc_idx)), limit=LIMIT, operating_points=OPS,
                model_hyperparameters={f: {str(s): m2_config(tuned, f, s) for s in range(n_seeds)}
                                       for f in ("ridge", "histgb")},
                caveat=("min_vm is NaN for every non-converged row, so no ground truth exists. "
                        "Whether these are voltage collapse or solver failure on a feasible "
                        "point is NOT determined by this data."))
    man = cm.build_manifest(OUT, meta, dict(task="non-converged gate audit", source=DATASET))
    with open(mf.manifest_path(OUT), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {mf.manifest_path(OUT)}", flush=True)


if __name__ == "__main__":
    main()
