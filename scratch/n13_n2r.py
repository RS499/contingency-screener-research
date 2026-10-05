import os
import sys
import json
import time
import multiprocessing
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import n13_common as c
import generate_dataset as gd
import sts_n2_label_audit as n2
import n11_n2_build as n11b
import label_crosscheck as lc
import sts_manifest as sm

# N13 N2R (scratch/n13_decision_rule.md §1-§2): the N-2 rows of scratch/n11_n2_build.py (draw_pairs, solve_shard,
# imported unchanged; pinned solve + N2 switch-back, both branches out) on the REBUILT D94 base cases (parameters from
# the D94 rebuild's phase-1 files). Same pair rule: 50 unordered pairs per base, in scenario_id order, numpy seed
# 20261001. One file per shard (seeds 100-103), skipped on restart.
# Checks: 3 (bases common to the old D94, i.e. same parameter hash, AND the same pair: pinned and corrected minima
# equal the old N-2 rows exactly / within 1e-9; statuses agree); 5 (failed switch-back <= 0.5% of rows); 6 (the
# label_crosscheck independent solver on 200 rows per stratum a-d, seed 20261004, both branches out; the N-0 states
# are D94's, already checked). Check 1/4 are D94's.
# Output: data/sts_n13_N2R.parquet (schema of data/sts_n11_n2_rows.parquet), data/sts_n13_build_N2R.json,
# data/sts_n13_indep_N2R.json, each with a manifest.

WORK = "scratch/n13_build/N2R"
OLD = "data/sts_n11_n2_rows.parquet"
OUT = "data/sts_n13_N2R.parquet"
NPROC = 8
SEED6 = 20261004
N_PER = 200
LIMIT = 0.94
TOL3 = 1e-9


def indep_pair(task):
    sid, ta, ia, tb, ib, params_json, ref_min = task
    gd.apply_config(n2.CFG)
    net = gd.build_net("case118")
    gd.apply_scenario(net, c.params_from_json(params_json))
    net[ta].at[int(ia), "in_service"] = False
    net[tb].at[int(ib), "in_service"] = False
    rec = dict(scenario_id=sid, ref_min=ref_min)
    try:
        m = lc.network_model(net)
    except Exception:
        rec.update(model_ok=False, indep_converged=False, consistent=False)
        return rec
    v = lc.solve(m, "pv")
    rec["pv_converged"] = bool(v["converged"])
    rec["pv_minus_pp_nolim"] = abs(float(v["vm"].min()) - m["pp_nolim_min"]) if v["converged"] else None
    r = lc.solve(m, "cc")
    rec["indep_converged"] = bool(r["converged"])
    if not r["converged"]:
        rec["consistent"] = False
        return rec
    ok, _n = lc.consistency(m, r)
    rec["consistent"] = bool(ok)
    rec["indep_min"] = float(r["vm"].min())
    rec["abs_diff"] = abs(rec["indep_min"] - ref_min)
    return rec


def main():
    t0 = time.time()
    os.makedirs(WORK, exist_ok=True)
    spec = c.DATASETS["D94"]
    bases = []
    for s in spec["seeds"]:
        bases.extend(json.load(open(f"scratch/n13_build/D94/phase1_{s}.json"))["accepted"])
    by_sid = {}
    for b in bases:
        by_sid[b["scenario_id"]] = b
    scen_ids = sorted(by_sid.keys())
    gd.apply_config(n2.CFG)
    net = gd.build_net("case118")
    n_branch = len(gd.branch_list(net))
    pairs = n11b.draw_pairs(scen_ids, n_branch)
    tasks = []
    for s in spec["seeds"]:
        sl = [dict(scenario_id=sid, params=c.params_from_json(by_sid[sid]["params"])) for sid in scen_ids if sid // 1_000_000 == s]
        tasks.append((os.path.join(WORK, f"shard_{s}.parquet"), sl, {x["scenario_id"]: pairs[x["scenario_id"]] for x in sl}))
    with multiprocessing.Pool(4) as pool:
        paths = pool.map(n11b.solve_shard, tasks)
    res = pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True)
    res = res.sort_values(["scenario_id", "a_pos", "b_pos"]).reset_index(drop=True)
    old = pd.read_parquet(OLD)
    schema_same = list(res.columns) == list(old.columns)
    dtype_diff = [col for col in old.columns if col in res.columns and res[col].dtype != old[col].dtype]
    res.to_parquet(OUT, index=False)
    print(f"N2R built: {len(res)} rows [{time.time() - t0:.0f}s]; schema same {schema_same}, dtype diffs {dtype_diff}", flush=True)
    # check 3: common bases (parameter hash) and the same pair
    old_hash = pd.concat([pd.read_parquet(f"scratch/n13_drawlogs/old_D94_{s}.parquet") for s in spec["seeds"]])
    old_hash = old_hash[old_hash.accepted][["params_hash", "scenario_id"]]
    new_hash = pd.DataFrame([dict(params_hash=by_sid[s]["params_hash"], scenario_id=s) for s in scen_ids])
    com = old_hash.merge(new_hash, on="params_hash", suffixes=("_old", "_new"))
    o = old.merge(com[["scenario_id_old", "scenario_id_new"]], left_on="scenario_id", right_on="scenario_id_old")
    m = o.merge(res, left_on=["scenario_id_new", "a_pos", "b_pos"], right_on=["scenario_id", "a_pos", "b_pos"], suffixes=("_o", "_n"))
    both = m["pinned_converged_o"].to_numpy(bool) & m["pinned_converged_n"].to_numpy(bool)
    pin_diff = np.abs(m.loc[both, "pinned_min_vm_o"].to_numpy() - m.loc[both, "pinned_min_vm_n"].to_numpy())
    ok_o = m["corrected_status_o"].isin(["converged", "not_needed"]).to_numpy()
    ok_n = m["corrected_status_n"].isin(["converged", "not_needed"]).to_numpy()
    cor_diff = np.abs(m.loc[ok_o & ok_n, "corrected_min_vm_o"].to_numpy() - m.loc[ok_o & ok_n, "corrected_min_vm_n"].to_numpy())
    st_mis = int((ok_o != ok_n).sum() + (m["pinned_converged_o"].to_numpy(bool) != m["pinned_converged_n"].to_numpy(bool)).sum())
    check3 = bool(len(m) > 0 and (pin_diff.max() if len(pin_diff) else 0) == 0.0 and (cor_diff.max() if len(cor_diff) else 0) <= TOL3 and st_mis == 0)
    conv = res["pinned_converged"].to_numpy(bool)
    okr = res["corrected_status"].isin(["converged", "not_needed"]).to_numpy()
    n_fail = int((conv & ~okr).sum())
    check5 = bool(n_fail / len(res) <= 0.005)
    # check 6 on N-2 rows
    e = res[conv & okr].reset_index(drop=True)
    pin = e["pinned_min_vm"].to_numpy()
    cor = e["corrected_min_vm"].to_numpy()
    flip = (pin < LIMIT) != (cor < LIMIT)
    d = np.abs(cor - pin)
    strata = dict(a=np.flatnonzero(flip), b=np.flatnonzero((~flip) & (d > 1e-4)), c=np.flatnonzero((~flip) & (d <= 1e-4)),
                  d=np.flatnonzero((cor >= 0.94) & (cor < 0.945)))
    rng = np.random.default_rng(SEED6)
    t6 = []
    lab6 = []
    for k in ["a", "b", "c", "d"]:
        idx = strata[k]
        if len(idx) > N_PER:
            idx = np.sort(rng.choice(idx, N_PER, replace=False))
        for i in idx:
            r = e.iloc[i]
            t6.append((int(r.scenario_id), r.a_type, int(r.a_idx), r.b_type, int(r.b_idx), by_sid[int(r.scenario_id)]["params"], float(r.corrected_min_vm)))
            lab6.append(k)
    with multiprocessing.Pool(NPROC) as pool:
        r6 = pd.DataFrame(pool.map(indep_pair, t6, chunksize=8))
    r6["stratum"] = lab6
    cv = r6["indep_converged"].fillna(False).astype(bool) & r6["consistent"].fillna(False).astype(bool)
    agree = cv & ((r6["ref_min"] < LIMIT) == (r6["indep_min"] < LIMIT))
    far = cv & ((r6["ref_min"] - LIMIT).abs() > 1e-3) & ((r6["indep_min"] - LIMIT).abs() > 1e-3)
    n6 = len(r6)
    valid = bool(((r6["pv_minus_pp_nolim"].astype(float) <= 1e-6) & r6["pv_converged"].fillna(False).astype(bool)).all())
    stop_conv = bool((~cv).sum() / n6 > 0.02)
    stop_label = bool((far & ~agree).sum() > 0)
    stop_diff = bool((r6.loc[cv, "abs_diff"] > 1e-3).sum() / n6 > 0.01)
    check6 = bool(valid and not (stop_conv or stop_label or stop_diff))
    per = {}
    for k in ["a", "b", "c", "d"]:
        msk = r6["stratum"] == k
        kk = int(agree[msk].sum())
        nn = int(msk.sum())
        dd = r6.loc[msk & cv, "abs_diff"].to_numpy()
        per[k] = dict(n=nn, label_agree=kk, ci95=lc.clopper_pearson(kk, nn), population=int(len(strata[k])),
                      median_abs_diff=float(np.median(dd)) if len(dd) else None, max_abs_diff=float(dd.max()) if len(dd) else None,
                      n_gt_1e6=int((dd > 1e-6).sum()), n_gt_1e4=int((dd > 1e-4).sum()))
    near = int((np.abs(cor - LIMIT) <= 1e-3).sum())
    b = dict(name="N2R", rows=int(len(res)), schema_same_columns=schema_same, schema_dtype_differences=dtype_diff,
             n_common_bases=int(len(com)), checks=dict(
                 check3_label_reproduction=dict(passed=check3, n_rows_compared=int(len(m)), max_abs_pinned_diff=float(pin_diff.max()) if len(pin_diff) else None,
                                                max_abs_corrected_diff=float(cor_diff.max()) if len(cor_diff) else None, status_mismatches=st_mis),
                 check5_failure_ceilings=dict(passed=check5, failed_rows=n_fail, share=n_fail / len(res)),
                 check6_independent=dict(passed=check6)),
             pinned_nonconverged=int((~conv).sum()), corrected_violation_rate=float((cor < LIMIT).mean()),
             adjacent_share=float(res["adjacent"].mean()), wall_s=time.time() - t0)
    b["all_checks_passed"] = bool(check3 and check5 and check6)
    with open("data/sts_n13_build_N2R.json", "w") as f:
        json.dump(b, f, indent=2)
    i6 = dict(check="N13 check 6 on N2R rows", passed=check6, validation_passed=valid, stop_rules=dict(
        nonconverged_or_inconsistent_share=float((~cv).sum() / n6), stop_conv=stop_conv,
        label_disagreements_far=int((far & ~agree).sum()), stop_label=stop_label,
        share_diff_gt_1e3=float((r6.loc[cv, "abs_diff"] > 1e-3).sum() / n6), stop_diff=stop_diff),
        per_stratum=per, near_limit_population=dict(count=near, share=near / max(len(e), 1)), seed=SEED6)
    with open("data/sts_n13_indep_N2R.json", "w") as f:
        json.dump(i6, f, indent=2, default=float)
    ins = ["scratch/n13_build/D94/phase1_100.json", OLD, "scratch/n11_n2_build.py", "scratch/n13_decision_rule.md"]
    params = dict(pair_seed=n11b.PAIR_SEED, n_pairs_per_base=n11b.N_PAIRS, check6_seed=SEED6, n_per_stratum=N_PER,
                  solver="pinned + N2 switch-back (n11_n2_build.solve_shard); independent: label_crosscheck",
                  model_hyperparameters="none (no model fit)")
    for art in [OUT, "data/sts_n13_build_N2R.json", "data/sts_n13_indep_N2R.json"]:
        man = sm.build_manifest([art], "scratch/n13_n2r.py", [".venv/bin/python", "scratch/n13_n2r.py"], ins, params, "")
        man["no_new_solves"] = "FALSE: N-2 pinned + switch-back solves; independent solves of sampled rows"
        sm.write_manifest(man, art)
    print(json.dumps(dict(checks=b["checks"], n_common=b["n_common_bases"], per_stratum=per, near=i6["near_limit_population"]), indent=1, default=float))


if __name__ == "__main__":
    main()
