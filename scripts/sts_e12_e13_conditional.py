import os
import sys
import json
import time
import hashlib
import subprocess
import numpy as np
import pandas as pd
from scipy.stats import binom

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
import gate_eval as ge
import manifest as mf

# E12/E13: conditional coverage under the committed global q_hat. No solves and no new fits: reads
# the M2 refit predictions written by scripts/sts_n1_class_conditional.py (checked there against
# data/tuned_metrics.json).
#   E12: coverage per outaged element (186) at target 0.90.
#   E13: coverage per test base case at target 0.90, and the share of test base cases with >= 1
#        missed violation at the operating points ridge@0.94 and histgb@0.97.

N1_PRED = "data/sts_n1_predictions_long.parquet"
OUT_JSON = "data/sts_e12_e13_conditional.json"
SEEDS = 5
LIMIT = 0.94
FAMILIES = ["ridge", "histgb"]
TARGET = 0.90
LOW = 0.85
OPERATING = {"ridge": 0.94, "histgb": 0.97}
ALSO_COVERAGES = [0.90, 0.94, 0.97]


def group_coverage(covered, keys):
    d = pd.DataFrame(dict(k=keys, c=covered))
    g = d.groupby("k")["c"].agg(["mean", "size"])
    return g


def coverage_stats(g, target):
    cov = g["mean"].to_numpy()
    n = g["size"].to_numpy()
    # reference: expected share below LOW if every group had coverage exactly `target`
    # (binomial sampling noise only), P(Binomial(n, target) < LOW * n)
    k_low = np.ceil(LOW * n).astype(np.int64) - 1
    p_low = binom.cdf(k_low, n, target)
    return dict(n_groups=int(len(cov)), rows_per_group_min=int(n.min()), rows_per_group_median=float(np.median(n)),
                min=float(cov.min()), p5=float(np.percentile(cov, 5)), median=float(np.median(cov)),
                share_below_085=float(np.mean(cov < LOW)),
                share_below_085_expected_if_exact_target=float(np.mean(p_low)))


def mean_std(vals):
    a = np.array(vals, dtype=np.float64)
    return dict(mean=float(a.mean()), std=float(a.std()), per_seed=[float(v) for v in a])


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def git_head():
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip()


def main():
    t0 = time.time()
    pl = pd.read_parquet(N1_PRED)
    per_seed = []
    worst_elements = []
    for seed in range(SEEDS):
        for fam in FAMILIES:
            sub = pl[(pl["seed"] == seed) & (pl["family"] == fam)]
            ca = sub[sub["split"] == "cal"]
            te = sub[sub["split"] == "test"]
            pt = te["pred"].to_numpy(); yt = te["y"].to_numpy()
            elem = (te["outaged_type"].astype(str) + "_" + te["outaged_idx"].astype(str)).to_numpy()
            sid = te["scenario_id"].to_numpy()
            rec = dict(seed=seed, family=fam)
            q90 = ge.calibrate_qhat(ca["pred"].to_numpy(), ca["y"].to_numpy(), TARGET)
            covered = yt >= pt - q90
            rec["q_hat_090"] = q90
            rec["marginal_coverage_090"] = float(covered.mean())
            ge_el = group_coverage(covered, elem)
            rec["E12_element"] = coverage_stats(ge_el, TARGET)
            low = ge_el.sort_values("mean").head(5)
            for k, row in low.iterrows():
                worst_elements.append(dict(seed=seed, family=fam, element=k, coverage=float(row["mean"]),
                                           n_rows=int(row["size"])))
            ge_base = group_coverage(covered, sid)
            rec["E13_base_coverage"] = coverage_stats(ge_base, TARGET)
            viol = yt < LIMIT
            any_viol = pd.Series(viol).groupby(sid).any()
            rec["n_test_bases"] = int(len(any_viol))
            rec["n_test_bases_with_violation"] = int(any_viol.sum())
            rec["any_miss"] = {}
            for cov in ALSO_COVERAGES:
                q = ge.calibrate_qhat(ca["pred"].to_numpy(), ca["y"].to_numpy(), cov)
                g = ge.run_gate(pt, q, LIMIT)
                missed = g["certify"] & viol
                per_base = pd.Series(missed).groupby(sid).any()
                n_missed_per_base = pd.Series(missed).groupby(sid).sum()
                rec["any_miss"][str(cov)] = dict(
                    q_hat=q,
                    share_of_test_bases_with_ge1_miss=float(per_base.mean()),
                    share_of_violating_test_bases_with_ge1_miss=float(per_base[any_viol].mean()),
                    missed_viol_rows=float(missed.sum() / max(int(viol.sum()), 1)),
                    max_misses_in_one_base=int(n_missed_per_base.max()),
                    mean_misses_per_base_given_ge1=(float(n_missed_per_base[per_base].mean())
                                                    if int(per_base.sum()) > 0 else 0.0))
            per_seed.append(rec)

    summary = {}
    for fam in FAMILIES:
        rs = [r for r in per_seed if r["family"] == fam]
        s = dict(marginal_coverage_090=mean_std([r["marginal_coverage_090"] for r in rs]))
        for block in ("E12_element", "E13_base_coverage"):
            s[block] = {}
            for k in ("min", "p5", "median", "share_below_085", "share_below_085_expected_if_exact_target"):
                s[block][k] = mean_std([r[block][k] for r in rs])
            s[block]["n_groups_per_seed"] = [r[block]["n_groups"] for r in rs]
            s[block]["rows_per_group_min_per_seed"] = [r[block]["rows_per_group_min"] for r in rs]
        s["any_miss"] = {}
        for cov in ALSO_COVERAGES:
            s["any_miss"][str(cov)] = {}
            for k in ("share_of_test_bases_with_ge1_miss", "share_of_violating_test_bases_with_ge1_miss",
                      "missed_viol_rows", "max_misses_in_one_base", "mean_misses_per_base_given_ge1"):
                s["any_miss"][str(cov)][k] = mean_std([r["any_miss"][str(cov)][k] for r in rs])
        s["operating_point"] = OPERATING[fam]
        s["any_miss_at_operating_point"] = s["any_miss"][str(OPERATING[fam])]
        summary[fam] = s

    wall = time.time() - t0
    out = dict(
        question="conditional coverage under the committed global q_hat: per outaged element and per base case",
        source_predictions=N1_PRED, target=TARGET, low_threshold=LOW, operating_points=OPERATING,
        definitions=dict(
            covered="y >= pred - q_hat (one-sided band), q_hat from ALL calibration rows (committed global rule)",
            E12_element="coverage over the test rows of each outaged element (186 elements), per split",
            E13_base_coverage="coverage over the 186 rows of each test base case, per split",
            share_below_085_expected_if_exact_target=("mean over groups of P(Binomial(n_g, 0.90) < 0.85 n_g): "
                                                      "the share expected below 0.85 from sampling noise alone if "
                                                      "every group had exactly 0.90 coverage"),
            any_miss=("share of test base cases in which at least one violation is certified safe "
                      "(certify & y < 0.94); also restricted to test base cases with at least one violation")),
        per_seed=per_seed, summary=summary, five_lowest_elements_per_split=worst_elements,
        std_convention="population std (ddof=0) over the five held-out splits",
        wall_time_s=wall)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    man = dict(
        schema="sts-new-analysis",
        artifacts=[OUT_JSON],
        generating_script="scripts/sts_e12_e13_conditional.py",
        regeneration_argv=[".venv/bin/python", "scripts/sts_e12_e13_conditional.py"],
        script_sha256=sha256_of("scripts/sts_e12_e13_conditional.py"),
        repo_head_commit=git_head(),
        inputs=[dict(path=N1_PRED, sha256=sha256_of(N1_PRED)),
                dict(path="data/tuned_metrics.json", sha256=sha256_of("data/tuned_metrics.json"))],
        output_sha256=sha256_of(OUT_JSON),
        model_hyperparameters=("M2 committed selections, see data/sts_n1_class_conditional.manifest.json "
                               "model_hyperparameters (predictions produced there)"),
        seeds=list(range(SEEDS)),
        solver=dict(note="no AC solves in this script", pinned=mf.SOLVER),
        environment=mf.build_manifest(),
        wall_time_s=wall,
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(mf.manifest_path(OUT_JSON), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {OUT_JSON} + manifest; wall {wall:.1f}s")
    for fam in FAMILIES:
        s = summary[fam]
        print(f"  {fam}: element min={s['E12_element']['min']['mean']:.3f} p5={s['E12_element']['p5']['mean']:.3f} "
              f"share<0.85={s['E12_element']['share_below_085']['mean']:.3f} | base min={s['E13_base_coverage']['min']['mean']:.3f} "
              f"share<0.85={s['E13_base_coverage']['share_below_085']['mean']:.3f} | any-miss@{OPERATING[fam]}="
              f"{s['any_miss_at_operating_point']['share_of_test_bases_with_ge1_miss']['mean']:.3f}")


if __name__ == "__main__":
    main()
