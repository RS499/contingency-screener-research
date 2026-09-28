"""Read-only semantic number audit for report/paper_current_STS.tex.

Each row: (tex line, literal as printed, the value recomputed from its INTENDED source key, source).
Writes nothing. Loads existing data/ files only; the parquet reads are column-restricted and fast.

Usage: .venv/bin/python scratch/number_audit.py
"""

import json
import numpy as np
import pandas as pd

LIMIT = 0.94


def load(path):
    with open(path) as fh:
        return json.load(fh)


def curve_row(curve, model, target):
    for r in curve["records"]:
        if r["model"] == model and abs(r["coverage_target"] - target) < 1e-9:
            return r
    return None


def case30_stats(recs, family, target):
    rows = [r for r in recs if r["family"] == family and abs(r["coverage_target"] - target) < 1e-9]
    out = {}
    for key in ["escalation", "missed_viol", "net_speedup", "coverage_emp"]:
        vals = np.array([r[key] for r in rows])
        out[key] = (vals.mean(), vals.std(), vals)
    return out


def show(line, printed, value, source):
    print(f"L{line:<4} {printed:<28} | {value:<44} | {source}")


if __name__ == "__main__":
    fz2 = load("data/frozen_poster_numbers_v2.json")
    tc2 = load("data/tradeoff_curve_v2.json")
    md = load("data/missed_depth.json")
    bh = load("data/barrier_height.json")
    c30 = load("data/case30_thermal/case30_thermal_frozen.json")
    ns2 = load("data/netstudy2/summary.json")
    pc = load("data/physics_conclusion.json")
    pa = load("data/physics_ablation.json")
    f1 = load("data/f1_leakage_audit.json")
    tm = load("data/tuned_metrics.json")
    be = load("data/break_even.json")
    clip = load("data/clip_artifact.json")

    print("=== Table I / II and Results (tradeoff_curve_v2.json records, model x target) ===")
    for model in ["ridge", "histgb"]:
        for t in [0.90, 0.94, 0.95, 0.96, 0.97, 0.98]:
            r = curve_row(tc2, model, t)
            print(f"  {model:6s} {t:.2f}: esc {100*r['escalation']:.1f}+-{100*r['escalation_std']:.1f}  "
                  f"cov {100*r['coverage_emp']:.1f}+-{100*r['coverage_emp_std']:.1f}  "
                  f"miss {100*r['missed_viol']:.2f}+-{100*r['missed_viol_std']:.2f}  "
                  f"spd {r['net_speedup']:.2f}+-{r['net_speedup_std']:.2f}  q_hat {r['q_hat']:.4f}")
    print("  keys available on a record:", sorted(curve_row(tc2, "ridge", 0.9).keys()))

    print("\n=== Model accuracy (tuned_metrics.json, m2 selections, per seed) ===")
    for fam in ["ridge", "histgb"]:
        rows = [r for r in tm["records"] if r["family"] == fam and r["metric"] == "m2"]
        maes = np.array([r["mae"] for r in rows])
        r2s = np.array([r["r2"] for r in rows])
        ms = np.array([r["ms_surrogate"] for r in rows])
        print(f"  {fam}: n={len(rows)} MAE {maes.mean():.5f}+-{maes.std():.5f}  R2 {r2s.mean():.3f}+-{r2s.std():.3f}"
              f"  ms_surrogate {ms.mean():.5f}+-{ms.std():.5f}")
    print("  break_even ms_infer_committed:", be["timing"]["ms_infer_committed"])
    print("  break_even ms_infer_measured_now:", be["timing"]["ms_infer_measured_now"])

    print("\n=== Crossings / ceilings (frozen_poster_numbers_v2.json) ===")
    print("  ", fz2["crossings_first_below_1pct_missed"])
    print("  ", fz2["ceilings"])
    for model, t in [("ridge", 0.94), ("histgb", 0.97)]:
        r = curve_row(tc2, model, t)
        print(f"  {model}@{t}: mean+1std missed = {100*(r['missed_viol']+r['missed_viol_std']):.2f}%")

    print("\n=== Miss depth at 0.90 (missed_depth.json pooled) ===")
    for fam in ["ridge", "histgb"]:
        p = md["families"][fam]["pooled"]["0.90"]
        print(f"  {fam}: " + ", ".join(f"{k}={v}" for k, v in p.items() if not isinstance(v, (list, dict))))
        print(f"  {fam} deepest: {md['families'][fam]['deepest_missed']}")
    for fam, t in [("ridge", "0.94"), ("histgb", "0.97")]:
        p = md["families"][fam]["pooled"].get(t)
        if p is not None:
            print(f"  {fam}@{t} pooled: count={p.get('count')} max={p.get('max')} p99={p.get('p99')}")

    print("\n=== S_mean (barrier_height.json summary_at_090.case118) ===")
    for fam in ["ridge", "histgb"]:
        s = bh["summary_at_090"]["case118"][fam]
        print(f"  {fam}: S_mean {s['S_mean_over_qhat_at_090_mean']:.4f}+-{s['S_mean_over_qhat_at_090_std']:.4f}"
              f"  q_hat {s['q_hat_at_090_mean']:.4f}")
    print("  identity_checks:", bh["identity_checks"])

    print("\n=== case30 thermal-feasible (case30_thermal_frozen.json records) ===")
    print(f"  boundary {c30['boundary_mass_pct']}  violation {c30['violation_rate_pct']}")
    for t in [0.90, 0.94, 0.95, 0.96, 0.97, 0.98]:
        for fam in ["ridge", "histgb"]:
            s = case30_stats(c30["records"], fam, t)
            n_under = int((s["missed_viol"][2] < 0.01).sum())
            print(f"  {fam:6s} {t:.2f}: esc {100*s['escalation'][0]:.2f}+-{100*s['escalation'][1]:.2f} "
                  f"miss {100*s['missed_viol'][0]:.2f}+-{100*s['missed_viol'][1]:.2f} ({n_under}/5 <1%) "
                  f"spd {s['net_speedup'][0]:.2f}+-{s['net_speedup'][1]:.2f}")

    print("\n=== Cross-network (netstudy2/summary.json) ===")
    print("  ", ns2["cross_network"]["A_mean_rel_error"], ns2["cross_network"]["B_mean_rel_error"],
          ns2["cross_network"]["A_mean_abs_error"], ns2["cross_network"]["B_mean_abs_error"])
    print("   within_network:", {k: v for k, v in ns2["within_network"].items() if k != "by_family"})

    print("\n=== Physics ablation ===")
    print("  best:", pc["best_config_by_mae"])
    for cfg in ["baseline", "+F1", "+F1+F2", "+F1+F3", "+F1+F2+F3+F4"]:
        for fam in ["ridge", "histgb"]:
            for mode in ["m2_searched", "m2_fixed"]:
                rows = [r for r in pa["records"] if r["config"] == cfg and r["family"] == fam
                        and r["mode"] == mode and r["status"] == "OK"]
                if not rows:
                    continue
                maes = np.array([r["mae"] for r in rows])
                op = "0.94" if fam == "ridge" else "0.97"
                esc = np.array([r["by_target"][op]["escalation"] for r in rows])
                mis = np.array([r["by_target"][op]["missed_viol"] for r in rows])
                print(f"  {cfg:14s} {fam:6s} {mode:11s} n={len(rows)} MAE {maes.mean():.6f}+-{maes.std():.6f}"
                      f"  @{op}: esc {100*esc.mean():.1f}+-{100*esc.std():.1f} miss {100*mis.mean():.2f}+-{100*mis.std():.2f}")
    print("  permutation:", {k: f1["check_4_permutation"][k]["mae"] for k in ["baseline", "F1_real", "F1_shuffled"]})

    print("\n=== Clip artifact ===")
    print("  clip_era:", {k: clip["clip_era"][k] for k in ["violation_rate_pct", "boundary_0p94_to_0p945_pct", "clip_atom_share_pct"]})
    print("  fixed_v2:", {k: clip["fixed_v2"][k] for k in ["violation_rate_pct", "boundary_0p94_to_0p945_pct", "clip_atom_share_pct"]})

    print("\n=== Recomputed from data/dataset.parquet (no artifact key exists) ===")
    df = pd.read_parquet("data/dataset.parquet")
    n1 = df[(df["outaged_type"] != "none")]
    conv = n1[n1["converged"]] if "converged" in n1.columns else n1.dropna(subset=["min_vm"])
    print(f"  converged N-1 rows {len(conv)}")
    if "max_vm" in conv.columns:
        print(f"  share max_vm > 1.05: {100*(conv['max_vm'] > 1.05).mean():.2f}%")
    y = conv["min_vm"].to_numpy()
    counts, edges = np.histogram(y, bins=np.arange(0.70, 0.97, 0.001))
    print(f"  tallest 0.001 bin share (bins from 0.70): {100*counts.max()/len(y):.2f}% at {edges[counts.argmax()]:.3f}")
    counts2, edges2 = np.histogram(y, bins=np.arange(0.94, 0.9451, 0.001))
    print(f"  tallest 0.001 bin inside [0.94,0.945): {100*counts2.max()/len(y):.2f}%")
    print(f"  share below 0.87: {100*(y < 0.87).mean():.2f}%")
    if "sampling_mode" in df.columns:
        base = df[df["outaged_type"] == "none"]
        print("  bases by sampling_mode:", base["sampling_mode"].value_counts().to_dict())
    print("  columns sample:", [c for c in df.columns if not c.startswith(("pload_", "qload_", "vm0_", "gen"))][:40])
