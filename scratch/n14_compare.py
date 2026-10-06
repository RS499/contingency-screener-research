import os
import sys
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import sts_manifest as sm
import n14_common as cm

# N14 Step 8 (scratch/n14_decision_rule.md §D): every N14 number with an N13 counterpart, compared both ways:
# the unpaired std-rule verdict (|N14 - N13| > max(stds) -> "differs") and the paired mean +- std of the per-split
# differences (same outer splits: they are drawn by base case, and removing outages does not change them).
# Primary ILL (trafo 63 removed) and the sensitivity runs (all islanding removed) vs the N13 results; C24 has no N13
# rebuilt counterpart (excluded in N13) and is listed as such. Output: data/sts_n14_compare.json + manifest.

OUT = "data/sts_n14_compare.json"
SEEDS = [0, 1, 2, 3, 4]
GATE_COLS = ["escalation", "missed", "speedup_A", "speedup_B", "gate_catch", "static_catch_B", "solve_share_B"]
CH_COLS = ["gate_catch", "static_fixed_catch", "condhist_catch", "global_static_catch"]


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def held(path, fam):
    g = json.load(open(path))
    pts = [p for p in g["points"] if p["family"] == fam and p["point"] == "held_out"]
    return [pts[i] for i in np.argsort([p["seed"] for p in pts])]


def pair(table, key, old, new):
    om, os_ = ms_(old)
    nm, ns = ms_(new)
    dm, ds = ms_(np.asarray(new, dtype=float) - np.asarray(old, dtype=float))
    return dict(table=table, key=key, n13_mean=om, n13_std=os_, n14_mean=nm, n14_std=ns, diff=nm - om,
                unpaired_std_rule="differs" if abs(nm - om) > max(os_, ns) else "within std", paired_diff_mean=dm, paired_diff_std=ds)


def main():
    h = cm.check_hash()
    rows = []
    for mode, tag in [("primary", ""), ("sensitivity", "_sens")]:
        for name in ["D94", "ILL", "C30", "C24"]:
            new_path = f"data/sts_n14_gate_{name}{tag}.json"
            old_path = f"data/sts_n13_gate_{name}.json"
            if mode == "primary" and name in ("D94", "C30"):
                continue
            if not os.path.exists(new_path):
                rows.append(dict(table=f"gate_{mode}", key=name, status="N14 not run"))
                continue
            if not os.path.exists(old_path):
                rows.append(dict(table=f"gate_{mode}", key=name, status="no N13 rebuilt counterpart (excluded in N13)"))
                continue
            for fam in ["histgb", "ridge"]:
                o = held(old_path, fam)
                n = held(new_path, fam)
                for col in GATE_COLS:
                    rows.append(pair(f"gate_{mode}", f"{name} {fam} held-out {col}", [p[col] for p in o], [p[col] for p in n]))
    oc = json.load(open("data/sts_n13_condhist.json"))["networks"]
    if os.path.exists("data/sts_n14_condhist.json"):
        nc = json.load(open("data/sts_n14_condhist.json"))["networks"]
        for name in ["ILL"]:
            for col in CH_COLS:
                rows.append(pair("condhist_primary", f"{name} {col}", [r[col] for r in oc[name]["per_split"]], [r[col] for r in nc[name]["per_split"]]))
        rows.append(dict(table="condhist_primary", key="C24", status="no N13 rebuilt counterpart (excluded in N13)"))
    if os.path.exists("data/sts_n14_sensitivity.json"):
        ns = json.load(open("data/sts_n14_sensitivity.json"))["networks"]
        for name in ["D94", "ILL", "C30"]:
            if isinstance(ns.get(name), dict):
                for col in CH_COLS:
                    rows.append(pair("condhist_sensitivity", f"{name} {col}", [r[col] for r in oc[name]["per_split"]],
                                     [r[col] for r in ns[name]["condhist"]["per_split"]]))
    if os.path.exists("data/sts_n14_guarantee.json"):
        og = json.load(open("data/sts_n13_guarantee.json"))["networks"]["ILL"]
        ng = json.load(open("data/sts_n14_guarantee.json"))["networks"]["ILL"]
        for fam in ["histgb", "ridge"]:
            for cal in ["global_gate", "row_level", "base_level"]:
                for col in ["escalation", "missed", "any_miss_share", "speedup_B"]:
                    rows.append(pair("guarantee_primary", f"ILL {fam} {cal} {col}", [r[cal][col] for r in og[fam]["per_split"]],
                                     [r[cal][col] for r in ng[fam]["per_split"]]))
    if os.path.exists("data/sts_n14_crossnet.json"):
        oc2 = {r["network"]: r for r in json.load(open("data/sts_n13_crossnet.json"))["table"]}
        nc2 = {r["network"]: r for r in json.load(open("data/sts_n14_crossnet.json"))["table"]}
        for k in ["boundary_mass", "violation_rate"]:
            rows.append(dict(table="crossnet_primary", key=f"ILL {k}", n13=oc2["ILL"][k], n14=nc2["ILL"][k], diff=nc2["ILL"][k] - oc2["ILL"][k],
                             note="single number, no std or split: no std rule"))
        for k in ["risk_spread", "top10_concentration"]:
            om, os_ = oc2["ILL"][k + "_mean"], oc2["ILL"][k + "_std"]
            nm, ns = nc2["ILL"][k + "_mean"], nc2["ILL"][k + "_std"]
            rows.append(dict(table="crossnet_primary", key=f"ILL {k}", n13_mean=om, n13_std=os_, n14_mean=nm, n14_std=ns, diff=nm - om,
                             unpaired_std_rule="differs" if abs(nm - om) > max(os_, ns) else "within std",
                             paired_diff_mean=None, paired_diff_std=None, note="paired not available: the N13 file keeps no per-split values"))
    n_diff = len([r for r in rows if r.get("unpaired_std_rule") == "differs"])
    n_within = len([r for r in rows if r.get("unpaired_std_rule") == "within std"])
    out = dict(part="N14 Step 8: N14 vs N13, unpaired std rule and paired per-split differences", decision_rule_sha256=h, n_rows=len(rows),
               n_differs=n_diff, n_within_std=n_within, rows=rows)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, default=float)
    ins = [p for p in ["data/sts_n13_gate_ILL.json", "data/sts_n14_gate_ILL.json", "data/sts_n13_condhist.json", "data/sts_n14_condhist.json",
                       "data/sts_n14_sensitivity.json", "data/sts_n13_guarantee.json", "data/sts_n14_guarantee.json", "data/sts_n13_crossnet.json",
                       "data/sts_n14_crossnet.json"] + [f"data/sts_n14_gate_{n}_sens.json" for n in ["D94", "ILL", "C30", "C24"]] if os.path.exists(p)]
    man = sm.build_manifest([OUT], "scratch/n14_compare.py", [".venv/bin/python", "scratch/n14_compare.py"], ins + [cm.RULE],
                            dict(model_hyperparameters="none fitted here"), "")
    sm.write_manifest(man, OUT)
    print(f"compare: {len(rows)} rows; differs {n_diff}; within std {n_within}")


if __name__ == "__main__":
    main()
