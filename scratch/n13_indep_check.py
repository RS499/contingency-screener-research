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
import n13_build as nb
import generate_dataset as gd
import label_crosscheck as lc
import sts_n2_label_audit as n2
import sts_manifest as sm

# N13 check 6 (scratch/n13_decision_rule.md §2): the from-scratch complementarity solver of
# scratch/label_crosscheck.py (network_model, solve, consistency, clopper_pearson imported unchanged), network as a
# parameter, on one rebuilt dataset. argv[1] = dataset name.
# Rows compared: every accepted N-0 state, plus 200 outage rows per stratum (numpy seed 20261004; all if fewer):
#   (a) label flipped pinned vs corrected; (b) not flipped, |corrected - pinned| > 1e-4; (c) unchanged (<= 1e-4);
#   (d) corrected min_vm in [0.94, 0.945). Only rows whose pinned and corrected solves converged are eligible.
# Validation first: with the limit rule replaced by voltage control, the solver reproduces pandapower's
# enforce_q_lims=False minimum within 1e-6 pu on every compared row.
# Stop rule (any one stops the dataset): independent solve not converged to a consistent state on > 2% of compared
# rows; any label disagreement where both min_vm are > 1e-3 pu from 0.94 (N-0 label = acceptance, min >= 0.94);
# > 1% of compared rows differ by > 1e-3 pu (N-0: max over the full bus-voltage vector).
# Output: data/sts_n13_indep_<name>.json + manifest.

NAME = sys.argv[1] if len(sys.argv) > 1 else "D94"
SEED = 20261004
N_PER = 200
LIMIT = 0.94
NPROC = 8


def base_net(spec):
    if spec["kind"] == "case118":
        gd.apply_config(n2.CFG)
        return gd.build_net("case118")
    gd.apply_config(nb.cfg_other(spec))
    return gd.build_net(spec["network"])


def solve_row(task):
    name, sid, otype, oidx, params_json, ref_min, ref_vec = task
    spec = c.DATASETS[name]
    net = base_net(spec)
    gd.apply_scenario(net, c.params_from_json(params_json))
    if otype != "none":
        net[otype].at[int(oidx), "in_service"] = False
    rec = dict(scenario_id=sid, outaged_type=otype, outaged_idx=int(oidx), ref_min=ref_min)
    try:
        m = lc.network_model(net)
    except Exception:
        rec.update(model_ok=False, indep_converged=False, consistent=False)
        return rec
    v = lc.solve(m, "pv")
    rec["pv_converged"] = bool(v["converged"])
    rec["pv_minus_pp_nolim"] = abs(float(v["vm"].min()) - m["pp_nolim_min"]) if v["converged"] else None
    r = lc.solve(m, "cc")
    rec["model_ok"] = True
    rec["indep_converged"] = bool(r["converged"])
    if not r["converged"]:
        rec["consistent"] = False
        return rec
    ok, n_lim = lc.consistency(m, r)
    rec["consistent"] = bool(ok)
    rec["indep_min"] = float(r["vm"].min())
    rec["abs_diff_min"] = abs(rec["indep_min"] - ref_min)
    if ref_vec is not None:
        lk = net._pd2ppc_lookups["bus"]
        nbus = len(net.bus)
        if m["nb"] == nbus:
            vec = np.array([r["vm"][lk[i]] for i in range(nbus)])
            rec["abs_diff_vec_max"] = float(np.max(np.abs(vec - np.asarray(ref_vec))))
        else:
            rec["abs_diff_vec_max"] = None
    return rec


def main():
    t0 = time.time()
    spec = c.DATASETS[NAME]
    seeds = spec.get("seeds", [100])
    params = {}
    for s in seeds:
        for b in json.load(open(f"scratch/n13_build/{NAME}/phase1_{s}.json"))["accepted"]:
            params[b["scenario_id"]] = b["params"]
    df = pd.read_parquet(f"data/sts_n13_{NAME}.parquet")
    aud = pd.read_parquet(f"data/sts_n13_audit_{NAME}.parquet")
    n_bus = len([col for col in df.columns if col.startswith("vm0_")])
    n0 = df[df.outaged_type == "none"]
    tasks = []
    for _, r in n0.iterrows():
        vec = [float(r[f"vm0_{i}"]) for i in range(n_bus)]
        tasks.append((NAME, int(r.scenario_id), "none", -1, params[int(r.scenario_id)], float(r.n0_min_vm), vec))
    a = aud[aud.outaged_type != "none"].merge(df[["scenario_id", "outaged_type", "outaged_idx", "converged", "min_vm"]],
                                              on=["scenario_id", "outaged_type", "outaged_idx"])
    a = a[a.converged.astype(bool) & a.status.isin(["converged", "not_needed"])].reset_index(drop=True)
    pin = a["pinned_min"].to_numpy(np.float64)
    cor = a["min_vm"].to_numpy(np.float64)
    flip = (pin < LIMIT) != (cor < LIMIT)
    d = np.abs(cor - pin)
    strata = dict(a=np.flatnonzero(flip), b=np.flatnonzero((~flip) & (d > 1e-4)), c=np.flatnonzero((~flip) & (d <= 1e-4)),
                  d=np.flatnonzero((cor >= 0.94) & (cor < 0.945)))
    rng = np.random.default_rng(SEED)
    picks = {}
    for k in ["a", "b", "c", "d"]:
        idx = strata[k]
        if len(idx) > N_PER:
            idx = np.sort(rng.choice(idx, N_PER, replace=False))
        picks[k] = idx
        for i in idx:
            r = a.iloc[i]
            tasks.append((NAME, int(r.scenario_id), r.outaged_type, int(r.outaged_idx), params[int(r.scenario_id)],
                          float(r.min_vm), None))
    stratum_of = ["n0"] * len(n0)
    for k in ["a", "b", "c", "d"]:
        stratum_of += [k] * len(picks[k])
    with multiprocessing.Pool(NPROC) as pool:
        res = pool.map(solve_row, tasks, chunksize=8)
    rows = pd.DataFrame(res)
    rows["stratum"] = stratum_of
    rows["pinned_min"] = np.nan
    pos = len(n0)
    for k in ["a", "b", "c", "d"]:
        rows.loc[pos:pos + len(picks[k]) - 1, "pinned_min"] = pin[picks[k]]
        pos += len(picks[k])
    conv = rows["indep_converged"].fillna(False).astype(bool) & rows["consistent"].fillna(False).astype(bool)
    is_n0 = (rows["stratum"] == "n0").to_numpy()
    ref_lab = np.where(is_n0, rows["ref_min"] >= LIMIT, rows["ref_min"] < LIMIT)
    ind_lab = np.where(is_n0, rows["indep_min"] >= LIMIT, rows["indep_min"] < LIMIT)
    agree = conv.to_numpy() & (ref_lab == ind_lab)
    far = conv.to_numpy() & (np.abs(rows["ref_min"] - LIMIT) > 1e-3).to_numpy() & (np.abs(rows["indep_min"] - LIMIT) > 1e-3).to_numpy()
    diff = np.where(is_n0, rows.get("abs_diff_vec_max", pd.Series(np.nan, index=rows.index)).astype(float), rows["abs_diff_min"].astype(float))
    n = len(rows)
    # validation on rows where the independent model could be built (interpretation, logged in N13 status/result):
    # a row whose model cannot be built (e.g. an outage that islands every bus but the slack) counts as an
    # independent-solve failure under the 2% stop rule, not as a validation failure
    model_ok = rows["model_ok"].fillna(False).astype(bool)
    vrows = rows[model_ok]
    validation_ok = bool(((vrows["pv_minus_pp_nolim"].astype(float) <= 1e-6) & vrows["pv_converged"].fillna(False).astype(bool)).all())
    n_model_failed = int((~model_ok).sum())
    stop_conv = bool((~conv).sum() / n > 0.02)
    stop_label = bool((far & (ref_lab != ind_lab)).sum() > 0)
    stop_diff = bool((np.nan_to_num(diff, nan=np.inf)[conv.to_numpy()] > 1e-3).sum() / n > 0.01)
    passed = bool(validation_ok and not (stop_conv or stop_label or stop_diff))
    per = {}
    for k in ["n0", "a", "b", "c", "d"]:
        msk = (rows["stratum"] == k).to_numpy()
        kk = int(agree[msk].sum())
        nn = int(msk.sum())
        dd = diff[msk & conv.to_numpy()]
        per[k] = dict(n=nn, n_converged_consistent=int((conv.to_numpy() & msk).sum()), label_agree=kk,
                      agree_share=kk / nn if nn else None, ci95=lc.clopper_pearson(kk, nn),
                      median_abs_diff=float(np.nanmedian(dd)) if len(dd) else None, max_abs_diff=float(np.nanmax(dd)) if len(dd) else None,
                      n_gt_1e6=int((dd > 1e-6).sum()), n_gt_1e4=int((dd > 1e-4).sum()),
                      population=int(len(strata[k])) if k in strata else int(len(n0)))
    near = int((np.abs(cor - LIMIT) <= 1e-3).sum())
    n_conv_out = int(len(df[(df.outaged_type != "none") & df.converged.astype(bool)]))
    out = dict(check="N13 check 6: independent complementarity solver", dataset=NAME, passed=passed,
               validation=dict(passed=validation_ok, max_pv_minus_pp_nolim=float(rows["pv_minus_pp_nolim"].astype(float).max()),
                               n_rows_validated=int(len(vrows)), n_model_build_failed=n_model_failed,
                               model_build_failed_rows=rows.loc[~model_ok, ["scenario_id", "outaged_type", "outaged_idx", "ref_min"]].to_dict("records"),
                               interpretation="validation over rows whose independent model could be built; model-build failures counted under the 2% non-convergence stop rule"),
               stop_rules=dict(nonconverged_or_inconsistent_share=float((~conv).sum() / n), stop_conv=stop_conv,
                               label_disagreements_far_from_limit=int((far & (ref_lab != ind_lab)).sum()), stop_label=stop_label,
                               share_diff_gt_1e3=float((np.nan_to_num(diff, nan=np.inf)[conv.to_numpy()] > 1e-3).sum() / n), stop_diff=stop_diff),
               per_stratum=per, stratum_d_figure=per["d"],
               near_limit_population=dict(count=near, share=near / max(n_conv_out, 1), n_converged_outage_rows=n_conv_out,
                                          definition="|corrected min_vm - 0.94| <= 1e-3 pu over all converged outage rows"),
               n_compared=n, seed=SEED, n_per_stratum=N_PER, wall_s=time.time() - t0)
    path = f"data/sts_n13_indep_{NAME}.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    rows.to_parquet(f"scratch/n13_indep_rows_{NAME}.parquet", index=False)
    man = sm.build_manifest([path], "scratch/n13_indep_check.py", [".venv/bin/python", "scratch/n13_indep_check.py", NAME],
                            [f"data/sts_n13_{NAME}.parquet", f"data/sts_n13_audit_{NAME}.parquet", "scratch/label_crosscheck.py",
                             "scratch/n13_decision_rule.md"],
                            dict(seed=SEED, n_per_stratum=N_PER, limit=LIMIT, solver="scratch/label_crosscheck.py semismooth Newton complementarity (C_SCALE, TOL, MAX_IT as in that file)",
                                 model_hyperparameters="none (no model fit)"), "")
    man["no_new_solves"] = "FALSE: independent AC solves of the compared rows"
    sm.write_manifest(man, path)
    print(json.dumps(dict(passed=passed, validation=out["validation"], stop_rules=out["stop_rules"],
                          per_stratum={k: dict(n=per[k]["n"], agree=per[k]["label_agree"], max=per[k]["max_abs_diff"]) for k in per},
                          near=out["near_limit_population"]), indent=1, default=float))


if __name__ == "__main__":
    main()
