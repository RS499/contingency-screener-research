import os
import sys
import json
import time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import make_splits as ms
import gate_eval as ge
import sts_manifest as sm
import n5_gate_eval as n5

# N11 Part 4 (scratch/n11_decision_rule.md §4): the committed linearized classical screen
# (data/classical_predictions.parquet -> pred_min_vm) re-scored against D94 corrected labels (N2 switch-back).
# Same splits (seeds 0-4), conformal at target 0.90 via feasibility/gate_eval.py, MAE, R2, escalation, missed,
# speedup with the classical timing accounting of scripts/eval_classical.py (ms_apply_plus_factor). No new solves.
# Check first: on the stored labels this script must reproduce data/classical_screen_metrics.json
# (fit MAE/R2 and conformalized @0.90) exactly, else stop.

PREDS = "data/classical_predictions.parquet"
META = "data/classical_predictions_meta.json"
REF = "data/classical_screen_metrics.json"
DATASET = "data/dataset.parquet"
LABELS = "data/sts_n2_label_audit.parquet"
OUT = "data/sts_n11_classical.json"
SEEDS = [0, 1, 2, 3, 4]
LIMIT = 0.94
MS_SOLVER = 9.14
TARGET = 0.90
KEY = ["scenario_id", "outaged_type", "outaged_idx"]


def ms_(a):
    a = np.asarray(a, dtype=np.float64)
    return float(a.mean()), float(a.std(ddof=0))


def score(df, ms_classical):
    preds = pd.read_parquet(PREDS)[KEY + ["pred_min_vm"]]
    j = df[KEY + ["min_vm"]].merge(preds, on=KEY, how="left", validate="one_to_one")
    if j["pred_min_vm"].isna().any():
        raise ValueError("rows without a classical prediction; stop")
    pred = j["pred_min_vm"].to_numpy(np.float64)
    y = j["min_vm"].to_numpy(np.float64)
    groups = df["scenario_id"].to_numpy()
    per = []
    for seed in SEEDS:
        sp = ms.make_splits(groups, seed)
        pc, yc = pred[sp["cal"]], y[sp["cal"]]
        pt, yt = pred[sp["test"]], y[sp["test"]]
        q = ge.calibrate_qhat(pc, yc, TARGET)
        g = ge.run_gate(pt, q, LIMIT)
        s = ge.score(g, yt, ms_classical, MS_SOLVER, LIMIT)
        e = pt - yt
        n = len(yt)
        n_flag = int(g["flag"].sum())
        per.append(dict(seed=seed, q_hat=q, mae=float(np.mean(np.abs(e))),
                        r2=float(1 - np.sum(e ** 2) / np.sum((yt - yt.mean()) ** 2)),
                        escalation=s["escalation"], coverage_emp=s["coverage"], missed_viol=s["missed_viol"],
                        net_speedup=s["net_speedup"], flag_share=n_flag / n,
                        speedup_B=float(n * MS_SOLVER / (n * ms_classical + (s["n_escalated"] + n_flag) * MS_SOLVER)),
                        n_test=n, n_true_viol=s["n_true_viol"]))
    return per


def main():
    t0 = time.time()
    ms_classical = json.load(open(META))["timing_ms_per_contingency"]["ms_apply_plus_factor"]
    ref = json.load(open(REF))
    # check on stored labels
    df_s, _ = ms.load_dataset(DATASET)
    st = score(df_s, ms_classical)
    r90 = [r for r in ref["conformalized"] if abs(r["coverage_target"] - TARGET) < 1e-9][0]
    chk = dict(mae=(ms_([p["mae"] for p in st])[0], ref["fit_quality"]["mae"]),
               r2=(ms_([p["r2"] for p in st])[0], ref["fit_quality"]["r2"]),
               escalation=(ms_([p["escalation"] for p in st])[0], r90["escalation"]),
               missed_viol=(ms_([p["missed_viol"] for p in st])[0], r90["missed_viol"]),
               net_speedup=(ms_([p["net_speedup"] for p in st])[0], r90["net_speedup"]),
               coverage_emp=(ms_([p["coverage_emp"] for p in st])[0], r90["coverage_emp"]))
    diffs = {k: abs(v[0] - v[1]) for k, v in chk.items()}
    exact = bool(max(diffs.values()) == 0.0)
    print(f"stored-label reproduction of {REF}: max abs diff {max(diffs.values())!r} (exact={exact})", flush=True)
    if max(diffs.values()) > 1e-12:
        raise ValueError(f"classical stored-label reproduction failed: {diffs}; stop")
    # corrected labels
    df_c, _, info = n5.load_relabeled(DATASET, LABELS)
    co = score(df_c, ms_classical)
    summ = {}
    for k in ["mae", "r2", "q_hat", "escalation", "coverage_emp", "missed_viol", "net_speedup", "flag_share", "speedup_B"]:
        summ[k] = dict(zip(["mean", "std"], ms_([p[k] for p in co])))
        summ[k + "_stored"] = dict(zip(["mean", "std"], ms_([p[k] for p in st])))
    row = (f"classical (linearized) & {1000 * summ['mae']['mean']:.1f}$\\pm${1000 * summ['mae']['std']:.1f} & "
           f"{summ['r2']['mean']:.2f}$\\pm${summ['r2']['std']:.2f} & "
           f"{100 * summ['escalation']['mean']:.1f}$\\pm${100 * summ['escalation']['std']:.1f} & "
           f"{100 * summ['missed_viol']['mean']:.2f}$\\pm${100 * summ['missed_viol']['std']:.2f} & "
           f"{summ['net_speedup']['mean']:.2f}$\\pm${summ['net_speedup']['std']:.2f} \\\\")
    out = dict(part="N11 Part 4: classical screen on corrected labels (descriptive)", labels=info, target=TARGET,
               ms_classical=ms_classical, ms_classical_basis="data/classical_predictions_meta.json timing_ms_per_contingency.ms_apply_plus_factor (the headline accounting of scripts/eval_classical.py)",
               ms_solver=MS_SOLVER, stored_label_reproduction=dict(values_n11_vs_ref=chk, abs_diffs=diffs, exact=exact),
               summary=summ, per_seed_corrected=co, per_seed_stored=st,
               table1_style_row_tex=row, table1_columns="model & MAE (mV) & R2 & escalation@0.90 (%) & missed (%) & speedup A",
               std_convention="population std (ddof=0) over 5 splits", wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    man = sm.build_manifest([OUT], "scratch/n11_classical.py", [".venv/bin/python", "scratch/n11_classical.py"],
                            [PREDS, META, REF, DATASET, LABELS], dict(seeds=SEEDS, target=TARGET, limit=LIMIT,
                            model_hyperparameters="none: committed linearized screen predictions, not refit",
                            solver_settings="no solve; labels = N2 pinned pandapower + switch-back"), "")
    sm.write_manifest(man, OUT)
    print(row)
    print(json.dumps({k: summ[k] for k in ["mae", "r2", "escalation", "missed_viol", "net_speedup", "speedup_B"]}, indent=1))


if __name__ == "__main__":
    main()
