import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import classical_manifest as cm

TUNED = "data/tuned_metrics.json"
COMMITTED_FROZEN = "data/frozen_poster_numbers.json"
OUT_CURVE = "data/tradeoff_curve_v2.json"
OUT_FROZEN = "data/frozen_poster_numbers_v2.json"
MODELS = ["ridge", "histgb"]
METRIC = "m2"
LIMIT = 0.94


def m2_rows(tuned, family):
    return [r for r in tuned["records"] if r["family"] == family and r["metric"] == METRIC]


def aggregate_curve(tuned, family):
    rows = m2_rows(tuned, family)
    covers = [round(c, 2) for c in tuned["coverage_levels"]]
    records = []
    for cov in covers:
        esc, cvg, mis, spd, qh = [], [], [], [], []
        for r in rows:
            pt = next(p for p in r["sweep"] if abs(p["coverage_target"] - cov) < 1e-9)
            esc.append(pt["escalation"]); cvg.append(pt["coverage_emp"]); mis.append(pt["missed_viol"])
            spd.append(pt["net_speedup"]); qh.append(pt["q_hat"])
        records.append(dict(
            coverage_target=cov, model=family,
            q_hat=float(np.mean(qh)), q_hat_std=float(np.std(qh)),
            escalation=float(np.mean(esc)), escalation_std=float(np.std(esc)),
            coverage_emp=float(np.mean(cvg)), coverage_emp_std=float(np.std(cvg)),
            missed_viol=float(np.mean(mis)), missed_viol_std=float(np.std(mis)),
            net_speedup=float(np.mean(spd)), net_speedup_std=float(np.std(spd))))
    return records


def point_at(records, family, cov):
    for r in records:
        if r["model"] == family and abs(r["coverage_target"] - cov) < 1e-9:
            return r
    raise ValueError(f"no record for {family} at {cov}")


def first_below_1pct(records, family):
    rows = sorted([r for r in records if r["model"] == family], key=lambda r: r["coverage_target"])
    for r in rows:
        if r["missed_viol"] < 0.01:
            return r["coverage_target"], r["missed_viol"]
    return None, None


def ceiling_p_pred_below(tuned, family):
    vals = [r["p_pred_below_limit"] for r in m2_rows(tuned, family)]
    return float(np.mean(vals)), float(np.std(vals))


def m2_configs(tuned, family):
    out = {}
    for r in m2_rows(tuned, family):
        out[f"seed{r['seed']}"] = dict(tag=r["tag"], config=r["config"], n_iter=r["n_iter"])
    return out


def build_frozen_v2(curve, tuned, committed):
    ops = {}
    four = {}
    crossings = {}
    for fam in MODELS:
        p90 = point_at(curve, fam, 0.90)
        four[fam] = dict(escalation=p90["escalation"], coverage=p90["coverage_emp"],
                         missed_viol=p90["missed_viol"], net_speedup=p90["net_speedup"])
        ops[fam] = []
        for cov in (0.90, 0.94, 0.95, 0.96, 0.97, 0.98):
            r = point_at(curve, fam, cov)
            ops[fam].append(dict(coverage_target=cov, coverage_emp=r["coverage_emp"],
                                 escalation=r["escalation"], missed_viol=r["missed_viol"],
                                 net_speedup=r["net_speedup"]))
        cov_x, mis_x = first_below_1pct(curve, fam)
        crossings[fam] = dict(first_coverage_below_1pct_missed=cov_x, missed_at_that_coverage=mis_x)

    ridge_ceil = 1.0 - ceiling_p_pred_below(tuned, "ridge")[0]
    histgb_ceil = 1.0 - ceiling_p_pred_below(tuned, "histgb")[0]

    out = dict(
        provenance=("v2 = PROMOTED M2 (gate-aware) tuned surrogates. Supersedes the committed "
                    "frozen_poster_numbers.json for the paper's primary results; the committed file "
                    "is retained unchanged as the record of the hand-set models. Selection metric M2 "
                    "fixed a priori for both families."),
        four_metrics_at_90pct_coverage=dict(source=TUNED, **four),
        safety_operating_points=dict(source=TUNED, **ops),
        crossings_first_below_1pct_missed=dict(source=TUNED, **crossings),
        ceilings={
            "source": TUNED,
            "perfect_model_floor_saturation":
                committed["ceilings"]["perfect_model_floor_saturation"],
            "true_violation_rate": committed["dataset_facts"]["violation_rate_pct"] / 100.0,
            "escalation_at_max_band_width_approaches_P_pred_ge_0.94": dict(
                ridge=ridge_ceil, histgb=histgb_ceil,
                persistence=committed["ceilings"][
                    "escalation_at_max_band_width_approaches_P_pred_ge_0.94"]["persistence"])},
        dataset_facts=committed["dataset_facts"],
        two_by_two_v2=committed["two_by_two_v2"],
        ms_solver=committed["ms_solver"],
        n0_gate_pass_rate_pct=committed["n0_gate_pass_rate_pct"],
        copied_unchanged_note=("dataset_facts, two_by_two_v2, ms_solver, and n0_gate_pass_rate_pct "
                               "are model-independent and copied verbatim from "
                               "frozen_poster_numbers.json"))
    return out


def main():
    with open(TUNED) as f:
        tuned = json.load(f)
    with open(COMMITTED_FROZEN) as f:
        committed = json.load(f)

    records = []
    for fam in MODELS:
        records.extend(aggregate_curve(tuned, fam))

    curve_out = dict(
        seeds=tuned["seeds"], coverage_levels=tuned["coverage_levels"], limit=LIMIT,
        ms_solver=tuned["ms_solver"], operating_point=0.90,
        models=MODELS, selection_metric="m2 (gate-aware); fixed a priori for both families",
        provenance=("v2 tradeoff curve for the PROMOTED M2-tuned surrogates, aggregated from the "
                    "per-seed sweeps in data/tuned_metrics.json. Same schema as the committed "
                    "tradeoff_curve.json minus the perfect-model floor column (unused downstream)."),
        std_convention="population std (ddof=0) over five held-out splits",
        records=records)

    model_config = dict(
        selection_metric="m2 (gate-aware): max avoided s.t. inner missed <= 1%, tuned inside train",
        note=("histgb resolves to a different config per seed, so the 'model' is a tuning procedure, "
              "not a single hyperparameter vector; all five per-seed selections are recorded"),
        ridge=m2_configs(tuned, "ridge"), histgb=m2_configs(tuned, "histgb"))

    settings_curve = dict(task="promote tuned models: v2 tradeoff curve (M2)",
                          source=TUNED, selection_metric="m2", recomputed_committed=False)
    cm.write_with_manifest(OUT_CURVE, curve_out, settings_curve, model_config=model_config)

    frozen_out = build_frozen_v2(records, tuned, committed)
    settings_frozen = dict(task="promote tuned models: v2 frozen poster numbers (M2)",
                           source=TUNED, committed_source=COMMITTED_FROZEN,
                           model_independent_blocks_copied=True)
    cm.write_with_manifest(OUT_FROZEN, frozen_out, settings_frozen, model_config=model_config)

    print("\nv2 headline (M2, mean over 5 seeds):")
    for fam in MODELS:
        p = point_at(records, fam, 0.90)
        cx, mx = first_below_1pct(records, fam)
        ceil = 1.0 - ceiling_p_pred_below(tuned, fam)[0]
        print(f"  {fam:6s} @0.90: esc={p['escalation']*100:.1f}% miss={p['missed_viol']*100:.2f}% "
              f"spd={p['net_speedup']:.2f}x | sub-1% at cov {cx:.2f} (miss {mx*100:.2f}%) | "
              f"ceiling P(pred>=0.94)={ceil*100:.1f}%")


if __name__ == "__main__":
    main()
