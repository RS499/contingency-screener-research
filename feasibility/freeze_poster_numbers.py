import json
import numpy as np
import pandas as pd
import manifest as mf

LIMIT = 0.94
SAFETY_LEVELS = [0.90, 0.94, 0.95, 0.96, 0.97, 0.98]
MODELS = ["ridge", "histgb"]
OUT = "data/frozen_poster_numbers.json"
GEN_ACCEPTED = 1500
GEN_REJECTED = 1287


def load(path):
    with open(path) as f:
        return json.load(f)


def mean_over_seeds(records, model, field):
    vals = [r[field] for r in records if r["model"] == model]
    return float(np.mean(vals))


def coverage_row(records, model, cov):
    for r in records:
        if r["model"] == model and abs(r["coverage_target"] - cov) < 1e-9:
            return r
    return None


def max_qhat_row(records, model):
    rows = [r for r in records if r["model"] == model]
    order = np.argsort([r["q_hat"] for r in rows])
    return rows[order[-1]]


def first_crossing(records, model, max_missed=0.01):
    rows = [r for r in records if r["model"] == model]
    order = np.argsort([r["coverage_target"] for r in rows])
    for i in order:
        if rows[i]["missed_viol"] < max_missed:
            return rows[i]["coverage_target"], rows[i]["missed_viol"]
    return None, None


def four_metrics(sm):
    d = {"source": "data/screener_metrics.json"}
    for m in MODELS:
        d[m] = dict(escalation=mean_over_seeds(sm["records"], m, "escalation"),
                    coverage=mean_over_seeds(sm["records"], m, "coverage"),
                    missed_viol=mean_over_seeds(sm["records"], m, "missed_viol"),
                    net_speedup=mean_over_seeds(sm["records"], m, "net_speedup"))
    return d


def safety_points(tc):
    d = {"source": "data/tradeoff_curve.json"}
    for m in MODELS:
        rows = []
        for cov in SAFETY_LEVELS:
            r = coverage_row(tc["records"], m, cov)
            if r is not None:
                rows.append(dict(coverage_target=cov, coverage_emp=r["coverage_emp"],
                                 escalation=r["escalation"], missed_viol=r["missed_viol"],
                                 net_speedup=r["net_speedup"]))
        d[m] = rows
    return d


def crossings(tc):
    d = {"source": "data/tradeoff_curve.json"}
    for m in MODELS:
        cov, missed = first_crossing(tc["records"], m)
        d[m] = dict(first_coverage_below_1pct_missed=cov, missed_at_that_coverage=missed)
    return d


def ceilings(tc):
    d = {"source": "data/tradeoff_curve.json"}
    d["perfect_model_floor_saturation"] = max_qhat_row(tc["records"], "persistence")["floor"]
    esc = {}
    for m in ["ridge", "histgb", "persistence"]:
        esc[m] = max_qhat_row(tc["records"], m)["escalation"]
    d["escalation_at_max_band_width_approaches_P_pred_ge_0.94"] = esc
    return d


def dataset_facts(path):
    df = pd.read_parquet(path)
    n1 = df[(df.outaged_type != "none") & (df.converged)]
    y = n1["min_vm"].to_numpy()
    ab = n1["argmin_bus"].to_numpy()
    vals, counts = np.unique(np.round(y, 9), return_counts=True)
    at_limit = counts[np.abs(vals - LIMIT) < 1e-9]
    atom = float(100.0 * at_limit.max() / len(n1)) if len(at_limit) > 0 else 0.0
    ub, cb = np.unique(ab, return_counts=True)
    order = np.argsort(cb)[::-1][:5]
    top5 = [dict(bus=int(ub[i]), share_pct=round(100.0 * cb[i] / len(n1), 2)) for i in order]
    return dict(source="data/dataset.parquet",
                rows=int(len(df)), scenarios=int(df.scenario_id.nunique()),
                converged_n1_rows=int(len(n1)),
                violation_rate_pct=round(100.0 * float(np.mean(y < LIMIT)), 2),
                boundary_0p94_to_0p945_pct=round(100.0 * float(np.mean((y >= LIMIT) & (y < 0.945))), 2),
                clip_atom_share_pct=round(atom, 2),
                min_vm_min=round(float(y.min()), 4), min_vm_max=round(float(y.max()), 4),
                critical_bus_top5=top5)


def two_by_two(ex):
    cells = {}
    for c in ex["cells"]:
        cells[f"{c['sampling']}_{c['oracle']}"] = c["distinct_buses"]
    samp = [cells["new_old"] - cells["old_old"], cells["new_new"] - cells["old_new"]]
    orac = [cells["old_new"] - cells["old_old"], cells["new_new"] - cells["new_old"]]
    ratio = [round(samp[0] / orac[0], 2), round(samp[1] / orac[1], 2)]
    return dict(source="data/experiment_2x2.json", cells=cells,
                sampling_effect_distinct_buses=samp, oracle_effect_distinct_buses=orac,
                ratio_sampling_over_oracle=ratio, n_scen=ex["n_scen"], seed=ex["seed"])


def print_table(frozen):
    fm = frozen["four_metrics_at_90pct_coverage"]
    print("=== four headline metrics at 90% coverage (data/screener_metrics.json) ===")
    print(f"{'model':8s} {'esc%':>7s} {'cov%':>7s} {'missed%':>8s} {'speedup':>8s}")
    for m in MODELS:
        v = fm[m]
        print(f"{m:8s} {v['escalation']*100:7.1f} {v['coverage']*100:7.1f} "
              f"{v['missed_viol']*100:8.2f} {v['net_speedup']:7.2f}x")

    sp = frozen["safety_operating_points"]
    print("\n=== safety operating points (data/tradeoff_curve.json) ===")
    print(f"{'model':8s} {'covT':>5s} {'covEmp%':>8s} {'esc%':>7s} {'missed%':>8s} {'speedup':>8s}")
    for m in MODELS:
        for r in sp[m]:
            print(f"{m:8s} {r['coverage_target']:5.2f} {r['coverage_emp']*100:8.1f} "
                  f"{r['escalation']*100:7.1f} {r['missed_viol']*100:8.2f} {r['net_speedup']:7.2f}x")

    cr = frozen["crossings_first_below_1pct_missed"]
    print("\n=== first coverage below 1% missed (data/tradeoff_curve.json) ===")
    for m in MODELS:
        print(f"  {m}: cov {cr[m]['first_coverage_below_1pct_missed']:.2f} "
              f"(missed {cr[m]['missed_at_that_coverage']*100:.2f}%)")

    ce = frozen["ceilings"]
    esc = ce["escalation_at_max_band_width_approaches_P_pred_ge_0.94"]
    print("\n=== ceilings (data/tradeoff_curve.json) ===")
    print(f"  perfect-model floor saturation: {ce['perfect_model_floor_saturation']*100:.1f}%")
    print(f"  escalation at max band width (approaches P(pred>=0.94)): "
          f"ridge {esc['ridge']*100:.1f}%, histgb {esc['histgb']*100:.1f}%, "
          f"persistence {esc['persistence']*100:.1f}%")

    dfacts = frozen["dataset_facts"]
    print("\n=== dataset facts (data/dataset.parquet) ===")
    print(f"  rows {dfacts['rows']}, scenarios {dfacts['scenarios']}, converged N-1 "
          f"{dfacts['converged_n1_rows']}")
    print(f"  violation {dfacts['violation_rate_pct']}%, boundary [0.94,0.945) "
          f"{dfacts['boundary_0p94_to_0p945_pct']}%, clip atom {dfacts['clip_atom_share_pct']}%")
    print(f"  min_vm [{dfacts['min_vm_min']}, {dfacts['min_vm_max']}]")
    tops = ", ".join([f"bus {t['bus']} {t['share_pct']}%" for t in dfacts["critical_bus_top5"]])
    print(f"  critical-bus top5: {tops}")

    tt = frozen["two_by_two_v2"]
    print("\n=== 2x2 v2 (data/experiment_2x2.json) ===")
    print(f"  cells {tt['cells']}")
    print(f"  sampling effect {tt['sampling_effect_distinct_buses']}, oracle effect "
          f"{tt['oracle_effect_distinct_buses']}, ratio {tt['ratio_sampling_over_oracle']}")

    ms = frozen["ms_solver"]
    print(f"\n=== ms_solver (data/solve_time.json) ===")
    print(f"  ms_solver {ms['ms_solver']} ms ({ms['basis']}), std {ms['std_ms']} ms")

    gp = frozen["n0_gate_pass_rate_pct"]
    print(f"\n=== N-0 gate pass rate (NOT a committed file) ===")
    print(f"  {gp['value']}%  [{gp['source']}]")


def main():
    sm = load("data/screener_metrics.json")
    tc = load("data/tradeoff_curve.json")
    ex = load("data/experiment_2x2.json")
    st = load("data/solve_time.json")

    frozen = dict(
        four_metrics_at_90pct_coverage=four_metrics(sm),
        safety_operating_points=safety_points(tc),
        crossings_first_below_1pct_missed=crossings(tc),
        ceilings=ceilings(tc),
        dataset_facts=dataset_facts("data/dataset.parquet"),
        two_by_two_v2=two_by_two(ex),
        ms_solver=dict(source="data/solve_time.json", ms_solver=st["ms_solver"],
                       basis=st.get("basis"), std_ms=st.get("std_ms")),
        n0_gate_pass_rate_pct=dict(
            source=("generate_dataset.py run log 2026-07-21 (NOT a committed file): "
                    f"accepted={GEN_ACCEPTED}, rejected={GEN_REJECTED}"),
            value=round(100.0 * GEN_ACCEPTED / (GEN_ACCEPTED + GEN_REJECTED), 2)),
    )
    mf.write_with_manifest(OUT, frozen)
    print_table(frozen)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
