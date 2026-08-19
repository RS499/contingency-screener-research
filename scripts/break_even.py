import os
import sys
import json
import time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import manifest as mf
import classical_manifest as cm
import tune_surrogates as T

DATASET = "data/dataset.parquet"
TUNED = "data/tuned_metrics.json"
SEARCH = "data/tuning_search.json"
CURVE_V2 = "data/tradeoff_curve_v2.json"
SOLVE = "data/solve_time.json"
OUT = "data/break_even.json"
OPS = {"ridge": 0.94, "histgb": 0.97}

GEN_ACCEPTED = 1500          # feasibility/freeze_poster_numbers.py:10
GEN_REJECTED = 1287          # feasibility/freeze_poster_numbers.py:11
BRANCHES = 186


def m2_config(tuned, fam, seed):
    for r in tuned["records"]:
        if r["family"] == fam and r["metric"] == "m2" and r["seed"] == seed:
            return r["config"]
    raise ValueError("missing")


def ms_surr(tuned, fam, seed):
    for r in tuned["records"]:
        if r["family"] == fam and r["metric"] == "m2" and r["seed"] == seed:
            return float(r["ms_surrogate"])
    raise ValueError("missing")


def main():
    t0 = time.time()
    tuned = json.load(open(TUNED))
    search = json.load(open(SEARCH))
    curve = json.load(open(CURVE_V2))
    solve = json.load(open(SOLVE))
    n_seeds = int(tuned["seeds"])
    ms_solver = float(solve["ms_solver"])
    targets = list(curve["coverage_levels"])

    # ---- 1. dataset generation solve accounting (counted, not assumed)
    raw = pd.read_parquet(DATASET)
    n_rows = int(len(raw))
    n_base_rows = int((raw.outaged_type == "none").sum())
    n_n1_rows = n_rows - n_base_rows
    gen = dict(
        rows_in_dataset=n_rows,
        base_solves_accepted=n_base_rows,
        n1_solves=n_n1_rows,
        solves_recorded_in_dataset=n_rows,
        rejected_scenarios=GEN_REJECTED,
        rejected_base_solves=GEN_REJECTED,
        total_solves_including_rejected=n_rows + GEN_REJECTED,
        rejected_provenance=("GEN_REJECTED is a hardcoded constant in "
                             "feasibility/freeze_poster_numbers.py whose stated source is a "
                             "generate_dataset.py run log that is NOT a committed file. The "
                             "rejected-scenario count is therefore unverifiable from the repo."),
        branches=BRANCHES,
        per_scenario_solves=1 + BRANCHES,
    )
    gen["t_generation_s_recorded"] = gen["solves_recorded_in_dataset"] * ms_solver / 1000.0
    gen["t_generation_s_including_rejected"] = gen["total_solves_including_rejected"] * ms_solver / 1000.0

    # ---- 1. training / calibration wall time, measured now
    df_c, fc_c = ms.load_dataset(DATASET)
    X, y, groups, _b = ms.build_design_matrix(df_c, fc_c)
    fit_times = {"ridge": [], "histgb": []}
    cal_times = {"ridge": [], "histgb": []}
    infer_measured = {"ridge": [], "histgb": []}
    for seed in range(n_seeds):
        splits = ms.make_splits(groups, seed)
        kept = ms.select_features(X, splits["train"])
        Xk = X[kept]
        Xtr = Xk.iloc[splits["train"]].to_numpy(np.float32)
        Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
        Xte = Xk.iloc[splits["test"]].to_numpy(np.float32)
        ytr, yca = y[splits["train"]], y[splits["cal"]]
        for fam in ("ridge", "histgb"):
            cfg = m2_config(tuned, fam, seed)
            t1 = time.perf_counter()
            fitted = T.fit_one(fam, cfg, Xtr, ytr, seed)
            fit_times[fam].append(time.perf_counter() - t1)
            p_ca = T.predict(fitted, Xca)
            t2 = time.perf_counter()
            ge.calibrate_qhat(p_ca, yca, 0.90)
            cal_times[fam].append(time.perf_counter() - t2)
            t3 = time.perf_counter()
            T.predict(fitted, Xte)
            infer_measured[fam].append((time.perf_counter() - t3) * 1000.0 / len(Xte))
        print(f"  seed {seed} timed {time.time()-t0:.0f}s", flush=True)

    tune_fit_s = float(np.sum([r["fit_s"] for r in search["records"]]))
    timing = dict(
        ms_solver=ms_solver, ms_solver_basis=solve["basis"],
        fit_s_mean={f: float(np.mean(v)) for f, v in fit_times.items()},
        fit_s_by_seed={f: [float(x) for x in v] for f, v in fit_times.items()},
        cal_s_mean={f: float(np.mean(v)) for f, v in cal_times.items()},
        ms_infer_measured_now={f: float(np.mean(v)) for f, v in infer_measured.items()},
        ms_infer_committed={f: float(np.mean([ms_surr(tuned, f, s) for s in range(n_seeds)]))
                            for f in ("ridge", "histgb")},
        m2_search_total_fit_s=tune_fit_s,
        m2_search_n_configs=len(search["records"]),
    )

    # ---- 2/3. break-even
    esc = {}
    for r in curve["records"]:
        esc[(r["model"], round(float(r["coverage_target"]), 4))] = float(r["escalation"])

    rows = []
    for fam in ("ridge", "histgb"):
        t_fit = timing["fit_s_mean"][fam]
        t_cal = timing["cal_s_mean"][fam]
        ms_inf = timing["ms_infer_committed"][fam]
        for tgt in targets:
            e = esc[(fam, round(float(tgt), 4))]
            save_ms = ms_solver * (1.0 - e) - ms_inf
            for label, once_s in (
                    ("gen_only", gen["t_generation_s_recorded"]),
                    ("gen_plus_training", gen["t_generation_s_recorded"] + t_fit + t_cal),
                    ("gen_plus_training_plus_search",
                     gen["t_generation_s_recorded"] + t_fit + t_cal + tune_fit_s),
                    ("gen_incl_rejected_plus_training_plus_search",
                     gen["t_generation_s_including_rejected"] + t_fit + t_cal + tune_fit_s)):
                be = (once_s * 1000.0 / save_ms) if save_ms > 0 else float("inf")
                rows.append(dict(model=fam, target=float(tgt), accounting=label,
                                 escalation=e, saving_ms_per_case=save_ms,
                                 one_time_cost_s=once_s, break_even_cases=be,
                                 break_even_full_sweeps=be / BRANCHES))
    out_df = pd.DataFrame(rows)

    comparator = dict(
        source="notes/lit/notes/Graph Neural Networks for Fast Contingency Analysis of Power Systems.md",
        quote=("Break-even point (total-time accounting, Fig. 10, p.9): \"approximately 500k "
               "scenarios\" where NN total cost crosses ACPF total cost; annotated as 503k "
               "scenarios for 57-bus and 498k for the 118-bus (p.9)"),
        value_118bus_scenarios=498000, value_57bus_scenarios=503000,
        value_headline_scenarios=500000,
        read_from_notes=True,
        unit_caveat=("the GNN figure is in SCENARIOS; this project's break-even is computed in "
                     "screened CONTINGENCIES. One scenario = 186 contingencies on case118, so the "
                     "two are not directly comparable without converting."),
    )

    summary = {}
    for fam, tgt in OPS.items():
        summary[fam] = {}
        for label in ("gen_only", "gen_plus_training", "gen_plus_training_plus_search",
                      "gen_incl_rejected_plus_training_plus_search"):
            r = out_df[(out_df.model == fam) & (np.isclose(out_df.target, tgt)) &
                       (out_df.accounting == label)].iloc[0]
            summary[fam][label] = dict(target=tgt, escalation=float(r.escalation),
                                       saving_ms_per_case=float(r.saving_ms_per_case),
                                       one_time_cost_s=float(r.one_time_cost_s),
                                       break_even_cases=float(r.break_even_cases),
                                       break_even_scenarios=float(r.break_even_full_sweeps))
    out = dict(generation=gen, timing=timing, comparator=comparator,
               break_even_at_operating_points=summary,
               break_even_table=rows, operating_points=OPS)
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"wrote {OUT}")
    meta = dict(artifact="break-even accounting including dataset generation and training",
                one_time_components=["dataset generation solves", "M2 refit", "calibration",
                                     "M2 hyperparameter search"],
                ms_solver=ms_solver, branches=BRANCHES,
                model_hyperparameters={f: {str(s): m2_config(tuned, f, s) for s in range(n_seeds)}
                                       for f in ("ridge", "histgb")})
    man = cm.build_manifest(OUT, meta, dict(task="break-even accounting", source=DATASET))
    json.dump(man, open(mf.manifest_path(OUT), "w"), indent=2)
    print(f"wrote {mf.manifest_path(OUT)}")


if __name__ == "__main__":
    main()
