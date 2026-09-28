import os
import sys
import json
import time
import hashlib
import subprocess
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
import gate_eval as ge
import manifest as mf

# N2 summary: counts and shares from data/sts_n2_label_audit.parquet, plus the mapping of the
# currently-missed cases (M2 refit predictions from scripts/sts_n1_class_conditional.py) onto the
# audited labels. No solves, no fits, no retraining on corrected labels.

AUDIT = "data/sts_n2_label_audit.parquet"
AUDIT_RUN = "data/sts_n2_label_audit.parquet.run.json"
N1_PRED = "data/sts_n1_predictions_long.parquet"
OUT_JSON = "data/sts_n2_label_audit.json"
LIMIT = 0.94
SEEDS = 5
WORST = dict(scenario_id=101000025, outaged_type="line", outaged_idx=78)
OPERATING = [("histgb", 0.97), ("ridge", 0.94), ("histgb", 0.90), ("ridge", 0.90)]
KEY = ["scenario_id", "outaged_type", "outaged_idx"]


def share(a, b):
    return float(a / b) if b else None


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def git_head():
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip()


def gen_counts(col):
    counts = {}
    for s in col:
        if not s:
            continue
        for g in s.split(","):
            counts[g] = counts.get(g, 0) + 1
    pairs = sorted([(n, int(g)) for g, n in counts.items()], reverse=True)[:10]
    return [dict(gen=g, n_rows=int(n)) for n, g in pairs]


def block_counts(a):
    n = len(a)
    inc = (a["n_inconsistent_absorbing"] + a["n_inconsistent_injecting"]) > 0
    inc_abs = a["n_inconsistent_absorbing"] > 0
    inc_inj = a["n_inconsistent_injecting"] > 0
    ok = a["corrected_status"].isin(["converged", "not_needed"])
    delta = (a["corrected_min_vm"] - a["resolved_min_vm"])[inc & ok]
    return dict(
        n_rows=int(n),
        n_any_inconsistent=int(inc.sum()), share_any_inconsistent=share(int(inc.sum()), n),
        n_inconsistent_absorbing=int(inc_abs.sum()), share_inconsistent_absorbing=share(int(inc_abs.sum()), n),
        n_inconsistent_injecting=int(inc_inj.sum()), share_inconsistent_injecting=share(int(inc_inj.sum()), n),
        corrected_status_counts={k: int(v) for k, v in a["corrected_status"].value_counts().items()},
        corrected_minus_pinned_min_vm_among_inconsistent=dict(
            n=int(len(delta)), mean=float(delta.mean()), median=float(delta.median()),
            min=float(delta.min()), max=float(delta.max()),
            n_abs_gt_1e3=int((delta.abs() > 1e-3).sum()), n_abs_gt_1e2=int((delta.abs() > 1e-2).sum())),
        n_flip_violation_to_safe=int(a["flip_viol_to_safe"].sum()),
        n_flip_safe_to_violation=int(a["flip_safe_to_viol"].sum()),
        top_gens_inconsistent_absorbing=gen_counts(a["inconsistent_absorbing_gens"]),
        top_gens_inconsistent_injecting=gen_counts(a["inconsistent_injecting_gens"]))


def main():
    t0 = time.time()
    a = pd.read_parquet(AUDIT)
    run = json.load(open(AUDIT_RUN))
    n1 = a[a["outaged_type"] != "none"].copy()
    n0 = a[a["outaged_type"] == "none"].copy()

    repro = dict(
        n_rows_resolved=int(len(a)),
        n_pinned_converged=int(a["resolved_converged"].sum()),
        n_reproduced_within_1e6=int((a["repro_abs_diff"] <= 1e-6).sum()),
        n_reproduced_exact=int((a["repro_abs_diff"] == 0).sum()),
        max_abs_diff=float(a["repro_abs_diff"].max()),
        replay_n0_max_abs_diff=run["replay_n0_max_abs_diff"],
        replay_n_scenarios=run["replay_n_scenarios"],
        rejects_per_shard=run["rejects_per_shard"])

    ok = n1["corrected_status"].isin(["converged", "not_needed"])
    viol_rows = n1[n1["stored_violation"]]
    stored_rate = float(n1["stored_violation"].mean())
    corr_label = np.where(ok, n1["corrected_violation"], n1["stored_violation"])
    corrected_rate = float(np.mean(corr_label))
    rate = dict(
        n_converged_n1_rows=int(len(n1)),
        stored_violations=int(n1["stored_violation"].sum()), stored_rate=stored_rate,
        corrected_violations=int(np.sum(corr_label)), corrected_rate=corrected_rate,
        corrected_rate_note=("rows whose switch-back loop did not converge keep their stored label; count in "
                             "all_n1_rows.corrected_status_counts"),
        n_flip_violation_to_safe=int(n1["flip_viol_to_safe"].sum()),
        n_flip_safe_to_violation=int(n1["flip_safe_to_viol"].sum()),
        share_of_stored_violations_flipping_to_safe=share(int(n1["flip_viol_to_safe"].sum()),
                                                          int(n1["stored_violation"].sum())),
        stored_boundary_mass_0p94_0p945=float(((n1["stored_min_vm"] >= 0.94) & (n1["stored_min_vm"] < 0.945)).mean()),
        corrected_boundary_mass_0p94_0p945=float(((n1["corrected_min_vm"] >= 0.94) & (n1["corrected_min_vm"] < 0.945))[ok].mean()),
        stored_min=float(n1["stored_min_vm"].min()),
        corrected_min=float(n1.loc[ok, "corrected_min_vm"].min()))
    flips = n1[n1["flip_viol_to_safe"]]
    rate["flip_violation_to_safe_stored_min_vm"] = dict(
        min=float(flips["stored_min_vm"].min()), median=float(flips["stored_min_vm"].median()),
        share_stored_below_0p93=float((flips["stored_min_vm"] < 0.93).mean()))
    deep = n1[n1["stored_min_vm"] < 0.90]
    rate["stored_violations_below_0p90"] = dict(
        n=int(len(deep)), n_flip_to_safe=int(deep["flip_viol_to_safe"].sum()),
        n_with_inconsistent_gen=int(((deep["n_inconsistent_absorbing"] + deep["n_inconsistent_injecting"]) > 0).sum()))

    w = n1[(n1["scenario_id"] == WORST["scenario_id"]) & (n1["outaged_type"] == WORST["outaged_type"])
           & (n1["outaged_idx"] == WORST["outaged_idx"])].iloc[0]
    worst = dict(WORST, stored_min_vm=float(w["stored_min_vm"]), resolved_min_vm=float(w["resolved_min_vm"]),
                 inconsistent_absorbing_gens=w["inconsistent_absorbing_gens"],
                 inconsistent_injecting_gens=w["inconsistent_injecting_gens"],
                 corrected_status=w["corrected_status"], corrected_min_vm=float(w["corrected_min_vm"]),
                 corrected_argmin_bus_index=int(w["corrected_argmin"]),
                 corrected_argmin_bus_ieee=int(w["corrected_argmin"]) + 1,
                 n_outer_iter=int(w["n_outer_iter"]), flips_to_safe=bool(w["flip_viol_to_safe"]))

    # missed cases at the operating points, mapped onto the audit
    pl = pd.read_parquet(N1_PRED)
    lab = n1[KEY + ["corrected_min_vm", "corrected_status", "flip_viol_to_safe",
                    "n_inconsistent_absorbing", "n_inconsistent_injecting"]]
    missed_map = {}
    for fam, cov in OPERATING:
        per_seed = []
        union = set()
        union_flip = set()
        for seed in range(SEEDS):
            sub = pl[(pl["seed"] == seed) & (pl["family"] == fam)]
            ca = sub[sub["split"] == "cal"]
            te = sub[sub["split"] == "test"].copy()
            q = ge.calibrate_qhat(ca["pred"].to_numpy(), ca["y"].to_numpy(), cov)
            te["certify"] = (te["pred"] - q) >= LIMIT
            te = te.merge(lab, on=KEY, how="left")
            n_unmatched = int(te["corrected_status"].isna().sum())
            viol = te["y"] < LIMIT
            missed = te[te["certify"] & viol]
            tok = te["corrected_status"].isin(["converged", "not_needed"])
            y_corr = np.where(tok, te["corrected_min_vm"], te["y"])
            viol_c = y_corr < LIMIT
            missed_c = te["certify"].to_numpy() & viol_c
            for r in missed.itertuples():
                union.add((r.scenario_id, r.outaged_type, r.outaged_idx))
                if r.flip_viol_to_safe:
                    union_flip.add((r.scenario_id, r.outaged_type, r.outaged_idx))
            deepest = missed.sort_values("y").head(1)
            per_seed.append(dict(
                seed=seed, q_hat=q, n_missed=int(len(missed)),
                n_missed_flip_to_safe=int(missed["flip_viol_to_safe"].sum()),
                n_missed_with_inconsistent_gen=int(((missed["n_inconsistent_absorbing"] +
                                                     missed["n_inconsistent_injecting"]) > 0).sum()),
                missed_rate_stored_labels=float(len(missed) / max(int(viol.sum()), 1)),
                missed_rate_corrected_labels_no_retrain=float(missed_c.sum() / max(int(viol_c.sum()), 1)),
                deepest_missed_stored=(float(deepest["y"].iloc[0]) if len(deepest) else None),
                deepest_missed_corrected_min_vm=(float(deepest["corrected_min_vm"].iloc[0]) if len(deepest) else None),
                deepest_missed_under_corrected_labels=(float(y_corr[missed_c].min()) if missed_c.sum() else None),
                n_test_rows_unmatched=n_unmatched))
        m_st = np.array([p["missed_rate_stored_labels"] for p in per_seed])
        m_co = np.array([p["missed_rate_corrected_labels_no_retrain"] for p in per_seed])
        missed_map[f"{fam}@{cov}"] = dict(
            per_seed=per_seed,
            total_missed_over_seeds=int(sum(p["n_missed"] for p in per_seed)),
            total_missed_flip_to_safe=int(sum(p["n_missed_flip_to_safe"] for p in per_seed)),
            share_missed_flip_to_safe=share(int(sum(p["n_missed_flip_to_safe"] for p in per_seed)),
                                            int(sum(p["n_missed"] for p in per_seed))),
            unique_missed_rows=len(union), unique_missed_rows_flip_to_safe=len(union_flip),
            missed_rate_stored_mean=float(m_st.mean()), missed_rate_stored_std=float(m_st.std()),
            missed_rate_corrected_no_retrain_mean=float(m_co.mean()),
            missed_rate_corrected_no_retrain_std=float(m_co.std()))

    n0_ok = n0["corrected_status"].isin(["converged", "not_needed"])
    n0_block = block_counts(n0)
    n0_block["n_corrected_n0_min_below_0p94"] = int(((n0["corrected_min_vm"] < LIMIT) & n0_ok).sum())
    n0_block["note"] = ("N-0 rows passed the N-0 gate under the pinned solver. Rejected draws were not re-solved, "
                        "so draws that the corrected solver would have accepted are not counted.")

    out = dict(
        question=("do the stored labels depend on generators left at a Q limit that contradicts their voltage "
                  "(pandapower enforce_q_lims switches PV->PQ and never back)?"),
        method=dict(
            reconstruction=("exact replay of the committed generator RNG (feasibility/generate_dataset.py functions, "
                            "seeds 100-103, 375 accepted scenarios each, committed flags, stress fixed, mixed modes) "
                            "including rejected draws; each converged row re-solved with the pinned solver"),
            inconsistent=("in-service gen with Q <= Qmin + 1e-3 Mvar and V < Vset - 1e-3 pu (absorbing), or "
                          "Q >= Qmax - 1e-3 Mvar and V > Vset + 1e-3 pu (injecting)"),
            correction=("outer loop: consistent limited gens held as PQ at their limit (modelled as a fixed-Q sgen), "
                        "inconsistent gens returned to PV; each pass solved with the pinned runpp "
                        "(enforce_q_lims=True, init=dc, numba) so free gens still switch PV->PQ; stop when no gen "
                        "is inconsistent; cap 30 passes; non-convergence recorded"),
            tolerances=dict(q_mvar=1e-3, v_pu=1e-3)),
        reproduction=repro,
        all_n1_rows=block_counts(n1),
        stored_violation_rows=block_counts(viol_rows),
        violation_rate=rate,
        worst_case_0p8485=worst,
        missed_cases=missed_map,
        n0_rows=n0_block,
        caveats=[
            "audit only: dataset not rebuilt and models not retrained on corrected labels",
            "missed_rate_corrected_labels_no_retrain applies the refit models (trained on stored labels) to corrected labels; it is not the result of a corrected pipeline",
            "the switch-back loop is one standard PV/PQ logic; a different switching order could reach a different consistent solution where several exist",
            "N-0 gate decisions and N-0 features (vm0_*) come from the same pinned solver and were not corrected"],
        wall_time_s_summary=time.time() - t0,
        audit_wall_time_s=run["wall_time_s"])
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    man = dict(
        schema="sts-new-analysis",
        artifacts=[OUT_JSON, AUDIT],
        generating_scripts=["scripts/sts_n2_label_audit.py", "scripts/sts_n2_summary.py"],
        regeneration_argv=[[".venv/bin/python", "scripts/sts_n2_label_audit.py"],
                           [".venv/bin/python", "scripts/sts_n1_class_conditional.py"],
                           [".venv/bin/python", "scripts/sts_n2_summary.py"]],
        script_sha256={p: sha256_of(p) for p in ("scripts/sts_n2_label_audit.py", "scripts/sts_n2_summary.py")},
        repo_head_commit=git_head(),
        inputs=[dict(path=p, sha256=sha256_of(p)) for p in
                ("data/dataset.parquet", "feasibility/generate_dataset.py", N1_PRED)],
        output_sha256={OUT_JSON: sha256_of(OUT_JSON), AUDIT: sha256_of(AUDIT)},
        model_hyperparameters=("missed-case mapping uses the M2 refit predictions; configs in "
                               "data/sts_n1_class_conditional.manifest.json"),
        generator_replay=dict(flags=dict(mult_lo=1.0, mult_hi=1.12, reg_lo=1.0, reg_hi=1.12, pf_lo=0.9,
                                         pf_hi=1.15, dvm=0.025), stress="fixed", mode="mixed",
                              shard_seeds=[100, 101, 102, 103], per_shard=375),
        solver=dict(pinned=mf.SOLVER, correction="pinned runpp inside a PV/PQ switch-back outer loop, cap 30",
                    tolerances=dict(q_mvar=1e-3, v_pu=1e-3)),
        audit_run=run,
        environment=mf.build_manifest(),
        wall_time_s=dict(audit=run["wall_time_s"], summary=time.time() - t0),
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(mf.manifest_path(OUT_JSON), "w") as f:
        json.dump(man, f, indent=2)
    print(json.dumps(dict(reproduction=repro, rate=rate, worst=worst), indent=1))
    for k, v in missed_map.items():
        print(k, v["total_missed_over_seeds"], v["total_missed_flip_to_safe"], v["share_missed_flip_to_safe"],
              v["missed_rate_stored_mean"], v["missed_rate_corrected_no_retrain_mean"])
    print(f"wrote {OUT_JSON} + manifest")


if __name__ == "__main__":
    main()
