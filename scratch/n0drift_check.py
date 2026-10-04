import os
import sys
import json
import time
import hashlib
import platform
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
sys.path.insert(0, HERE)
import make_splits as ms
import gate_eval as ge
import manifest as mf
import n9_budget_curve as bc

# No-retrain check of the feature/label mismatch (plan review 2026-10-04 (e)).
# Model inputs (vm0_*, n0_min_vm) come from the pinned one-way N-0 solve; labels from the switch-back solve.
# (1) case118 held-out point, histgb and ridge, N5 M2 configs refit on train (unchanged): missed rate and
#     any-miss share on test, (a) as evaluated, (b) with the 9 bases whose corrected N-0 minimum is below 0.94
#     removed from calibration AND test (no retraining).
# (2) Missed rate on test by the size of each base's N-0 drift |corrected - stored N-0 minimum|.
# (3) N-0 drift counts for case_illinois200, case30_thermal, case24_ieee_rts from their relabel files.

N2 = "data/sts_n2_label_audit.parquet"
N5 = "data/sts_n5_gate_094.json"
OUT = "data/sts_n0drift_check.json"
LIMIT = 0.94
SEEDS = [0, 1, 2, 3, 4]
FAMILIES = ["histgb", "ridge"]
BINS = [0.0, 1e-6, 1e-4, 1e-3, 1.0]
BIN_NAMES = ["none (<=1e-6)", "1e-6..1e-4", "1e-4..1e-3", ">1e-3"]
OTHER = {
    "case_illinois200": "data/sts_n10_relabel_illinois200.parquet",
    "case30_thermal": "data/sts_n11_relabel_case30_thermal.parquet",
    "case24_ieee_rts": "data/sts_n11_relabel_case24_ieee_rts.parquet",
}


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def n0_table(path):
    a = pd.read_parquet(path, columns=["scenario_id", "outaged_type", "stored_min_vm", "corrected_min_vm"])
    n0 = a[a["outaged_type"] == "none"].copy()
    n0["drift"] = (n0["corrected_min_vm"] - n0["stored_min_vm"]).abs()
    return n0


def drift_counts(n0):
    if len(n0) == 0:
        return dict(n_bases=0, note="N-0 rows were not audited in this relabel file; drift not measurable without N-0 switch-back solves")
    d = n0["drift"].to_numpy()
    return dict(n_bases=int(len(d)), gt_1e6=int((d > 1e-6).sum()), gt_1e4=int((d > 1e-4).sum()),
                gt_1e3=int((d > 1e-3).sum()), max=float(np.nanmax(d)),
                corrected_n0_below_limit=int((n0["corrected_min_vm"] < LIMIT).sum()))


def gate_metrics(p_ca, y_ca, p_te, y_te, scen_te, tgt):
    q = ge.calibrate_qhat(p_ca, y_ca, tgt)
    cert = (p_te - q) >= LIMIT
    tv = y_te < LIMIT
    missed_rows = cert & tv
    per = pd.DataFrame({"s": scen_te, "m": missed_rows, "v": tv}).groupby("s")
    any_miss = per["m"].any()
    has_v = per["v"].any()
    return dict(q_hat=float(q), missed=float(missed_rows.sum() / tv.sum()),
                any_miss_share=float(any_miss.mean()),
                any_miss_share_bases_with_violation=float(any_miss[has_v].mean()),
                n_test=int(len(y_te)), n_true_viol=int(tv.sum())), missed_rows, tv


def main():
    t0 = time.time()
    n0 = n0_table(N2)
    bad = set(n0.loc[n0["corrected_min_vm"] < LIMIT, "scenario_id"].tolist())
    drift_of = dict(zip(n0["scenario_id"], n0["drift"]))
    g = json.load(open(N5))
    d = bc.load("094")
    scen_all = d["df"]["scenario_id"].to_numpy(np.int64)
    rows = []
    for seed in SEEDS:
        spl = ms.make_splits(d["groups"], seed)
        kept = ms.select_features(d["X"], spl["train"])
        te, ca = spl["test"], spl["cal"]
        Xte = d["X"][kept].iloc[te].to_numpy(np.float32)
        y_te = d["y"][te]
        scen_te = scen_all[te]
        keep_te = ~np.isin(scen_te, list(bad))
        keep_ca = ~np.isin(scen_all[ca], list(bad))
        for fam in FAMILIES:
            f5 = bc.n5_config(g, seed, fam)
            tgt = g["selections"][str(seed)][fam]["m2_inner_cov_at"]
            p_ca, y_ca, p_te = bc.fit_predict(d, seed, fam, f5["config"], Xte, kept)
            a, missed_rows, tv = gate_metrics(p_ca, y_ca, p_te, y_te, scen_te, tgt)
            b, _, _ = gate_metrics(p_ca[keep_ca], y_ca[keep_ca], p_te[keep_te], y_te[keep_te], scen_te[keep_te], tgt)
            ref = [p for p in g["points"] if p["seed"] == seed and p["family"] == fam and p["point"] == "held_out"][0]
            dr = np.array([drift_of[s] for s in scen_te])
            by_bin = []
            for i in range(len(BIN_NAMES)):
                m = (dr > BINS[i]) & (dr <= BINS[i + 1]) if i > 0 else (dr <= BINS[1])
                nv = int(tv[m].sum())
                by_bin.append(dict(bin=BIN_NAMES[i], n_rows=int(m.sum()), n_true_viol=nv,
                                   missed=float(missed_rows[m].sum() / nv) if nv > 0 else None))
            rows.append(dict(seed=seed, family=fam, target=tgt, as_evaluated=a, without_9_bases=b,
                             repro_missed_vs_n5=abs(a["missed"] - ref["missed"]), missed_by_n0_drift=by_bin,
                             n_test_rows_removed=int((~keep_te).sum()), n_cal_rows_removed=int((~keep_ca).sum())))
            print(f"seed {seed} {fam}: missed {100*a['missed']:.2f}% -> {100*b['missed']:.2f}% without 9 bases; "
                  f"any-miss {100*a['any_miss_share']:.1f}% -> {100*b['any_miss_share']:.1f}%", flush=True)
    summary = {}
    for fam in FAMILIES:
        r = [x for x in rows if x["family"] == fam]
        def ms2(vals):
            v = np.array(vals, dtype=float)
            return [float(v.mean()), float(v.std())]
        bins = {}
        for i, name in enumerate(BIN_NAMES):
            mv = sum(x["missed_by_n0_drift"][i]["missed"] * x["missed_by_n0_drift"][i]["n_true_viol"]
                     for x in r if x["missed_by_n0_drift"][i]["missed"] is not None)
            nv = sum(x["missed_by_n0_drift"][i]["n_true_viol"] for x in r)
            nr = sum(x["missed_by_n0_drift"][i]["n_rows"] for x in r)
            bins[name] = dict(n_rows_pooled=nr, n_true_viol_pooled=nv, missed_pooled=(mv / nv) if nv else None)
        summary[fam] = dict(
            missed_as_evaluated=ms2([x["as_evaluated"]["missed"] for x in r]),
            missed_without_9=ms2([x["without_9_bases"]["missed"] for x in r]),
            any_miss_as_evaluated=ms2([x["as_evaluated"]["any_miss_share"] for x in r]),
            any_miss_without_9=ms2([x["without_9_bases"]["any_miss_share"] for x in r]),
            splits_missed_le_1pct_as_evaluated=int(sum(x["as_evaluated"]["missed"] <= 0.01 for x in r)),
            splits_missed_le_1pct_without_9=int(sum(x["without_9_bases"]["missed"] <= 0.01 for x in r)),
            max_repro_diff_vs_n5=float(max(x["repro_missed_vs_n5"] for x in r)),
            missed_by_n0_drift_pooled=bins)
    other = {k: drift_counts(n0_table(p)) for k, p in OTHER.items()}
    other["case118"] = drift_counts(n0)
    out = dict(question="does the pinned-vs-corrected N-0 mismatch change case118 held-out safety? (no retraining)",
               nine_bases=sorted(int(s) for s in bad), summary=summary, per_split=rows, n0_drift_counts=other,
               std="population ddof=0 over 5 splits", wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    inputs = [N2, N5, "data/dataset.parquet"] + list(OTHER.values())
    man = dict(artifacts=[OUT], generating_script="scratch/n0drift_check.py",
               regeneration_argv=[".venv/bin/python", "scratch/n0drift_check.py"],
               script_sha256=sha256_of("scratch/n0drift_check.py"), inputs={p: sha256_of(p) for p in inputs},
               model_hyperparameters="N5 M2 per-seed configs from data/sts_n5_gate_094.json (fits[].config), refit on train; held-out targets = selections[].m2_inner_cov_at",
               drift_bins=BINS, limit=LIMIT, seeds=SEEDS,
               packages={p: mf.pkg_version(p) for p in mf.PACKAGES}, python=platform.python_version(),
               output_sha256=sha256_of(OUT), generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(OUT.replace(".json", ".manifest.json"), "w") as f:
        json.dump(man, f, indent=2)
    print(json.dumps(dict(summary=summary, n0_drift_counts=other), indent=1, default=str))


if __name__ == "__main__":
    main()
