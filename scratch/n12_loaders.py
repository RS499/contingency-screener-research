import os
import sys
import json
import time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import make_splits as ms
import baselines as bl
import n5_gate_eval as n5

# N12 Step 2: loaders for the four networks and the reproduction check (scratch/n12_decision_rule.md §0).
# Each network is loaded exactly as the script that produced its gate results did: n5_gate_eval.load_relabeled
# (used directly by scratch/n5_gate_eval.py, and by scratch/n10_gate_illinois.py and scratch/n11_smallnets.py),
# then make_splits.build_design_matrix; element key = outaged_idx + (n_line if trafo). Per split (seeds 0-4) the
# fixed-budget static catch at the gate's k_B (histgb, held-out point) is recomputed and must equal the stored
# value exactly; a network that does not reproduce is stopped.
# Run directly: writes scratch/n12_repro_check.json.

NETS = {
    "case118": dict(data="data/dataset.parquet", labels="data/sts_n2_label_audit.parquet",
                    gate="data/sts_n5_gate_094.json", n_line=173, n_branch=186),
    "case_illinois200": dict(data="data/netstudy/case_illinois200/dataset.parquet",
                             labels="data/sts_n10_relabel_illinois200.parquet",
                             gate="data/sts_n10_illinois.json", n_line=179, n_branch=245),
    "case30_thermal": dict(data="data/case30_thermal/dataset.parquet",
                           labels="data/sts_n11_relabel_case30_thermal.parquet",
                           gate="data/sts_n11_smallnets.json", n_line=41, n_branch=41),
    "case24_ieee_rts": dict(data="data/netstudy/case24_ieee_rts/dataset.parquet",
                            labels="data/sts_n11_relabel_case24_ieee_rts.parquet",
                            gate="data/sts_n11_smallnets.json", n_line=33, n_branch=38),
}
SEEDS = [0, 1, 2, 3, 4]
LIMIT = 0.94
OUT = "scratch/n12_repro_check.json"


def gate_json(name):
    g = json.load(open(NETS[name]["gate"]))
    if name in ("case30_thermal", "case24_ieee_rts"):
        return g["networks"][name]
    return g


def held_out_points(name, fam):
    pts = [p for p in gate_json(name)["points"] if p["family"] == fam and p["point"] == "held_out"]
    out = {}
    for p in pts:
        out[int(p["seed"])] = p
    return out


def load(name):
    cfg = NETS[name]
    df, feature_cols, info = n5.load_relabeled(cfg["data"], cfg["labels"])
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    is_trafo = df["outaged_type"].to_numpy() == "trafo"
    ek = df["outaged_idx"].to_numpy(np.int64) + np.where(is_trafo, cfg["n_line"], 0)
    return dict(name=name, df=df, X=X, y=y, groups=groups, elem_key=ek, info=info)


def static_at_k(d, seed, k):
    # the baselines.py fixed-budget static ranking (same k for every test base case) at budget k
    splits = ms.make_splits(d["groups"], seed)
    te = splits["test"]
    train_mask = np.zeros(len(d["df"]), dtype=bool)
    train_mask[splits["train"]] = True
    score, _ = bl.static_severity_score(d["df"], train_mask, d["elem_key"])
    scen = d["df"]["scenario_id"].to_numpy(np.int64)[te]
    viol = d["y"][te] < LIMIT
    k_max = max(NETS[d["name"]]["n_branch"], int(pd.Series(scen).value_counts().max()))
    curve, _, _ = bl.capture_curve(scen, score[te], d["elem_key"][te].astype(float), viol, k_max)
    if k <= 0:
        return 0.0
    return float(bl.at_k(curve, k))


def check(d):
    pts = held_out_points(d["name"], "histgb")
    rows = []
    for seed in SEEDS:
        p = pts[seed]
        mine = static_at_k(d, seed, int(p["k_B"]))
        rows.append(dict(seed=seed, k_B=int(p["k_B"]), static_catch_B_stored=p["static_catch_B"],
                         static_catch_B_n12=mine, exact=bool(mine == p["static_catch_B"])))
    return rows


def main():
    t0 = time.time()
    out = {}
    for name in NETS:
        d = load(name)
        rows = check(d)
        ok = bool(len([r for r in rows if r["exact"]]) == len(rows))
        out[name] = dict(labels=d["info"], per_split=rows, all_exact=ok)
        print(f"{name}: static catch at k_B reproduced exactly in {len([r for r in rows if r['exact']])}/5 splits", flush=True)
    with open(OUT, "w") as f:
        json.dump(dict(check="N12 Step 2: per-split fixed-budget static catch at k_B (histgb, held-out) reproduced exactly",
                       networks=out, wall_s=time.time() - t0), f, indent=2)


if __name__ == "__main__":
    main()
