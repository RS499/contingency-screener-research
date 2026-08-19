import os
import sys
import json
import time
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import manifest as mf
import classical_manifest as cm
import tune_surrogates as T

DATASET = "data/dataset.parquet"
TUNED = "data/tuned_metrics.json"
OUT = "data/element_conditional_escalation.json"
SOLVE = "data/solve_time.json"
LIMIT = 0.94
KS = [0, 1, 3, 5, 10, 20]
OPS = {"ridge": 0.94, "histgb": 0.97}


def m2_config(tuned, fam, seed):
    for r in tuned["records"]:
        if r["family"] == fam and r["metric"] == "m2" and r["seed"] == seed:
            return r["config"]
    raise ValueError("missing")


def ms_surr(tuned, fam, seed):
    for r in tuned["records"]:
        if r["family"] == fam and r["metric"] == "m2" and r["seed"] == seed:
            return float(r["ms_surrogate"])
    raise ValueError("missing")


def main():
    t0 = time.time()
    tuned = json.load(open(TUNED))
    ms_solver = float(json.load(open(SOLVE))["ms_solver"])
    n_seeds = int(tuned["seeds"])

    raw = pd.read_parquet(DATASET)
    n1 = raw[raw.outaged_type != "none"].reset_index(drop=True)
    n1["element"] = n1.outaged_type.astype(str) + "_" + n1.outaged_idx.astype(str)
    conv = n1["converged"].to_numpy()

    # ---- Q1 element ranking
    g = n1.groupby("element", as_index=False).agg(
        n_contingencies=("converged", "size"),
        n_nonconv=("converged", lambda s: int((~s).sum())))
    g["rate"] = g.n_nonconv / g.n_contingencies
    g = g.sort_values(["n_nonconv", "rate"], ascending=False).reset_index(drop=True)
    total_nc = int(g.n_nonconv.sum())
    g["cum_share"] = g.n_nonconv.cumsum() / total_nc
    ranking = [dict(rank=i + 1, element=r.element, n_contingencies=int(r.n_contingencies),
                    n_nonconv=int(r.n_nonconv), rate=float(r.rate), cum_share=float(r.cum_share))
               for i, r in g.head(20).iterrows()]
    order = list(g.element)

    # ---- design matrices
    feature_cols = [c for c in n1.columns
                    if c not in ms.EXCLUDE_COLS and pd.api.types.is_numeric_dtype(n1[c])]
    X_all, _ya, groups_all, _b = ms.build_design_matrix(n1, feature_cols)
    df_c, fc_c = ms.load_dataset(DATASET)
    X_c, y_c, groups_c, _b2 = ms.build_design_matrix(df_c, fc_c)
    assert list(X_all.columns) == list(X_c.columns)
    nc_idx = np.flatnonzero(~conv)
    nc = n1.iloc[nc_idx]

    results = {f: {str(k): [] for k in KS} for f in OPS}
    for seed in range(n_seeds):
        splits = ms.make_splits(groups_c, seed)
        kept = ms.select_features(X_c, splits["train"])
        Xk_c = X_c[kept]
        Xtr = Xk_c.iloc[splits["train"]].to_numpy(np.float32)
        Xca = Xk_c.iloc[splits["cal"]].to_numpy(np.float32)
        Xte = Xk_c.iloc[splits["test"]].to_numpy(np.float32)
        ytr, yca, yte = y_c[splits["train"]], y_c[splits["cal"]], y_c[splits["test"]]
        Xk_nc = X_all[kept].iloc[nc_idx].to_numpy(np.float32)

        test_scen = set(np.unique(groups_c[splits["test"]]).tolist())
        elem_te = df_c.iloc[splits["test"]].outaged_type.astype(str) + "_" + \
            df_c.iloc[splits["test"]].outaged_idx.astype(str)
        elem_te = elem_te.to_numpy()
        nc_in_test = nc.scenario_id.isin(test_scen).to_numpy()
        elem_nc = nc.element.to_numpy()

        for fam, tgt in OPS.items():
            fitted = T.fit_one(fam, m2_config(tuned, fam, seed), Xtr, ytr, seed)
            q = ge.calibrate_qhat(T.predict(fitted, Xca), yca, tgt)
            p_te = np.asarray(T.predict(fitted, Xte), dtype=np.float64)
            p_nc = np.asarray(T.predict(fitted, Xk_nc), dtype=np.float64)
            msur = ms_surr(tuned, fam, seed)
            g_te = ge.run_gate(p_te, q, LIMIT)
            g_nc = ge.run_gate(p_nc, q, LIMIT)
            viol_te = yte < LIMIT

            for k in KS:
                forced = set(order[:k])
                fte = np.isin(elem_te, list(forced)) if k else np.zeros(len(elem_te), bool)
                fnc = np.isin(elem_nc, list(forced)) if k else np.zeros(len(elem_nc), bool)
                cert_te = g_te["certify"] & ~fte
                esc_te = g_te["escalate"] | fte
                cert_nc = g_nc["certify"] & ~fnc
                esc_nc = (g_nc["escalate"] | fnc) & nc_in_test

                n_pop = int(len(yte) + nc_in_test.sum())
                n_esc = int(esc_te.sum() + esc_nc.sum())
                missed = int((cert_te & viol_te).sum() + (cert_nc & nc_in_test).sum())
                n_viol = int(viol_te.sum() + nc_in_test.sum())
                results[fam][str(k)].append(dict(
                    seed=seed,
                    nc_escalated_share=float((((g_nc["escalate"] | fnc))).mean()),
                    nc_certified=int((g_nc["certify"] & ~fnc).sum()),
                    missed_rate_conservative=float(missed / max(n_viol, 1)),
                    escalation_rate=float(n_esc / n_pop),
                    speedup=float(n_pop * ms_solver / (n_pop * msur + n_esc * ms_solver))))
        print(f"  seed {seed} done {time.time()-t0:.0f}s", flush=True)

    summary = {}
    for fam in OPS:
        summary[fam] = {}
        base = None
        for k in KS:
            rows = results[fam][str(k)]
            m = dict(k=k,
                     nc_escalated_share=float(np.mean([r["nc_escalated_share"] for r in rows])),
                     nc_certified_mean=float(np.mean([r["nc_certified"] for r in rows])),
                     missed_rate_conservative=float(np.mean([r["missed_rate_conservative"] for r in rows])),
                     escalation_rate=float(np.mean([r["escalation_rate"] for r in rows])),
                     speedup=float(np.mean([r["speedup"] for r in rows])))
            if k == 0:
                base = m
            m["speedup_cost_vs_unmitigated"] = base["speedup"] - m["speedup"]
            m["speedup_cost_pct"] = 100.0 * (base["speedup"] - m["speedup"]) / base["speedup"]
            summary[fam][str(k)] = m
        below = [k for k in KS if summary[fam][str(k)]["missed_rate_conservative"] < 0.01]
        summary[fam]["smallest_k_below_1pct"] = (min(below) if below else None)

    # ---- Q4 deployability
    q4 = dict(
        element_identity_is_a_feature=True,
        element_identity_note=("build_design_matrix one-hot encodes outaged_type+outaged_idx, so "
                               "WHICH element is being outaged is known pre-outage and is already "
                               "a model input."),
        per_element_rate_requires_solves=True,
        per_element_rate_note=("the non-convergence RATE per element is an empirical statistic over "
                               "solves already run; it is not derivable from the pre-outage feature "
                               "columns of an unsolved scenario."),
    )
    top_elem = order[0]
    sub = n1[n1.element == top_elem].reset_index(drop=True)
    yfail = (~sub.converged.to_numpy()).astype(int)
    feats = [c for c in feature_cols]
    Xs = sub[feats].astype(np.float64).to_numpy()
    Xs = np.nan_to_num(Xs)
    gsub = sub.scenario_id.to_numpy()
    aucs = []
    for seed in range(n_seeds):
        splits = ms.make_splits(groups_c, seed)
        tr_scen = set(np.unique(groups_c[splits["train"]]).tolist())
        te_scen = set(np.unique(groups_c[splits["test"]]).tolist())
        tr = np.isin(gsub, list(tr_scen)); te = np.isin(gsub, list(te_scen))
        if yfail[tr].sum() < 2 or yfail[te].sum() < 1:
            continue
        mu, sd = Xs[tr].mean(0), Xs[tr].std(0); sd[sd == 0] = 1.0
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit((Xs[tr] - mu) / sd, yfail[tr])
        s = clf.decision_function((Xs[te] - mu) / sd)
        aucs.append(float(roc_auc_score(yfail[te], s)))
    q4["within_element_scenario_signal"] = dict(
        element=top_elem, n_contingencies=int(len(sub)), n_failures=int(yfail.sum()),
        auc_by_seed=aucs, auc_mean=(float(np.mean(aucs)) if aucs else None),
        note=("logistic regression on the SAME pre-outage scenario features, restricted to this "
              "element, scenario-grouped train/test. Tiny positive count: treat as indicative only."))

    out = dict(n_nonconverged=total_nc,
               premise_correction=("The request states 1,545 non-converged rows, 100% certified, "
                                   "missed rate 0.79%->3.87%. Measured: 45 non-converged rows "
                                   "(1,545 includes 1,500 converged N-0 base rows excluded by "
                                   "design); 0/45 certified for ridge@0.94 and 1/225 seed-rows for "
                                   "histgb@0.97; conservative missed rate 0.7927% and 0.8334%. See "
                                   "data/nonconverged_gate.json."),
               q1_top20=ranking, q1_n_elements_with_any=int((g.n_nonconv > 0).sum()),
               q1_n_elements_total=int(len(g)),
               q2_q3_summary=summary, q2_per_seed=results, q4_deployability=q4,
               ms_solver=ms_solver, limit=LIMIT, operating_points=OPS)
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"wrote {OUT} in {time.time()-t0:.0f}s")
    meta = dict(artifact="element-conditional forced escalation over the non-converged rows",
                n_nonconverged=total_nc, ks=KS, operating_points=OPS,
                model_hyperparameters={f: {str(s): m2_config(tuned, f, s) for s in range(n_seeds)}
                                       for f in OPS})
    man = cm.build_manifest(OUT, meta, dict(task="element-conditional escalation", source=DATASET))
    json.dump(man, open(mf.manifest_path(OUT), "w"), indent=2)
    print(f"wrote {mf.manifest_path(OUT)}")


if __name__ == "__main__":
    main()
