import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import sts_manifest as sm

# N9 Step 5, Part 3 of scratch/n9_decision_rule.md: floor replication (descriptive). For each 0.95-floor build,
# on converged N-1 rows: BM = share in [0.94, 0.945); CBM = BM / share >= 0.94; VR = share < 0.94; on stored
# (pinned-solver) labels and on switch-back corrected labels (failed relabel rows dropped). Across builds:
# mean +/- std (ddof=0 and ddof=1). Each build's stored values are compared with the ranges in the hashed N3
# prediction (scratch/n3_floor_prediction.md).

BUILDS = [
    ("D95a", "data/sts_n3_floor095.parquet", "data/sts_n5_relabel095.parquet"),
    ("D95b", "data/sts_n5_floor095_seed200.parquet", "data/sts_n9_relabel095_seed200.parquet"),
    ("D95c", "data/sts_n9_floor095_seed300.parquet", "data/sts_n9_relabel095_seed300.parquet"),
]
PRED = "scratch/n3_floor_prediction.md"
PRED_SHA = "9975a07ec1c1a3004b524636239194a1584a8eadc5b6e3748766c4714446ba0f"
# point and range for the 0.95 floor, as stated in the hashed prediction (Q1-Q3, build B)
PRED_RANGES = {"BM": (33.0, 20.0, 45.0), "CBM": (40.0, 28.0, 55.0), "VR": (15.5, 12.0, 18.0)}
OUT = "data/sts_n9_floor_replication.json"


def metrics(v):
    v = np.asarray(v, dtype=float)
    strip = (v >= 0.94) & (v < 0.945)
    safe = v >= 0.94
    return dict(n_rows=int(len(v)), BM=100.0 * strip.sum() / len(v), CBM=100.0 * strip.sum() / safe.sum(),
                VR=100.0 * (v < 0.94).sum() / len(v))


def main():
    h = hashlib.sha256(open(PRED, "rb").read()).hexdigest()
    if h != PRED_SHA:
        raise ValueError("N3 prediction file changed; stop")
    per_build = []
    inputs = [PRED]
    for name, data_path, label_path in BUILDS:
        if not os.path.exists(data_path) or not os.path.exists(label_path):
            print(f"{name}: missing {data_path} or {label_path}; skipped")
            continue
        inputs.extend([data_path, label_path])
        df = pd.read_parquet(data_path, columns=["outaged_type", "converged", "min_vm"])
        stored = df[(df["outaged_type"] != "none") & (df["converged"])]["min_vm"].to_numpy()
        lab = pd.read_parquet(label_path, columns=["outaged_type", "corrected_status", "corrected_min_vm"])
        lab = lab[lab["outaged_type"] != "none"]
        ok = lab["corrected_status"].isin(["converged", "not_needed"])
        corr = lab.loc[ok, "corrected_min_vm"].to_numpy()
        r = dict(build=name, dataset=data_path, labels=label_path, n_relabel_failed=int((~ok).sum()),
                 stored=metrics(stored), corrected=metrics(corr),
                 stored_min_vm_min=float(stored.min()), corrected_min_vm_min=float(corr.min()))
        inr = {}
        for k in PRED_RANGES:
            pt, lo, hi = PRED_RANGES[k]
            inr[k] = bool(lo <= r["stored"][k] <= hi)
        r["stored_in_n3_predicted_range"] = inr
        per_build.append(r)

    across = {}
    for lab in ["stored", "corrected"]:
        across[lab] = {}
        for k in ["BM", "CBM", "VR"]:
            v = np.array([b[lab][k] for b in per_build])
            across[lab][k] = dict(values=[float(x) for x in v], mean=float(v.mean()), std_ddof0=float(v.std()),
                                  std_ddof1=float(v.std(ddof=1)) if len(v) > 1 else None)
    out = dict(part="N9 Part 3: floor replication (descriptive)", decision_rule="scratch/n9_decision_rule.md",
               n3_prediction=PRED, n3_prediction_sha256=h, n3_predicted_ranges_pct=PRED_RANGES,
               n_builds=len(per_build), per_build=per_build, across_builds=across)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    man = sm.build_manifest([OUT], "scratch/n9_replication.py", [".venv/bin/python", "scratch/n9_replication.py"],
                            inputs, dict(builds=[b[0] for b in BUILDS], model_hyperparameters="none (no model fit)"), "")
    sm.write_manifest(man, OUT)
    for b in per_build:
        print(f"{b['build']}: stored BM {b['stored']['BM']:.3f} CBM {b['stored']['CBM']:.3f} VR {b['stored']['VR']:.3f} "
              f"| corrected BM {b['corrected']['BM']:.3f} CBM {b['corrected']['CBM']:.3f} VR {b['corrected']['VR']:.3f} "
              f"| in N3 range {b['stored_in_n3_predicted_range']} | failed {b['n_relabel_failed']}")
    for lab in across:
        for k in across[lab]:
            a = across[lab][k]
            print(f"{lab:9s} {k:3s} mean {a['mean']:.3f} std0 {a['std_ddof0']:.3f} std1 {a['std_ddof1']}")


if __name__ == "__main__":
    main()
