
import json

import numpy as np
import pandas as pd

DATA = "data/dataset.parquet"
OUT = "data/quintile_boundary_mass.json"
MANIFEST = "data/quintile_boundary_mass.manifest.json"

LIMIT = 0.94
STRIP_HI = 0.945

CASE118_FROZEN_BOUNDARY_PCT = 56.86

def boundary_mass_pct(min_vm):
    return float(100.0 * np.mean((min_vm >= LIMIT) & (min_vm < STRIP_HI)))


def violation_pct(min_vm):
    return float(100.0 * np.mean(min_vm < LIMIT))


def quintile_analysis(df):
    base = df.groupby("scenario_id")["n0_min_vm"].first()
    q = pd.Series(pd.qcut(base, 5, labels=False), index=base.index)

    n1 = df[(df.outaged_type != "none") & (df.converged)].copy()
    n1["quintile"] = n1["scenario_id"].map(q)

    rows = []
    for k in range(5):
        bases_k = base[q == k]
        mv = n1.loc[n1["quintile"] == k, "min_vm"].to_numpy()
        rows.append(dict(
            quintile=k,
            n_bases=int(len(bases_k)),
            base_vm_min=round(float(bases_k.min()), 5),
            base_vm_max=round(float(bases_k.max()), 5),
            base_vm_mean=round(float(bases_k.mean()), 5),
            n1_rows=int(mv.size),
            boundary_mass_pct=round(boundary_mass_pct(mv), 2),
            violation_pct=round(violation_pct(mv), 2),
        ))
    return rows


def main():
    df = pd.read_parquet(DATA, columns=["scenario_id", "n0_min_vm", "outaged_type",
                                        "converged", "min_vm"])
    rows = quintile_analysis(df)

    top = rows[-1]
    means = np.array([r["base_vm_mean"] for r in rows])
    bmass = np.array([r["boundary_mass_pct"] for r in rows])
    vrate = np.array([r["violation_pct"] for r in rows])

    out = {
        "what": "case118 bases split into equal-count quintiles by n0_min_vm; boundary mass and "
                "violation rate recomputed over each quintile's own converged N-1 rows.",
        "purpose": "isolate the FILTER effect (base tightness against 0.94) from the NETWORK "
                   "effect, within a single network (case118).",
        "boundary_definition_source": "feasibility/freeze_poster_numbers.py:dataset_facts (line 121); "
                                      "mirrored feasibility/case57_gonogo.py:152",
        "boundary_strip": [LIMIT, STRIP_HI],
        "n_bases_total": int(df.scenario_id.nunique()),
        "quintiles_low_to_high": rows,
        "step2_base_vm_mean_vs_boundary_mass": {
            "base_vm_mean": [round(float(x), 5) for x in means],
            "boundary_mass_pct": [round(float(x), 2) for x in bmass],
            "spearman_rank_corr": round(float(np.corrcoef(
                np.argsort(np.argsort(means)), np.argsort(np.argsort(bmass)))[0, 1]), 4),
        },
        "step3_top_quintile_boundary_mass": {
            "top_quintile_base_range": [top["base_vm_min"], top["base_vm_max"]],
            "top_quintile_boundary_mass_pct": top["boundary_mass_pct"],
            "case118_frozen_boundary_mass_pct": CASE118_FROZEN_BOUNDARY_PCT,
        },
        "step4_violation_rate_by_quintile": {
            "base_vm_mean": [round(float(x), 5) for x in means],
            "violation_pct": [round(float(x), 2) for x in vrate],
            "spearman_rank_corr": round(float(np.corrcoef(
                np.argsort(np.argsort(means)), np.argsort(np.argsort(vrate)))[0, 1]), 4),
        },
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)

    manifest = {
        "python": "3.13",
        "generated_by": "feasibility/quintile_boundary_mass.py",
        "inputs": {"dataset": DATA},
        "boundary_definition_source": out["boundary_definition_source"],
        "boundary_strip": [LIMIT, STRIP_HI],
        "packages": {"numpy": np.__version__, "pandas": pd.__version__},
        "note": "Zero new solves; read-only over data/dataset.parquet. No model, no solver.",
    }
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"wrote {OUT} and {MANIFEST}")
    print(f"boundary strip [{LIMIT}, {STRIP_HI}) from {out['boundary_definition_source']}")
    print(f"{'quint':>5} {'n_base':>6} {'base_range':>18} {'base_mean':>9} "
          f"{'n1_rows':>8} {'bmass%':>7} {'viol%':>7}")
    for r in rows:
        rng = f"[{r['base_vm_min']:.5f},{r['base_vm_max']:.5f}]"
        print(f"{r['quintile']:>5} {r['n_bases']:>6} {rng:>18} {r['base_vm_mean']:>9.5f} "
              f"{r['n1_rows']:>8} {r['boundary_mass_pct']:>7.2f} {r['violation_pct']:>7.2f}")
    print(f"top quintile boundary {top['boundary_mass_pct']:.2f}%")


if __name__ == "__main__":
    main()
