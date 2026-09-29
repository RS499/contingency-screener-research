import os
import sys
import json
import time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import make_splits as ms
import gate_eval as ge
import manifest as mf
import baselines as bl
import tune_surrogates as tu
import sts_manifest as sm

# N5 Step 3: gate re-evaluation on switch-back labels. Pre-registered rule: scratch/n5_decision_rule.md.
# Per dataset and split (seeds 0-4): the scripts/tune_surrogates.py search is run unchanged on the relabeled
# data (search_one_family, select_best, same candidates, same inner split). The M2 config is refit on the full
# train split, calibrated on cal, and evaluated on test at targets 0.90-0.98 and at the held-out point
# (the M2 inner_cov_at). At each point: escalation, flag share, missed rate, speedup A and B, gate catch,
# and the static ranking's catch at the matched budget (scratch/matched_budget.py definition).
#
# argv[1] = run name:
#   "094"        data/dataset.parquet with N2 switch-back labels (data/sts_n2_label_audit.parquet)
#   "095"        data/sts_n3_floor095.parquet with N5 switch-back labels (data/sts_n5_relabel095.parquet)
#   "094stored"  data/dataset.parquet with its stored pandapower labels: reproduction check of this
#                script against data/tuned_metrics.json (selections and sweep), not an N5 result
# argv[2] = comma-separated seeds (default 0,1,2,3,4)

RUNS = {
    "094": ("data/dataset.parquet", "data/sts_n2_label_audit.parquet"),
    "095": ("data/sts_n3_floor095.parquet", "data/sts_n5_relabel095.parquet"),
    "094stored": ("data/dataset.parquet", ""),
}
LIMIT = 0.94
TARGETS = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98]
FAIL_CEIL = 0.005
N_LINE = 173
KEYS = ["scenario_id", "outaged_type", "outaged_idx"]


def load_relabeled(data_path, label_path):
    df, feature_cols = ms.load_dataset(data_path)
    info = dict(n_rows_loaded=int(len(df)))
    if label_path == "":
        info["labels"] = "stored pandapower labels"
        return df, feature_cols, info
    lab = pd.read_parquet(label_path, columns=KEYS + ["stored_min_vm", "corrected_status", "corrected_min_vm"])
    lab = lab[lab["outaged_type"] != "none"]
    m = df[KEYS + ["min_vm"]].merge(lab, on=KEYS, how="left", validate="one_to_one")
    if m["corrected_status"].isna().any():
        raise ValueError("some dataset rows have no relabel record")
    if not np.array_equal(m["stored_min_vm"].to_numpy(), df["min_vm"].to_numpy()):
        raise ValueError("relabel file stored_min_vm does not match the dataset min_vm")
    ok = m["corrected_status"].isin(["converged", "not_needed"]).to_numpy()
    info["labels"] = f"switch-back corrected_min_vm from {label_path}"
    info["n_failed_dropped"] = int((~ok).sum())
    info["failed_share"] = float((~ok).mean())
    counts = m.loc[~ok, "corrected_status"].value_counts()
    info["failed_status_counts"] = {str(k): int(counts[k]) for k in counts.index}
    if info["failed_share"] > FAIL_CEIL:
        raise ValueError(f"failed relabel share {info['failed_share']:.4f} > {FAIL_CEIL}: stop and report")
    new_vm = m["corrected_min_vm"].to_numpy(np.float64)
    info["n_label_flips"] = int(((new_vm < LIMIT) != (df["min_vm"].to_numpy() < LIMIT))[ok].sum())
    df["min_vm"] = new_vm
    df["violation"] = new_vm < LIMIT
    df = df[ok].reset_index(drop=True)
    info["n_rows_used"] = int(len(df))
    return df, feature_cols, info


def evaluate_point(p_ca, y_ca, p_te, y_te, tgt, ms_surr, ms_solver, curve, rows_per_scen):
    q = ge.calibrate_qhat(p_ca, y_ca, tgt)
    certify = (p_te - q) >= LIMIT
    flag = p_te < LIMIT
    esc = (~certify) & (~flag)
    true_v = y_te < LIMIT
    n = len(y_te)
    n_esc = int(esc.sum())
    n_flag = int(flag.sum())
    missed = float((certify & true_v).sum() / max(int(true_v.sum()), 1))
    solve_b = float((esc | flag).mean())
    k_a = int(round(float(esc.mean()) * rows_per_scen))
    k_b = int(round(solve_b * rows_per_scen))
    return dict(target=float(tgt), q_hat=float(q), escalation=float(esc.mean()), flag_share=float(flag.mean()),
                solve_share_B=solve_b, missed=missed, gate_catch=1.0 - missed,
                gate_catch_escalate_only=float((esc & true_v).sum() / max(int(true_v.sum()), 1)),
                coverage_emp=float((y_te >= p_te - q).mean()),
                speedup_A=float(n * ms_solver / (n * ms_surr + n_esc * ms_solver)),
                speedup_B=float(n * ms_solver / (n * ms_surr + (n_esc + n_flag) * ms_solver)),
                k_A=k_a, k_B=k_b,
                static_catch_A=float(bl.at_k(curve, k_a)) if k_a > 0 else 0.0,
                static_catch_B=float(bl.at_k(curve, k_b)) if k_b > 0 else 0.0,
                n_test=int(n), n_true_viol=int(true_v.sum()))


def run_seed(df, X, y, groups, seed, ms_solver, r_cands, h_cands, elem_key):
    print(f"\n=== seed {seed} ===", flush=True)
    splits = ms.make_splits(groups, seed)
    kept = ms.select_features(X, splits["train"])
    Xk = X[kept]
    tr = splits["train"]
    inner = ms.make_splits(groups[tr], tu.INNER_SEED_OFFSET + seed)
    i_fit, i_cal, i_score = tr[inner["train"]], tr[inner["cal"]], tr[inner["test"]]
    Xfit = Xk.iloc[i_fit].to_numpy(np.float32)
    Xic = Xk.iloc[i_cal].to_numpy(np.float32)
    Xis = Xk.iloc[i_score].to_numpy(np.float32)

    search_rows = []
    sel = {}
    for family, cands in (("ridge", r_cands), ("histgb", h_cands)):
        rows = tu.search_one_family(family, cands, Xfit, y[i_fit], Xic, y[i_cal], Xis, y[i_score], seed, ms_solver)
        search_rows.extend(rows)
        m1_tag, m2_tag = tu.select_best(rows)
        m2_row = [r for r in rows if r["tag"] == m2_tag][0]
        sel[family] = dict(m1=m1_tag, m2=m2_tag, m2_inner_cov_at=m2_row["inner_cov_at"],
                           m2_inner_avoided=m2_row["inner_avoided"])
        print(f"  -> {family}: M1 {m1_tag}, M2 {m2_tag}, held-out target {m2_row['inner_cov_at']}", flush=True)

    te = splits["test"]
    train_mask = np.zeros(len(df), dtype=bool)
    train_mask[tr] = True
    stat_score, _ = bl.static_severity_score(df, train_mask, elem_key)
    scen = df["scenario_id"].to_numpy(np.int64)[te]
    viol = df["violation"].to_numpy(bool)[te]
    k_max = int(pd.Series(scen).value_counts().max())
    curve, _, _ = bl.capture_curve(scen, stat_score[te], elem_key[te].astype(float), viol, k_max)
    rows_per_scen = len(te) / len(np.unique(scen))

    Xtr = Xk.iloc[tr].to_numpy(np.float32)
    Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
    Xte = Xk.iloc[te].to_numpy(np.float32)
    y_ca, y_te = y[splits["cal"]], y[te]
    points = []
    fits = []
    for family, cands in (("ridge", r_cands), ("histgb", h_cands)):
        cfg = tu.find_config(cands, sel[family]["m2"])
        fitted = tu.fit_one(family, cfg, Xtr, y[tr], seed)
        p_ca = tu.predict(fitted, Xca)
        t0 = time.time()
        p_te = tu.predict(fitted, Xte)
        ms_surr = (time.time() - t0) / len(y_te) * 1000.0
        mae, r2 = tu.mae_r2(p_te, y_te)
        fits.append(dict(seed=seed, family=family, tag=sel[family]["m2"], config=dict(cfg), mae=mae, r2=r2,
                         ms_surrogate=ms_surr))
        tlist = [(t, "grid") for t in TARGETS]
        if sel[family]["m2_inner_cov_at"] is not None:
            tlist.append((sel[family]["m2_inner_cov_at"], "held_out"))
        for tgt, kind in tlist:
            r = evaluate_point(p_ca, y_ca, p_te, y_te, tgt, ms_surr, ms_solver, curve, rows_per_scen)
            r.update(seed=seed, family=family, point=kind, tag=sel[family]["m2"])
            points.append(r)
        for sw in tu.coverage_sweep(p_ca, y_ca, p_te, y_te, ms_surr, ms_solver):
            points.append(dict(seed=seed, family=family, point="sweep", tag=sel[family]["m2"],
                               target=sw["coverage_target"], escalation=sw["escalation"], missed=sw["missed_viol"]))
        ho = [p for p in points if p["family"] == family and p["point"] == "held_out" and p["seed"] == seed]
        if ho:
            h = ho[0]
            print(f"  TEST {family} M2 {sel[family]['m2']} MAE={mae:.5f} held-out {h['target']:.2f}: "
                  f"esc {100*h['escalation']:.1f}% missed {100*h['missed']:.2f}% spB {h['speedup_B']:.3f} "
                  f"catch {100*h['gate_catch']:.2f} static_B {100*h['static_catch_B']:.2f}", flush=True)
    return search_rows, sel, fits, points


def main():
    run = sys.argv[1]
    seeds = [0, 1, 2, 3, 4]
    if len(sys.argv) > 2:
        seeds = [int(s) for s in sys.argv[2].split(",")]
    data_path, label_path = RUNS[run]
    t0 = time.time()
    ms_solver = mf.load_solve_time()["ms_solver"]
    df, feature_cols, info = load_relabeled(data_path, label_path)
    print(json.dumps(info), flush=True)
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    is_trafo = df["outaged_type"].to_numpy() == "trafo"
    elem_key = df["outaged_idx"].to_numpy(np.int64) + np.where(is_trafo, N_LINE, 0)
    r_cands = tu.ridge_candidates()
    h_cands = tu.histgb_candidates()

    all_search, all_sel, all_fits, all_points = [], {}, [], []
    for seed in seeds:
        s_rows, sel, fits, pts = run_seed(df, X, y, groups, seed, ms_solver, r_cands, h_cands, elem_key)
        all_search.extend(s_rows)
        all_sel[str(seed)] = sel
        all_fits.extend(fits)
        all_points.extend(pts)

    tag = "_".join(str(s) for s in seeds) if seeds != [0, 1, 2, 3, 4] else "all"
    out_path = f"data/sts_n5_gate_{run}.json" if tag == "all" else f"scratch/n5_gate_{run}_seeds{tag}.json"
    out = dict(run=run, dataset=data_path, labels=info, seeds=seeds, limit=LIMIT, ms_solver=ms_solver,
               decision_rule="scratch/n5_decision_rule.md", selections=all_sel, fits=all_fits,
               points=all_points, search=all_search, wall_s=time.time() - t0)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    inputs = [data_path, "data/solve_time.json", "scripts/tune_surrogates.py", "scripts/baselines.py"]
    if label_path != "":
        inputs.append(label_path)
    params = dict(run=run, seeds=seeds, targets=TARGETS, limit=LIMIT, fail_ceiling=FAIL_CEIL,
                  model_hyperparameters=dict(search="scripts/tune_surrogates.py candidates (15 ridge alphas, 26 histgb)",
                                             selected_m2_per_seed={s: {f: [c for c in all_fits if c["seed"] == int(s) and c["family"] == f][0]["config"]
                                                                       for f in ["ridge", "histgb"]} for s in all_sel}),
                  inner_seed_offset=tu.INNER_SEED_OFFSET, inner_missed_ceiling=tu.INNER_MISSED_CEIL,
                  omp_num_threads=os.environ.get("OMP_NUM_THREADS", "unset"))
    man = sm.build_manifest([out_path], "scratch/n5_gate_eval.py", [".venv/bin/python", "scratch/n5_gate_eval.py"] + sys.argv[1:],
                            inputs, params, "")
    man["no_new_solves"] = "No AC solve. Model fits: the full tune_surrogates search plus M2 refits, per seed."
    sm.write_manifest(man, out_path)
    print(f"wrote {out_path}; wall {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
