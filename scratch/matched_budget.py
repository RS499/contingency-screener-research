import os
import sys
import json
import time
import hashlib
import platform
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import make_splits as ms
import gate_eval as ge
import manifest as mf
import baselines as bl

# Matched-budget comparison: static line ranking vs the ridge and histgb gates at equal solver
# calls, coverage targets 0.90-0.98. Stored (committed pandapower) labels throughout.
#   Accounting A (the paper's Eq. 2): gate solver calls = escalated contingencies only.
#   Accounting B: flagged contingencies are also solved (an operator re-solves predicted violations).
# Budget for the static ranking = the same share of contingencies, k = round(share * rows per
# scenario), the same k for every test scenario (baselines.py definition).
# Gate catch rate = share of true violations NOT silently certified = 1 - missed_viol (escalated or
# flagged). Under A the gate's flagged violations cost no solver call; the strict like-for-like
# number under A is the escalate-only capture, also reported.

DATASET = "data/dataset.parquet"
PRED = "data/sts_n1_predictions_long.parquet"
TUNED = "data/tuned_metrics.json"
BASELINES = "data/baselines.json"
OUT = "data/sts_matched_budget.json"
LIMIT = 0.94
SEEDS = [0, 1, 2, 3, 4]
TARGETS = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98]
FAMILIES = ["ridge", "histgb"]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mean_std(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def main():
    t0 = time.time()
    df, feature_cols = ms.load_dataset(DATASET)
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    n_line = 173
    is_trafo = df["outaged_type"].to_numpy() == "trafo"
    elem_key = df["outaged_idx"].to_numpy(np.int64) + np.where(is_trafo, n_line, 0)
    scen_all = df["scenario_id"].to_numpy(np.int64)
    viol_all = df["violation"].to_numpy(bool)
    pred = pd.read_parquet(PRED)
    tuned = json.load(open(TUNED))
    base = json.load(open(BASELINES))

    per_seed = []
    checks = []
    for seed in SEEDS:
        splits = ms.make_splits(groups, seed)
        te = splits["test"]
        train_mask = np.zeros(len(df), dtype=bool)
        train_mask[splits["train"]] = True
        stat_score, _ = bl.static_severity_score(df, train_mask, elem_key)
        scen = scen_all[te]
        viol = viol_all[te]
        k_max = int(pd.Series(scen).value_counts().max())
        curve, n_viol, _ = bl.capture_curve(scen, stat_score[te], elem_key[te].astype(float), viol, k_max)
        rows_per_scen = len(te) / len(np.unique(scen))
        checks.append(dict(seed=seed, static_at_89=float(curve[88]), static_at_138=float(curve[137]),
                           baselines_json_curve_mean_89=base["comparators"]["static_severity"]["curve_mean"][88]))

        for fam in FAMILIES:
            p = pred[(pred.seed == seed) & (pred.family == fam)]
            ca = p[p.split == "cal"]
            ts = p[p.split == "test"].sort_values("row_pos")
            if not np.array_equal(ts.row_pos.to_numpy(), np.sort(te)):
                raise ValueError("test rows in predictions do not match make_splits test rows")
            yt = ts.y.to_numpy()
            pt = ts.pred.to_numpy()
            true_v = yt < LIMIT
            for tgt in TARGETS:
                q = ge.calibrate_qhat(ca.pred.to_numpy(), ca.y.to_numpy(), tgt)
                certify = (pt - q) >= LIMIT
                flag = pt < LIMIT
                esc = (~certify) & (~flag)
                esc_share = float(esc.mean())
                solve_b = float((esc | flag).mean())
                missed = float((certify & true_v).sum() / true_v.sum())
                cap_esc_only = float((esc & true_v).sum() / true_v.sum())
                k_a = int(round(esc_share * rows_per_scen))
                k_b = int(round(solve_b * rows_per_scen))
                per_seed.append(dict(seed=seed, family=fam, target=tgt, q_hat=float(q),
                                     escalation=esc_share, flag_share=float(flag.mean()),
                                     solve_share_B=solve_b, missed=missed,
                                     gate_catch=1.0 - missed, gate_catch_escalate_only=cap_esc_only,
                                     k_A=k_a, k_B=k_b,
                                     static_catch_A=float(curve[max(k_a, 1) - 1]) if k_a > 0 else 0.0,
                                     static_catch_B=float(curve[max(k_b, 1) - 1]) if k_b > 0 else 0.0,
                                     rows_per_scenario=rows_per_scen))

    ps = pd.DataFrame(per_seed)
    # reproduction check against the committed sweep
    repro = []
    for r in tuned["records"]:
        if r.get("metric") != "m2":
            continue
        for s in r["sweep"]:
            tg = round(float(s["coverage_target"]), 2)
            if tg not in TARGETS:
                continue
            m = ps[(ps.seed == r["seed"]) & (ps.family == r["family"]) & (ps.target == tg)]
            if len(m) == 1:
                repro.append(dict(seed=r["seed"], family=r["family"], target=tg,
                                  d_esc=abs(float(m.escalation.iloc[0]) - float(s["escalation"])),
                                  d_missed=abs(float(m.missed.iloc[0]) - float(s["missed_viol"]))))
    rp = pd.DataFrame(repro)

    table = []
    for fam in FAMILIES:
        for tgt in TARGETS:
            m = ps[(ps.family == fam) & (ps.target == tgt)]
            row = dict(family=fam, target=tgt)
            for col in ["escalation", "flag_share", "solve_share_B", "gate_catch", "gate_catch_escalate_only",
                        "static_catch_A", "static_catch_B", "k_A", "k_B"]:
                mu, sd = mean_std(m[col])
                row[col + "_mean"] = mu
                row[col + "_std"] = sd
            for acc, g_col, s_col in [("A_vs_gate_catch", "gate_catch", "static_catch_A"),
                                      ("A_strict_escalate_only", "gate_catch_escalate_only", "static_catch_A"),
                                      ("B_flags_solved", "gate_catch", "static_catch_B")]:
                gm, gs = mean_std(m[g_col])
                sm, ss = mean_std(m[s_col])
                gap = gm - sm
                larger = max(gs, ss)
                if abs(gap) > larger:
                    verdict = "gate higher" if gap > 0 else "static higher"
                else:
                    verdict = "tie (gap within larger std)"
                row["std_rule_" + acc] = verdict
            table.append(row)

    out = dict(
        question="static line ranking vs ridge/histgb gates at equal solver calls, targets 0.90-0.98",
        labels="stored pandapower labels (data/dataset.parquet violation / y); N2-corrected labels NOT used",
        accountings=dict(A="gate solver calls = escalated share (paper Eq. 2); static solves the same share",
                         B="gate solver calls = escalated + flagged share; static solves the same share"),
        catch_definitions=dict(gate_catch="1 - missed_viol: true violations escalated or flagged",
                               gate_catch_escalate_only="true violations in the escalated set only",
                               static_catch="true violations among the top-k statically ranked contingencies per test scenario"),
        std_convention="population std (ddof=0) over 5 seeds; std rule: difference real only if |gap| > larger std",
        k_rule="k = round(share * mean converged test rows per scenario), same k for every scenario",
        reproduction=dict(
            tuned_metrics_max_abs_diff_escalation=float(rp.d_esc.max()),
            tuned_metrics_max_abs_diff_missed=float(rp.d_missed.max()),
            n_cells_compared=int(len(rp)),
            static_curve_seed_mean_at_89=float(np.mean([c["static_at_89"] for c in checks])),
            static_curve_seed_mean_at_138=float(np.mean([c["static_at_138"] for c in checks])),
            baselines_json_curve_mean_at_89=base["comparators"]["static_severity"]["curve_mean"][88],
            baselines_json_curve_mean_at_138=base["comparators"]["static_severity"]["curve_mean"][137]),
        table=table,
        per_seed=per_seed,
        wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    man = dict(artifacts=[OUT], generating_script="scratch/matched_budget.py",
               regeneration_argv=[".venv/bin/python", "scratch/matched_budget.py"],
               script_sha256=sha256_of("scratch/matched_budget.py"),
               inputs={pth: sha256_of(pth) for pth in [DATASET, PRED, TUNED, BASELINES]},
               model_hyperparameters="M2 per-seed configs as recorded in data/tuned_metrics.json (predictions from data/sts_n1_predictions_long.parquet, a refit that reproduces tuned_metrics exactly)",
               limit=LIMIT, targets=TARGETS, seeds=SEEDS,
               packages={p: mf.pkg_version(p) for p in mf.PACKAGES}, python=platform.python_version(),
               output_sha256=sha256_of(OUT),
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(OUT.replace(".json", ".manifest.json"), "w") as f:
        json.dump(man, f, indent=2)
    print(json.dumps(out["reproduction"], indent=1))
    for r in table:
        print(f"{r['family']:6s} {r['target']:.2f} | A: esc {100*r['escalation_mean']:5.1f}% gate {100*r['gate_catch_mean']:6.2f}±{100*r['gate_catch_std']:.2f} "
              f"(esc-only {100*r['gate_catch_escalate_only_mean']:5.2f}) static {100*r['static_catch_A_mean']:6.2f}±{100*r['static_catch_A_std']:.2f} [{r['std_rule_A_vs_gate_catch']}] | "
              f"B: solve {100*r['solve_share_B_mean']:5.1f}% static {100*r['static_catch_B_mean']:6.2f}±{100*r['static_catch_B_std']:.2f} [{r['std_rule_B_flags_solved']}]")


if __name__ == "__main__":
    main()
