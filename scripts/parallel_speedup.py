import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manifest as mf
import classical_manifest as cm

RAW = sys.argv[1]
OUT = "data/parallel_speedup.json"
CURVE_V2 = "data/tradeoff_curve_v2.json"
TUNED = "data/tuned_metrics.json"
BE = "data/break_even.json"
SOLVE = "data/solve_time.json"
OPS = {"ridge": 0.94, "histgb": 0.97}
BRANCHES = 186


def main():
    raw = json.load(open(RAW))
    curve = json.load(open(CURVE_V2))
    tuned = json.load(open(TUNED))
    be = json.load(open(BE))
    solve = json.load(open(SOLVE))
    cores = int(raw["cores"])

    runs = {r["n_workers"]: r for r in raw["runs"]}
    def eff_ms(P):
        r = runs[P]
        return 1000.0 * r["worker_busy_s"] / (P * r["total_solves"])
    base_ms = eff_ms(1)
    scaling = {str(P): dict(n_workers=P,
                            per_core_ms=1000.0 * runs[P]["worker_busy_s"] / runs[P]["total_solves"],
                            effective_ms_per_case=eff_ms(P),
                            speedup_vs_serial=base_ms / eff_ms(P),
                            parallel_efficiency=(base_ms / eff_ms(P)) / P)
               for P in sorted(runs)}
    Pmax = max(runs)
    ms_par = eff_ms(Pmax)
    par_speedup = base_ms / ms_par
    par_eff = par_speedup / Pmax

    ms_solver_committed = float(solve["ms_solver"])
    ms_inf = {f: float(np.mean([r["ms_surrogate"] for r in tuned["records"]
                                if r["family"] == f and r["metric"] == "m2"]))
              for f in ("ridge", "histgb")}

    rows = []
    for r in curve["records"]:
        fam, tgt, esc = r["model"], float(r["coverage_target"]), float(r["escalation"])
        pub = float(r["net_speedup"])
        ti = ms_inf[fam]
        # serial recomputation on the committed t_solve (sanity)
        s_serial = ms_solver_committed / (ti + esc * ms_solver_committed)
        # A: baseline parallel, GATE ALSO PARALLEL (escalated solves + inference both scale)
        s_both = ms_par / (ti / Pmax + esc * ms_par)
        # B: baseline parallel, gate serial (the unfair comparison a reviewer might make)
        s_baseline_par_gate_serial = ms_par / (ti + esc * ms_solver_committed)
        # C: both parallel but escalated batch too small to saturate cores
        n_esc_per_sweep = esc * BRANCHES
        P_eff_esc = min(Pmax, max(1.0, n_esc_per_sweep))
        ms_esc_eff = base_ms / (P_eff_esc * par_eff) if P_eff_esc > 1 else base_ms
        s_saturation = ms_par / (ti / Pmax + esc * ms_esc_eff)
        rows.append(dict(model=fam, target=tgt, escalation=esc,
                         published_net_speedup=pub,
                         serial_recomputed=s_serial,
                         parallel_both_sides=s_both,
                         parallel_baseline_serial_gate=s_baseline_par_gate_serial,
                         parallel_with_escalation_saturation=s_saturation,
                         delta_both_vs_published=s_both - pub,
                         escalated_solves_per_sweep=n_esc_per_sweep,
                         effective_cores_for_escalated=P_eff_esc))

    # ---- item 5: break-even under the parallel baseline
    gen = be["generation"]
    tim = be["timing"]
    search_s = float(tim["m2_search_total_fit_s"])
    n_gen = int(gen["solves_recorded_in_dataset"])
    be_rows = []
    for r in rows:
        fam, tgt, esc = r["model"], r["target"], r["escalation"]
        ti = ms_inf[fam]
        fit = float(tim["fit_s_mean"][fam]) + float(tim["cal_s_mean"][fam])
        for label, gen_ms, run_ms in (
                ("serial_generation_serial_deployment", ms_solver_committed, ms_solver_committed),
                ("parallel_generation_parallel_deployment", ms_par, ms_par),
                ("serial_generation_parallel_deployment", ms_solver_committed, ms_par)):
            once_s = n_gen * gen_ms / 1000.0 + fit + search_s
            save_ms = run_ms * (1.0 - esc) - ti / (Pmax if run_ms == ms_par else 1)
            bec = once_s * 1000.0 / save_ms if save_ms > 0 else float("inf")
            be_rows.append(dict(model=fam, target=tgt, accounting=label,
                                one_time_cost_s=once_s, saving_ms_per_case=save_ms,
                                break_even_cases=bec, break_even_scenarios=bec / BRANCHES))

    out = dict(
        hardware_recorded=json.load(open("data/solve_time.manifest.json"))["hardware"],
        hardware_gap=("the manifest hardware block records machine/processor/system/release/cpu "
                      "but NOT core count, thread count, or whether the solve was single-threaded. "
                      "Core count below is measured on the machine running this benchmark and is "
                      "NOT evidence about the machine that produced ms_solver=9.14."),
        solver_config=json.load(open("data/solve_time.manifest.json"))["solver"],
        cores_measured_now=cores,
        constraint_note=("item 2 required MEASURING parallel solve time, which runs the AC solver "
                         "and so conflicts with the 'zero new solves' header. Treated as a hardware "
                         "benchmark: 930 contingency solves per configuration, no dataset row, no "
                         "result artifact regenerated."),
        benchmark_basis=("mean over 930 solves per configuration with the JIT warm-up scenario "
                         "discarded; the committed ms_solver=9.14 is a MINIMUM over 400 solves, a "
                         "different basis, so the P=1 figure here is not directly comparable"),
        scaling=scaling, best_parallel=dict(n_workers=Pmax, effective_ms_per_case=ms_par,
                                            speedup=par_speedup, efficiency=par_eff),
        ms_inference=ms_inf, speedup_table=rows, break_even_table=be_rows,
        operating_points=OPS)
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"wrote {OUT}")
    meta = dict(artifact="parallel-baseline sensitivity of the reported speedups",
                cores=cores, solves_per_configuration=930,
                parallel_efficiency_at_max=par_eff, ms_per_case_parallel=ms_par)
    man = cm.build_manifest(OUT, meta, dict(task="parallel baseline", source=CURVE_V2))
    json.dump(man, open(mf.manifest_path(OUT), "w"), indent=2)
    print(f"wrote {mf.manifest_path(OUT)}")


if __name__ == "__main__":
    main()
