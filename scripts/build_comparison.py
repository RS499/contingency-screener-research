import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import classical_manifest as cm

TRADEOFF = "data/tradeoff_curve.json"
CLASSICAL = "data/classical_screen_metrics.json"
OUT = "data/comparison_curve.json"
COVERAGES = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98]
MODELS = ["ridge", "histgb"]


def conformal_points(records, model, coverages):
    points = []
    for r in records:
        cov = round(r["coverage_target"], 2)
        if r["model"] != model or cov not in coverages:
            continue
        points.append(dict(label=f"coverage {cov:.2f}", coverage_target=cov,
                           avoided=1.0 - r["escalation"],
                           avoided_std=r["escalation_std"],
                           missed_viol=r["missed_viol"],
                           missed_viol_std=r["missed_viol_std"],
                           net_speedup=r["net_speedup"],
                           net_speedup_std=r["net_speedup_std"],
                           coverage_emp=r["coverage_emp"],
                           q_hat=r["q_hat"]))
    points.sort(key=lambda p: p["coverage_target"])
    return points


def classical_points(rows, keyfield, labelfmt):
    points = []
    for r in rows:
        p = dict(label=labelfmt.format(r[keyfield]), **{keyfield: r[keyfield]},
                 avoided=r["avoided"], avoided_std=r.get("avoided_std", 0.0),
                 missed_viol=r["missed_viol"], missed_viol_std=r.get("missed_viol_std", 0.0),
                 net_speedup=r["net_speedup"], net_speedup_std=r.get("net_speedup_std", 0.0))
        if "q_hat" in r:
            p["q_hat"] = r["q_hat"]
            p["coverage_emp"] = r.get("coverage_emp")
        points.append(p)
    return points


def dominance_check(conformal, classical):
    out = []
    for c in classical:
        dominated_by = None
        for k in conformal:
            if k["avoided"] >= c["avoided"] and k["missed_viol"] <= c["missed_viol"]:
                dominated_by = k["label"]
                break
        beats_all = all(c["avoided"] > k["avoided"] or c["missed_viol"] < k["missed_viol"]
                        for k in conformal)
        out.append(dict(classical_point=c["label"], avoided=c["avoided"],
                        missed_viol=c["missed_viol"],
                        dominated_by_conformal=dominated_by,
                        on_frontier=(dominated_by is None), pareto_incomparable=beats_all))
    return out


def main():
    global TRADEOFF, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--tradeoff", default=TRADEOFF, help="conformal-gate curve JSON to compare against")
    ap.add_argument("--out", default=OUT, help="output comparison-curve JSON path")
    args = ap.parse_args()
    TRADEOFF, OUT = args.tradeoff, args.out

    with open(TRADEOFF) as f:
        tradeoff = json.load(f)
    with open(CLASSICAL) as f:
        cl = json.load(f)

    curves = {}
    for m in MODELS:
        curves[f"conformal_{m}"] = dict(
            kind="conformal gate (committed)", model=m,
            source=TRADEOFF, sweep="coverage target 0.90-0.98",
            has_coverage_guarantee=True,
            points=conformal_points(tradeoff["records"], m, COVERAGES))

    curves["classical_conformal"] = dict(
        kind="classical sensitivity screen, CONFORMALIZED (same gate code)",
        model="sensitivity", source=CLASSICAL, sweep="coverage target 0.90-0.98",
        has_coverage_guarantee=True,
        points=classical_points(cl["conformalized"], "coverage_target", "coverage {:.2f}"))
    curves["classical_delta"] = dict(
        kind="classical sensitivity screen, uncalibrated margin sweep",
        model="sensitivity", source=CLASSICAL, sweep="delta = tau - 0.94, 0 to 0.03",
        has_coverage_guarantee=False,
        points=classical_points(cl["delta_sweep"], "delta", "delta {:.3f}"))
    curves["classical_pi"] = dict(
        kind="Ejebe-Wollenberg performance-index ranking, solve top-k",
        model="PI rank", source=CLASSICAL, sweep="k = 1..186",
        has_coverage_guarantee=False,
        points=classical_points(cl["pi_ranking"], "k", "k={}"))

    dominance = {}
    for name in ("classical_conformal", "classical_delta", "classical_pi"):
        for m in MODELS:
            dominance[f"{name}_vs_conformal_{m}"] = dominance_check(
                curves[f"conformal_{m}"]["points"], curves[name]["points"])

    out = dict(
        axes=dict(x="fraction of exact solves avoided (1 - escalation)",
                  y="missed-violation rate (share of true violations)",
                  reading="lower-right dominates: more solves avoided at less safety cost"),
        n_seeds=cl["n_seeds"], seeds=cl["seeds"],
        std_convention="population std (ddof=0) over the five held-out splits",
        ms_solver=cl["ms_solver"], ms_solver_basis=cl["ms_solver_basis"],
        ms_classical_headline=cl["ms_classical_headline"],
        ms_classical_accountings=cl["ms_classical_accountings"],
        net_speedup_accounting=("every net_speedup in the classical curves uses the HEADLINE "
                                "accounting (apply + amortized Jacobian factorization); the other "
                                "two accountings are in ms_classical_accountings"),
        coverage_note=cl["coverage_note"],
        nonconverged_convention=cl["nonconverged_convention"],
        pi_definition=cl["pi_definition"],
        curves=curves, dominance=dominance)

    run_settings = dict(task="classical baseline: comparison artifact",
                        conformal_source=TRADEOFF, classical_source=CLASSICAL,
                        recomputed_any_surrogate_number=False,
                        tuned=("yes - v2 promoted M2 models" if "_v2" in TRADEOFF
                               else "no - untuned M1 models"))
    cm.write_with_manifest(OUT, out, run_settings)

    print("\n=== dominance: is any classical point NOT dominated by a conformal point? ===")
    for key, rows in dominance.items():
        frontier = [r for r in rows if r["on_frontier"]]
        print(f"  {key}: {len(frontier)} of {len(rows)} classical points on the frontier")
        for r in frontier[:6]:
            print(f"      {r['classical_point']}: avoided={r['avoided']*100:.1f}% "
                  f"missed={r['missed_viol']*100:.2f}%")


if __name__ == "__main__":
    main()
