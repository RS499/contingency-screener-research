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
import baselines as bl
import tune_surrogates as tu
import sts_manifest as sm
import n5_gate_eval as n5

# N9 Step 3, Part 1 of scratch/n9_decision_rule.md: budget curve on D94 and D95a (switch-back labels),
# ridge and histgb, 5 splits. The M2 config per split comes unchanged from N5 (data/sts_n5_gate_*.json).
# Refit on train, calibrate on cal. Within each test base case, contingencies are ranked by
#   SURR   ascending predicted min_vm
#   STATIC descending train violation frequency per element (scripts/baselines.py static_severity_score)
#   ORACLE ascending true min_vm
# and catch at k = pooled share of test violations in each base case's top k (baselines.capture_curve).
# Before any new number: seed 0 test MAE and held-out escalation / missed must equal N5 exactly.

RUNS = {"D94": ("094", "data/sts_n5_gate_094.json"), "D95a": ("095", "data/sts_n5_gate_095.json")}
FAMILIES = ["ridge", "histgb"]
SEEDS = [0, 1, 2, 3, 4]
K_DECLARED = [20, 40, 57, 89, 120]
K_MAX = 186
LIMIT = 0.94
N_LINE = 173
OUT = "data/sts_n9_budget_curve.json"


def load(run):
    data_path, label_path = n5.RUNS[run]
    df, feature_cols, info = n5.load_relabeled(data_path, label_path)
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    is_trafo = df["outaged_type"].to_numpy() == "trafo"
    elem_key = df["outaged_idx"].to_numpy(np.int64) + np.where(is_trafo, N_LINE, 0)
    return dict(df=df, X=X, y=y, groups=groups, elem_key=elem_key, info=info)


def n5_config(n5json, seed, fam):
    for f in n5json["fits"]:
        if f["seed"] == seed and f["family"] == fam:
            return f
    return None


def n5_held_out(n5json, seed, fam):
    for p in n5json["points"]:
        if p["seed"] == seed and p["family"] == fam and p["point"] == "held_out":
            return p
    return None


def fit_predict(d, seed, fam, cfg, rows_test, kept):
    # refit the N5 M2 config on d's train split; predict cal and the given test rows (of dataset d or another)
    splits = ms.make_splits(d["groups"], seed)
    Xk = d["X"][kept]
    fitted = tu.fit_one(fam, cfg, Xk.iloc[splits["train"]].to_numpy(np.float32), d["y"][splits["train"]], seed)
    p_ca = tu.predict(fitted, Xk.iloc[splits["cal"]].to_numpy(np.float32))
    p_te = tu.predict(fitted, rows_test)
    return p_ca, d["y"][splits["cal"]], p_te


def gate_point(p_ca, y_ca, p_te, y_te, tgt):
    q = ge.calibrate_qhat(p_ca, y_ca, tgt)
    certify = (p_te - q) >= LIMIT
    flag = p_te < LIMIT
    esc = (~certify) & (~flag)
    true_v = y_te < LIMIT
    return dict(q_hat=float(q), escalation=float(esc.mean()), flag_share=float(flag.mean()),
                solve_share_B=float((esc | flag).mean()),
                missed=float((certify & true_v).sum() / max(int(true_v.sum()), 1)),
                coverage_emp=float((y_te >= p_te - q).mean()))


def verdict(a, b):
    am, asd = float(np.mean(a)), float(np.std(a))
    bm, bsd = float(np.mean(b)), float(np.std(b))
    gap = am - bm
    if abs(gap) > max(asd, bsd):
        if gap > 0:
            return "SURR higher"
        return "STATIC higher"
    return "tie"


def main():
    t0 = time.time()
    repro = []
    per_seed = []
    curves = []
    infos = {}
    for name in RUNS:
        run, n5path = RUNS[name]
        n5json = json.load(open(n5path))
        d = load(run)
        infos[name] = d["info"]
        for seed in SEEDS:
            splits = ms.make_splits(d["groups"], seed)
            kept = ms.select_features(d["X"], splits["train"])
            te = splits["test"]
            Xte = d["X"][kept].iloc[te].to_numpy(np.float32)
            y_te = d["y"][te]
            scen = d["df"]["scenario_id"].to_numpy(np.int64)[te]
            viol = y_te < LIMIT
            tb = d["elem_key"][te].astype(float)
            train_mask = np.zeros(len(d["df"]), dtype=bool)
            train_mask[splits["train"]] = True
            stat_score, _ = bl.static_severity_score(d["df"], train_mask, d["elem_key"])
            c_static, _, _ = bl.capture_curve(scen, stat_score[te], tb, viol, K_MAX)
            c_oracle, _, _ = bl.capture_curve(scen, y_te, tb, viol, K_MAX)
            for fam in FAMILIES:
                f5 = n5_config(n5json, seed, fam)
                p_ca, y_ca, p_te = fit_predict(d, seed, fam, f5["config"], Xte, kept)
                mae, r2 = tu.mae_r2(p_te, y_te)
                h5 = n5_held_out(n5json, seed, fam)
                g = gate_point(p_ca, y_ca, p_te, y_te, h5["target"])
                rec = dict(dataset=name, seed=seed, family=fam, mae_n9=mae, mae_n5=f5["mae"],
                           esc_n9=g["escalation"], esc_n5=h5["escalation"], missed_n9=g["missed"], missed_n5=h5["missed"])
                rec["exact"] = bool(mae == f5["mae"] and g["escalation"] == h5["escalation"] and g["missed"] == h5["missed"])
                repro.append(rec)
                print(f"{name} seed {seed} {fam}: repro exact={rec['exact']} MAE {mae:.6f} vs {f5['mae']:.6f}", flush=True)
                if seed == 0 and not rec["exact"]:
                    raise ValueError(f"seed-0 reproduction of N5 failed for {name} {fam}: {rec}; stop")
                c_surr, _, _ = bl.capture_curve(scen, p_te, tb, viol, K_MAX)
                row = dict(dataset=name, seed=seed, family=fam, tag=f5["tag"], n_test_viol=int(viol.sum()),
                           n_test_scenarios=int(len(np.unique(scen))))
                for k in K_DECLARED:
                    row[f"surr_{k}"] = float(c_surr[k - 1])
                    row[f"static_{k}"] = float(c_static[k - 1])
                    row[f"oracle_{k}"] = float(c_oracle[k - 1])
                per_seed.append(row)
                curves.append(dict(dataset=name, seed=seed, family=fam, surr=[float(v) for v in c_surr],
                                   static=[float(v) for v in c_static], oracle=[float(v) for v in c_oracle]))

    ps = pd.DataFrame(per_seed)
    table = []
    for name in RUNS:
        for fam in FAMILIES:
            m = ps[(ps.dataset == name) & (ps.family == fam)]
            crossover = None
            for k in K_DECLARED:
                r = dict(dataset=name, family=fam, k=k)
                for kind in ["surr", "static", "oracle"]:
                    r[kind + "_mean"] = float(m[f"{kind}_{k}"].mean())
                    r[kind + "_std"] = float(m[f"{kind}_{k}"].std(ddof=0))
                r["verdict"] = verdict(m[f"surr_{k}"], m[f"static_{k}"])
                if crossover is None and r["verdict"] != "SURR higher":
                    crossover = k
                table.append(r)
            for r in table:
                if r["dataset"] == name and r["family"] == fam:
                    r["crossover_k"] = crossover

    out = dict(part="N9 Part 1: budget curve (descriptive, no verdict)", decision_rule="scratch/n9_decision_rule.md",
               labels=infos, k_declared=K_DECLARED, k_max=K_MAX,
               std_convention="population std (ddof=0) over 5 splits; verdict: gap > larger std",
               crossover_definition="smallest declared k at which SURR is no longer 'SURR higher'; null if SURR higher at every declared k",
               reproduction_of_n5=repro, reproduction_all_exact=bool(all(r["exact"] for r in repro)),
               table=table, per_seed=per_seed, curves=curves, wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    hyper = {}
    for name in RUNS:
        n5json = json.load(open(RUNS[name][1]))
        hyper[name] = [dict(seed=f["seed"], family=f["family"], tag=f["tag"], config=f["config"]) for f in n5json["fits"]]
    params = dict(k_declared=K_DECLARED, k_max=K_MAX, seeds=SEEDS, families=FAMILIES, limit=LIMIT,
                  model_hyperparameters=dict(source="N5 M2 selections, unchanged", per_dataset=hyper))
    man = sm.build_manifest([OUT], "scratch/n9_budget_curve.py", [".venv/bin/python", "scratch/n9_budget_curve.py"],
                            ["data/dataset.parquet", "data/sts_n2_label_audit.parquet", "data/sts_n3_floor095.parquet",
                             "data/sts_n5_relabel095.parquet", "data/sts_n5_gate_094.json", "data/sts_n5_gate_095.json",
                             "scratch/n9_decision_rule.md"], params, "")
    man["no_new_solves"] = "No AC solve. Model fits: N5 M2 configs refit per split (no search)."
    sm.write_manifest(man, OUT)
    for r in table:
        print(f"{r['dataset']:4s} {r['family']:6s} k={r['k']:3d} SURR {100*r['surr_mean']:6.2f}±{100*r['surr_std']:.2f} "
              f"STATIC {100*r['static_mean']:6.2f}±{100*r['static_std']:.2f} ORACLE {100*r['oracle_mean']:6.2f} "
              f"[{r['verdict']}] crossover {r['crossover_k']}")
    print(f"wall {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
