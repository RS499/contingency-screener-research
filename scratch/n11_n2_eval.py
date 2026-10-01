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
import tune_surrogates as tu
import sts_manifest as sm
import n9_budget_curve as bc

# N11 Part 1 evaluation (scratch/n11_decision_rule.md §1): N-1 -> N-2 coverage.
# - Models: the N5 D94 M2 configs, refit per split on D94 train (corrected labels); q_hat from the split's N-1 cal.
#   Nothing is refit on N-2 data.
# - N-2 rows (data/sts_n11_n2_rows.parquet) of the split's TEST base cases get the base case's scenario features
#   (from data/dataset.parquet) and a two-hot branch encoding (1 in both outaged branches' br_ columns).
# - Check before the verdict: for every split and family, the refit reproduces the N5 N-1 test escalation and
#   missed at 0.90 exactly; stop if not.
# - COVERAGE-HOLDS-N2 (histgb, target 0.90): mean(cov_N2) >= 0.90 - max(std cov_N2, std cov_N1).
# - Pinned-nonconverged N-2 rows are reported separately and excluded; failed corrected solves are dropped and
#   counted (stop if > 0.5% of converged N-2 rows).

RULE = "scratch/n11_decision_rule.md"
RULE_SHA = "scratch/n11_decision_rule.sha256"
N2ROWS = "data/sts_n11_n2_rows.parquet"
N5 = "data/sts_n5_gate_094.json"
OUT = "data/sts_n11_n2.json"
LIMIT = 0.94
SEEDS = [0, 1, 2, 3, 4]
FAMILIES = ["ridge", "histgb"]
FAIL_CEIL = 0.005


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def n5_grid(n5json, seed, fam, tgt):
    for p in n5json["points"]:
        if p["seed"] == seed and p["family"] == fam and p["point"] == "grid" and abs(p["target"] - tgt) < 1e-9:
            return p
    return None


def two_hot_matrix(d, kept, n2rows):
    # scenario features: first converged N-1 row of each base case (scenario features are constant within a base)
    df = d["df"]
    first = df.groupby("scenario_id").head(1)
    scen_cols = [c for c in kept if not c.startswith("br_")]
    base = d["X"].loc[first.index, scen_cols].copy()
    base.index = first["scenario_id"].to_numpy()
    pos = {c: i for i, c in enumerate(kept)}
    arr = np.zeros((len(n2rows), len(kept)), dtype=np.float32)
    arr[:, [pos[c] for c in scen_cols]] = base.loc[n2rows["scenario_id"].to_numpy()].to_numpy(np.float32)
    col_a = "br_" + n2rows["a_type"].astype(str) + "_" + n2rows["a_idx"].astype(str)
    col_b = "br_" + n2rows["b_type"].astype(str) + "_" + n2rows["b_idx"].astype(str)
    missing = 0
    for r, (ca, cb) in enumerate(zip(col_a, col_b)):
        for c in (ca, cb):
            if c in pos:
                arr[r, pos[c]] = 1.0
            else:
                missing += 1
    return arr, missing


def gate_metrics(p_ca, y_ca, p, y, tgt, ms_surr, ms_solver):
    q = ge.calibrate_qhat(p_ca, y_ca, tgt)
    certify = (p - q) >= LIMIT
    flag = p < LIMIT
    esc = (~certify) & (~flag)
    tv = y < LIMIT
    n = len(y)
    return dict(target=float(tgt), q_hat=float(q), coverage=float((y >= p - q).mean()), escalation=float(esc.mean()),
                flag_share=float(flag.mean()), missed=float((certify & tv).sum() / max(int(tv.sum()), 1)),
                speedup_A=float(n * ms_solver / (n * ms_surr + esc.sum() * ms_solver)),
                speedup_B=float(n * ms_solver / (n * ms_surr + (esc.sum() + flag.sum()) * ms_solver)),
                n=int(n), n_true_viol=int(tv.sum()))


def main():
    t0 = time.time()
    n5json = json.load(open(N5))
    ms_solver = n5json["ms_solver"]
    d = bc.load("094")
    rows = pd.read_parquet(N2ROWS)
    conv = rows["pinned_converged"].to_numpy(bool)
    ok = rows["corrected_status"].isin(["converged", "not_needed"]).to_numpy()
    n_fail = int((conv & ~ok).sum())
    fail_share = n_fail / max(int(conv.sum()), 1)
    if fail_share > FAIL_CEIL:
        raise ValueError(f"N-2 corrected failed share {fail_share:.4f} > 0.5%; stop")
    use = rows[conv & ok].reset_index(drop=True)
    per = []
    checks = []
    for seed in SEEDS:
        splits = ms.make_splits(d["groups"], seed)
        kept = ms.select_features(d["X"], splits["train"])
        te = splits["test"]
        test_scen = set(d["df"]["scenario_id"].to_numpy()[te].tolist())
        sub = use[use["scenario_id"].isin(test_scen)].reset_index(drop=True)
        sub_all = rows[rows["scenario_id"].isin(test_scen)]
        X2, missing = two_hot_matrix(d, kept, sub)
        X1 = d["X"][kept].iloc[te].to_numpy(np.float32)
        y1 = d["y"][te]
        y2 = sub["corrected_min_vm"].to_numpy(np.float64)
        for fam in FAMILIES:
            f5 = bc.n5_config(n5json, seed, fam)
            h5 = bc.n5_held_out(n5json, seed, fam)
            g90 = n5_grid(n5json, seed, fam, 0.90)
            # fit as bc.fit_predict does; predict N-1 and N-2 rows SEPARATELY (a stacked matrix changes the BLAS
            # blocking of a linear model's matmul and can move a prediction by an ulp; fix logged in N11 status)
            Xk = d["X"][kept]
            fitted = tu.fit_one(fam, f5["config"], Xk.iloc[splits["train"]].to_numpy(np.float32), d["y"][splits["train"]], seed)
            p_ca = tu.predict(fitted, Xk.iloc[splits["cal"]].to_numpy(np.float32))
            y_ca = d["y"][splits["cal"]]
            p1 = tu.predict(fitted, X1)
            p2 = tu.predict(fitted, X2)
            m1 = gate_metrics(p_ca, y_ca, p1, y1, 0.90, f5["ms_surrogate"], ms_solver)
            exact = bool(m1["escalation"] == g90["escalation"] and m1["missed"] == g90["missed"])
            checks.append(dict(seed=seed, family=fam, esc=m1["escalation"], esc_n5=g90["escalation"],
                               missed=m1["missed"], missed_n5=g90["missed"], exact=exact))
            print(f"seed {seed} {fam}: N-1 reproduction exact={exact}", flush=True)
            if not exact:
                raise ValueError("refit does not reproduce N5 N-1 test numbers at 0.90; stop")
            for tgt, kind in [(0.90, "t090"), (h5["target"], "held_out")]:
                m2 = gate_metrics(p_ca, y_ca, p2, y2, tgt, f5["ms_surrogate"], ms_solver)
                n1 = gate_metrics(p_ca, y_ca, p1, y1, tgt, f5["ms_surrogate"], ms_solver)
                adj = sub["adjacent"].to_numpy(bool)
                q = m2["q_hat"]
                rec = dict(seed=seed, family=fam, point=kind, n2=m2, n1=n1,
                           coverage_n2_adjacent=float((y2[adj] >= p2[adj] - q).mean()) if adj.any() else None,
                           coverage_n2_nonadjacent=float((y2[~adj] >= p2[~adj] - q).mean()) if (~adj).any() else None,
                           n_adjacent=int(adj.sum()), n2_rows_test=int(len(sub)),
                           n2_rows_test_all=int(len(sub_all)),
                           n2_nonconverged_test=int((~sub_all["pinned_converged"]).sum()),
                           n2_violation_rate=float((y2 < LIMIT).mean()), two_hot_missing_cols=int(missing))
                per.append(rec)
                if fam == "histgb":
                    print(f"  {kind} {tgt:.2f}: N-2 cov {m2['coverage']:.4f} missed {100 * m2['missed']:.2f}% "
                          f"esc {100 * m2['escalation']:.1f}% | N-1 cov {n1['coverage']:.4f}", flush=True)

    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise ValueError("decision rule changed since hashing; stop")
    summary = []
    for fam in FAMILIES:
        for kind in ["t090", "held_out"]:
            m = [r for r in per if r["family"] == fam and r["point"] == kind]
            s = dict(family=fam, point=kind)
            for side in ["n2", "n1"]:
                for k in ["coverage", "missed", "escalation", "flag_share", "speedup_A", "speedup_B", "target"]:
                    s[f"{side}_{k}_mean"], s[f"{side}_{k}_std"] = ms_([r[side][k] for r in m])
            s["n2_splits_missed_le_1pct"] = len([r for r in m if r["n2"]["missed"] <= 0.01])
            for k in ["coverage_n2_adjacent", "coverage_n2_nonadjacent", "n2_violation_rate"]:
                s[k + "_mean"], s[k + "_std"] = ms_([r[k] for r in m])
            s["threshold"] = 0.90 - max(s["n2_coverage_std"], s["n1_coverage_std"]) if kind == "t090" else None
            summary.append(s)
    prim = [s for s in summary if s["family"] == "histgb" and s["point"] == "t090"][0]
    holds = bool(prim["n2_coverage_mean"] >= prim["threshold"])
    verdict = dict(COVERAGE_HOLDS_N2=holds, coverage_n2_mean=prim["n2_coverage_mean"], coverage_n2_std=prim["n2_coverage_std"],
                   coverage_n1_std=prim["n1_coverage_std"], threshold=prim["threshold"],
                   shortfall=(None if holds else prim["threshold"] - prim["n2_coverage_mean"]),
                   rule="histgb, target 0.90: mean(cov_N2) >= 0.90 - max(std cov_N2, std cov_N1)")
    out = dict(part="N11 Part 1: N-1 -> N-2 coverage", decision_rule=RULE, decision_rule_sha256=h,
               decision_rule_hash_verified=True, verdict=verdict, summary=summary, per_split=per,
               reproduction_of_n5_n1=checks,
               n2_rows=dict(total=int(len(rows)), pinned_nonconverged=int((~conv).sum()),
                            pinned_nonconverged_share=float((~conv).mean()), corrected_failed=n_fail,
                            corrected_failed_share_of_converged=fail_share, used=int(len(use))),
               std_convention="population std (ddof=0) over 5 splits", ms_solver=ms_solver, wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    params = dict(seeds=SEEDS, families=FAMILIES, limit=LIMIT, targets=["0.90", "held-out (N5 m2_inner_cov_at)"],
                  model_hyperparameters=[dict(seed=f["seed"], family=f["family"], tag=f["tag"], config=f["config"]) for f in n5json["fits"]],
                  encoding="scenario features of the base case + two-hot branch columns",
                  solver_settings="N-2 labels from data/sts_n11_n2_rows.parquet (pinned pandapower + N2 switch-back)")
    man = sm.build_manifest([OUT], "scratch/n11_n2_eval.py", [".venv/bin/python", "scratch/n11_n2_eval.py"],
                            [N2ROWS, N5, "data/dataset.parquet", "data/sts_n2_label_audit.parquet", RULE], params, "")
    man["no_new_solves"] = "No AC solve. Model fits: N5 D94 M2 configs refit per split (no search)."
    sm.write_manifest(man, OUT)
    print(json.dumps(verdict, indent=1))


if __name__ == "__main__":
    main()
