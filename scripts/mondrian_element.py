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
OUT = "data/mondrian_element_long.parquet"
SIDE = "data/mondrian_element_summary.json"
LIMIT = 0.94
TARGETS = [0.90, 0.94, 0.97]


def m2_config(tuned, fam, seed):
    for r in tuned["records"]:
        if r["family"] == fam and r["metric"] == "m2" and r["seed"] == seed:
            return r["config"]
    raise ValueError("missing")


def qhat_from(resid, coverage):
    s = np.sort(resid)
    n = len(s)
    k = int(np.ceil((n + 1) * coverage))
    k_clipped = min(k, n)
    achieved = k / (n + 1.0)
    return float(s[k_clipped - 1]), int(k), float(achieved), bool(k > n)


def main():
    t0 = time.time()
    tuned = json.load(open(TUNED))
    n_seeds = int(tuned["seeds"])

    raw = pd.read_parquet(DATASET)
    n1 = raw[raw.outaged_type != "none"].reset_index(drop=True)
    n1["element"] = n1.outaged_type.astype(str) + "_" + n1.outaged_idx.astype(str)
    conv = n1["converged"].to_numpy()
    nc_idx = np.flatnonzero(~conv)
    nc_elem = n1.iloc[nc_idx].element.to_numpy()
    nc_scen = n1.iloc[nc_idx].scenario_id.to_numpy()

    feature_cols = [c for c in n1.columns
                    if c not in ms.EXCLUDE_COLS and pd.api.types.is_numeric_dtype(n1[c])]
    X_all, _ya, _ga, _b = ms.build_design_matrix(n1, feature_cols)
    df_c, fc_c = ms.load_dataset(DATASET)
    X_c, y_c, groups_c, _b2 = ms.build_design_matrix(df_c, fc_c)
    assert list(X_all.columns) == list(X_c.columns)
    elem_c = (df_c.outaged_type.astype(str) + "_" + df_c.outaged_idx.astype(str)).to_numpy()

    rows = []
    agg = []
    nc_effect = []
    for seed in range(n_seeds):
        splits = ms.make_splits(groups_c, seed)
        kept = ms.select_features(X_c, splits["train"])
        Xk = X_c[kept]
        Xtr = Xk.iloc[splits["train"]].to_numpy(np.float32)
        Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
        Xte = Xk.iloc[splits["test"]].to_numpy(np.float32)
        ytr, yca, yte = y_c[splits["train"]], y_c[splits["cal"]], y_c[splits["test"]]
        e_ca, e_te = elem_c[splits["cal"]], elem_c[splits["test"]]
        Xk_nc = X_all[kept].iloc[nc_idx].to_numpy(np.float32)
        test_scen = set(np.unique(groups_c[splits["test"]]).tolist())
        nc_in_test = np.isin(nc_scen, list(test_scen))

        for fam in ("ridge", "histgb"):
            fitted = T.fit_one(fam, m2_config(tuned, fam, seed), Xtr, ytr, seed)
            p_ca = np.asarray(T.predict(fitted, Xca), dtype=np.float64)
            p_te = np.asarray(T.predict(fitted, Xte), dtype=np.float64)
            p_nc = np.asarray(T.predict(fitted, Xk_nc), dtype=np.float64)
            resid_ca = p_ca - yca

            for tgt in TARGETS:
                q_glob, k_g, ach_g, clip_g = qhat_from(resid_ca, tgt)
                q_by_elem = {}
                for el in np.unique(e_ca):
                    m = e_ca == el
                    q_e, k_e, ach_e, clip_e = qhat_from(resid_ca[m], tgt)
                    q_by_elem[el] = q_e
                    te_m = e_te == el
                    n_te_g = int(te_m.sum())
                    if n_te_g:
                        yg, pg = yte[te_m], p_te[te_m]
                        gate = ge.run_gate(pg, q_e, LIMIT)
                        viol = yg < LIMIT
                        cov = float((yg >= pg - q_e).mean())
                        esc = float(gate["escalate"].mean())
                        miss = float((gate["certify"] & viol).sum() / max(int(viol.sum()), 1))
                    else:
                        cov = esc = miss = np.nan
                    rows.append(dict(
                        calibration="mondrian", model=fam, target=float(tgt), seed=int(seed),
                        element=str(el), n_cal=int(m.sum()), k_index=k_e,
                        achieved_level=ach_e, finite_sample_penalty=ach_e - tgt,
                        index_clipped=clip_e, q_hat=q_e, n_test_group=n_te_g,
                        coverage_emp=cov, escalation=esc, missed_rate=miss,
                        n_viol_group=int((yte[te_m] < LIMIT).sum()) if n_te_g else 0))

                # aggregate: mondrian vs global on the same test split
                q_vec = np.array([q_by_elem[e] for e in e_te])
                for label, qv in (("mondrian", q_vec), ("global", np.full(len(e_te), q_glob))):
                    lower = p_te - qv
                    certify = lower >= LIMIT
                    flag = p_te < LIMIT
                    escal = ~(certify | flag)
                    viol = yte < LIMIT
                    agg.append(dict(calibration=label, model=fam, target=float(tgt), seed=int(seed),
                                    coverage_emp=float((yte >= lower).mean()),
                                    escalation=float(escal.mean()),
                                    missed_rate=float((certify & viol).sum() / max(int(viol.sum()), 1)),
                                    certified_frac=float(certify.mean()),
                                    q_hat_global=q_glob,
                                    q_hat_mean=float(qv.mean()), q_hat_std=float(qv.std(ddof=0))))
                # item 5: the non-converged rows
                q_nc = np.array([q_by_elem.get(e, q_glob) for e in nc_elem])
                for label, qv in (("mondrian", q_nc), ("global", np.full(len(nc_elem), q_glob))):
                    cert = (p_nc - qv) >= LIMIT
                    fl = p_nc < LIMIT
                    nc_effect.append(dict(calibration=label, model=fam, target=float(tgt),
                                          seed=int(seed),
                                          certified_all=int(cert.sum()),
                                          flagged_all=int(fl.sum()),
                                          escalated_all=int((~(cert | fl)).sum()),
                                          certified_in_test=int((cert & nc_in_test).sum())))
        print(f"  seed {seed} done {time.time()-t0:.0f}s", flush=True)

    out = pd.DataFrame(rows)
    out.to_parquet(OUT, index=False)
    print(f"wrote {OUT} rows={len(out)}")

    side = dict(aggregate=agg, nonconverged_effect=nc_effect,
                n_elements=int(out.element.nunique()),
                n_nonconverged=int(len(nc_idx)),
                schema_note=("written as a SEPARATE artifact rather than appended to "
                             "data/sweep_results_long.parquet: that file is tracked in git and its "
                             "rows are an L-sweep under global calibration with an incompatible "
                             "schema (L, boundary_mass, esc_pred_*). Appending would mutate a "
                             "committed artifact, invalidate its manifest content hash, and mix two "
                             "row semantics in one table."))
    json.dump(side, open(SIDE, "w"), indent=2)
    print(f"wrote {SIDE}")

    meta = dict(artifact="Mondrian (group-conditional) split conformal, grouped by outaged element",
                grouping="outaged element (outaged_type + outaged_idx), 186 groups",
                targets=TARGETS, limit=LIMIT, seeds=n_seeds,
                quantile_note=("k = ceil((n_g+1)*coverage); achieved level = k/(n_g+1); "
                               "finite_sample_penalty = achieved - target; index_clipped marks "
                               "groups where k > n_g so the quantile saturates at the max residual"),
                model_hyperparameters={f: {str(s): m2_config(tuned, f, s) for s in range(n_seeds)}
                                       for f in ("ridge", "histgb")})
    man = cm.build_manifest(OUT, meta, dict(task="mondrian element calibration", source=DATASET))
    json.dump(man, open(mf.manifest_path(OUT), "w"), indent=2)
    print(f"wrote {mf.manifest_path(OUT)}")


if __name__ == "__main__":
    main()
