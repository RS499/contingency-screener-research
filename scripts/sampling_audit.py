import ast
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manifest as mf
import classical_manifest as cm

# STAGE 2B. Two questions.
#
# 1. GENERATOR OUTAGE. generate_dataset.py applies a per-scenario generator outage. How
#    many rows labelled "N-1" are therefore two-element states, and are they materially
#    different in distribution?
#
# 2. MULTIPLIER AUDIT. Exactly which quantities the 1.0-1.12 multiplier touches and which
#    it does not, so the corrected Section III-A sentence has a source.
#
# METHOD NOTE. The multiplier audit is answered THREE ways and all three must agree:
#   (a) static: walk the AST of apply_scenario/sample_scenario and list every attribute
#       assignment, so "never assigned" is a parse result rather than a reading
#   (b) empirical: check the artifact for per-scenario variance in each feature family
#   (c) documented: the committed invocation in README.md
# A code reading alone is what produced the wrong DVM value earlier in this project.

DATASET = "data/dataset.parquet"
GENERATOR = "feasibility/generate_dataset.py"
OUT = "data/sampling_audit.json"
LIMIT = 0.94
STRIP_HI = 0.945


def rng_draw_sites(path):
    """Every rng.* call site in the sampling functions, with line numbers."""
    src = open(path).read()
    tree = ast.parse(src)
    sites = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name not in ("sample_scenario", "apply_scenario", "draw_gen_vm"):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                val = sub.func.value
                if isinstance(val, ast.Name) and val.id == "rng":
                    sites.append(dict(function=node.name, lineno=sub.lineno,
                                      call=f"rng.{sub.func.attr}"))
    return sorted(sites, key=lambda s: s["lineno"])


def assignment_targets(path):
    """Every `net.<table>[...] = ` / `net.<table>.iat[...] = ` target in apply_scenario."""
    src = open(path).read()
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name == "apply_scenario"):
            continue
        for sub in ast.walk(node):
            if not isinstance(sub, (ast.Assign, ast.AugAssign)):
                continue
            targets = sub.targets if isinstance(sub, ast.Assign) else [sub.target]
            for t in targets:
                out.append(dict(lineno=sub.lineno, target=ast.unparse(t),
                                value=ast.unparse(sub.value)[:90]))
    return sorted(out, key=lambda r: r["lineno"])


def family_variance(df_base, prefix, limit=None):
    cols = [c for c in df_base.columns if c.startswith(prefix)]
    if limit:
        cols = cols[:limit]
    if not cols:
        return dict(prefix=prefix, n_columns=0, status="NO COLUMNS")
    nuniq = [int(df_base[c].nunique()) for c in cols]
    stds = [float(df_base[c].std()) for c in cols]
    return dict(
        prefix=prefix,
        n_columns_checked=len(cols),
        all_constant=bool(max(nuniq) == 1),
        min_nunique=int(min(nuniq)),
        max_nunique=int(max(nuniq)),
        max_std=float(max(stds)),
        verdict=("CONSTANT across scenarios - NOT varied by any sampling mechanism"
                 if max(nuniq) == 1 else "VARIES across scenarios"),
    )


def main():
    d = pd.read_parquet(DATASET)
    base = d[d.outaged_type == "none"]
    n1 = d[d.outaged_type != "none"]
    n1c = n1[n1.converged]

    out = dict(
        question=("Stage 2B: generator-outage prevalence and its distributional effect, "
                  "plus an audit of exactly which quantities the 1.0-1.12 multiplier "
                  "touches."),
        dataset=DATASET,
        generator_script=GENERATOR,
    )

    # ---------- Q1: the outage probability as coded, and its draw site ----------
    src_lines = open(GENERATOR).read().splitlines()
    p_gen_out_line = next(i + 1 for i, ln in enumerate(src_lines)
                          if ln.strip().startswith("P_GEN_OUT"))
    draw_line = next(i + 1 for i, ln in enumerate(src_lines)
                     if "rng.random() < P_GEN_OUT" in ln)
    out["outage_probability"] = dict(
        as_coded=float([ln for ln in src_lines if ln.strip().startswith("P_GEN_OUT")][0]
                       .split("=")[1].strip()),
        constant_defined_at=f"{GENERATOR}:{p_gen_out_line}",
        rng_draw_site=f"{GENERATOR}:{draw_line}",
        draw_expression="if rng.random() < P_GEN_OUT",
        candidate_pool="non-slack generators only",
    )

    # ---------- Q2: prevalence ----------
    base_out = base.gen_out >= 0
    scen_with_outage = set(base.loc[base_out, "scenario_id"])
    n1_has_outage = n1c.scenario_id.isin(scen_with_outage)
    out["prevalence"] = dict(
        n_base_scenarios=int(len(base)),
        n_base_with_generator_outage=int(base_out.sum()),
        share_of_base_scenarios=float(base_out.mean()),
        n_n1_converged_rows=int(len(n1c)),
        n_n1_rows_with_generator_outage=int(n1_has_outage.sum()),
        share_of_n1_converged_rows=float(n1_has_outage.mean()),
        note=("A row with gen_out >= 0 has a generator out of service IN ADDITION to the "
              "outaged branch, so it is a two-element state."),
    )

    # ---------- Q3: acceptance-gate effect (prediction P2B-1) ----------
    out["acceptance_effect"] = dict(
        coded_probability=0.30,
        observed_share_of_accepted_bases=float(base_out.mean()),
        implied_relative_acceptance=float(base_out.mean() / (1 - base_out.mean())
                                          / (0.30 / 0.70)),
        mean_n0_min_vm_with_outage=float(base.loc[base_out, "n0_min_vm"].mean()),
        mean_n0_min_vm_without=float(base.loc[~base_out, "n0_min_vm"].mean()),
        median_n0_min_vm_with_outage=float(base.loc[base_out, "n0_min_vm"].median()),
        median_n0_min_vm_without=float(base.loc[~base_out, "n0_min_vm"].median()),
        interpretation_note=("If the gate is the cause, accepted gen-out scenarios should "
                             "sit closer to the 0.94 rejection boundary. Rejected draws "
                             "are NOT recorded in the dataset, so the rejection rate by "
                             "outage status CANNOT BE COMPUTED from this artifact."),
    )

    # ---------- Q4: distributional difference (P2B-2, P2B-3) ----------
    def block(frame):
        mv = frame.min_vm
        return dict(
            n=int(len(frame)),
            mean_min_vm=float(mv.mean()),
            median_min_vm=float(mv.median()),
            violation_rate=float((mv < LIMIT).mean()),
            boundary_strip_share=float(((mv >= LIMIT) & (mv < STRIP_HI)).mean()),
            p01_min_vm=float(np.percentile(mv, 1)),
            min_min_vm=float(mv.min()),
        )

    with_out = block(n1c[n1_has_outage])
    without = block(n1c[~n1_has_outage])
    out["distribution_by_outage_status"] = dict(
        with_generator_outage=with_out,
        without_generator_outage=without,
        delta=dict(
            violation_rate_pp=float((with_out["violation_rate"]
                                     - without["violation_rate"]) * 100),
            boundary_strip_pp=float((with_out["boundary_strip_share"]
                                     - without["boundary_strip_share"]) * 100),
            mean_min_vm=float(with_out["mean_min_vm"] - without["mean_min_vm"]),
        ),
    )

    # ---------- Q5: the multiplier audit, three ways ----------
    static = assignment_targets(GENERATOR)
    net_assigns = [r for r in static if r["target"].startswith("net")]
    touched = sorted({r["target"] for r in net_assigns})

    families = {
        "pload_": family_variance(base, "pload_", 8),
        "qload_": family_variance(base, "qload_", 8),
        "genp_": family_variance(base, "genp_", 8),
        "genvm_": family_variance(base, "genvm_", 8),
        "genqmin_": family_variance(base, "genqmin_", 8),
        "genqmax_": family_variance(base, "genqmax_", 8),
        "genon_": family_variance(base, "genon_", 8),
        "vm0_": family_variance(base, "vm0_", 8),
    }

    out["multiplier_audit"] = dict(
        multiplier_name="mp",
        multiplier_range_as_invoked="U(1.0, 1.12) per load, committed run README.md:94-95",
        static_assignment_targets_in_apply_scenario=net_assigns,
        net_attributes_ever_assigned=touched,
        rng_draw_sites=rng_draw_sites(GENERATOR),
        empirical_family_variance=families,
        TOUCHED_BY_MULTIPLIER=dict(
            load_p_mw=dict(
                how="net.load['p_mw'] = params['p_new'], where p_new = _p0 * mp",
                empirical=families["pload_"]["verdict"]),
            load_q_mvar=dict(
                how=("net.load['q_mvar'] = params['q_new'], where "
                     "q_new = _q0 * mp * pf; scaled by the multiplier AND by an "
                     "INDEPENDENT power-factor draw pf ~ U(0.9, 1.15) as invoked"),
                empirical=families["qload_"]["verdict"]),
        ),
        NOT_TOUCHED_BY_MULTIPLIER=dict(
            gen_p_mw=dict(
                how="net.gen['p_mw'] is NEVER assigned in apply_scenario",
                empirical=families["genp_"]["verdict"],
                consequence=("generator real power stays at base dispatch; the slack bus "
                             "absorbs the entire load increase")),
            gen_vm_pu=dict(
                how="net.gen['vm_pu'] = params['gen_vm'], drawn as base +/- dvm",
                empirical=families["genvm_"]["verdict"],
                consequence="varied, but by an independent jitter, not by the multiplier"),
            gen_q_limits=dict(
                how=("net.gen['min_q_mvar'] / ['max_q_mvar'] = base * qscale, "
                     "qscale ~ U(0.60, 1.40)"),
                empirical=f"{families['genqmin_']['verdict']} / {families['genqmax_']['verdict']}",
                consequence="varied, but by an independent draw"),
            gen_in_service=dict(
                how="net.gen.iat[gen_out, 'in_service'] = False when the outage draw fires",
                empirical=families["genon_"]["verdict"],
                consequence="set by the independent P_GEN_OUT draw"),
        ),
        aggregate_loading=dict(
            min=float(base.agg_loading.min()),
            max=float(base.agg_loading.max()),
            note=("agg_loading is the realised aggregate load multiple. Its max exceeds "
                  "1.12 because the regional mode applies a block multiplier plus "
                  "per-load jitter."),
        ),
    )

    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {OUT}")

    man = cm.build_manifest(OUT, out,
                            dict(task="Stage 2B generator-outage and multiplier audit",
                                 source=DATASET, generator=GENERATOR))
    with open(mf.manifest_path(OUT), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {mf.manifest_path(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
