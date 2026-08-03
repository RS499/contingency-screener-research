import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import manifest as mf
import classical_manifest as cm
import tune_surrogates as T

TUNED = "data/tuned_metrics.json"
OUT = "data/escalation_at_095.json"
COVERAGE = 0.90
LIMITS = [0.94, 0.95]


def m2_config(tuned, family, seed):
    for r in tuned["records"]:
        if r["family"] == family and r["metric"] == "m2" and r["seed"] == seed:
            return r["config"]
    raise ValueError(f"no M2 config for {family} seed {seed}")


def escalation_at_limit(gate_pred_cal, y_cal, gate_pred_test, limit):
    q_hat = ge.calibrate_qhat(gate_pred_cal, y_cal, COVERAGE)
    gate = ge.run_gate(gate_pred_test, q_hat, limit)
    return float(gate["escalate"].mean()), float(q_hat)


def main():
    with open(TUNED) as f:
        tuned = json.load(f)
    df, feature_cols = ms.load_dataset("data/dataset.parquet")
    X, y, groups, _b = ms.build_design_matrix(df, feature_cols)

    per = {fam: {f"{L}": [] for L in LIMITS} for fam in ("ridge", "histgb")}
    for seed in range(tuned["seeds"]):
        splits = ms.make_splits(groups, seed)
        kept = ms.select_features(X, splits["train"])
        Xk = X[kept]
        Xtr = Xk.iloc[splits["train"]].to_numpy(np.float32)
        Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
        Xte = Xk.iloc[splits["test"]].to_numpy(np.float32)
        ytr, yca = y[splits["train"]], y[splits["cal"]]
        for fam in ("ridge", "histgb"):
            cfg = m2_config(tuned, fam, seed)
            fitted = T.fit_one(fam, cfg, Xtr, ytr, seed)
            p_ca = T.predict(fitted, Xca)
            p_te = T.predict(fitted, Xte)
            for L in LIMITS:
                esc, q_hat = escalation_at_limit(p_ca, yca, p_te, L)
                per[fam][f"{L}"].append(esc)
            print(f"  seed={seed} {fam:6s} esc@0.94={per[fam]['0.94'][-1]*100:.1f}% "
                  f"esc@0.95={per[fam]['0.95'][-1]*100:.1f}%", flush=True)

    summary = {}
    for fam in ("ridge", "histgb"):
        summary[fam] = {}
        for L in LIMITS:
            a = np.array(per[fam][f"{L}"])
            summary[fam][f"escalation_at_{L}"] = dict(mean=float(a.mean()), std=float(a.std()))

    out = dict(
        purpose="Discussion placeholder: escalation rate at a 0.95 pu screening limit, M2 models",
        operating_point=f"coverage target {COVERAGE} (the headline escalation)",
        note=("q_hat is limit-independent (residual quantile); only the gate boundaries move from "
              "0.94 to 0.95. Refit of the five per-seed M2 models per family; cal and test untouched. "
              "The 0.94 column is a consistency check against the v2 curve headline."),
        std_convention="population std (ddof=0) over five held-out splits",
        coverage_target=COVERAGE, limits=LIMITS, per_seed=per, summary=summary)
    model_config = dict(selection_metric="m2", per_seed_configs={
        fam: {f"seed{s}": m2_config(tuned, fam, s) for s in range(tuned["seeds"])}
        for fam in ("ridge", "histgb")})
    settings = dict(task="promote tuned models: escalation at 0.95 pu limit", source=TUNED,
                    ms_solver=mf.load_solve_time()["ms_solver"])
    cm.write_with_manifest(OUT, out, settings, model_config=model_config)

    print("\n=== escalation at coverage 0.90, mean +/- std over 5 seeds ===")
    for fam in ("ridge", "histgb"):
        s = summary[fam]
        print(f"  {fam:6s}: L=0.94 -> {s['escalation_at_0.94']['mean']*100:.1f}"
              f"±{s['escalation_at_0.94']['std']*100:.1f}%   "
              f"L=0.95 -> {s['escalation_at_0.95']['mean']*100:.1f}"
              f"±{s['escalation_at_0.95']['std']*100:.1f}%")


if __name__ == "__main__":
    main()
