import os
import sys
import json
import time
import hashlib
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import make_splits as ms
import baselines as bl
import sts_manifest as sm
import n9_budget_curve as bc

# N9 Step 4, Part 2 of scratch/n9_decision_rule.md: shift test. The gate (N5 M2 config, refit on the source
# train split, q_hat on the source cal split, held-out target = the source N5 selection) and the static
# ranking (violation frequency over the source train split) are built on the SOURCE dataset only and applied
# to the TARGET dataset's test split for the same seed. Nothing from the target is used to fit, calibrate,
# choose the target or build the static table.
# Primary: D94 -> D95a, histgb, rule B. Reported only: ridge, and the reverse direction D95a -> D94.

RULE = "scratch/n9_decision_rule.md"
RULE_SHA = "scratch/n9_decision_rule.sha256"
DIRECTIONS = [("D94", "D95a"), ("D95a", "D94")]
FAMILIES = ["ridge", "histgb"]
SEEDS = [0, 1, 2, 3, 4]
LIMIT = 0.94
OUT = "data/sts_n9_shift.json"


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def static_scores(freq, elem_key):
    out = np.zeros(len(elem_key))
    for i, e in enumerate(elem_key):
        out[i] = -freq.get(int(e), 0.0)
    return out


def main():
    t0 = time.time()
    data = {}
    n5json = {}
    for name in bc.RUNS:
        data[name] = bc.load(bc.RUNS[name][0])
        n5json[name] = json.load(open(bc.RUNS[name][1]))

    rows = []
    align = []
    for src_name, tgt_name in DIRECTIONS:
        src = data[src_name]
        tgt = data[tgt_name]
        for seed in SEEDS:
            s_spl = ms.make_splits(src["groups"], seed)
            t_spl = ms.make_splits(tgt["groups"], seed)
            kept = ms.select_features(src["X"], s_spl["train"])
            missing = [c for c in kept if c not in tgt["X"].columns]
            align.append(dict(source=src_name, target=tgt_name, seed=seed, n_kept=len(kept), n_missing_in_target=len(missing)))
            te = t_spl["test"]
            Xte = tgt["X"].reindex(columns=kept, fill_value=0.0).iloc[te].to_numpy(np.float32)
            y_te = tgt["y"][te]
            scen = tgt["df"]["scenario_id"].to_numpy(np.int64)[te]
            viol = y_te < LIMIT
            tb = tgt["elem_key"][te].astype(float)
            rows_per_scen = len(te) / len(np.unique(scen))
            k_max = int(pd.Series(scen).value_counts().max())
            s_mask = np.zeros(len(src["df"]), dtype=bool)
            s_mask[s_spl["train"]] = True
            _, s_freq = bl.static_severity_score(src["df"], s_mask, src["elem_key"])
            c_shift, _, _ = bl.capture_curve(scen, static_scores(s_freq, tgt["elem_key"][te]), tb, viol, k_max)
            t_mask = np.zeros(len(tgt["df"]), dtype=bool)
            t_mask[t_spl["train"]] = True
            t_score, _ = bl.static_severity_score(tgt["df"], t_mask, tgt["elem_key"])
            c_indist, _, _ = bl.capture_curve(scen, t_score[te], tb, viol, k_max)
            for fam in FAMILIES:
                f5 = bc.n5_config(n5json[src_name], seed, fam)
                target = n5json[src_name]["selections"][str(seed)][fam]["m2_inner_cov_at"]
                p_ca, y_ca, p_te = bc.fit_predict(src, seed, fam, f5["config"], Xte, kept)
                g = bc.gate_point(p_ca, y_ca, p_te, y_te, target)
                k_b = int(round(g["solve_share_B"] * rows_per_scen))
                ref_t = bc.n5_held_out(n5json[tgt_name], seed, fam)
                r = dict(source=src_name, target=tgt_name, seed=seed, family=fam, tag=f5["tag"], held_out_target=target,
                         q_hat=g["q_hat"], escalation=g["escalation"], flag_share=g["flag_share"],
                         solve_share_B=g["solve_share_B"], missed=g["missed"], gate_catch=1.0 - g["missed"],
                         coverage_emp=g["coverage_emp"], k_B=k_b,
                         static_catch_B=float(bl.at_k(c_shift, k_b)) if k_b > 0 else 0.0,
                         static_indist_catch_at_same_k=float(bl.at_k(c_indist, k_b)) if k_b > 0 else 0.0,
                         target_indist_gate_catch_n5=ref_t["gate_catch"],
                         target_indist_static_catch_B_n5=ref_t["static_catch_B"],
                         n_test=int(len(y_te)), n_test_viol=int(viol.sum()))
                r["gate_degradation"] = r["gate_catch"] - r["target_indist_gate_catch_n5"]
                r["static_degradation"] = r["static_catch_B"] - r["static_indist_catch_at_same_k"]
                rows.append(r)
                print(f"{src_name}->{tgt_name} seed {seed} {fam:6s} tgt {target:.2f} solveB {100*r['solve_share_B']:5.1f}% "
                      f"miss {100*r['missed']:5.2f}% cov {r['coverage_emp']:.3f} gate {100*r['gate_catch']:6.2f} "
                      f"static {100*r['static_catch_B']:6.2f} (k_B {k_b})", flush=True)

    df = pd.DataFrame(rows)
    summary = []
    for src_name, tgt_name in DIRECTIONS:
        for fam in FAMILIES:
            m = df[(df.source == src_name) & (df.target == tgt_name) & (df.family == fam)]
            s = dict(source=src_name, target=tgt_name, family=fam)
            for c in ["held_out_target", "solve_share_B", "escalation", "flag_share", "missed", "gate_catch", "static_catch_B",
                      "coverage_emp", "k_B", "gate_degradation", "static_degradation", "target_indist_gate_catch_n5",
                      "target_indist_static_catch_B_n5", "static_indist_catch_at_same_k"]:
                mu, sd = ms_(m[c])
                s[c + "_mean"] = mu
                s[c + "_std"] = sd
            s["splits_missed_le_1pct"] = int((m["missed"] <= 0.01).sum())
            gm, gs = ms_(m["gate_catch"])
            sm_, ss = ms_(m["static_catch_B"])
            s["gap"] = gm - sm_
            s["STD"] = max(gs, ss)
            s["gate_higher_by_std_rule"] = bool(s["gap"] > s["STD"])
            summary.append(s)

    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    recorded = open(RULE_SHA).read().split()[0]
    if h != recorded:
        raise ValueError("decision rule changed since hashing; stop")
    prim = [s for s in summary if s["source"] == "D94" and s["target"] == "D95a" and s["family"] == "histgb"][0]
    verdict = dict(SHIFT_ADVANTAGE=prim["gate_higher_by_std_rule"], gate_catch_mean=prim["gate_catch_mean"],
                   gate_catch_std=prim["gate_catch_std"], static_catch_mean=prim["static_catch_B_mean"],
                   static_catch_std=prim["static_catch_B_std"], gap=prim["gap"], STD=prim["STD"],
                   rule="mean(gate catch) - mean(static catch) > max(std gate, std static); D94->D95a, histgb, held-out target, rule B")
    out = dict(part="N9 Part 2: shift test", decision_rule=RULE, decision_rule_sha256=h, decision_rule_hash_verified=True,
               verdict=verdict, summary=summary, per_split=rows, feature_alignment=align,
               std_convention="population std (ddof=0) over 5 splits", wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    hyper = {}
    for name in bc.RUNS:
        hyper[name] = [dict(seed=f["seed"], family=f["family"], tag=f["tag"], config=f["config"]) for f in n5json[name]["fits"]]
    params = dict(directions=DIRECTIONS, seeds=SEEDS, families=FAMILIES, limit=LIMIT,
                  model_hyperparameters=dict(source="N5 M2 selections of the SOURCE dataset, unchanged", per_dataset=hyper))
    man = sm.build_manifest([OUT], "scratch/n9_shift.py", [".venv/bin/python", "scratch/n9_shift.py"],
                            ["data/dataset.parquet", "data/sts_n2_label_audit.parquet", "data/sts_n3_floor095.parquet",
                             "data/sts_n5_relabel095.parquet", "data/sts_n5_gate_094.json", "data/sts_n5_gate_095.json", RULE],
                            params, "")
    man["no_new_solves"] = "No AC solve. Model fits: N5 M2 configs refit on the source train split (no search)."
    sm.write_manifest(man, OUT)
    for s in summary:
        print(f"{s['source']}->{s['target']} {s['family']:6s} gate {100*s['gate_catch_mean']:6.2f}±{100*s['gate_catch_std']:.2f} "
              f"static {100*s['static_catch_B_mean']:6.2f}±{100*s['static_catch_B_std']:.2f} gap {100*s['gap']:.2f} STD {100*s['STD']:.2f} "
              f"missed<=1%: {s['splits_missed_le_1pct']}/5 cov {s['coverage_emp_mean']:.3f} vs tgt {s['held_out_target_mean']:.3f}")
    print(f"SHIFT-ADVANTAGE: {'YES' if verdict['SHIFT_ADVANTAGE'] else 'NO'} (gap {100*verdict['gap']:.2f} pp vs STD {100*verdict['STD']:.2f} pp)")


if __name__ == "__main__":
    main()
