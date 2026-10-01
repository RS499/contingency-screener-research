import os
import sys
import json
import time
import hashlib
import subprocess
import numpy as np
import pandas as pd
import pandapower as pp
from scipy.stats import beta
from pandapower.converter.matpower.to_mpc import to_mpc

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import generate_dataset as gd
import sts_n2_label_audit as n2
import sts_manifest as sm

# N10 Part A: independent-solver label check (scratch/n10_decision_rule.md, Part A).
# Rows: the 201 rows of data/sts_label_crosscheck_rows.parquet (100 viol_to_safe, 100 safe_to_viol, and the named
# worst case 101000025 / line 78). Each case is rebuilt as scratch/label_crosscheck.py does (replay of the committed
# generator RNG, apply_scenario, branch out), exported with pandapower.converter.matpower.to_mpc (init="flat"),
# and solved in MATPOWER under Octave by scratch/n10_switchback.m (M0, M1, M2).
# Checks (each with an exact 95% Clopper-Pearson interval), over all 201 rows; the 200 sampled rows are also
# reported. A row whose MATPOWER solve does not converge counts as a failure of the check.
#   A0  |M0 min_vm - pandapower no-limit min_vm| <= 1e-6 on >= 99% of rows
#   A1  M1 label == stored label on >= 95% of rows
#   A2  M2 label == N2 label on >= 95% of rows AND named worst case M2 min_vm >= 0.94  (primary)

ROWS = "data/sts_label_crosscheck_rows.parquet"
RULE = "scratch/n10_decision_rule.md"
RULE_SHA = "scratch/n10_decision_rule.sha256"
CASE_DIR = "scratch/n10_mpc_cases"
OUT = "data/sts_n10_matpower_check.parquet"
OUT_JSON = "data/sts_n10_matpower_check.json"
LIMIT = 0.94
TOL_A0 = 1e-6
WORST = (101000025, "line", 78)


def clopper_pearson(k, n):
    if n == 0:
        return [float("nan"), float("nan")]
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return [lo, hi]


def share_check(ok_mask, need):
    k = int(ok_mask.sum())
    n = int(len(ok_mask))
    return dict(k=k, n=n, share=k / n, ci95=clopper_pearson(k, n), threshold=need, passes=bool(k / n >= need))


def export_cases(rows):
    os.makedirs(CASE_DIR, exist_ok=True)
    gd.apply_config(n2.CFG)
    mlists = n2.mode_lists()
    scen_params = {}
    for s0 in sorted(set((rows.scenario_id // 1_000_000).astype(int).tolist())):
        w = n2.SHARD_SEEDS.index(s0)
        rep = n2.replay_shard((s0, n2.N_TOTAL // len(n2.SHARD_SEEDS), mlists[w]))
        for sc in rep["scenarios"]:
            scen_params[sc["scenario_id"]] = sc["params"]
    pp_min = []
    for rid, r in rows.iterrows():
        net = gd.build_net("case118")
        gd.apply_scenario(net, scen_params[int(r.scenario_id)])
        net[r.outaged_type].at[int(r.outaged_idx), "in_service"] = False
        to_mpc(net, filename=os.path.join(CASE_DIR, f"row_{rid:03d}.mat"), init="flat")
        pp.runpp(net, enforce_q_lims=False, init="dc", numba=True)
        pp_min.append(float(np.nanmin(net.res_bus.vm_pu.values)))
    pd.DataFrame(dict(row_id=rows.index.to_numpy(), file=[f"row_{i:03d}.mat" for i in rows.index])).to_csv(
        os.path.join(CASE_DIR, "index.csv"), index=False, columns=["row_id"])
    return np.array(pp_min)


def main():
    t0 = time.time()
    rows = pd.read_parquet(ROWS)[["scenario_id", "outaged_type", "outaged_idx", "stratum", "stored_min_vm",
                                  "n2_min_vm", "stored_violation", "n2_violation"]].reset_index(drop=True)
    pp_nolim = export_cases(rows)
    t_export = time.time() - t0
    oct = subprocess.run(["octave", "--no-gui", "--quiet", "scratch/n10_switchback.m", CASE_DIR],
                         capture_output=True, text=True)
    print(oct.stdout.strip(), flush=True)
    if oct.returncode != 0:
        print(oct.stderr[-2000:])
        raise RuntimeError("octave failed")
    res = pd.read_csv(os.path.join(CASE_DIR, "matpower_results.csv"))
    df = rows.merge(res, left_index=True, right_on="row_id", how="left").reset_index(drop=True)
    df["pp_nolim_min_vm"] = pp_nolim
    df["a0_abs_diff"] = (df["m0_min_vm"] - df["pp_nolim_min_vm"]).abs()
    df["m1_violation"] = df["m1_min_vm"] < LIMIT
    df["m2_violation"] = df["m2_min_vm"] < LIMIT
    m0_ok = df["m0_success"] == 1
    m1_ok = df["m1_success"] == 1
    m2_ok = df["m2_status"] == "converged"
    df["a0_ok"] = m0_ok & (df["a0_abs_diff"] <= TOL_A0)
    df["a1_ok"] = m1_ok & (df["m1_violation"] == df["stored_violation"])
    df["a2_ok"] = m2_ok & (df["m2_violation"] == df["n2_violation"])
    df.to_parquet(OUT, index=False)

    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise ValueError("decision rule changed since hashing; stop")
    is_w = (df.scenario_id == WORST[0]) & (df.outaged_type == WORST[1]) & (df.outaged_idx == WORST[2])
    w = df[is_w].iloc[0]
    sample = df[~is_w]
    checks = {}
    for scope, d in [("all_201", df), ("sample_200", sample)]:
        checks[scope] = dict(A0=share_check(d["a0_ok"].to_numpy(), 0.99),
                             A1=share_check(d["a1_ok"].to_numpy(), 0.95),
                             A2_share=share_check(d["a2_ok"].to_numpy(), 0.95))
    worst_ok = bool(w["m2_status"] == "converged" and w["m2_min_vm"] >= LIMIT)
    a0 = checks["all_201"]["A0"]["passes"]
    a1 = checks["all_201"]["A1"]["passes"]
    a2 = checks["all_201"]["A2_share"]["passes"] and worst_ok
    verdict = dict(A0_pass=a0, A1_pass=a1, A2="CONFIRMED" if a2 else "NOT CONFIRMED",
                   A2_marking=("" if (a0 and a1) else "export not validated"),
                   named_worst_case=dict(m0_min_vm=float(w["m0_min_vm"]), m1_min_vm=float(w["m1_min_vm"]),
                                         m2_status=str(w["m2_status"]), m2_min_vm=float(w["m2_min_vm"]),
                                         m2_n_outer=int(w["m2_n_outer"]), stored_min_vm=float(w["stored_min_vm"]),
                                         n2_min_vm=float(w["n2_min_vm"]), m2_ge_limit=worst_ok),
                   scope_of_verdict="all 201 rows (the 200 sampled rows plus the named worst case)")
    by_stratum = {}
    for s in ["viol_to_safe", "safe_to_viol"]:
        d = df[df.stratum == s]
        by_stratum[s] = dict(n=int(len(d)), a1_agree=int(d["a1_ok"].sum()), a2_agree=int(d["a2_ok"].sum()),
                             m2_status_counts={str(k): int(v) for k, v in d["m2_status"].value_counts().items()})
    diag = dict(a0_max_abs_diff=float(df["a0_abs_diff"].max()),
                m1_minus_stored_max_abs=float((df["m1_min_vm"] - df["stored_min_vm"]).abs().max()),
                m2_minus_n2_max_abs=float((df.loc[m2_ok, "m2_min_vm"] - df.loc[m2_ok, "n2_min_vm"]).abs().max()),
                m2_minus_n2_median_abs=float((df.loc[m2_ok, "m2_min_vm"] - df.loc[m2_ok, "n2_min_vm"]).abs().median()),
                m0_nonconverged=int((~m0_ok).sum()), m1_nonconverged=int((~m1_ok).sum()),
                m2_status_counts={str(k): int(v) for k, v in df["m2_status"].value_counts().items()})
    ver = subprocess.run(["octave", "--no-gui", "--quiet", "--eval",
                          "addpath(genpath('~/matpower')); v=mpver('all'); printf('%s|%s\\n', v.Version, version())"],
                         capture_output=True, text=True).stdout.strip().splitlines()[-1]
    out = dict(part="N10 Part A: independent-solver (MATPOWER) label check", decision_rule=RULE,
               decision_rule_sha256=h, decision_rule_hash_verified=True, verdict=verdict, checks=checks,
               by_stratum=by_stratum, diagnostics=diag,
               matpower_version=ver.split("|")[0], octave_version=ver.split("|")[1],
               export="pandapower.converter.matpower.to_mpc(net, init='flat')",
               alignment_note="slack (ext_grid) generator QMAX/QMIN set to +/-Inf for M1/M2, because pandapower's enforce_q_lims never limits the ext_grid",
               nonconvergence_rule="a MATPOWER solve that does not converge counts as a failure of the check",
               export_wall_s=t_export, wall_s=time.time() - t0)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    params = dict(limit=LIMIT, tol_a0=TOL_A0, switchback_tol_q_mvar=1e-3, switchback_tol_v_pu=1e-3, max_outer=30,
                  matpower_options=dict(alg="NR", tol=1e-8, nr_max_it=30, enforce_q_lims="M0: 0; M1, M2: 1"),
                  matpower=out["matpower_version"], octave=out["octave_version"],
                  case_generator_config=n2.CFG, model_hyperparameters="none (no model fit)")
    man = sm.build_manifest([OUT, OUT_JSON], "scratch/n10_matpower_check.py",
                            [".venv/bin/python", "scratch/n10_matpower_check.py"],
                            [ROWS, "scratch/n10_switchback.m", "scripts/sts_n2_label_audit.py",
                             "feasibility/generate_dataset.py", RULE], params, "")
    man["no_new_solves"] = "FALSE: pandapower no-limit solve per row, plus MATPOWER M0/M1/M2 solves under Octave"
    sm.write_manifest(man, OUT)
    print(json.dumps(dict(verdict=verdict, checks=checks["all_201"], diagnostics=diag), indent=1))


if __name__ == "__main__":
    main()
