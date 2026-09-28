import os
import sys
import json
import time
import hashlib
import subprocess
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import manifest as mf
import tune_surrogates as T

# N4: paired 5-seed F1 shuffle control. Extends check_4_permutation of scripts/f1_leakage_audit.py
# (one seed, histgb only) to 5 seeds and both families. Per seed: the committed M2 config is fit
# with the real F1 block and with F1 permuted across scenarios WITHIN each outaged element (the
# check_4 scheme), and the paired difference real - shuffled is reported for MAE and gate metrics.
# The no-F1 baseline arm is read from the N1 refit (same model, same split).

DATASET = "data/dataset.parquet"
TUNED = "data/tuned_metrics.json"
F1_PATH = "data/physics/base_flows.parquet"
N1_PRED = "data/sts_n1_predictions_long.parquet"
OUT_JSON = "data/sts_n4_f1_shuffle.json"
F1COLS = ["pre_p_mw", "pre_q_mvar", "pre_loading_percent", "pre_i_ka"]
SEEDS = 5
LIMIT = 0.94
FAMILIES = ["ridge", "histgb"]
COVERAGES = [0.90, 0.94, 0.97]
PERM_SEED_OFFSET = 12345


def m2_records():
    tm = json.load(open(TUNED))
    out = {}
    for r in tm["records"]:
        if r["metric"] == "m2":
            out[(r["family"], r["seed"])] = r
    return out


def shuffled_f1(fl, perm_seed):
    # same scheme as f1_leakage_audit.check_4: permute the F1 rows across scenarios within each element
    rng = np.random.default_rng(perm_seed)
    sh = fl.copy()
    for _k, idx in sh.groupby(["outaged_type", "outaged_idx"]).groups.items():
        idx = np.array(list(idx))
        perm = rng.permutation(len(idx))
        sh.loc[idx, F1COLS] = sh.loc[idx[perm], F1COLS].to_numpy()
    return sh


def arm_metrics(pred_cal, y_cal, pred_test, y_test, ms_solver):
    out = dict(mae=float(np.mean(np.abs(pred_test - y_test))))
    for cov in COVERAGES:
        q = ge.calibrate_qhat(pred_cal, y_cal, cov)
        g = ge.run_gate(pred_test, q, LIMIT)
        s = ge.score(g, y_test, 1e-6, ms_solver, LIMIT)
        out[f"escalation_{cov}"] = s["escalation"]
        out[f"missed_{cov}"] = s["missed_viol"]
    return out


def fit_arm(fam, cfg, Xc, y, sp, seed, ms_solver):
    kept = ms.select_features(Xc, sp["train"])
    Xk = Xc[kept]
    fitted = T.fit_one(fam, cfg, Xk.iloc[sp["train"]].to_numpy(np.float32), y[sp["train"]], seed)
    pc = T.predict(fitted, Xk.iloc[sp["cal"]].to_numpy(np.float32))
    pt = T.predict(fitted, Xk.iloc[sp["test"]].to_numpy(np.float32))
    m = arm_metrics(pc, y[sp["cal"]], pt, y[sp["test"]], ms_solver)
    m["n_features"] = int(len(kept))
    return m


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
    ms_solver = mf.load_solve_time()["ms_solver"]
    recs = m2_records()
    df, feature_cols = ms.load_dataset(DATASET)
    X, y, groups, _b = ms.build_design_matrix(df, feature_cols)
    key = df[["scenario_id", "outaged_type", "outaged_idx"]].reset_index(drop=True)
    fl = pd.read_parquet(F1_PATH)
    real = key.merge(fl, on=["scenario_id", "outaged_type", "outaged_idx"], how="left")[F1COLS]
    if int(real.isna().sum().sum()) != 0:
        raise RuntimeError("F1 merge left missing values")
    Xreal = pd.concat([X, real.astype(np.float32).add_prefix("f1_")], axis=1)
    pl = pd.read_parquet(N1_PRED)

    per_seed = []
    for seed in range(SEEDS):
        sp = ms.make_splits(groups, seed)
        perm_seed = PERM_SEED_OFFSET + seed
        sh = shuffled_f1(fl, perm_seed)
        shuf = key.merge(sh, on=["scenario_id", "outaged_type", "outaged_idx"], how="left")[F1COLS]
        Xshuf = pd.concat([X, shuf.astype(np.float32).add_prefix("f1_")], axis=1)
        for fam in FAMILIES:
            rec = recs[(fam, seed)]
            t1 = time.time()
            m_real = fit_arm(fam, rec["config"], Xreal, y, sp, seed, ms_solver)
            m_shuf = fit_arm(fam, rec["config"], Xshuf, y, sp, seed, ms_solver)
            sub = pl[(pl["seed"] == seed) & (pl["family"] == fam)]
            ca = sub[sub["split"] == "cal"]
            te = sub[sub["split"] == "test"]
            m_base = arm_metrics(ca["pred"].to_numpy(), ca["y"].to_numpy(),
                                 te["pred"].to_numpy(), te["y"].to_numpy(), ms_solver)
            per_seed.append(dict(seed=seed, family=fam, tag=rec["tag"], config=rec["config"],
                                 perm_seed=perm_seed, baseline=m_base, f1_real=m_real, f1_shuffled=m_shuf,
                                 fit_s=round(time.time() - t1, 1)))
            print(f"  seed {seed} {fam:6s} MAE base={m_base['mae']:.7f} real={m_real['mae']:.7f} "
                  f"shuf={m_shuf['mae']:.7f} [{time.time() - t1:.0f}s]", flush=True)
        del Xshuf

    keys = ["mae"]
    for cov in COVERAGES:
        keys.append(f"escalation_{cov}")
        keys.append(f"missed_{cov}")
    summary = {}
    for fam in FAMILIES:
        rs = [r for r in per_seed if r["family"] == fam]
        block = {}
        for k in keys:
            real_v = np.array([r["f1_real"][k] for r in rs])
            shuf_v = np.array([r["f1_shuffled"][k] for r in rs])
            base_v = np.array([r["baseline"][k] for r in rs])
            d_rs = real_v - shuf_v
            d_rb = real_v - base_v
            block[k] = dict(
                baseline_mean=float(base_v.mean()), baseline_std=float(base_v.std()),
                real_mean=float(real_v.mean()), real_std=float(real_v.std()),
                shuffled_mean=float(shuf_v.mean()), shuffled_std=float(shuf_v.std()),
                paired_real_minus_shuffled_mean=float(d_rs.mean()),
                paired_real_minus_shuffled_std=float(d_rs.std()),
                paired_real_minus_shuffled_per_seed=[float(v) for v in d_rs],
                n_seeds_real_lower=int((d_rs < 0).sum()),
                paired_real_minus_baseline_mean=float(d_rb.mean()),
                paired_real_minus_baseline_std=float(d_rb.std()))
        summary[fam] = block

    c4 = json.load(open("data/f1_leakage_audit.json"))["check_4_permutation"]
    s0 = [r for r in per_seed if r["seed"] == 0 and r["family"] == "histgb"][0]
    check4 = dict(committed_baseline_mae=c4["baseline"]["mae"], refit_baseline_mae=s0["baseline"]["mae"],
                  committed_real_mae=c4["F1_real"]["mae"], refit_real_mae=s0["f1_real"]["mae"],
                  committed_shuffled_mae=c4["F1_shuffled"]["mae"], refit_shuffled_mae=s0["f1_shuffled"]["mae"])
    print(f"check_4 comparison (seed 0 histgb): {check4}", flush=True)

    wall = time.time() - t0
    out = dict(
        reproduction_vs_check_4=check4,
        question="does the pre-outage flow block F1 carry scenario-specific information beyond the element identity?",
        design=("paired per seed: committed M2 config (data/tuned_metrics.json) fit on the train split with "
                "(a) no F1 [baseline, read from the N1 refit], (b) real F1, (c) F1 permuted across scenarios "
                "within each outaged element (f1_leakage_audit.check_4 scheme), permutation seed 12345+split seed; "
                "q_hat calibrated on the cal split, metrics on the test split."),
        note_vs_single_seed=("data/f1_leakage_audit.json check_4 used permutation seed 12345 on split seed 0 "
                             "for histgb; this run uses the same permutation seed on split seed 0, so its "
                             "seed-0 histgb arms should match check_4 up to column naming."),
        coverages=COVERAGES, seeds=SEEDS, families=FAMILIES,
        per_seed=per_seed, summary=summary,
        std_convention="population std (ddof=0) over the five held-out splits; paired differences are per split",
        wall_time_s=wall)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    hyper = {}
    for r in per_seed:
        hyper[f"{r['family']}_seed{r['seed']}"] = dict(tag=r["tag"], config=r["config"])
    man = dict(
        schema="sts-new-analysis",
        artifacts=[OUT_JSON],
        generating_script="scripts/sts_n4_f1_shuffle.py",
        regeneration_argv=[".venv/bin/python", "scripts/sts_n4_f1_shuffle.py"],
        script_sha256=sha256_of("scripts/sts_n4_f1_shuffle.py"),
        repo_head_commit=git_head(),
        inputs=[dict(path=p, sha256=sha256_of(p)) for p in (DATASET, TUNED, F1_PATH, N1_PRED, "data/solve_time.json",
                                                             "data/f1_leakage_audit.json")],
        output_sha256=sha256_of(OUT_JSON),
        model_hyperparameters=hyper,
        seeds=list(range(SEEDS)), permutation_seeds=[PERM_SEED_OFFSET + s for s in range(SEEDS)],
        split_protocol="make_splits(groups, seed): GroupShuffleSplit 60/20/20 on scenario_id",
        solver=dict(note="no AC solves in this script", pinned=mf.SOLVER),
        environment=mf.build_manifest(),
        wall_time_s=wall,
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(mf.manifest_path(OUT_JSON), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {OUT_JSON} + manifest; wall {wall:.0f}s", flush=True)
    for fam in FAMILIES:
        b = summary[fam]["mae"]
        print(f"  {fam}: MAE real-shuffled {b['paired_real_minus_shuffled_mean']:.3e} +/- "
              f"{b['paired_real_minus_shuffled_std']:.3e}", flush=True)


if __name__ == "__main__":
    main()
