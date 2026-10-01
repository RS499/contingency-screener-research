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
import gate_eval as ge
import baselines as bl
import sts_manifest as sm
import n9_budget_curve as bc

# N11 Part 6 (scratch/n11_decision_rule.md §2): per-element (Mondrian) calibration vs the static ranking, D94.
# Per split and family: N5 M2 config refit on train; for each outaged element a one-sided q_hat_e is calibrated on
# that element's cal rows at the split's held-out target (N5 m2_inner_cov_at) with gate_eval.calibrate_qhat (same
# finite-sample rank); elements with < 20 cal rows use the global q_hat. Certify / flag / escalate with q_hat_e.
# MONDRIAN-BEATS-STATIC (histgb, held-out, rule B): mean(gate catch) - mean(static catch at the Mondrian k_B)
# > max(std gate, std static). Static = scripts/baselines.py training-frequency ranking, k_B per split as in N9.

RULE = "scratch/n11_decision_rule.md"
RULE_SHA = "scratch/n11_decision_rule.sha256"
N5 = "data/sts_n5_gate_094.json"
OUT = "data/sts_n11_mondrian.json"
LIMIT = 0.94
SEEDS = [0, 1, 2, 3, 4]
FAMILIES = ["ridge", "histgb"]
MIN_CAL = 20


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def main():
    t0 = time.time()
    n5json = json.load(open(N5))
    ms_solver = n5json["ms_solver"]
    d = bc.load("094")
    per = []
    for seed in SEEDS:
        splits = ms.make_splits(d["groups"], seed)
        kept = ms.select_features(d["X"], splits["train"])
        te, ca, tr = splits["test"], splits["cal"], splits["train"]
        Xte = d["X"][kept].iloc[te].to_numpy(np.float32)
        y_te = d["y"][te]
        ek_te = d["elem_key"][te]
        ek_ca = d["elem_key"][ca]
        scen = d["df"]["scenario_id"].to_numpy(np.int64)[te]
        viol = y_te < LIMIT
        rows_per_scen = len(te) / len(np.unique(scen))
        train_mask = np.zeros(len(d["df"]), dtype=bool)
        train_mask[tr] = True
        stat_score, _ = bl.static_severity_score(d["df"], train_mask, d["elem_key"])
        k_max = int(pd.Series(scen).value_counts().max())
        c_static, _, _ = bl.capture_curve(scen, stat_score[te], ek_te.astype(float), viol, k_max)
        for fam in FAMILIES:
            f5 = bc.n5_config(n5json, seed, fam)
            h5 = bc.n5_held_out(n5json, seed, fam)
            tgt = h5["target"]
            p_ca, y_ca, p_te = bc.fit_predict(d, seed, fam, f5["config"], Xte, kept)
            q_glob = ge.calibrate_qhat(p_ca, y_ca, tgt)
            q_row = np.full(len(y_te), q_glob)
            n_elem_own = 0
            n_elem_fallback = 0
            for e in np.unique(ek_te):
                m_ca = ek_ca == e
                if m_ca.sum() >= MIN_CAL:
                    q_row[ek_te == e] = ge.calibrate_qhat(p_ca[m_ca], y_ca[m_ca], tgt)
                    n_elem_own += 1
                else:
                    n_elem_fallback += 1
            certify = (p_te - q_row) >= LIMIT
            flag = p_te < LIMIT
            esc = (~certify) & (~flag)
            n = len(y_te)
            missed = float((certify & viol).sum() / max(int(viol.sum()), 1))
            solve_b = float((esc | flag).mean())
            k_b = int(round(solve_b * rows_per_scen))
            g_glob = bc.gate_point(p_ca, y_ca, p_te, y_te, tgt)
            if g_glob["missed"] != h5["missed"] or g_glob["escalation"] != h5["escalation"]:
                raise ValueError("global-q refit does not reproduce N5 held-out numbers; stop")
            per.append(dict(seed=seed, family=fam, target=tgt, q_global=q_glob,
                            n_elements_own_q=n_elem_own, n_elements_global_fallback=n_elem_fallback,
                            escalation=float(esc.mean()), flag_share=float(flag.mean()), solve_share_B=solve_b,
                            missed=missed, gate_catch=1.0 - missed, coverage_emp=float((y_te >= p_te - q_row).mean()),
                            speedup_A=float(n * ms_solver / (n * f5["ms_surrogate"] + esc.sum() * ms_solver)),
                            speedup_B=float(n * ms_solver / (n * f5["ms_surrogate"] + (esc.sum() + flag.sum()) * ms_solver)),
                            k_B=k_b, static_catch_B=float(bl.at_k(c_static, k_b)) if k_b > 0 else 0.0,
                            global_gate=dict(escalation=h5["escalation"], missed=h5["missed"], gate_catch=h5["gate_catch"],
                                             speedup_B=h5["speedup_B"], static_catch_B=h5["static_catch_B"], k_B=h5["k_B"])))
            print(f"seed {seed} {fam}: Mondrian esc {100 * esc.mean():.1f}% missed {100 * missed:.2f}% catch "
                  f"{100 * (1 - missed):.2f} static {100 * per[-1]['static_catch_B']:.2f} (k_B {k_b}) | global missed "
                  f"{100 * h5['missed']:.2f}%", flush=True)

    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise ValueError("decision rule changed since hashing; stop")
    summary = []
    for fam in FAMILIES:
        m = [r for r in per if r["family"] == fam]
        s = dict(family=fam)
        for k in ["escalation", "flag_share", "solve_share_B", "missed", "gate_catch", "coverage_emp", "speedup_A",
                  "speedup_B", "static_catch_B", "k_B"]:
            s[k + "_mean"], s[k + "_std"] = ms_([r[k] for r in m])
        for k in ["escalation", "missed", "gate_catch", "speedup_B", "static_catch_B"]:
            s["global_" + k + "_mean"], s["global_" + k + "_std"] = ms_([r["global_gate"][k] for r in m])
        s["splits_missed_le_1pct"] = len([r for r in m if r["missed"] <= 0.01])
        s["gap"] = s["gate_catch_mean"] - s["static_catch_B_mean"]
        s["STD"] = max(s["gate_catch_std"], s["static_catch_B_std"])
        s["gate_higher_by_std_rule"] = bool(s["gap"] > s["STD"])
        summary.append(s)
    prim = [s for s in summary if s["family"] == "histgb"][0]
    verdict = dict(MONDRIAN_BEATS_STATIC=prim["gate_higher_by_std_rule"], gate_catch_mean=prim["gate_catch_mean"],
                   gate_catch_std=prim["gate_catch_std"], static_catch_mean=prim["static_catch_B_mean"],
                   static_catch_std=prim["static_catch_B_std"], gap=prim["gap"], STD=prim["STD"],
                   rule="histgb, held-out target, rule B: mean(gate catch) - mean(static catch at Mondrian k_B) > max(std gate, std static)")
    out = dict(part="N11 Part 6: Mondrian calibration vs static", decision_rule=RULE, decision_rule_sha256=h,
               decision_rule_hash_verified=True, verdict=verdict, summary=summary, per_split=per, min_cal_rows=MIN_CAL,
               std_convention="population std (ddof=0) over 5 splits", ms_solver=ms_solver, wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    params = dict(seeds=SEEDS, families=FAMILIES, limit=LIMIT, min_cal_rows=MIN_CAL,
                  model_hyperparameters=[dict(seed=f["seed"], family=f["family"], tag=f["tag"], config=f["config"]) for f in n5json["fits"]],
                  solver_settings="no solve; D94 corrected labels (N2)")
    man = sm.build_manifest([OUT], "scratch/n11_mondrian.py", [".venv/bin/python", "scratch/n11_mondrian.py"],
                            [N5, "data/dataset.parquet", "data/sts_n2_label_audit.parquet", RULE], params, "")
    man["no_new_solves"] = "No AC solve. Model fits: N5 D94 M2 configs refit per split."
    sm.write_manifest(man, OUT)
    print(json.dumps(verdict, indent=1))


if __name__ == "__main__":
    main()
