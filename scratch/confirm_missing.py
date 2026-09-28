"""Read-only: recompute every "missing result" E1-E11 from notes/sts_review.md §6a directly from its
source file and print it next to the value the review claimed. Writes nothing.

Usage: .venv/bin/python scratch/confirm_missing.py
"""

import os
import json
import numpy as np
import pandas as pd


def load(path):
    with open(path) as fh:
        return json.load(fh)


def exists(path):
    ok = os.path.exists(path)
    if not ok:
        print(f"  FILE MISSING: {path}")
    return ok


def pm(vals, scale=100.0, dp=2):
    a = np.array(vals, dtype=float) * scale
    return f"{a.mean():.{dp}f}±{a.std():.{dp}f}"


if __name__ == "__main__":
    print("=== E1 limit sweep (data/sweep_results_long.parquet, target 0.90, seed mean) ===")
    if exists("data/sweep_results_long.parquet"):
        d = pd.read_parquet("data/sweep_results_long.parquet")
        s = d[np.isclose(d["target"], 0.9)].groupby(["L", "model"]).agg(esc=("esc_observed", "mean"),
                                                                        bm=("boundary_mass", "mean")).reset_index()
        for fam in ["histgb", "ridge"]:
            sub = s[s["model"] == fam]
            low = sub[(sub["L"] >= 0.8999) & (sub["L"] <= 0.9361)]
            print(f"  {fam}: esc over L in [0.900, 0.936]: {100*low['esc'].min():.2f}%–{100*low['esc'].max():.2f}%")
            for L in [0.920, 0.930, 0.936, 0.938, 0.939, 0.940, 0.945, 0.950]:
                row = sub[np.isclose(sub["L"], L)]
                print(f"    L={L:.3f}: esc {100*row['esc'].iloc[0]:.2f}%  boundary mass [L, L+q_hat) {100*row['bm'].iloc[0]:.2f}%")
        print(f"  seeds: {d['seed'].nunique()}; L grid {d['L'].min():.3f}–{d['L'].max():.3f} ({d['L'].nunique()} values)")
    print("\n=== E1 N-0 quintiles (data/quintile_boundary_mass.json) ===")
    if exists("data/quintile_boundary_mass.json"):
        q = load("data/quintile_boundary_mass.json")
        for r in q["quintiles_low_to_high"]:
            print(f"  Q{r['quintile']}: base N-0 min {r['base_vm_min']:.5f}–{r['base_vm_max']:.5f}  "
                  f"boundary {r['boundary_mass_pct']:.2f}%  violation {r['violation_pct']:.2f}%")
        print(f"  spearman(base mean, boundary) = {q['step2_base_vm_mean_vs_boundary_mass']['spearman_rank_corr']}")
    print("\n=== E1 unconditioned build (data/unconditioned_base.json) ===")
    if exists("data/unconditioned_base.json"):
        u = load("data/unconditioned_base.json")
        for k in ["committed_gated", "unconditioned"]:
            x = u[k]
            print(f"  {k}: boundary {x['boundary_0p94_to_0p945_pct']}%  violation {x['violation_rate_pct']}%  "
                  f"N-0 median {x['n0_min_vm_median']}  N-0 below 0.94 {x['n0_share_below_0p94_pct']}%  "
                  f"converged N-1 {x['converged_n1_rows']}")
        print(f"  unconditioned manifest present: {os.path.exists('data/unconditioned_base.manifest.json')}")
        # recompute the headline 28.83 from the parquet itself
        if exists("data/unconditioned_base.parquet"):
            up = pd.read_parquet("data/unconditioned_base.parquet", columns=["outaged_type", "converged", "min_vm"])
            n1 = up[(up["outaged_type"] != "none") & (up["converged"].astype(bool))]
            y = n1["min_vm"].to_numpy()
            print(f"  recomputed from parquet: boundary {100*((y >= 0.94) & (y < 0.945)).mean():.2f}%  "
                  f"violation {100*(y < 0.94).mean():.2f}%  rows {len(y)}")

    print("\n=== E4 case30 speedup (data/case30_thermal/case30_thermal_frozen.json → records) ===")
    c30 = load("data/case30_thermal/case30_thermal_frozen.json")
    for fam in ["histgb", "ridge"]:
        for t in [0.90, 0.96, 0.97]:
            rows = [r for r in c30["records"] if r["family"] == fam and abs(r["coverage_target"] - t) < 1e-9]
            print(f"  {fam}@{t}: speedup {pm([r['net_speedup'] for r in rows], 1.0)}x  esc {pm([r['escalation'] for r in rows])}%  "
                  f"missed {pm([r['missed_viol'] for r in rows])}%")

    print("\n=== E5 held-out operating point (tuning_search inner_cov_at x tuned_metrics sweep) ===")
    ts = load("data/tuning_search.json")
    tm = load("data/tuned_metrics.json")
    for fam in ["histgb", "ridge"]:
        miss, esc, spd, covs = [], [], [], []
        for seed in range(5):
            tag = ts["selections"][str(seed)][fam]["m2"]
            cov = [r for r in ts["records"] if r["family"] == fam and r["seed"] == seed and r["tag"] == tag][0]["inner_cov_at"]
            rec = [r for r in tm["records"] if r["family"] == fam and r["seed"] == seed and r["metric"] == "m2"][0]
            sw = [x for x in rec["sweep"] if abs(x["coverage_target"] - cov) < 1e-9][0]
            covs.append(cov)
            miss.append(sw["missed_viol"])
            esc.append(sw["escalation"])
            spd.append(sw["net_speedup"])
        print(f"  {fam}: inner targets {covs}; missed {pm(miss)}% (per seed {[round(100*m, 2) for m in miss]}; "
              f"{sum(1 for m in miss if m > 0.01)}/5 above 1%); esc {pm(esc, 100, 1)}%; speedup {pm(spd, 1.0)}x")

    print("\n=== E6 classical conformal screen (data/comparison_curve_v2.json) ===")
    cc = load("data/comparison_curve_v2.json")
    for p in cc["curves"]["classical_conformal"]["points"][:3]:
        print(f"  {p['label']}: avoided {100*p['avoided']:.1f}%  missed {100*p['missed_viol']:.2f}±{100*p['missed_viol_std']:.2f}%  "
              f"speedup {p['net_speedup']:.2f}x")
    dom = cc["dominance"]
    for key in dom:
        pts = dom[key]
        if isinstance(pts, list):
            n_dom = sum(1 for x in pts if x.get("dominated_by_conformal"))
            print(f"  {key}: dominated at {n_dom}/{len(pts)} points")

    print("\n=== E7 Mondrian vs global (data/mondrian_element_summary.json → aggregate) ===")
    agg = pd.DataFrame(load("data/mondrian_element_summary.json")["aggregate"])
    for (cal, model, t), g in agg.groupby(["calibration", "model", "target"]):
        print(f"  {cal:8s} {model:6s} {t:.2f}: esc {pm(g['escalation'], 100, 1)}%  missed {pm(g['missed_rate'])}%  "
              f"cov {pm(g['coverage_emp'], 100, 1)}%")

    print("\n=== E8 certify-only speedup, false flags (data/flag_confusion_long.parquet) ===")
    fc = pd.read_parquet("data/flag_confusion_long.parquet")
    for fam, t in [("histgb", 0.90), ("ridge", 0.90), ("histgb", 0.97), ("ridge", 0.94)]:
        sub = fc[(fc["model"] == fam) & np.isclose(fc["target"], t)]
        cert = sub["certified_frac"].to_numpy()
        print(f"  {fam}@{t}: certified {pm(cert, 100, 1)}%  certify-only speedup {pm(1 / (1 - cert), 1.0)}x  "
              f"flag precision {sub['flag_precision'].mean():.3f}  false flags (of all) {pm(sub['false_flag_rate_of_all'], 100, 1)}%")

    print("\n=== E9 miss depth at operating points (data/missed_depth.json pooled; data/qlimit_class.json) ===")
    md = load("data/missed_depth.json")
    ql = load("data/qlimit_class.json")
    for fam, t in [("ridge", "0.94"), ("histgb", "0.97")]:
        p = md["families"][fam]["pooled"][t]
        seeds_deep = [x["seed"] for x in ql["per_operating_point"][fam]["per_seed_depth"] if x["max_depth"] > 0.09]
        print(f"  {fam}@{t}: n missed {p['count']}  max depth {p['max']:.4f} pu  p99 {p['p99']:.4f}  "
              f"within q_hat {100*p['share_below_qhat']:.1f}%  seeds certifying the 0.0915 case: {seeds_deep}")

    print("\n=== E10 drift tests: see scratch/drift_summary.py ===")

    print("\n=== E11 break-even (data/break_even.json → break_even_at_operating_points) ===")
    be = load("data/break_even.json")["break_even_at_operating_points"]
    for fam in ["ridge", "histgb"]:
        for acct in ["gen_only", "gen_plus_training_plus_search"]:
            x = be[fam][acct]
            print(f"  {fam} {acct}: target {x['target']}  saving {x['saving_ms_per_case']:.3f} ms/case  "
                  f"one-time {x['one_time_cost_s']:.0f} s  break-even {x['break_even_cases']:,.0f} contingencies "
                  f"= {x['break_even_scenarios']:,.0f} base-case sweeps")
    ps = load("data/parallel_speedup.json")["best_parallel"]
    print(f"  parallel context: {ps['n_workers']} workers → {ps['speedup']:.2f}x")


def extras():
    """Table-ready extras for the placement plan: E5 held-out coverage, E8 certify-only speedup at
    every Table II target, E6 classical Table I row."""
    ts = load("data/tuning_search.json")
    tm = load("data/tuned_metrics.json")
    print("\n=== E5 held-out rows incl. coverage ===")
    for fam in ["ridge", "histgb"]:
        cov_emp = []
        for seed in range(5):
            tag = ts["selections"][str(seed)][fam]["m2"]
            cov = [r for r in ts["records"] if r["family"] == fam and r["seed"] == seed and r["tag"] == tag][0]["inner_cov_at"]
            rec = [r for r in tm["records"] if r["family"] == fam and r["seed"] == seed and r["metric"] == "m2"][0]
            cov_emp.append([x for x in rec["sweep"] if abs(x["coverage_target"] - cov) < 1e-9][0]["coverage_emp"])
        print(f"  {fam}: empirical coverage at held-out targets {pm(cov_emp, 100, 1)}%")
    print("\n=== E8 certify-only speedup at every Table II target ===")
    fc = pd.read_parquet("data/flag_confusion_long.parquet")
    for fam in ["ridge", "histgb"]:
        out = []
        for t in [0.90, 0.94, 0.95, 0.96, 0.97, 0.98]:
            sub = fc[(fc["model"] == fam) & np.isclose(fc["target"], t)]
            out.append(f"{t:.2f}: {pm(1 / (1 - sub['certified_frac'].to_numpy()), 1.0)}")
        print(f"  {fam}: " + "; ".join(out))
    print("\n=== E6 classical Table I row (data/classical_screen_metrics.json) ===")
    c = load("data/classical_screen_metrics.json")
    fq = c["fit_quality"]
    k = c["conformalized"][0]
    print(f"  MAE {1000*fq['mae']:.2f}±{1000*fq['mae_std']:.2f} (x1e-3)  R2 {fq['r2']:.2f}±{fq['r2_std']:.2f}  "
          f"target {k['coverage_target']}  esc {100*k['escalation']:.1f}±{100*k['escalation_std']:.1f}  "
          f"missed {100*k['missed_viol']:.2f}±{100*k['missed_viol_std']:.2f}  speedup {k['net_speedup']:.2f}±{k['net_speedup_std']:.2f}")


if __name__ == "__main__":
    extras()
