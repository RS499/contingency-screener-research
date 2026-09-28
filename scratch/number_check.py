"""Read-only full number check of report/paper_current_STS.tex.

Every numeric literal occurrence (scratch/extract_literals.py) is mapped by its surrounding TEXT,
not by line number, to the data file and key it should come from, recomputed here, and given a
status:
  MATCH      printed == recomputed value rounded to the printed precision (or, for a hedged word
             such as "about"/"around"/"roughly", within the stated tolerance)
  ROUNDING   off by at most one unit in the last printed digit
  MISMATCH   anything larger
  NO SOURCE  no data/*.json key holds the value; the recomputed column then shows what the
             parquet (or code) gives, so the number can still be judged
Kinds: result (a measured number), config (a design constant read from data/code), name (a
network size used as a name, e.g. "118-bus"), arith (follows arithmetically from other printed
numbers), meta (figure attribution: library version, year).

Writes nothing. Prints a markdown table to stdout plus a summary.
Usage: .venv/bin/python scratch/number_check.py > /dev/null   (or read the output)
"""

import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, "scratch")
import extract_literals

LIMIT = 0.94


def load(path):
    with open(path) as fh:
        return json.load(fh)


def pstd(vals):
    return float(np.std(np.array(vals, dtype=float)))


def tc_row(tc, model, target):
    for r in tc["records"]:
        if r["model"] == model and abs(r["coverage_target"] - target) < 1e-9:
            return r
    return None


def build_sources():
    """Load every source once; return a dict of named values (all in the units the paper prints)."""
    S = {}
    tc = load("data/tradeoff_curve_v2.json")
    tm = load("data/tuned_metrics.json")
    fz2 = load("data/frozen_poster_numbers_v2.json")
    sm = load("data/screener_metrics.json")
    md = load("data/missed_depth.json")
    bh = load("data/barrier_height.json")
    c30 = load("data/case30_thermal/case30_thermal_frozen.json")
    h3 = load("data/case30_thermal/h3_build_stats.json")
    ns2 = load("data/netstudy2/summary.json")
    pa = load("data/physics_ablation.json")
    f1 = load("data/f1_leakage_audit.json")
    clip = load("data/clip_artifact.json")
    sa = load("data/sampling_audit.json")
    th = load("data/thermal_check.json")
    tri = load("data/network_triage.json")
    st = load("data/solve_time.json")
    be = load("data/break_even.json")
    unc = load("data/unconditioned_base.json")
    b95 = load("data/bases_clearing_0p95.json")
    e95 = load("data/escalation_at_095.json")
    c57 = load("data/netstudy/case57/nofeasible_diagnostic.json")
    peg = load("data/netstudy2/case89pegase_nofeasible_diagnostic.json")
    spl = load("data/splits.json")
    ts = load("data/tuning_search.json")
    ece = load("data/element_conditional_escalation.json")

    # --- Table II and every results-prose restatement of it
    for model in ["ridge", "histgb"]:
        for t in [0.90, 0.94, 0.95, 0.96, 0.97, 0.98]:
            r = tc_row(tc, model, t)
            k = f"{model}@{t:.2f}"
            S[f"esc {k}"] = (100 * r["escalation"], "data/tradeoff_curve_v2.json → records[model,target].escalation")
            S[f"esc_sd {k}"] = (100 * r["escalation_std"], "data/tradeoff_curve_v2.json → .escalation_std")
            S[f"cov {k}"] = (100 * r["coverage_emp"], "data/tradeoff_curve_v2.json → .coverage_emp")
            S[f"cov_sd {k}"] = (100 * r["coverage_emp_std"], "data/tradeoff_curve_v2.json → .coverage_emp_std")
            S[f"miss {k}"] = (100 * r["missed_viol"], "data/tradeoff_curve_v2.json → .missed_viol")
            S[f"miss_sd {k}"] = (100 * r["missed_viol_std"], "data/tradeoff_curve_v2.json → .missed_viol_std")
            S[f"spd {k}"] = (r["net_speedup"], "data/tradeoff_curve_v2.json → .net_speedup")
            S[f"spd_sd {k}"] = (r["net_speedup_std"], "data/tradeoff_curve_v2.json → .net_speedup_std")
            S[f"qhat {k}"] = (r["q_hat"], "data/tradeoff_curve_v2.json → .q_hat")
            S[f"miss+sd {k}"] = (100 * (r["missed_viol"] + r["missed_viol_std"]),
                                 "data/tradeoff_curve_v2.json → missed_viol + missed_viol_std")

    # --- Table I model rows (M2) and baselines (committed)
    for fam in ["ridge", "histgb"]:
        rows = [r for r in tm["records"] if r["family"] == fam and r["metric"] == "m2"]
        src = "data/tuned_metrics.json → records[family, metric=m2]"
        S[f"mae {fam}"] = (1000 * np.mean([r["mae"] for r in rows]), src + ".mae (×10³, seed mean)")
        S[f"mae_sd {fam}"] = (1000 * pstd([r["mae"] for r in rows]), src + ".mae (×10³, pop. std)")
        S[f"mae_pu {fam}"] = (np.mean([r["mae"] for r in rows]), src + ".mae (pu)")
        S[f"r2 {fam}"] = (np.mean([r["r2"] for r in rows]), src + ".r2")
        S[f"r2_sd {fam}"] = (pstd([r["r2"] for r in rows]), src + ".r2 (pop. std)")
        S[f"tsurr {fam}"] = (np.mean([r["ms_surrogate"] for r in rows]), src + ".ms_surrogate")
        S[f"tsurr_sd {fam}"] = (pstd([r["ms_surrogate"] for r in rows]), src + ".ms_surrogate (pop. std)")
    for model, key in [("persistence", "pers"), ("train_mean", "tm")]:
        rows = [r for r in sm["records"] if r["model"] == model]
        src = f"data/screener_metrics.json → records[model={model}]"
        S[f"mae {key}"] = (1000 * np.mean([r["mae"] for r in rows]), src + ".mae (×10³)")
        S[f"mae_sd {key}"] = (1000 * pstd([r["mae"] for r in rows]), src + ".mae (×10³, pop. std)")
        S[f"r2 {key}"] = (np.mean([r["r2"] for r in rows]), src + ".r2")
        S[f"r2_sd {key}"] = (pstd([r["r2"] for r in rows]), src + ".r2 (pop. std)")
        S[f"esc {key}"] = (100 * np.mean([r["escalation"] for r in rows]), src + ".escalation")
        S[f"esc_sd {key}"] = (100 * pstd([r["escalation"] for r in rows]), src + ".escalation (pop. std)")
        S[f"miss {key}"] = (100 * np.mean([r["missed_viol"] for r in rows]), src + ".missed_viol")
        S[f"miss_sd {key}"] = (100 * pstd([r["missed_viol"] for r in rows]), src + ".missed_viol (pop. std)")
        S[f"spd {key}"] = (np.mean([r["net_speedup"] for r in rows]), src + ".net_speedup")
        S[f"spd_sd {key}"] = (pstd([r["net_speedup"] for r in rows]), src + ".net_speedup (pop. std)")

    cr = fz2["crossings_first_below_1pct_missed"]
    S["cross ridge"] = (cr["ridge"]["first_coverage_below_1pct_missed"], "data/frozen_poster_numbers_v2.json → crossings_first_below_1pct_missed.ridge")
    S["cross histgb"] = (cr["histgb"]["first_coverage_below_1pct_missed"], "data/frozen_poster_numbers_v2.json → crossings_first_below_1pct_missed.histgb")
    ce = fz2["ceilings"]
    S["saturation"] = (100 * ce["perfect_model_floor_saturation"], "data/frozen_poster_numbers_v2.json → ceilings.perfect_model_floor_saturation")
    S["ceil ridge"] = (100 * ce["escalation_at_max_band_width_approaches_P_pred_ge_0.94"]["ridge"], "data/frozen_poster_numbers_v2.json → ceilings.escalation_at_max_band_width_…ridge")
    S["ceil histgb"] = (100 * ce["escalation_at_max_band_width_approaches_P_pred_ge_0.94"]["histgb"], "data/frozen_poster_numbers_v2.json → ceilings.escalation_at_max_band_width_…histgb")

    df = fz2["dataset_facts"]
    S["rows"] = (df["rows"], "data/frozen_poster_numbers_v2.json → dataset_facts.rows")
    S["scen"] = (df["scenarios"], "data/frozen_poster_numbers_v2.json → dataset_facts.scenarios")
    S["conv"] = (df["converged_n1_rows"], "data/frozen_poster_numbers_v2.json → dataset_facts.converged_n1_rows")
    S["viol"] = (df["violation_rate_pct"], "data/frozen_poster_numbers_v2.json → dataset_facts.violation_rate_pct")
    S["bm118"] = (df["boundary_0p94_to_0p945_pct"], "data/frozen_poster_numbers_v2.json → dataset_facts.boundary_0p94_to_0p945_pct")
    S["vmin"] = (df["min_vm_min"], "data/frozen_poster_numbers_v2.json → dataset_facts.min_vm_min")
    S["vmax"] = (df["min_vm_max"], "data/frozen_poster_numbers_v2.json → dataset_facts.min_vm_max")
    top = df["critical_bus_top5"]
    for rank in range(3):
        S[f"bus{rank}"] = (top[rank]["bus"] + 1, f"data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[{rank}].bus (+1, IEEE name)")
        S[f"busshare{rank}"] = (top[rank]["share_pct"], f"data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[{rank}].share_pct")
    S["n1 solves"] = (be["generation"]["n1_solves"], "data/break_even.json → generation.n1_solves")
    S["base solves"] = (be["generation"]["base_solves_accepted"], "data/break_even.json → generation.base_solves_accepted")
    S["nonconv"] = (ece["n_nonconverged"], "data/element_conditional_escalation.json → n_nonconverged")
    S["n branch"] = (be["generation"]["branches"], "data/break_even.json → generation.branches")
    ra = th["networks"]["case118"]["rating_audit"]
    S["n lines"] = (ra["n_lines"], "data/thermal_check.json → networks.case118.rating_audit.n_lines")
    S["n trafos"] = (ra["n_trafos"], "data/thermal_check.json → networks.case118.rating_audit.n_trafos")
    S["rating"] = (ra["trafo_sn_mva"]["max"], "data/thermal_check.json → networks.case118.rating_audit.trafo_sn_mva / line implied_mva (both 9900)")
    S["overvolt"] = (100 * th["networks"]["case118"]["overvoltage"]["n1"]["share_above_1p05"], "data/thermal_check.json → networks.case118.overvoltage.n1.share_above_1p05")
    S["ov thr"] = (th["over_voltage_threshold"], "data/thermal_check.json → over_voltage_threshold")
    tri118 = [n for n in tri["networks"] if n["network"] == "case118"][0]
    tri30 = [n for n in tri["networks"] if n["network"] == "case30"][0]
    S["bus118"] = (tri118["n_bus"], "data/network_triage.json → networks[case118].n_bus")
    S["bus30"] = (tri30["n_bus"], "data/network_triage.json → networks[case30].n_bus")
    S["br30"] = (tri30["n_branch_n1"], "data/network_triage.json → networks[case30].n_branch_n1")
    S["load30 pub"] = (tri30["base_max_loading_pct"], "data/network_triage.json → networks[case30].base_max_loading_pct")
    S["thermal thr"] = (tri["criteria"]["thermal_max_pct"], "data/network_triage.json → criteria.thermal_max_pct")
    S["limit"] = (tc["limit"], "data/tradeoff_curve_v2.json → limit")
    S["oppt"] = (100 * tc["operating_point"], "data/tradeoff_curve_v2.json → operating_point")
    S["oppt frac"] = (tc["operating_point"], "data/tradeoff_curve_v2.json → operating_point")
    S["ceil1"] = (100 * ts["inner_missed_ceiling"], "data/tuning_search.json → inner_missed_ceiling")
    S["strip"] = (md["boundary_strip_width"], "data/missed_depth.json → boundary_strip_width")
    S["strip hi"] = (unc["strip_hi"], "data/unconditioned_base.json → strip_hi")
    S["bin"] = (unc["committed_gated"]["largest_bin_hi"] - unc["committed_gated"]["largest_bin_lo"], "data/unconditioned_base.json → committed_gated.largest_bin_hi − _lo")
    S["bin share"] = (unc["committed_gated"]["largest_bin_share_pct"], "data/unconditioned_base.json → committed_gated.largest_bin_share_pct")
    S["tsolve"] = (st["ms_solver"], "data/solve_time.json → ms_solver")
    S["ntimed"] = (st["n_timed"], "data/solve_time.json → n_timed")
    S["train frac"] = (100 * spl["train_frac"], "data/splits.json → train_frac")
    S["cal frac"] = (100 * spl["cal_frac"], "data/splits.json → cal_frac / test_frac")
    S["pgen"] = (100 * sa["outage_probability"]["as_coded"], "data/sampling_audit.json → outage_probability.as_coded")
    S["n genout"] = (sa["prevalence"]["n_base_with_generator_outage"], "data/sampling_audit.json → prevalence.n_base_with_generator_outage")
    S["share genout"] = (100 * sa["prevalence"]["share_of_base_scenarios"], "data/sampling_audit.json → prevalence.share_of_base_scenarios")
    S["rows genout"] = (sa["prevalence"]["n_n1_rows_with_generator_outage"], "data/sampling_audit.json → prevalence.n_n1_rows_with_generator_outage")
    S["mult lo"] = (1.0, "data/sampling_audit.json → multiplier_audit.multiplier_range_as_invoked ('U(1.0, 1.12)')")
    S["mult hi"] = (1.12, "data/sampling_audit.json → multiplier_audit.multiplier_range_as_invoked ('U(1.0, 1.12)')")
    assert "U(1.0, 1.12)" in sa["multiplier_audit"]["multiplier_range_as_invoked"]
    S["range30 lo"] = (h3["range"]["lo"], "data/case30_thermal/h3_build_stats.json → range.lo")
    S["range30 hi"] = (h3["range"]["hi"], "data/case30_thermal/h3_build_stats.json → range.hi")
    S["maxload30"] = (h3["max_base_loading_pct"], "data/case30_thermal/h3_build_stats.json → max_base_loading_pct")
    S["n30"] = (h3["n1_loading"]["n"], "data/case30_thermal/h3_build_stats.json → n1_loading.n")
    S["bases30"] = (h3["n_accepted"], "data/case30_thermal/h3_build_stats.json → n_accepted")
    S["over100 30"] = (100 * h3["n1_loading"]["share_above_100"], "data/case30_thermal/h3_build_stats.json → n1_loading.share_above_100")
    S["max30"] = (h3["n1_loading"]["max"], "data/case30_thermal/h3_build_stats.json → n1_loading.max")
    S["bm30"] = (c30["boundary_mass_pct"], "data/case30_thermal/case30_thermal_frozen.json → boundary_mass_pct")
    S["viol30"] = (c30["violation_rate_pct"], "data/case30_thermal/case30_thermal_frozen.json → violation_rate_pct")
    for t in [0.96, 0.97]:
        rows = [r for r in c30["records"] if r["family"] == "histgb" and abs(r["coverage_target"] - t) < 1e-9]
        src = "data/case30_thermal/case30_thermal_frozen.json → records[histgb, target]"
        S[f"c30 esc {t}"] = (100 * np.mean([r["escalation"] for r in rows]), src + ".escalation")
        S[f"c30 esc_sd {t}"] = (100 * pstd([r["escalation"] for r in rows]), src + ".escalation (pop. std)")
        S[f"c30 miss {t}"] = (100 * np.mean([r["missed_viol"] for r in rows]), src + ".missed_viol")
        S[f"c30 miss_sd {t}"] = (100 * pstd([r["missed_viol"] for r in rows]), src + ".missed_viol (pop. std)")
        S[f"c30 nunder {t}"] = (int(sum(1 for r in rows if r["missed_viol"] < 0.01)), src + " count(missed < 1%)")
    first_all5 = None
    for t in sorted(set(r["coverage_target"] for r in c30["records"])):
        rows = [r for r in c30["records"] if r["family"] == "histgb" and abs(r["coverage_target"] - t) < 1e-9]
        if first_all5 is None and all(r["missed_viol"] < 0.01 for r in rows):
            first_all5 = t
    S["c30 all5"] = (first_all5, "data/case30_thermal/case30_thermal_frozen.json → first target with all 5 histgb splits < 1%")

    ca = clip["clip_era"]
    S["atom"] = (ca["clip_atom_share_pct"], "data/clip_artifact.json → clip_era.clip_atom_share_pct")
    S["atom bus"] = (ca["atom_top_buses"][0]["ieee_bus"], "data/clip_artifact.json → clip_era.atom_top_buses[0].ieee_bus")
    S["bm clip"] = (ca["boundary_0p94_to_0p945_pct"], "data/clip_artifact.json → clip_era.boundary_0p94_to_0p945_pct")
    S["genvm lo"] = (0.94, "feasibility/generate_dataset.py:10 GEN_VM_LO; data/archive_clip/README.md:4 ('CLIPPED at the 0.94')")
    S["atom tol"] = (1e-9, "data/clip_artifact.json → atom_definition ('rounded to 9 decimals' = ±0.5e-9, inside the printed ±1e-9)")

    for fam, key in [("ridge", "ridge"), ("histgb", "histgb")]:
        s = bh["summary_at_090"]["case118"][fam]
        S[f"smean {key}"] = (s["S_mean_over_qhat_at_090_mean"], "data/barrier_height.json → summary_at_090.case118." + fam + ".S_mean_over_qhat_at_090_mean")
        S[f"smean_sd {key}"] = (s["S_mean_over_qhat_at_090_std"], "data/barrier_height.json → …S_mean_over_qhat_at_090_std")
        p = md["families"][fam]["pooled"]["0.90"]
        S[f"within_q {key}"] = (100 * p["share_below_qhat"], f"data/missed_depth.json → families.{fam}.pooled['0.90'].share_below_qhat")
        S[f"beyond_strip {key}"] = (100 * (1 - p["share_below_strip"]), f"data/missed_depth.json → 1 − families.{fam}.pooled['0.90'].share_below_strip")
    S["deep"] = (md["families"]["histgb"]["deepest_missed"]["depth"], "data/missed_depth.json → families.*.deepest_missed.depth")
    S["deep y"] = (md["families"]["histgb"]["deepest_missed"]["y_true"], "data/missed_depth.json → families.*.deepest_missed.y_true")

    cn = ns2["cross_network"]
    S["A rel"] = (cn["A_mean_rel_error"], "data/netstudy2/summary.json → cross_network.A_mean_rel_error")
    S["B rel"] = (cn["B_mean_rel_error"], "data/netstudy2/summary.json → cross_network.B_mean_rel_error")
    S["A abs"] = (cn["A_mean_abs_error"], "data/netstudy2/summary.json → cross_network.A_mean_abs_error")
    S["B abs"] = (cn["B_mean_abs_error"], "data/netstudy2/summary.json → cross_network.B_mean_abs_error")
    S["n cross"] = (cn["n"], "data/netstudy2/summary.json → cross_network.n")
    comps = ns2["cross_comparisons"]
    S["cross nets"] = (len(set(c["network"] for c in comps)), "data/netstudy2/summary.json → distinct cross_comparisons[].network")
    S["cross fams"] = (len(set(c["family"] for c in comps)), "data/netstudy2/summary.json → distinct cross_comparisons[].family")
    S["cross tgts"] = (len(set(c["coverage_target"] for c in comps)), "data/netstudy2/summary.json → distinct cross_comparisons[].coverage_target")
    z57 = [s for s in c57["scaling"] if s["multiplier"] == 0.0][0]
    S["c57 mult"] = (0.0, "data/netstudy/case57/nofeasible_diagnostic.json → scaling[multiplier=0.0]")
    S["c57 vmin"] = (z57["min_vm_pu"], "data/netstudy/case57/nofeasible_diagnostic.json → scaling[multiplier=0.0].min_vm_pu")
    S["c57 nb"] = (z57["n_bus_below_094"], "data/netstudy/case57/nofeasible_diagnostic.json → scaling[multiplier=0.0].n_bus_below_094")
    S["peg trafo"] = (peg["worst_trafos_at_nominal"][0]["loading_pct"], "data/netstudy2/case89pegase_nofeasible_diagnostic.json → worst_trafos_at_nominal[0].loading_pct (the WORST trafo)")
    S["peg n100"] = (peg["n_trafo_over_100_at_nominal"], "data/netstudy2/case89pegase_nofeasible_diagnostic.json → n_trafo_over_100_at_nominal")
    S["peg ntr"] = (peg["n_trafo"], "data/netstudy2/case89pegase_nofeasible_diagnostic.json → n_trafo")
    zp = [s for s in peg["scaling"] if s["multiplier"] == 0.0][0]
    S["peg zero"] = (zp["max_loading_pct"], "data/netstudy2/case89pegase_nofeasible_diagnostic.json → scaling[multiplier=0.0].max_loading_pct")
    S["b95"] = (b95["canonical_v2"]["ge_0p95"], "data/bases_clearing_0p95.json → canonical_v2.ge_0p95")
    S["e95"] = (100 * e95["summary"]["ridge"]["escalation_at_0.95"]["mean"], "data/escalation_at_095.json → summary.ridge.escalation_at_0.95.mean")
    S["e95 sd"] = (100 * e95["summary"]["ridge"]["escalation_at_0.95"]["std"], "data/escalation_at_095.json → summary.ridge.escalation_at_0.95.std")

    def abl(cfg, fam, mode="m2_searched"):
        return [r["mae"] for r in pa["records"] if r["config"] == cfg and r["family"] == fam and r["mode"] == mode and r["status"] == "OK"]
    src = "data/physics_ablation.json → records[config, family, m2_searched].mae"
    S["abl ridge"] = (np.mean(abl("+F1+F3", "ridge")), src + " (+F1+F3, ridge, mean)")
    S["abl ridge sd"] = (pstd(abl("+F1+F3", "ridge")), src + " (+F1+F3, ridge, pop. std)")
    S["abl hgb"] = (np.mean(abl("+F1+F2+F3+F4", "histgb")), src + " (+F1+F2+F3+F4, histgb, mean)")
    S["abl hgb sd"] = (pstd(abl("+F1+F2+F3+F4", "histgb")), src + " (+F1+F2+F3+F4, histgb, pop. std)")
    S["abl base"] = (np.mean(abl("baseline", "ridge")), src + " (baseline, ridge, mean)")
    S["abl base sd"] = (pstd(abl("baseline", "ridge")), src + " (baseline, ridge, pop. std)")
    S["abl f2"] = (np.mean(abl("+F1+F2", "ridge")), src + " (+F1+F2, ridge, mean)")
    S["abl f2 sd"] = (pstd(abl("+F1+F2", "ridge")), src + " (+F1+F2, ridge, pop. std)")
    S["abl pct"] = (100 * (np.mean(abl("+F1+F2", "ridge")) / np.mean(abl("baseline", "ridge")) - 1), src + " (+F1+F2 / baseline − 1, ridge)")
    S["hgb seed sd"] = (pstd(abl("baseline", "histgb")), src + " (baseline, histgb, pop. std)")
    cp = f1["check_4_permutation"]
    S["perm base"] = (cp["baseline"]["mae"], "data/f1_leakage_audit.json → check_4_permutation.baseline.mae")
    S["perm real"] = (cp["F1_real"]["mae"], "data/f1_leakage_audit.json → check_4_permutation.F1_real.mae")
    S["perm shuf"] = (cp["F1_shuffled"]["mae"], "data/f1_leakage_audit.json → check_4_permutation.F1_shuffled.mae")
    S["perm gap"] = (cp["F1_real"]["mae"] - cp["F1_shuffled"]["mae"], "data/f1_leakage_audit.json → F1_real.mae − F1_shuffled.mae")
    S["audit n"] = (f1["check_2_base_solve_integrity"]["n_scenarios_checked"], "data/f1_leakage_audit.json → check_2_base_solve_integrity.n_scenarios_checked")

    # --- parquet-only facts (no data/*.json key: NO SOURCE, but recomputed)
    import pandapower.networks as pn
    net = pn.case118()
    S["setpoint76"] = (float(net.gen[net.gen.bus == 75].vm_pu.iloc[0]), "pandapower case118() → gen at bus index 75 (IEEE 76) .vm_pu")
    cols = pd.read_parquet("data/dataset.parquet").columns
    pcols = [c for c in cols if c.startswith("pload_")]
    qcols = [c for c in cols if c.startswith("qload_")]
    d = pd.read_parquet("data/dataset.parquet", columns=["outaged_type", "sampling_mode", "converged", "min_vm"] + pcols + qcols)
    base = d[d["outaged_type"] == "none"]
    # pload_i / qload_i are per BUS index i (118 columns); base load summed per bus
    p0 = net.load.groupby("bus").p_mw.sum().reindex(range(len(pcols)), fill_value=0.0).to_numpy()
    q0 = net.load.groupby("bus").q_mvar.sum().reindex(range(len(qcols)), fill_value=0.0).to_numpy()
    pmask = np.abs(p0) > 1e-9
    pm = base[[f"pload_{i}" for i in range(len(pcols))]].to_numpy()[:, pmask] / p0[pmask]
    qmask = np.abs(q0) > 1e-9
    qm = base[[f"qload_{i}" for i in range(len(qcols))]].to_numpy()[:, qmask] / q0[qmask]
    reg = (base["sampling_mode"] == "regional").to_numpy()
    S["n indep"] = (int((~reg).sum()), "NO KEY — data/dataset.parquet → base rows, sampling_mode == independent")
    S["n reg"] = (int(reg.sum()), "NO KEY — data/dataset.parquet → base rows, sampling_mode == regional")
    S["reg lo"] = (float(pm[reg].min()), "NO KEY — dataset.parquet pload_i / case118 p_mw, regional bases, min")
    S["reg hi"] = (float(pm[reg].max()), "NO KEY — dataset.parquet pload_i / case118 p_mw, regional bases, max")
    S["reg out"] = (100 * float(((pm[reg] < 1.0 - 1e-9) | (pm[reg] > 1.12 + 1e-9)).mean()), "NO KEY — share of regional per-load multipliers outside [1.0, 1.12]")
    S["q lo"] = (float(qm.min()), "NO KEY — dataset.parquet qload_i / case118 q_mvar, all bases, min")
    S["q hi"] = (float(qm.max()), "NO KEY — dataset.parquet qload_i / case118 q_mvar, all bases, max")
    n1 = d[(d["outaged_type"] != "none") & (d["converged"])]
    S["below087"] = (100 * float((n1["min_vm"] < 0.87).mean()), "NO KEY — dataset.parquet converged N-1 rows, share min_vm < 0.87")
    S["view lo"] = (0.87, "feasibility/boundary_mass_hist.py:21 VIEW_LO")
    return S


# ---------------------------------------------------------------------------------------------
# Rules: (context substring or None, printed literal, source name, kind, tolerance or None).
# The context substring must appear in the ~100 characters around the literal. First match wins,
# so more specific rules come first. Table rows are mapped positionally in TABLE_ROWS.
RULES = [
    # hedged / approximate words
    ("takes around 9", "9", "tsolve", "result", 0.5),
    ("roughly 1.58", "1.58", "spd histgb@0.97", "result", None),
    ("more than about 14", "14", "bin share", "result", 0.5),
    ("accept about a 1.6", "1.6", "spd histgb@0.97", "result", 0.05),
    ("instead of the 2 to", "2", "spd ridge@0.90", "result", 0.05),
    ("to 3.3 times", "3.3", "spd histgb@0.90", "result", 0.05),
    ("speed-up factor of 1.6", "1.6", "spd ridge@0.94", "result", 0.05),
    ("reach up to about 1.0", "1.0", "miss+sd ridge@0.94", "result", None),
    ("1.07\\%, as Fig", "1.07", "miss+sd histgb@0.97", "result", None),
    ("slightly above 1", "1", "miss+sd histgb@0.97", "claim>1", None),
    ("slightly above 1", "1", "miss+sd histgb@0.97", "claim>1", None),
    ("touching the 1", "1", "miss+sd histgb@0.97", "claim~1", None),
    ("just under 100", "100", "maxload30", "result", 0.01),
    # abstract / results prose restating Table II
    ("model is 3.29 times", "3.29", "spd histgb@0.90", "result", None),
    ("3.29 times faster than the solver but misses", "4.72", "miss histgb@0.90", "result", None),
    ("under a 1\\% mean", "1", "ceil1", "config", None),
    ("rate at a 0.97", "0.97", "cross histgb", "result", None),
    ("in a 63.7", "63.7", "esc histgb@0.97", "result", None),
    ("regenerated 30-bus network has 7.09", "7.09", "bm30", "result", None),
    ("30-bus network has 7.09\\% of its contingencies in the [0.94, 0.945", "0.945", "strip hi", "config", None),
    ("compared to 56.86", "56.86", "bm118", "result", None),
    ("model at 0.97 coverage results", "0.97", "c30 all5", "result", None),
    ("results in a 5.84", "5.84", "c30 esc 0.97", "result", None),
    ("5.84$ \\pm $1.25", "1.25", "c30 esc_sd 0.97", "result", None),
    ("5.84 $\\pm$1.25", "1.25", "c30 esc_sd 0.97", "result", None),
    ("1.25\\% escalation", "1.25", "c30 esc_sd 0.97", "result", None),
    ("gives 5.84", "5.84", "c30 esc 0.97", "result", None),
    ("5.84$ \\pm $1.25\\% escalations", "1.25", "c30 esc_sd 0.97", "result", None),
    ("escalations and misses 0.76", "0.76", "c30 miss 0.97", "result", None),
    ("0.76$ \\pm $0.20", "0.20", "c30 miss_sd 0.97", "result", None),
    ("mean is 0.91", "0.91", "c30 miss 0.96", "result", None),
    ("0.91$ \\pm $0.22", "0.22", "c30 miss_sd 0.96", "result", None),
    ("All five splits are under 1", "1", "ceil1", "config", None),
    ("under 1\\% at 0.97", "0.97", "c30 all5", "result", None),
    ("but not at 0.96", "0.96", None, "config", None),
    ("coverage target of 0.97 gives", "0.97", "c30 all5", "result", None),
    # dataset / background
    ("indicates a 6", "6", None, "arith", None),
    ("where 1.0 is nominal", "1.0", None, "definition", None),
    ("73.1", "73.1", "overvolt", "result", None),
    ("over 1.05", "1.05", "ov thr", "config", None),
    ("9,900", "9,900", "rating", "result", None),
    ("with 118 buses", "118", "bus118", "name", None),
    ("173 lines", "173", "n lines", "result", None),
    ("13 transformers", "13", "n trafos", "result", None),
    ("there are 186", "186", "n branch", "result", None),
    ("simulation of 186", "186", "n branch", "result", None),
    ("generates 186", "186", "n branch", "result", None),
    ("rather than 186", "186", "n branch", "result", None),
    ("Independent mode (750", "750", "n indep", "nokey", None),
    ("Regional mode (750", "750", "n reg", "nokey", None),
    ("from 0.9009", "0.9009", "reg lo", "nokey", None),
    ("to 1.2310", "1.2310", "reg hi", "nokey", None),
    ("(43.91", "43.91", "reg out", "nokey", None),
    ("from 0.8156", "0.8156", "q lo", "nokey", None),
    ("to 1.4083", "1.4083", "q hi", "nokey", None),
    ("multipliers ranging from 1.0", "1.0", "mult lo", "config", None),
    ("ranging from 1.0 to 1.12", "1.12", "mult hi", "config", None),
    ("outside the 1.0", "1.0", "mult lo", "config", None),
    ("the 1.0 to 1.12", "1.12", "mult hi", "config", None),
    ("across all 1,500", "1,500", "scen", "result", None),
    ("generator (never the slack) 30", "30", "pgen", "config", None),
    ("only 374", "374", "n genout", "result", None),
    ("which 374", "374", "n genout", "result", None),
    ("374 of the 1{,}500", "1{,}500", "scen", "result", None),
    ("(24.93", "24.93", "share genout", "result", None),
    ("69{,}532", "69{,}532", "rows genout", "result", None),
    ("contained 1{,}500", "1{,}500", "scen", "result", None),
    ("280{,}500", "280{,}500", "rows", "result", None),
    ("rows, 1{,}500 were", "1{,}500", "base solves", "result", None),
    ("279{,}000", "279{,}000", "n1 solves", "result", None),
    (", 45 were", "45", "nonconv", "result", None),
    ("278{,}955", "278{,}955", "conv", "result", None),
    ("278,955", "278,955", "conv", "result", None),
    ("from 0.7179", "0.7179", "vmin", "result", None),
    ("to 0.9603", "0.9603", "vmax", "result", None),
    ("111.83", "111.83", "load30 pub", "result", None),
    ("at most 100", "100", "thermal thr", "config", None),
    ("window to 0.87", "0.87", "range30 lo", "config", None),
    ("0.99, which brought", "0.99", "range30 hi", "config", None),
    ("41 rather", "41", "br30", "result", None),
    ("the 1{,}500 bases produce", "1{,}500", "bases30", "result", None),
    ("61{,}500", "61{,}500", "n30", "result", None),
    ("lower bound of 0.94", "0.94", "genvm lo", "config", None),
    ("35.17", "35.17", "atom", "result", None),
    ("mainly to bus 76", "76", "atom bus", "result", None),
    ("0.943", "0.943", "setpoint76", "result", None),
    ("near $0.940000", "0.940000", "limit", "config", None),
    ("spike at 0.940000", "0.940000", "limit", "config", None),
    ("1\\times10^{-9}", "1\\times10^{-9}", "atom tol", "config", None),
    ("from 55.5", "55.5", "bm clip", "result", None),
    ("to 56.86", "56.86", "bm118", "result", None),
    ("60\\%, 20", "60", "train frac", "config", None),
    ("20\\%, and 20", "20", "cal frac", "config", None),
    ("and 20\\% sets", "20", "cal frac", "config", None),
    ("missing 1\\% or fewer", "1", "ceil1", "config", None),
    ("widths are 0.0052", "0.0052", "qhat ridge@0.90", "result", None),
    ("and 0.0023 per unit", "0.0023", "qhat histgb@0.90", "result", None),
    ("band is only 0.0023", "0.0023", "qhat histgb@0.90", "result", None),
    ("set at 9.14", "9.14", "tsolve", "result", None),
    ("over 400", "400", "ntimed", "result", None),
    ("0.00116", "0.00116", "tsurr ridge", "result", None),
    ("0.00116 \\pm 0.00012", "0.00012", "tsurr_sd ridge", "result", None),
    ("0.00241", "0.00241", "tsurr histgb", "result", None),
    ("0.00241 \\pm 0.00062", "0.00062", "tsurr_sd histgb", "result", None),
    ("0.6038", "0.6038", "smean ridge", "result", None),
    ("0.6038$ \\pm $0.0757", "0.0757", "smean_sd ridge", "result", None),
    ("0.7919", "0.7919", "smean histgb", "result", None),
    ("0.7919$ \\pm $0.0743", "0.0743", "smean_sd histgb", "result", None),
    # results prose
    ("$R^2$ of 0.77", "0.77", "r2 ridge", "result", None),
    ("0.77", "0.77", "r2 ridge", "result", None),
    ("model 0.92", "0.92", "r2 histgb", "result", None),
    ("errors of 0.0038", "0.0038", "mae_pu ridge", "result", None),
    ("and 0.0016 per", "0.0016", "mae_pu histgb", "result", None),
    ("ridge model escalates 49.1", "49.1", "esc ridge@0.90", "result", None),
    ("has 89.3", "89.3", "cov ridge@0.90", "result", None),
    ("misses 2.96", "2.96", "miss ridge@0.90", "result", None),
    ("is 2.04 times", "2.04", "spd ridge@0.90", "result", None),
    ("escalates 30.6", "30.6", "esc histgb@0.90", "result", None),
    ("has 89.8", "89.8", "cov histgb@0.90", "result", None),
    ("and is 3.29 times", "3.29", "spd histgb@0.90", "result", None),
    ("yet it misses 4.72", "4.72", "miss histgb@0.90", "result", None),
    ("coverage is close to 90", "90", "oppt", "config", None),
    ("from 4.72", "4.72", "miss histgb@0.90", "result", None),
    ("to 2.48", "2.48", "miss histgb@0.94", "result", None),
    ("from 30.6", "30.6", "esc histgb@0.90", "result", None),
    ("to 46.7", "46.7", "esc histgb@0.94", "result", None),
    ("from 3.29", "3.29", "spd histgb@0.90", "result", None),
    ("to 2.15", "2.15", "spd histgb@0.94", "result", None),
    ("from 0.90 to 0.94 decreases", "0.90", "oppt frac", "config", None),
    ("from 0.90 to 0.94 decreases", "0.94", "cross ridge", "config", None),
    ("target from 0.90 to 0.98", "0.90", "oppt frac", "config", None),
    ("target from 0.90 to 0.98", "0.98", None, "config", None),
    ("below 1\\% at 0.94", "1", "ceil1", "config", None),
    ("below 1\\% at 0.94", "0.94", "cross ridge", "result", None),
    ("(0.79", "0.79", "miss ridge@0.94", "result", None),
    ("0.79\\% missed, 64.3", "64.3", "esc ridge@0.94", "result", None),
    ("escalation, 1.56", "1.56", "spd ridge@0.94", "result", None),
    ("and 0.97 for the gradient-boosted model (0.83", "0.97", "cross histgb", "result", None),
    ("(0.83", "0.83", "miss histgb@0.97", "result", None),
    ("missed, 63.7", "63.7", "esc histgb@0.97", "result", None),
    ("escalation, 1.58", "1.58", "spd histgb@0.97", "result", None),
    ("just under 1\\% at 0.94", "1", "ceil1", "config", None),
    ("just under 1\\% at 0.94", "0.94", "cross ridge", "result", None),
    ("and 0.97 for the gradient-boosted model, with", "0.97", "cross histgb", "result", None),
    ("0.97 for the gradient-boosted model, with", "0.97", "cross histgb", "result", None),
    ("has a 3.29", "3.29", "spd histgb@0.90", "result", None),
    ("compared to 2.04", "2.04", "spd ridge@0.90", "result", None),
    ("at a coverage of 0.96", "0.96", None, "config", None),
    ("misses 0.14", "0.14", "miss ridge@0.96", "result", None),
    ("misses 1.36", "1.36", "miss histgb@0.96", "result", None),
    ("At 0.90 coverage, 74", "0.90", "oppt frac", "config", None),
    ("coverage, 74", "74", "within_q ridge", "result", None),
    ("and 55\\% for", "55", "within_q histgb", "result", None),
    ("with 26.7", "26.7", "beyond_strip ridge", "result", None),
    ("and 21.4", "21.4", "beyond_strip histgb", "result", None),
    ("more than 0.005", "0.005", "strip", "config", None),
    ("at 0.0915", "0.0915", "deep", "result", None),
    ("falls 0.0915", "0.0915", "deep", "result", None),
    ("fell to 0.8485", "0.8485", "deep y", "result", None),
    ("fallen to 0.8485", "0.8485", "deep y", "result", None),
    ("0.94 pu floor at 90", "90", "oppt", "config", None),
    ("74\\% of ridge misses", "74", "within_q ridge", "result", None),
    ("55\\% of histgb", "55", "within_q histgb", "result", None),
    ("within 0.005", "0.005", "strip", "config", None),
    ("Of all converged cases, 56.86", "56.86", "bm118", "result", None),
    ("and 17.48", "17.48", "viol", "result", None),
    ("single 0.001", "0.001", "bin", "config", None),
    ("tallest 0.001", "0.001", "bin", "config", None),
    ("with bus 76", "76", "bus0", "result", None),
    ("contingencies, while bus 53", "53", "bus1", "result", None),
    ("in 27.1", "27.1", "busshare0", "result", None),
    ("second at 16.81", "16.81", "busshare1", "result", None),
    ("bus 107", "107", "bus2", "result", None),
    ("third at 9.31", "9.31", "busshare2", "result", None),
    ("buses are 76", "76", "bus0", "result", None),
    ("76, 53", "53", "bus1", "result", None),
    ("and 107", "107", "bus2", "result", None),
    ("shares: 27.1", "27.1", "busshare0", "result", None),
    ("27.1\\%, 16.81", "16.81", "busshare1", "result", None),
    ("and 9.31", "9.31", "busshare2", "result", None),
    ("holds 56.9", "56.9", "bm118", "result", None),
    ("holds only 14.1", "14.1", "bin share", "result", None),
    ("truncated at 0.87", "0.87", "view lo", "config", None),
    ("which 0.5", "0.5", "below087", "nokey", None),
    ("captures 30.6", "30.6", "esc histgb@0.90", "result", None),
    ("is 82.64", "82.64", "saturation", "result", None),
    ("ceiling of 74.89", "74.89", "ceil ridge", "result", None),
    ("versus 82.79", "82.79", "ceil histgb", "result", None),
    ("escalates 99.5", "99.5", "esc pers", "result", None),
    ("rate around 1", "1", "ceil1", "config", None),
    ("at a 0.94 or", "0.94", "cross ridge", "result", None),
    ("or a 0.97 target", "0.97", "cross histgb", "result", None),
    ("available at 0.90", "0.90", "oppt frac", "config", None),
    ("54 predictions", "54", "n cross", "result", None),
    ("(3 networks", "3", "cross nets", "result", None),
    ("2 models", "2", "cross fams", "result", None),
    ("9 coverage", "9", "cross tgts", "result", None),
    ("0.4726", "0.4726", "A rel", "result", None),
    ("0.4933", "0.4933", "B rel", "result", None),
    ("at 0.1056", "0.1056", "B abs", "result", None),
    ("versus 0.1163", "0.1163", "A abs", "result", None),
    ("multiplier 0.0 the minimum", "0.0", "c57 mult", "config", None),
    ("remained 0.9012", "0.9012", "c57 vmin", "result", None),
    ("with 24 buses", "24", "c57 nb", "result", None),
    ("at 392", "392", "peg trafo", "result", None),
    ("(16 of 50", "16", "peg n100", "result", None),
    ("16 of 50", "50", "peg ntr", "result", None),
    ("transformers over 100", "100", "thermal thr", "config", None),
    ("At load multiplier 0.0, the maximum", "0.0", "c57 mult", "config", None),
    ("199.37", "199.37", "peg zero", "result", None),
    ("while another 15.40", "15.40", "viol30", "result", None),
    ("For case118, 56.86", "56.86", "bm118", "result", None),
    ("and 17.48\\% fall below it", "17.48", "viol", "result", None),
    ("fall below it. The original", "17.48", "viol", "result", None),
    ("Only 86", "86", "b95", "result", None),
    ("86 of the 1,500", "1,500", "scen", "result", None),
    ("above 0.95", "0.95", None, "config", None),
    ("threshold to 0.95", "0.95", None, "config", None),
    ("escalation of 1.38", "1.38", "e95", "result", None),
    ("1.38$ \\pm $0.33", "0.33", "e95 sd", "result", None),
    ("base case, 7.09", "7.09", "bm30", "result", None),
    ("21.5", "21.5", "over100 30", "result", None),
    ("over 100\\% line loading (up to", "100", "thermal thr", "config", None),
    ("145.8", "145.8", "max30", "result", None),
    ("MAE of $0.00371", "0.00371", "abl ridge", "result", None),
    ("0.00371 \\pm 0.00010", "0.00010", "abl ridge sd", "result", None),
    ("and $0.00153", "0.00153", "abl hgb", "result", None),
    ("0.00153 \\pm 0.00011", "0.00011", "abl hgb sd", "result", None),
    ("+10.82", "10.82", "abl pct", "result", None),
    ("baseline $0.003754", "0.003754", "abl base", "result", None),
    ("0.003754 \\pm 0.000133", "0.000133", "abl base sd", "result", None),
    ("+F1+F2 $0.004161", "0.004161", "abl f2", "result", None),
    ("0.004161 \\pm 0.000247", "0.000247", "abl f2 sd", "result", None),
    ("were 0.0015638", "0.0015638", "perm base", "result", None),
    ("0.0015539", "0.0015539", "perm real", "result", None),
    ("0.0015300", "0.0015300", "perm shuf", "result", None),
    ("2.39\\times", "2.39\\times 10^{-5}", "perm gap", "result", None),
    ("7.58\\times", "7.58\\times 10^{-5}", "hgb seed sd", "result", None),
    ("across 25", "25", "audit n", "result", None),
    ("At 90\\% coverage, both", "90", "oppt", "config", None),
    ("approaches 1\\%", "1", "ceil1", "config", None),
    ("versus 0.1163) under", "0.1163", "A abs", "result", None),
    # 90 % operating point and limit used generically
    ("at 90\\% coverage", "90", "oppt", "config", None),
    ("At 90\\% coverage", "90", "oppt", "config", None),
    ("a 90\\% coverage", "90", "oppt", "config", None),
    ("At a 90\\%", "90", "oppt", "config", None),
    ("comparison at 90", "90", "oppt", "config", None),
    ("0.945", "0.945", "strip hi", "config", None),
    ("0.94", "0.94", "limit", "config", None),
    ("118-bus", "118", "bus118", "name", None),
    ("118 bus", "118", "bus118", "name", None),
    ("30-bus", "30", "bus30", "name", None),
    ("1,500 base cases are above", "1,500", "scen", "result", None),
]

# Table rows: row prefix → list of source names, one per numeric cell, in order.
TABLE_ROWS = {
    "persistence": ["mae pers", "mae_sd pers", "r2 pers", "r2_sd pers", "esc pers", "esc_sd pers",
                    "miss pers", "miss_sd pers", "spd pers", "spd_sd pers"],
    "train mean": ["mae tm", "mae_sd tm", "r2 tm", "r2_sd tm", "esc tm", "esc_sd tm", "miss tm", "miss_sd tm"],
    "ridge       &": ["mae ridge", "mae_sd ridge", "r2 ridge", "r2_sd ridge", "esc ridge@0.90", "esc_sd ridge@0.90",
                      "miss ridge@0.90", "miss_sd ridge@0.90", "spd ridge@0.90", "spd_sd ridge@0.90"],
    "histgb      &": ["mae histgb", "mae_sd histgb", "r2 histgb", "r2_sd histgb", "esc histgb@0.90", "esc_sd histgb@0.90",
                      "miss histgb@0.90", "miss_sd histgb@0.90", "spd histgb@0.90", "spd_sd histgb@0.90"],
}
for fam in ["ridge", "histgb"]:
    for t in ["0.90", "0.94", "0.95", "0.96", "0.97", "0.98"]:
        k = f"{fam}@{t}"
        TABLE_ROWS[f"{fam}  & {t}" if fam == "ridge" else f"{fam} & {t}"] = [
            None, f"esc {k}", f"esc_sd {k}", f"cov {k}", f"cov_sd {k}", f"miss {k}", f"miss_sd {k}", f"spd {k}", f"spd_sd {k}"]

META_YEAR = {"gate_schematic_v4": 158, "tradeoff_hero_col_v2": 284, "miss_depth_v3": 306,
             "boundary_mass_hist_v2": 327, "critical_bus_map": 342}


def member_check(x, ctx):
    """A target or limit named in the text: VERIFIED only if it is one of the values actually run."""
    if "0.95" in ctx and ("threshold to 0.95" in ctx or "above 0.95" in ctx):
        lims = load("data/escalation_at_095.json")["limits"]
        ok = any(abs(x - v) < 1e-9 for v in lims)
        return (x if ok else None), f"data/escalation_at_095.json → limits {lims} ({'contains' if ok else 'MISSING'} {x})"
    levels = load("data/tradeoff_curve_v2.json")["coverage_levels"]
    ok = any(abs(x - v) < 1e-9 for v in levels)
    return (x if ok else None), f"data/tradeoff_curve_v2.json → coverage_levels ({'contains' if ok else 'MISSING'} {x})"


def status_for(printed, dp, sci, value, kind, tol):
    if kind in ("definition", "arith_ok"):
        return "MATCH"
    if value is None:
        return "NO SOURCE"
    p = float(printed.split("\\times")[0].replace("{,}", "").replace(",", ""))
    if sci:
        exp = int(printed.split("{")[-1].rstrip("}"))
        value = value / 10 ** exp
    if kind == "claim>1":
        return "MATCH" if value > float(p) else "MISMATCH"
    if kind == "claim~1":
        return "MATCH" if abs(value - float(p)) <= 0.1 else "MISMATCH"
    if tol is not None:
        return "MATCH" if abs(p - value) <= tol + 1e-12 else "MISMATCH"
    unit = 10 ** (-dp)
    if abs(round(value, dp) - p) < unit / 100:
        status = "MATCH"
    elif abs(value - p) <= unit * 1.01:
        status = "ROUNDING"
    else:
        status = "MISMATCH"
    return "NO SOURCE" if kind == "nokey" else status


def fmt(v):
    if v is None:
        return "—"
    if isinstance(v, (int, np.integer)) or float(v).is_integer():
        return f"{int(v):,}" if abs(v) >= 1000 else f"{int(v)}"
    a = abs(v)
    if a >= 100:
        return f"{v:.3f}"
    if a >= 1:
        return f"{v:.4f}"
    return f"{v:.6g}"


def check():
    S = build_sources()
    occ, excluded = extract_literals.occurrences()
    with open(extract_literals.TEX) as fh:
        lines = fh.read().split("\n")
    rows = []
    table_pos = {}
    for o in occ:
        line_text = lines[o["line"] - 1]
        src = None
        kind = None
        tol = None
        name = None
        stripped = line_text.strip()
        row_key = next((k for k in TABLE_ROWS if stripped.startswith(k)), None)
        if row_key is not None:
            i = table_pos.get(o["line"], 0)
            table_pos[o["line"]] = i + 1
            cells = TABLE_ROWS[row_key]
            name = cells[i] if i < len(cells) else None
            kind = "config" if name is None else "result"
            if name is None:
                src_value = member_check(float(o["printed"]), o["ctx"])
        elif o["printed"] == "3.11.1":
            fig = [k for k, v in META_YEAR.items() if v == o["line"]]
            man = load(f"data/{fig[0]}.manifest.json") if fig else None
            ok = man is not None and man.get("plotting_library") == "matplotlib 3.11.1"
            rows.append(dict(o, source=f"data/{fig[0]}.manifest.json → plotting_library" if fig else "no manifest",
                             recomputed=man.get("plotting_library") if man else "—", status="MATCH" if ok else "NO SOURCE", kind="meta"))
            continue
        elif o["printed"] == "2026" and o["line"] in META_YEAR.values():
            fig = [k for k, v in META_YEAR.items() if v == o["line"]][0]
            man = load(f"data/{fig}.manifest.json")
            yr = man.get("generated_utc", "")[:4]
            rows.append(dict(o, source=f"data/{fig}.manifest.json → generated_utc", recomputed=yr,
                             status="MATCH" if yr == "2026" else "NO SOURCE", kind="meta"))
            continue
        elif o["printed"] == "2026":
            rows.append(dict(o, source="table attribution year — no manifest records a table build date",
                             recomputed="—", status="NO SOURCE", kind="meta"))
            continue
        else:
            for ctx, printed, nm, kd, tl in RULES:
                if printed == o["printed"] and (ctx is None or ctx in o["ctx"]):
                    name, kind, tol = nm, kd, tl
                    break
        if row_key is not None and name is None:
            value, source = src_value
        elif name is None and kind in ("definition", "arith", "config"):
            value, source = None, {"definition": "definition (1.0 pu = nominal)",
                                   "arith": "arithmetic: 1 − 0.94 = 0.06 → 6%",
                                   "config": "design constant (sweep target / threshold named in the text)"}[kind]
            if kind == "arith":
                value, kind = 6.0, "result"
            elif kind == "config":
                value, source = member_check(float(o["value"]), o["ctx"])
        elif name is None:
            value, source, kind = None, "UNMAPPED — no rule", "unmapped"
        else:
            value, source = S[name]
        st = "UNMAPPED" if kind == "unmapped" else status_for(o["printed"], o["dp"], o["sci"], value, kind, tol)
        if kind == "definition":
            st = "MATCH"
        rows.append(dict(o, source=source, recomputed=fmt(value) if not isinstance(value, str) else value,
                         status=st, kind=kind, tol=tol, name=name))
    return rows, excluded


if __name__ == "__main__":
    rows, excluded = check()
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"<!-- {len(rows)} occurrences; {excluded} name/layout tokens excluded; {counts} -->")
    print("| Line | Printed | Kind | Source file → key | Recomputed | Status |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        pr = r["printed"].replace("\\times", "×").replace("{,}", ",").replace("|", "\\|")
        tolnote = f" (hedged, tol ±{r['tol']})" if r.get("tol") else ""
        print(f"| {r['line']} | {pr} | {r['kind']}{tolnote} | {r['source']} | {r['recomputed']} | {r['status']} |")
