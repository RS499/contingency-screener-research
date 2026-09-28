import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sts_manifest as sm

# Screening-limit sweep at coverage target 0.90: escalation rate and boundary mass
# [L, L + q_hat) against the screening limit L, seed mean with a +-1 std band, for the M2
# ridge and histgb surrogates. Re-plotted from data/sweep_results_long.parquet (no refit).
#
# usage: .venv/bin/python scripts/sts_limit_sweep.py OUT_DIR [REF_DIR]

SRC = "data/sweep_results_long.parquet"
SRC_MANIFEST = "data/sweep_results_long.manifest.json"
CURVE_V2 = "data/tradeoff_curve_v2.json"
TUNED = "data/tuned_metrics.json"
SCRIPT = "scripts/sts_limit_sweep.py"
PNG_NAME = "sts_limit_sweep.png"
JSON_NAME = "sts_limit_sweep.json"

TARGET = 0.90
STUDY_LIMIT = 0.94
MODELS = ["ridge", "histgb"]
COLORS = {"ridge": "#b8860b", "histgb": "#00798c"}
FIGSIZE = (3.5, 4.3)
FS_LABEL, FS_TICK = 9, 8
BAND_ALPHA = 0.25


def per_limit(d):
    # seed mean and population std (ddof=0) of each quantity, per model and limit L
    s = d[np.isclose(d["target"], TARGET)]
    out = {}
    for m in MODELS:
        rows = []
        x = s[s["model"] == m]
        for L in sorted(x["L"].unique()):
            y = x[np.isclose(x["L"], L)]
            rows.append({
                "L": round(float(L), 3),
                "n_seeds": int(y["seed"].nunique()),
                "escalation_mean": float(y["esc_observed"].mean()),
                "escalation_std": float(y["esc_observed"].std(ddof=0)),
                "boundary_mass_mean": float(y["boundary_mass"].mean()),
                "boundary_mass_std": float(y["boundary_mass"].std(ddof=0)),
                "q_hat_mean": float(y["q_hat"].mean()),
                "violation_rate_mean": float(y["violation_rate"].mean()),
            })
        out[m] = rows
    return out


def row_at(rows, L):
    for r in rows:
        if abs(r["L"] - L) < 1e-9:
            return r
    return None


def crosscheck_v2(curves):
    # the sweep's L = 0.94 row must reproduce the committed v2 curve at the same target
    with open(CURVE_V2) as f:
        recs = json.load(f)["records"]
    out = {}
    for m in MODELS:
        ref = None
        for r in recs:
            if r["model"] == m and abs(r["coverage_target"] - TARGET) < 1e-9:
                ref = r
        mine = row_at(curves[m], STUDY_LIMIT)
        out[m] = {
            "sweep_escalation_mean": mine["escalation_mean"],
            "sweep_escalation_std": mine["escalation_std"],
            "tradeoff_curve_v2_escalation": ref["escalation"],
            "tradeoff_curve_v2_escalation_std": ref["escalation_std"],
            "abs_diff": abs(mine["escalation_mean"] - ref["escalation"]),
        }
    return out


def summary(curves):
    out = {}
    for m in MODELS:
        low = [r["escalation_mean"] for r in curves[m] if r["L"] <= 0.936 + 1e-9]
        esc = np.array([r["escalation_mean"] for r in curves[m]])
        top = curves[m][int(np.argmax(esc))]
        out[m] = {
            "escalation_mean_at_0p940": row_at(curves[m], 0.940)["escalation_mean"],
            "escalation_std_at_0p940": row_at(curves[m], 0.940)["escalation_std"],
            "escalation_mean_at_0p950": row_at(curves[m], 0.950)["escalation_mean"],
            "escalation_std_at_0p950": row_at(curves[m], 0.950)["escalation_std"],
            "escalation_mean_min_for_L_le_0p936": float(min(low)),
            "escalation_mean_max_for_L_le_0p936": float(max(low)),
            "L_of_max_escalation_mean": top["L"],
            "max_escalation_mean": top["escalation_mean"],
        }
    return out


def m2_configs():
    with open(TUNED) as f:
        tm = json.load(f)
    out = {}
    for r in tm["records"]:
        if r["metric"] == "m2":
            out[f"{r['family']}_seed{r['seed']}"] = r["config"]
    return out


def draw(curves, out_path):
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE, sharex=True)
    keys = [("escalation", "escalation rate (%)"),
            ("boundary_mass", "boundary mass\n" + r"in $[L,\,L+\hat{q})$ (%)")]
    for ax, key_label in zip(axes, keys):
        key, label = key_label
        for m in MODELS:
            L = np.array([r["L"] for r in curves[m]])
            mean = 100.0 * np.array([r[key + "_mean"] for r in curves[m]])
            std = 100.0 * np.array([r[key + "_std"] for r in curves[m]])
            ax.fill_between(L, mean - std, mean + std, color=COLORS[m], alpha=BAND_ALPHA,
                            linewidth=0)
            ax.plot(L, mean, color=COLORS[m], lw=1.5, label=m)
        ax.axvline(STUDY_LIMIT, color="black", lw=0.8, zorder=0,
                   label=f"$L$ = {STUDY_LIMIT:.2f} pu")
        ax.set_ylabel(label, fontsize=FS_LABEL)
        ax.set_ylim(bottom=0)
        ax.tick_params(labelsize=FS_TICK)
        ax.grid(True, color="#e5e5e5", lw=0.5)
        for side in ["top", "right"]:
            ax.spines[side].set_visible(False)
    axes[0].legend(fontsize=FS_TICK - 1, frameon=False, loc="upper left")
    axes[1].set_xlabel("screening limit $L$ (per unit)", fontsize=FS_LABEL)
    axes[1].set_xlim(curves[MODELS[0]][0]["L"], curves[MODELS[0]][-1]["L"])
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")


def main():
    out_dir = sys.argv[1]
    ref_dir = ""
    if len(sys.argv) > 2:
        ref_dir = sys.argv[2]
    png_path = os.path.join(out_dir, PNG_NAME)
    json_path = os.path.join(out_dir, JSON_NAME)

    with open(SRC_MANIFEST) as f:
        src_man = json.load(f)
    src_sha_ok = src_man["content_sha256"] == sm.sha256_of(SRC)

    d = pd.read_parquet(SRC)
    curves = per_limit(d)
    out = {
        "source": SRC,
        "source_sha256_matches_its_manifest": src_sha_ok,
        "coverage_target": TARGET,
        "study_limit": STUDY_LIMIT,
        "boundary_mass_definition": "share of test outcomes Y with L <= Y < L + q_hat, q_hat the "
                                    "per-seed conformal quantile at the coverage target (column "
                                    "boundary_mass of the source parquet; model- and seed-specific)",
        "std_convention": "population std (ddof=0) over the 5 held-out splits",
        "units": "rates are fractions (0-1); the figure plots them as %",
        "summary": summary(curves),
        "crosscheck_at_0p94_vs_tradeoff_curve_v2": crosscheck_v2(curves),
        "curves": curves,
    }
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {json_path}")
    draw(curves, png_path)

    params = {
        "coverage_target": TARGET, "study_limit_marked": STUDY_LIMIT, "models": MODELS,
        "selection": "M2 (gate-aware) surrogates, as in the source sweep",
        "limit_grid": "0.900 to 0.955 step 0.001 (56 limits), as stored in the source parquet",
        "boundary_mass_choice": "[L, L + q_hat): the only boundary-mass column the parquet holds; "
                                "[L, L + 0.005) is not stored there",
        "band": "seed mean +- 1 population std (ddof=0), 5 seeds",
        "colors": COLORS, "figsize_in": list(FIGSIZE), "dpi": 300,
        "font_sizes": {"label": FS_LABEL, "tick": FS_TICK}, "band_alpha": BAND_ALPHA,
        "in_image_text": "axis labels, tick labels and legend only; no title, no annotation",
        "upstream_model_hyperparameters_m2": m2_configs(),
        "upstream_generator": "scripts/limit_sweep.py (wrote the source parquet)",
    }
    inputs = [SRC, SRC_MANIFEST, CURVE_V2, TUNED]
    argv = [SCRIPT, "data"]
    man = sm.build_manifest([json_path, png_path], SCRIPT, argv, inputs, params, ref_dir)
    sm.write_manifest(man, json_path)


if __name__ == "__main__":
    main()
