import os
import sys
import json
import time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import n13_common as c
import sts_manifest as sm

# N13 checks 2-5 (scratch/n13_decision_rule.md §2) and the per-dataset build summary (§5) for one rebuilt dataset.
# argv[1] = dataset name. Inputs: data/sts_n13_<name>.parquet, data/sts_n13_audit_<name>.parquet, the build work
# dir (phase-1 accepted lists, N-0 draw logs), the old draw logs from check 1 (scratch/n13_drawlogs), the original
# dataset and its old switch-back labels.
#   check 2 shared prefix: per shard, draws before the first acceptance that differs have identical parameters
#   check 3 label reproduction on bases common to both builds (same parameter hash): pinned outage minima equal
#           the old stored min_vm exactly; corrected minima equal the old switch-back labels within 1e-9 pu;
#           pinned and switch-back statuses agree
#   check 4 every rebuilt base has a converged corrected N-0 state with minimum >= 0.94
#   check 5 failed outage switch-back rows <= 0.5% of outage rows; N-0 correction-failed draws <= 0.5% of draws
# Output: data/sts_n13_build_<name>.json + manifests for it, the dataset and the audit file.

NAME = sys.argv[1] if len(sys.argv) > 1 else "D94"
WORK = f"scratch/n13_build/{NAME}"
LIMIT = 0.94
TOL3 = 1e-9
CEIL = 0.005
FAIL_STATUS = ["nonconverged", "iteration_cap"]
OK_STATUS = ["converged", "not_needed"]


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def shard_prefix(seed, phase1):
    old = pd.read_parquet(f"scratch/n13_drawlogs/old_{NAME}_{seed}.parquet").sort_values("draw").reset_index(drop=True)
    new = pd.read_parquet(os.path.join(WORK, f"n0log_{seed}.parquet")).sort_values("draw").reset_index(drop=True)
    acc_draws = set([b["draw"] for b in phase1["accepted"]])
    new_acc = new["draw"].isin(acc_draws).to_numpy()
    old_acc = old["accepted"].to_numpy(bool)
    n = min(len(old), len(new))
    diff = np.flatnonzero(old_acc[:n] != new_acc[:n])
    first = int(diff[0]) if len(diff) else n
    same_hash = old["params_hash"].to_numpy()[:first] == new["params_hash"].to_numpy()[:first]
    return dict(shard_seed=seed, first_differing_draw=first, prefix_draws=first,
                prefix_accepted=int(old_acc[:first].sum()), prefix_hashes_identical=bool(same_hash.all()),
                draw_at_divergence_hash_identical=bool(first < n and old["params_hash"].iloc[first] == new["params_hash"].iloc[first]),
                old_draws=int(len(old)), new_draws=int(len(new)),
                old_hashes=old.loc[old_acc, ["params_hash", "scenario_id"]], new_n0log=new)


def main():
    t0 = time.time()
    spec = c.DATASETS[NAME]
    seeds = spec.get("seeds", [100])
    phase1 = {}
    for s in seeds:
        phase1[s] = json.load(open(os.path.join(WORK, f"phase1_{s}.json")))
    df = pd.read_parquet(f"data/sts_n13_{NAME}.parquet")
    aud = pd.read_parquet(f"data/sts_n13_audit_{NAME}.parquet")
    old = pd.read_parquet(spec["file"], columns=["scenario_id", "outaged_type", "outaged_idx", "converged", "min_vm"])
    lab = pd.read_parquet(spec["labels"], columns=["scenario_id", "outaged_type", "outaged_idx", "corrected_status", "corrected_min_vm"])
    # check 2 and base-set changes
    pref = []
    old_acc = []
    for s in seeds:
        p = shard_prefix(s, phase1[s])
        old_acc.append(p.pop("old_hashes"))
        p.pop("new_n0log")
        pref.append(p)
    old_acc = pd.concat(old_acc, ignore_index=True)
    new_acc = pd.DataFrame([dict(params_hash=b["params_hash"], scenario_id=b["scenario_id"]) for s in seeds for b in phase1[s]["accepted"]])
    common = old_acc.merge(new_acc, on="params_hash", suffixes=("_old", "_new"))
    check2 = bool(all([p["prefix_hashes_identical"] for p in pref]))
    # check 3 on common bases
    o = old[old.outaged_type != "none"].merge(lab, on=["scenario_id", "outaged_type", "outaged_idx"], how="left")
    o = o.merge(common[["scenario_id_old", "scenario_id_new"]], left_on="scenario_id", right_on="scenario_id_old")
    a = aud[aud.outaged_type != "none"]
    nrow = df[df.outaged_type != "none"][["scenario_id", "outaged_type", "outaged_idx", "converged", "min_vm"]]
    a = a.merge(nrow, on=["scenario_id", "outaged_type", "outaged_idx"], how="left")
    m = o.merge(a, left_on=["scenario_id_new", "outaged_type", "outaged_idx"], right_on=["scenario_id", "outaged_type", "outaged_idx"],
                suffixes=("_o", "_n"))
    both_pinned = m["converged_o"].to_numpy(bool) & (m["status"] != "pinned_nonconverged").to_numpy()
    pin_diff = np.abs(m.loc[both_pinned, "min_vm_o"].to_numpy() - m.loc[both_pinned, "pinned_min"].to_numpy(np.float64))
    pin_status_mismatch = int((m["converged_o"].to_numpy(bool) != (m["status"] != "pinned_nonconverged").to_numpy()).sum())
    old_ok = m["corrected_status"].isin(OK_STATUS).to_numpy()
    new_ok = m["status"].isin(OK_STATUS).to_numpy()
    cor_status_mismatch = int((old_ok != new_ok).sum())
    both_ok = old_ok & new_ok
    cor_diff = np.abs(m.loc[both_ok, "corrected_min_vm"].to_numpy() - m.loc[both_ok, "min_vm_n"].to_numpy())
    check3 = bool(len(m) > 0 and (pin_diff.max() if len(pin_diff) else 0.0) == 0.0 and pin_status_mismatch == 0
                  and (cor_diff.max() if len(cor_diff) else 0.0) <= TOL3 and cor_status_mismatch == 0)
    # check 4
    n0 = df[df.outaged_type == "none"]
    check4_bad = int((~n0["n0_converged"].astype(bool) | (n0["n0_min_vm"] < LIMIT)).sum())
    check4 = bool(check4_bad == 0 and len(n0) == 1500)
    # check 5
    n_out = int(len(a))
    n_fail = int(a["status"].isin(FAIL_STATUS).sum())
    draws = sum([phase1[s]["n_draws"] for s in seeds])
    rej = {}
    for s in seeds:
        for k in phase1[s]["rejected"]:
            rej[k] = rej.get(k, 0) + phase1[s]["rejected"][k]
    n0_fail = rej.get("n0_correction_failed", 0)
    check5 = bool(n_fail / max(n_out, 1) <= CEIL and n0_fail / max(draws, 1) <= CEIL)
    # descriptives (converged N-1 rows, corrected state)
    n1 = df[(df.outaged_type != "none") & df.converged.astype(bool)]
    v = n1["min_vm"].to_numpy(np.float64)
    strip = (v >= 0.94) & (v < 0.945)
    crit = n1["argmin_bus"].value_counts(normalize=True).head(5)
    needed = a[a["status"].isin(["converged"] + FAIL_STATUS)]
    out = dict(
        name=NAME, tier=spec["tier"], original_file=spec["file"],
        draws=draws, accepted=int(len(n0)), rejected_by_reason=rej,
        base_set=dict(per_shard_prefix=pref, n_old_bases=int(len(old_acc)), n_new_bases=int(len(new_acc)),
                      n_common=int(len(common)), n_old_rejected=int(len(old_acc) - len(common)),
                      n_new_added=int(len(new_acc) - len(common))),
        checks=dict(
            check2_shared_prefix=dict(passed=check2),
            check3_label_reproduction=dict(passed=check3, n_rows_compared=int(len(m)), n_pinned_compared=int(both_pinned.sum()),
                                           max_abs_pinned_diff=float(pin_diff.max()) if len(pin_diff) else None,
                                           pinned_status_mismatches=pin_status_mismatch, n_corrected_compared=int(both_ok.sum()),
                                           max_abs_corrected_diff=float(cor_diff.max()) if len(cor_diff) else None,
                                           corrected_status_mismatches=cor_status_mismatch, tolerance=TOL3),
            check4_acceptance=dict(passed=check4, n_bases=int(len(n0)), n_bad=check4_bad),
            check5_failure_ceilings=dict(passed=check5, failed_outage_rows=n_fail, outage_rows=n_out,
                                         failed_outage_share=n_fail / max(n_out, 1), n0_correction_failed_draws=n0_fail,
                                         draws=draws, n0_correction_failed_share=n0_fail / max(draws, 1), ceiling=CEIL)),
        failed_rows=n_fail, pinned_nonconverged_outage_rows=int((a["status"] == "pinned_nonconverged").sum()),
        VR=float((v < LIMIT).mean()), BM=float(strip.mean()), CBM=float(strip.sum() / (v >= LIMIT).sum()),
        min_vm_range=[float(v.min()), float(v.max())],
        over_voltage_share_max_vm_gt_1p05=float((n1["max_vm"] > 1.05).mean()),
        critical_bus_top5_share={str(int(k)): float(x) for k, x in crit.items()},
        switchback_outer_iterations=dict(mean_all_outage_rows=float(a["n_outer"].mean()), max=int(a["n_outer"].max()),
                                         mean_rows_needing_switchback=float(needed["n_outer"].mean()) if len(needed) else 0.0,
                                         n_rows_needing_switchback=int(len(needed))),
        n0_switchback_needed=int(aud[(aud.outaged_type == "none")]["status"].isin(["converged"]).sum()),
        build_info=json.load(open(os.path.join(WORK, "build_info.json"))),
        wall_s=time.time() - t0)
    out["all_checks_2_5_passed"] = bool(check2 and check3 and check4 and check5)
    path = f"data/sts_n13_build_{NAME}.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    params = dict(dataset=NAME, spec=spec, solver="corrected: pandapower runpp enforce_q_lims=True init=dc numba=True, then the N2 switch-back (TOL_V = TOL_Q = 1e-3, 30 outer iterations)",
                  invocation="scratch/n13_build.py " + NAME, model_hyperparameters="none (no model fit)")
    ins = [spec["file"], spec["labels"], "scratch/n13_decision_rule.md"]
    for art in [f"data/sts_n13_{NAME}.parquet", f"data/sts_n13_audit_{NAME}.parquet"]:
        man = sm.build_manifest([art], "scratch/n13_build.py", [".venv/bin/python", "scratch/n13_build.py", NAME], ins, params, "")
        man["no_new_solves"] = "FALSE: corrected-solver rebuild (N-0 and every outage)"
        sm.write_manifest(man, art)
    man = sm.build_manifest([path], "scratch/n13_checks.py", [".venv/bin/python", "scratch/n13_checks.py", NAME],
                            ins + [f"data/sts_n13_{NAME}.parquet", f"data/sts_n13_audit_{NAME}.parquet"], params, "")
    man["no_new_solves"] = "No AC solve; checks and summaries from the rebuild outputs."
    sm.write_manifest(man, path)
    print(json.dumps(dict(checks=out["checks"], base_set={k: out["base_set"][k] for k in out["base_set"] if k != "per_shard_prefix"},
                          prefix=[dict(seed=p["shard_seed"], prefix_draws=p["prefix_draws"], identical=p["prefix_hashes_identical"]) for p in pref],
                          VR=out["VR"], BM=out["BM"], CBM=out["CBM"], rejected=rej, draws=draws), indent=1, default=str))


if __name__ == "__main__":
    main()
