import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import classical_manifest as cm

TUNED = "data/tuned_metrics.json"
TRADEOFF = "data/tradeoff_curve.json"
OUT = "data/tuned_frontier.json"
CEILINGS = [0.05, 0.01, 0.005, 0.001]
COVERAGES = [round(0.70 + 0.01 * i, 2) for i in range(30)]


def committed_curve(tradeoff, model):
    curve = {}
    for r in tradeoff["records"]:
        if r["model"] != model:
            continue
        cov = round(r["coverage_target"], 2)
        curve[cov] = dict(avoided=1.0 - r["escalation"], avoided_std=r["escalation_std"],
                          missed=r["missed_viol"], missed_std=r["missed_viol_std"],
                          net_speedup=r["net_speedup"], net_speedup_std=r["net_speedup_std"])
    return curve


def tuned_curve(tuned, family, metric):
    rows = [r for r in tuned["records"] if r["family"] == family and r["metric"] == metric]
    by_cov = {}
    for cov in COVERAGES:
        av, mi, sp = [], [], []
        for r in rows:
            pt = next((p for p in r["sweep"] if round(p["coverage_target"], 2) == cov), None)
            if pt is None:
                continue
            av.append(1.0 - pt["escalation"])
            mi.append(pt["missed_viol"])
            sp.append(pt["net_speedup"])
        if av:
            by_cov[cov] = dict(avoided=float(np.mean(av)), avoided_std=float(np.std(av)),
                               missed=float(np.mean(mi)), missed_std=float(np.std(mi)),
                               net_speedup=float(np.mean(sp)), net_speedup_std=float(np.std(sp)),
                               avoided_per_seed=[float(x) for x in av],
                               missed_per_seed=[float(x) for x in mi])
    return by_cov


def frontier_mean_selected(curve, ceilings):
    covs = sorted(curve.keys())
    out = {}
    for ceil in ceilings:
        best = None
        for cov in covs:
            c = curve[cov]
            if c["missed"] <= ceil:
                best = dict(coverage=cov, avoided=c["avoided"], avoided_std=c["avoided_std"],
                            missed=c["missed"], missed_std=c["missed_std"],
                            net_speedup=c["net_speedup"], net_speedup_std=c["net_speedup_std"])
                break
        out[f"<= {ceil*100:g}%"] = best
    return out


def frontier_strict_per_seed(curve, ceilings):
    covs = sorted(curve.keys())
    n_seed = len(next(iter(curve.values()))["avoided_per_seed"])
    out = {}
    for ceil in ceilings:
        avoided_hits = []
        n_qual = 0
        for si in range(n_seed):
            hit = None
            for cov in covs:
                c = curve[cov]
                if c["missed_per_seed"][si] <= ceil:
                    hit = c["avoided_per_seed"][si]
                    break
            if hit is not None:
                avoided_hits.append(hit)
                n_qual += 1
        if avoided_hits:
            out[f"<= {ceil*100:g}%"] = dict(avoided=float(np.mean(avoided_hits)),
                                            avoided_std=float(np.std(avoided_hits)),
                                            n_seeds_qualifying=n_qual, n_seeds=n_seed)
        else:
            out[f"<= {ceil*100:g}%"] = None
    return out


def pred_below_stats(tuned, family, metric):
    vals = [r["p_pred_below_limit"] for r in tuned["records"]
            if r["family"] == family and r["metric"] == metric]
    return float(np.mean(vals)), float(np.std(vals))


def fit_stats(tuned, family, metric):
    rows = [r for r in tuned["records"] if r["family"] == family and r["metric"] == metric]
    mae = [r["mae"] for r in rows]
    r2 = [r["r2"] for r in rows]
    q90 = [r["q_hat_90"] for r in rows]
    return dict(mae=float(np.mean(mae)), mae_std=float(np.std(mae)),
                r2=float(np.mean(r2)), r2_std=float(np.std(r2)),
                q_hat_90=float(np.mean(q90)), q_hat_90_std=float(np.std(q90)))


def fmt_point(p):
    if p is None:
        return "unreachable"
    return f"{p['avoided']*100:.1f}+/-{p.get('avoided_std', 0)*100:.1f}% (cov {p['coverage']:.2f})"


def main():
    with open(TUNED) as f:
        tuned = json.load(f)
    with open(TRADEOFF) as f:
        tradeoff = json.load(f)

    families = ["ridge", "histgb"]
    table = {}
    fit = {}
    pbelow = {}
    frontier_strict = {}
    for fam in families:
        committed = committed_curve(tradeoff, fam)
        table[fam] = {"committed": frontier_mean_selected(committed, CEILINGS)}
        fit[fam] = {"committed": None}
        pbelow[fam] = {}
        frontier_strict[fam] = {}
        for metric in ("m1", "m2"):
            tc = tuned_curve(tuned, fam, metric)
            table[fam][metric] = frontier_mean_selected(tc, CEILINGS)
            frontier_strict[fam][metric] = frontier_strict_per_seed(tc, CEILINGS)
            fit[fam][metric] = fit_stats(tuned, fam, metric)
            m, s = pred_below_stats(tuned, fam, metric)
            pbelow[fam][metric] = dict(mean=m, std=s)

    out = dict(
        ceilings=CEILINGS,
        frontier_rule=("max fraction of exact solves avoided (1 - escalation) subject to MEAN "
                       "missed-violation <= ceiling; qualifying coverage chosen on the mean, avoided "
                       "reported as mean +/- population std at that coverage; applied IDENTICALLY to "
                       "committed and tuned rows"),
        mean_selected_limitation=("committed rows have no stored per-seed raw values "
                                  "(tradeoff_curve.json keeps only per-coverage mean+/-std), so the "
                                  "rule is mean-selected for cross-row comparability; the strict "
                                  "per-seed variant is provided for the tuned rows only in "
                                  "frontier_strict_per_seed_tuned. Do NOT convert the committed rows "
                                  "to strict-per-seed - it would make the four rows non-comparable."),
        committed_source=TRADEOFF, committed_recomputed=False,
        tuned_source=TUNED,
        std_convention="population std (ddof=0) over five held-out splits",
        frontier=table,
        frontier_strict_per_seed_tuned=frontier_strict,
        fit_quality_tuned=fit,
        p_pred_below_limit_tuned=pbelow,
        committed_ceilings_note="committed P(pred<0.94): ridge ~75.2%, histgb ~84.2% (paper IV-C)")
    settings = dict(task="hyperparameter tuning: matched-missed-rate frontier table",
                    committed_source=TRADEOFF, tuned_source=TUNED,
                    recomputed_any_committed_number=False)
    cm.write_with_manifest(OUT, out, settings)

    print("\n=== Matched-missed-rate frontier: max % solves avoided s.t. mean missed <= ceiling ===")
    for fam in families:
        print(f"\n--- {fam} ---")
        print(f"{'ceiling':>8} {'committed':>26} {'M1 (MAE)':>26} {'M2 (gate)':>26}")
        for ceil in CEILINGS:
            key = f"<= {ceil*100:g}%"
            print(f"{key:>8} {fmt_point(table[fam]['committed'][key]):>26} "
                  f"{fmt_point(table[fam]['m1'][key]):>26} {fmt_point(table[fam]['m2'][key]):>26}")
    print("\n=== fit quality (tuned) + P(pred<0.94) ===")
    for fam in families:
        for metric in ("m1", "m2"):
            fq = fit[fam][metric]
            pb = pbelow[fam][metric]
            print(f"  {fam:6s} {metric.upper()}: MAE={fq['mae']:.5f}+/-{fq['mae_std']:.5f} "
                  f"R2={fq['r2']:.4f}+/-{fq['r2_std']:.4f} q90={fq['q_hat_90']:.5f} "
                  f"P(pred<0.94)={pb['mean']*100:.1f}+/-{pb['std']*100:.1f}%")


if __name__ == "__main__":
    main()
