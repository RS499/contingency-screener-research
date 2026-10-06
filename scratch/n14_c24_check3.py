import os
import sys
import json
import time
import hashlib
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import n13_common as c
import sts_manifest as sm

# N14 Step 3 (scratch/n14_decision_rule.md §A): N13 check 3 for C24 under the amendment. The pinned clause is
# "its pinned outage minima equal the old stored min_vm within 1e-9 pu"; the corrected clause is unchanged (within 1e-9
# pu); pinned and switch-back statuses must agree. Inputs: data/sts_n13_C24.parquet, data/sts_n13_audit_C24.parquet,
# the C24 build's phase-1 files and the old draw logs (common bases by parameter hash), the old C24 dataset and its old
# N11 switch-back labels. The comparison logic is that of scratch/n13_checks.py (check 3), with the amended tolerance.
# Also re-states, from the N13 build files, every other dataset's pinned maximum difference.
# Output: data/sts_n14_c24_check3.json + manifest.

RULE = "scratch/n14_decision_rule.md"
RULE_SHA = "scratch/n14_decision_rule.sha256"
OUT = "data/sts_n14_c24_check3.json"
NAME = "C24"
TOL = 1e-9
OK_STATUS = ["converged", "not_needed"]


def main():
    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    spec = c.DATASETS[NAME]
    p1 = json.load(open(f"scratch/n13_build/{NAME}/phase1_100.json"))
    old_log = pd.read_parquet(f"scratch/n13_drawlogs/old_{NAME}_100.parquet")
    old_acc = old_log[old_log.accepted][["params_hash", "scenario_id"]]
    new_acc = pd.DataFrame([dict(params_hash=b["params_hash"], scenario_id=b["scenario_id"]) for b in p1["accepted"]])
    common = old_acc.merge(new_acc, on="params_hash", suffixes=("_old", "_new"))
    df = pd.read_parquet(f"data/sts_n13_{NAME}.parquet", columns=["scenario_id", "outaged_type", "outaged_idx", "converged", "min_vm"])
    aud = pd.read_parquet(f"data/sts_n13_audit_{NAME}.parquet")
    old = pd.read_parquet(spec["file"], columns=["scenario_id", "outaged_type", "outaged_idx", "converged", "min_vm"])
    lab = pd.read_parquet(spec["labels"], columns=["scenario_id", "outaged_type", "outaged_idx", "corrected_status", "corrected_min_vm"])
    o = old[old.outaged_type != "none"].merge(lab, on=["scenario_id", "outaged_type", "outaged_idx"], how="left")
    o = o.merge(common[["scenario_id_old", "scenario_id_new"]], left_on="scenario_id", right_on="scenario_id_old")
    a = aud[aud.outaged_type != "none"].merge(df[df.outaged_type != "none"], on=["scenario_id", "outaged_type", "outaged_idx"], how="left")
    m = o.merge(a, left_on=["scenario_id_new", "outaged_type", "outaged_idx"], right_on=["scenario_id", "outaged_type", "outaged_idx"],
                suffixes=("_o", "_n"))
    both_pinned = m["converged_o"].to_numpy(bool) & (m["status"] != "pinned_nonconverged").to_numpy()
    pin_diff = np.abs(m.loc[both_pinned, "min_vm_o"].to_numpy() - m.loc[both_pinned, "pinned_min"].to_numpy(np.float64))
    pin_status_mis = int((m["converged_o"].to_numpy(bool) != (m["status"] != "pinned_nonconverged").to_numpy()).sum())
    old_ok = m["corrected_status"].isin(OK_STATUS).to_numpy()
    new_ok = m["status"].isin(OK_STATUS).to_numpy()
    both_ok = old_ok & new_ok
    cor_diff = np.abs(m.loc[both_ok, "corrected_min_vm"].to_numpy() - m.loc[both_ok, "min_vm_n"].to_numpy())
    cor_status_mis = int((old_ok != new_ok).sum())
    passed = bool(len(m) > 0 and pin_diff.max() <= TOL and pin_status_mis == 0 and cor_diff.max() <= TOL and cor_status_mis == 0)
    others = {}
    for n in ["D94", "ILL", "C30", "D93", "D95a", "D96", "D95b", "D95c"]:
        c3 = json.load(open(f"data/sts_n13_build_{n}.json"))["checks"]["check3_label_reproduction"]
        others[n] = dict(max_abs_pinned_diff=c3["max_abs_pinned_diff"], within_1e9=bool(c3["max_abs_pinned_diff"] <= TOL))
    nb = json.load(open("data/sts_n13_build_N2R.json"))["checks"]["check3_label_reproduction"]
    others["N2R"] = dict(max_abs_pinned_diff=nb["max_abs_pinned_diff"], within_1e9=bool(nb["max_abs_pinned_diff"] <= TOL))
    out = dict(step="N14 Step 3: C24 check 3 under the amendment (pinned clause tolerance 1e-9 pu)", decision_rule_sha256=h,
               C24=dict(passed=passed, n_common_bases=int(len(common)), n_rows_compared=int(len(m)), n_pinned_compared=int(both_pinned.sum()),
                        max_abs_pinned_diff=float(pin_diff.max()), n_pinned_diff_nonzero=int((pin_diff > 0).sum()),
                        pinned_status_mismatches=pin_status_mis, n_corrected_compared=int(both_ok.sum()),
                        max_abs_corrected_diff=float(cor_diff.max()), corrected_status_mismatches=cor_status_mis, tolerance=TOL),
               other_datasets_pinned_max_diff_from_n13=others,
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    man = sm.build_manifest([OUT], "scratch/n14_c24_check3.py", [".venv/bin/python", "scratch/n14_c24_check3.py"],
                            [f"data/sts_n13_{NAME}.parquet", f"data/sts_n13_audit_{NAME}.parquet", spec["file"], spec["labels"], RULE],
                            dict(tolerance_pinned=TOL, tolerance_corrected=TOL, model_hyperparameters="none (check only)"), "")
    sm.write_manifest(man, OUT)
    print(json.dumps(dict(C24=out["C24"], others={k: others[k]["max_abs_pinned_diff"] for k in others}), indent=1))


if __name__ == "__main__":
    main()
