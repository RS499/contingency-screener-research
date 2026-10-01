import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import sts_manifest as sm

# N11 Part 3 (scratch/n11_decision_rule.md §3): generator voltage floor dose-response. Four floors on case118,
# seeds 100-103: 0.93 and 0.96 (N11 builds), 0.94 (D94 = data/dataset.parquet) and 0.95 (D95a). BM = share of
# converged N-1 rows in [0.94, 0.945); CBM = BM / share >= 0.94; VR = share < 0.94; on stored and on switch-back
# corrected labels. Each stored value is compared with the hashed §3 prediction (point and range).
# FLOOR-DOSE-RESPONSE (stored labels): BM(0.96) < BM(0.95) - 5 pp  AND  |BM(0.93) - BM(0.94)| <= 5 pp.

RULE = "scratch/n11_decision_rule.md"
RULE_SHA = "scratch/n11_decision_rule.sha256"
OUT = "data/sts_n11_dose_response.json"
FLOORS = [
    (0.93, "data/sts_n11_floor093.parquet", "data/sts_n11_floor093_relabel.parquet"),
    (0.94, "data/dataset.parquet", "data/sts_n2_label_audit.parquet"),
    (0.95, "data/sts_n3_floor095.parquet", "data/sts_n5_relabel095.parquet"),
    (0.96, "data/sts_n11_floor096.parquet", "data/sts_n11_floor096_relabel.parquet"),
]
# §3 predictions, stored labels, percent: (point, lo, hi)
PRED = {0.93: dict(BM=(55.0, 50.0, 62.0), CBM=(67.0, 62.0, 73.0), VR=(17.5, 15.5, 19.5)),
        0.96: dict(BM=(20.0, 8.0, 30.0), CBM=(24.0, 10.0, 36.0), VR=(15.0, 12.0, 17.5))}


def metrics(v):
    v = np.asarray(v, dtype=float)
    strip = (v >= 0.94) & (v < 0.945)
    return dict(n_rows=int(len(v)), BM=100.0 * strip.mean(), CBM=100.0 * strip.sum() / (v >= 0.94).sum(),
                VR=100.0 * (v < 0.94).mean())


def main():
    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise ValueError("decision rule changed since hashing; stop")
    per = []
    inputs = [RULE]
    for floor, data_path, lab_path in FLOORS:
        inputs += [data_path, lab_path]
        df = pd.read_parquet(data_path, columns=["outaged_type", "converged", "min_vm"])
        stored = df[(df.outaged_type != "none") & df.converged]["min_vm"].to_numpy()
        lab = pd.read_parquet(lab_path, columns=["outaged_type", "corrected_status", "corrected_min_vm"])
        lab = lab[lab.outaged_type != "none"]
        ok = lab["corrected_status"].isin(["converged", "not_needed"])
        r = dict(floor=floor, dataset=data_path, labels=lab_path, stored=metrics(stored),
                 corrected=metrics(lab.loc[ok, "corrected_min_vm"].to_numpy()), n_relabel_failed=int((~ok).sum()),
                 relabel_failed_share=float((~ok).mean()))
        if floor in PRED:
            cmp = {}
            for k in ["BM", "CBM", "VR"]:
                pt, lo, hi = PRED[floor][k]
                cmp[k] = dict(predicted_point=pt, predicted_range=[lo, hi], observed=r["stored"][k],
                              in_range=bool(lo <= r["stored"][k] <= hi), error_vs_point=r["stored"][k] - pt)
            r["vs_prediction"] = cmp
        per.append(r)
    bm = {r["floor"]: r["stored"]["BM"] for r in per}
    c1 = bool(bm[0.96] < bm[0.95] - 5.0)
    c2 = bool(abs(bm[0.93] - bm[0.94]) <= 5.0)
    bmc = {r["floor"]: r["corrected"]["BM"] for r in per}
    verdict = dict(FLOOR_DOSE_RESPONSE=bool(c1 and c2),
                   clause1=dict(rule="BM(0.96) < BM(0.95) - 5 pp", bm_096=bm[0.96], bm_095=bm[0.95], holds=c1),
                   clause2=dict(rule="|BM(0.93) - BM(0.94)| <= 5 pp", bm_093=bm[0.93], bm_094=bm[0.94],
                                abs_diff=abs(bm[0.93] - bm[0.94]), holds=c2),
                   same_on_corrected_labels_reported_only=dict(clause1=bool(bmc[0.96] < bmc[0.95] - 5.0),
                                                               clause2=bool(abs(bmc[0.93] - bmc[0.94]) <= 5.0),
                                                               bm=bmc))
    out = dict(part="N11 Part 3: floor dose-response", decision_rule=RULE, decision_rule_sha256=h,
               decision_rule_hash_verified=True, verdict=verdict, per_floor=per,
               note="one build per floor (seeds 100-103); common random numbers across floors until redraw counts diverge")
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    man = sm.build_manifest([OUT], "scratch/n11_dose_response.py", [".venv/bin/python", "scratch/n11_dose_response.py"],
                            inputs, dict(floors=[f[0] for f in FLOORS], predictions=PRED, model_hyperparameters="none (no model fit)",
                                         solver_settings="labels: stored pinned pandapower and N2 switch-back"), "")
    man["no_new_solves"] = "No AC solve; reads the four builds and their relabels."
    sm.write_manifest(man, OUT)
    for r in per:
        print(f"floor {r['floor']:.2f}: stored BM {r['stored']['BM']:.2f} CBM {r['stored']['CBM']:.2f} VR {r['stored']['VR']:.2f} | "
              f"corrected BM {r['corrected']['BM']:.2f} VR {r['corrected']['VR']:.2f} | {r.get('vs_prediction', '')}")
    print(json.dumps(verdict, indent=1))


if __name__ == "__main__":
    main()
