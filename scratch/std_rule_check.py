"""Read-only: (1) every directional mean ± std claim in the STS paper tested against the project std
rule (a difference is real only if it exceeds the LARGER of the two stds); (2) numbers that refer to
the same quantity but are printed differently. Writes nothing.

Usage: .venv/bin/python scratch/std_rule_check.py
"""

import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, "scratch")
import number_check


def load(path):
    with open(path) as fh:
        return json.load(fh)


def verdict(gap, sd, same):
    if same:
        return "SUPPORTED (no-difference claim; gap <= std)" if abs(gap) <= sd else "NOT SUPPORTED (gap > std)"
    return "SUPPORTED" if abs(gap) > sd else "NOT SUPPORTED (gap <= larger std)"


def line(claim, a, sa, b, sb, where, same=False):
    gap = a - b
    sd = max(sa, sb)
    print(f"| {where} | {claim} | {a:.4g} ± {sa:.3g} vs {b:.4g} ± {sb:.3g} | {gap:+.4g} | {sd:.3g} | {verdict(gap, sd, same)} |")


if __name__ == "__main__":
    tc = load("data/tradeoff_curve_v2.json")
    tm = load("data/tuned_metrics.json")
    pa = load("data/physics_ablation.json")
    ns2 = load("data/netstudy2/summary.json")
    fc = pd.read_parquet("data/flag_confusion_long.parquet")

    def r(model, t):
        return number_check.tc_row(tc, model, t)

    print("| Where (search text) | Claim | Values (mean ± pop. std) | Gap | Larger std | Verdict |")
    print("|---|---|---|---|---|---|")
    for fam in ["ridge", "histgb"]:
        x = r(fam, 0.90)
        line(f"{fam} coverage 'close to 90%' (no-difference claim)", 100 * x["coverage_emp"], 100 * x["coverage_emp_std"], 90.0, 0.0,
             "'coverage is close to 90'", same=True)
    for fam, t in [("ridge", 0.94), ("histgb", 0.97)]:
        x = r(fam, t)
        line(f"{fam}@{t} missed 'below 1%'", 1.0, 0.0, 100 * x["missed_viol"], 100 * x["missed_viol_std"],
             "'falling below 1\\% at 0.94' / 'just under a 1\\% mean'")
    for t in [0.90, 0.94, 0.95, 0.96, 0.97, 0.98]:
        a, b = r("histgb", t), r("ridge", t)
        line(f"ridge misses less than histgb at target {t}", 100 * a["missed_viol"], 100 * a["missed_viol_std"],
             100 * b["missed_viol"], 100 * b["missed_viol_std"], "'not safer at any point in the coverage axis'")
    maes = {f: [q["mae"] for q in tm["records"] if q["family"] == f and q["metric"] == "m2"] for f in ["ridge", "histgb"]}
    line("histgb 'much more accurate' (MAE, ×10³)", 1000 * np.mean(maes["ridge"]), 1000 * np.std(maes["ridge"]),
         1000 * np.mean(maes["histgb"]), 1000 * np.std(maes["histgb"]), "'much more accurate than the linear'")
    line("histgb faster at 0.90 (3.29 vs 2.04)", r("histgb", 0.9)["net_speedup"], r("histgb", 0.9)["net_speedup_std"],
         r("ridge", 0.9)["net_speedup"], r("ridge", 0.9)["net_speedup_std"], "'3.29 times speedup compared to 2.04'")
    a, b = r("ridge", 0.94), r("histgb", 0.97)
    line("ridge@0.94 vs histgb@0.97 missed (treated as equivalent, C8)", 100 * b["missed_viol"], 100 * b["missed_viol_std"],
         100 * a["missed_viol"], 100 * a["missed_viol_std"], "'run the models at a 0.94 or a 0.97'", same=True)
    line("ridge@0.94 vs histgb@0.97 escalation", 100 * a["escalation"], 100 * a["escalation_std"],
         100 * b["escalation"], 100 * b["escalation_std"], "'run the models at a 0.94 or a 0.97'", same=True)

    # ceilings vs saturation, per seed
    ceil = {f: [1 - q["p_pred_below_limit"] for q in tm["records"] if q["family"] == f and q["metric"] == "m2"] for f in ["ridge", "histgb"]}
    sub = fc[(fc["model"] == "histgb") & np.isclose(fc["target"], 0.9)].sort_values("seed")
    sat = (1 - sub["n_viol"] / sub["n_test"]).to_numpy()
    line("histgb ceiling 'just above' saturation (82.79 vs 82.64)", 100 * np.mean(ceil["histgb"]), 100 * np.std(ceil["histgb"]),
         100 * np.mean(sat), 100 * np.std(sat), "'lands just above the saturation point'")
    line("ridge ceiling lower than histgb (74.89 vs 82.79)", 100 * np.mean(ceil["histgb"]), 100 * np.std(ceil["histgb"]),
         100 * np.mean(ceil["ridge"]), 100 * np.std(ceil["ridge"]), "'lower escalation ceiling of 74.89'")

    # cross-network A vs B absolute error
    comps = ns2["cross_comparisons"]
    ea = [c["abs_err_A"] for c in comps]
    eb = [abs(c["measured"] - c["pred_B_fit"]) if "pred_B_fit" in c else c.get("abs_err_B") for c in comps]
    line("predictor B 'slightly better' on abs. error (0.1056 vs 0.1163)", np.mean(ea), np.std(ea), np.mean(eb), np.std(eb),
         "'slightly better on absolute error'")

    # physics ablation
    def abl(cfg, fam, mode="m2_searched"):
        return [q["mae"] for q in pa["records"] if q["config"] == cfg and q["family"] == fam and q["mode"] == mode and q["status"] == "OK"]
    for fam in ["ridge", "histgb"]:
        base = abl("baseline", fam)
        for cfg in ["+F1", "+F1+F2", "+F1+F3", "+F1+F2+F3+F4"]:
            for mode in ["m2_searched", "m2_fixed"]:
                x = abl(cfg, fam, mode)
                line(f"{fam} {cfg} vs baseline MAE ({mode})", 1e6 * np.mean(x), 1e6 * np.std(x), 1e6 * np.mean(base), 1e6 * np.std(base),
                     "'no meaningful increase' / '+10.82\\%'", same=(cfg in ("+F1", "+F1+F3") or fam == "histgb"))
    f1 = load("data/f1_leakage_audit.json")["check_4_permutation"]
    line("F1 real vs shuffled (single seed; std is between-seed, unpaired)", 1e6 * f1["F1_real"]["mae"], 0.0,
         1e6 * f1["F1_shuffled"]["mae"], 1e6 * np.std(abl("baseline", "histgb")), "'falls within normal seed variation'", same=True)

    # formatting consistency: same source, different printed forms
    print("\n| Quantity (source) | Printed forms (line) |")
    print("|---|---|")
    rows, _ = number_check.check()
    groups = {}
    for q in rows:
        key = q.get("name") or q["source"]
        form = q["printed"].replace("{,}", ",")
        groups.setdefault(key, {}).setdefault(form, []).append(q["line"])
    for key, forms in groups.items():
        if len(forms) > 1 and key not in ("limit", "strip hi", "bus118", "bus30") and "coverage_levels" not in key:
            txt = "; ".join(f"`{f}` ({', '.join(str(l) for l in sorted(set(ls)))})" for f, ls in forms.items())
            print(f"| {key} | {txt} |")
