"""Read-only: independently recompute the reviewer-subagent claims that the review relies on.
Loads existing data/ files only; writes nothing.

Usage: .venv/bin/python scratch/verify_reviewer_claims.py
"""

import json
import numpy as np
import pandas as pd

LIMIT = 0.94


def load(path):
    with open(path) as fh:
        return json.load(fh)


def sweep_at(rec, target):
    for s in rec["sweep"]:
        if abs(s["coverage_target"] - target) < 1e-9:
            return s
    return None


if __name__ == "__main__":
    tm = load("data/tuned_metrics.json")
    ts = load("data/tuning_search.json")

    print("=== (a) held-out (inner-split) operating point vs test-picked point ===")
    for fam in ["ridge", "histgb"]:
        miss = []
        esc = []
        covs = []
        for seed in range(5):
            tag = ts["selections"][str(seed)][fam]["m2"]
            inner = [r for r in ts["records"] if r["family"] == fam and r["seed"] == seed and r["tag"] == tag]
            cov = inner[0]["inner_cov_at"]
            rec = [r for r in tm["records"] if r["family"] == fam and r["seed"] == seed and r["metric"] == "m2"][0]
            s = sweep_at(rec, cov)
            covs.append(cov)
            miss.append(s["missed_viol"])
            esc.append(s["escalation"])
        miss = np.array(miss)
        esc = np.array(esc)
        print(f"  {fam}: inner-chosen targets {covs}; test missed {100*miss.mean():.2f}+-{100*miss.std():.2f} "
              f"per-seed {[round(100*m, 2) for m in miss]}; esc {100*esc.mean():.1f}+-{100*esc.std():.1f}")
    for fam, t in [("ridge", 0.94), ("histgb", 0.97)]:
        per = [100 * sweep_at(r, t)["missed_viol"] for r in tm["records"] if r["family"] == fam and r["metric"] == "m2"]
        print(f"  test-picked {fam}@{t}: per-seed missed {[round(v, 2) for v in per]}")

    print("\n=== (b) Mondrian-by-element vs global calibration ===")
    ms = load("data/mondrian_element_summary.json")
    agg = pd.DataFrame(ms["aggregate"])
    g = agg.groupby(["calibration", "model", "target"]).agg(
        esc=("escalation", "mean"), esc_sd=("escalation", lambda x: x.std(ddof=0)),
        miss=("missed_rate", "mean"), miss_sd=("missed_rate", lambda x: x.std(ddof=0)),
        cov=("coverage_emp", "mean"))
    print((g * 100).round(2).to_string())

    print("\n=== (c) P(overshoot > q_hat | violation) at 0.90 ===")
    bh = load("data/barrier_height.json")
    for fam in ["ridge", "histgb"]:
        s = bh["summary_at_090"]["case118"][fam]
        keys = [k for k in s if "overshoot_gt" in k or "p99" in k]
        print(f"  {fam}: " + ", ".join(f"{k}={s[k]:.3f}" for k in keys))

    print("\n=== (d)/(h) flag precision, false flags, certify-only speedup ===")
    fc = pd.read_parquet("data/flag_confusion_long.parquet")
    print("  columns:", list(fc.columns))
    for fam, t in [("ridge", 0.90), ("histgb", 0.90), ("ridge", 0.94), ("histgb", 0.97)]:
        sub = fc[(fc["model"] == fam) & np.isclose(fc["target"], t)]
        cert = sub["certified_frac"].mean()
        line = f"  {fam}@{t}: certified {100*cert:.1f}%  certify-only speedup ~{1/(1-cert):.2f}x"
        for col in ["flagged_frac", "flag_precision", "false_flag_rate_of_all"]:
            if col in sub.columns:
                line += f"  {col}={sub[col].mean():.3f}"
        print(line)

    print("\n=== (e)/(f) N-1 insecurity per base; persistence of the N-0 minimum ===")
    df = pd.read_parquet("data/dataset.parquet", columns=["scenario_id", "outaged_type", "converged", "min_vm",
                                                           "n0_min_vm", "argmin_bus"])
    n1 = df[(df["outaged_type"] != "none") & (df["converged"])]
    per_base = n1.groupby("scenario_id")["min_vm"].apply(lambda v: int((v < LIMIT).sum()))
    print(f"  violating contingencies per base: min {per_base.min()}, median {per_base.median()}, "
          f"bases with zero: {(per_base == 0).sum()} of {len(per_base)}")
    d = (n1["min_vm"] - n1["n0_min_vm"]).abs()
    print(f"  median |min_vm - n0_min_vm| = {d.median():.2e}; share within 0.001 pu = {100*(d < 0.001).mean():.1f}%")
    base = df[df["outaged_type"] == "none"][["scenario_id", "argmin_bus"]].rename(columns={"argmin_bus": "n0_bus"})
    strip = n1[(n1["min_vm"] >= LIMIT) & (n1["min_vm"] < 0.945)].merge(base, on="scenario_id")
    print(f"  strip rows with same weakest bus as N-0 base: {100*(strip['argmin_bus'] == strip['n0_bus']).mean():.1f}%")
    print(f"  strip rows whose base n0_min_vm < 0.945: {100*(strip['n0_min_vm'] < 0.945).mean():.1f}%")
    print(f"  strip rows at bus index 75 (IEEE 76): {100*(strip['argmin_bus'] == 75).mean():.1f}%")

    print("\n=== (g) worst-miss mechanism record ===")
    mm = load("data/miss_mechanism.json")
    p1 = mm.get("part1_mechanism", {})
    for k, v in p1.items():
        print(f"  {k}: {json.dumps(v)[:400]}")

    print("\n=== (i)/(j) Q-limit class; deepest miss at operating points ===")
    ql = load("data/qlimit_class.json")
    for fam in ["ridge", "histgb"]:
        op = ql["per_operating_point"][fam]
        print(f"  {fam}: " + json.dumps({k: v for k, v in op.items() if k != "per_seed_depth"})[:300])
        print(f"     per_seed_depth: {json.dumps(op.get('per_seed_depth'))[:500]}")
    cs = load("data/classical_screen_metrics.json")
    print("  gens_at_qlim_base:", json.dumps(cs.get("gens_at_qlim_base", "absent"))[:200])
