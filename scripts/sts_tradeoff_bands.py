import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, HERE)
import manifest as mf
import classical_manifest as cm

# Fig. 2 with error bars: the same escalation / missed-violation curves as
# data/tradeoff_hero_col_v2.png (feasibility/paper_hero.py, unchanged), plus a +-1 std band
# (population std over 5 seeds) around all four curves, from data/tradeoff_curve_v2.json.
#
# usage: .venv/bin/python scripts/sts_tradeoff_bands.py OUT_DIR [REF_DIR]

CURVE = "data/tradeoff_curve_v2.json"
TUNED = "data/tuned_metrics.json"
SCRIPT = "scripts/sts_tradeoff_bands.py"
PNG_NAME = "sts_tradeoff_bands.png"
JSON_NAME = "sts_tradeoff_bands.json"
MODELS = ["ridge", "histgb"]
COLORS = {"ridge": "#b8860b", "histgb": "#00798c"}
FS_LABEL, FS_TICK, FS_LEG, FS_ANNOT = 9, 7, 6, 7
FIGSIZE = (3.5, 2.7)
ESC_ALPHA = 0.20
MISS_ALPHA = 0.12


def rows_for(records, model):
    rows = [r for r in records if r["model"] == model]
    order = np.argsort([r["coverage_target"] for r in rows])
    return [rows[i] for i in order]


def first_safe_coverage(rows):
    safe = [r["coverage_target"] for r in rows if r["missed_viol"] < 0.01]
    if len(safe) == 0:
        return None
    return min(safe)


def draw(records, out_path):
    fig, axL = plt.subplots(figsize=FIGSIZE)
    axR = axL.twinx()
    ymax_esc = 0.0
    for i, model in enumerate(MODELS):
        rows = rows_for(records, model)
        cov = np.array([r["coverage_target"] for r in rows])
        esc = np.array([r["escalation"] * 100 for r in rows])
        esc_sd = np.array([r["escalation_std"] * 100 for r in rows])
        mis = np.array([r["missed_viol"] * 100 for r in rows])
        mis_sd = np.array([r["missed_viol_std"] * 100 for r in rows])
        ymax_esc = max(ymax_esc, esc.max())
        axL.fill_between(cov, esc - esc_sd, esc + esc_sd, color=COLORS[model], alpha=ESC_ALPHA,
                         linewidth=0)
        # a missed rate cannot be negative, so the lower edge of its band stops at 0
        axR.fill_between(cov, np.clip(mis - mis_sd, 0.0, None), mis + mis_sd, color=COLORS[model],
                         alpha=MISS_ALPHA, linewidth=0)
        axL.plot(cov, esc, "-", lw=1.6, color=COLORS[model], label=f"{model} escalation")
        axR.plot(cov, mis, ":", lw=1.4, color=COLORS[model], label=f"{model} missed")
        c = first_safe_coverage(rows)
        if c is not None:
            axL.axvline(c, color=COLORS[model], lw=1.0, ls="-.")
            side = "right"
            dx = -0.003
            if i == 1:
                side = "left"
                dx = 0.003
            axL.text(c + dx, ymax_esc * 0.05, f"{c:.2f}", ha=side, va="bottom",
                     fontsize=FS_ANNOT, color=COLORS[model])

    axR.axhline(1.0, color="grey", lw=0.9, ls=":")
    axR.text(0.70, 1.0, "1% missed", ha="left", va="bottom", fontsize=FS_ANNOT - 1, color="grey")
    axL.set_xlim(0.70, 0.99)
    axL.set_xlabel("target coverage", fontsize=FS_LABEL)
    axL.set_ylabel("escalation (%)", fontsize=FS_LABEL)
    axR.set_ylabel("missed-violation (% of true violations)", fontsize=FS_LABEL)
    axL.tick_params(labelsize=FS_TICK)
    axR.tick_params(labelsize=FS_TICK)
    axL.grid(alpha=0.3)
    lL, nL = axL.get_legend_handles_labels()
    lR, nR = axR.get_legend_handles_labels()
    axL.legend(lL + lR, nL + nR, fontsize=FS_LEG, loc="upper left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")


def values(records):
    out = {}
    for model in MODELS:
        rows = rows_for(records, model)
        pts = []
        for r in rows:
            pts.append({
                "coverage_target": r["coverage_target"],
                "escalation": r["escalation"], "escalation_std": r["escalation_std"],
                "missed_viol": r["missed_viol"], "missed_viol_std": r["missed_viol_std"],
                "missed_band_lower_clipped_at_0": bool(r["missed_viol"] - r["missed_viol_std"] < 0),
            })
        out[model] = {"first_sub_1pct_missed_coverage": first_safe_coverage(rows), "points": pts}
    return out


def m2_configs():
    # hyperparameters of the M2 surrogates whose per-seed sweeps the curve aggregates
    with open(TUNED) as f:
        tm = json.load(f)
    out = {}
    for r in tm["records"]:
        if r["metric"] == "m2":
            out[f"{r['family']}_seed{r['seed']}"] = r["config"]
    return out


def repro(path, ref_dir):
    if ref_dir == "":
        return "not checked in this run"
    ref = os.path.join(ref_dir, os.path.basename(path))
    return {"compared_with": ref, "same_sha256": cm.content_hash(ref) == cm.content_hash(path)}


def main():
    out_dir = sys.argv[1]
    ref_dir = ""
    if len(sys.argv) > 2:
        ref_dir = sys.argv[2]
    png_path = os.path.join(out_dir, PNG_NAME)
    json_path = os.path.join(out_dir, JSON_NAME)

    with open(CURVE) as f:
        curve = json.load(f)
    out = {
        "source": CURVE,
        "std_convention": curve["std_convention"],
        "units": "fractions (0-1); the figure plots %",
        "band": "mean +- 1 std for all four curves; missed band lower edge clipped at 0",
        "models": values(curve["records"]),
    }
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {json_path}")
    draw(curve["records"], png_path)

    settings = {
        "task": "STS Fig. 2 with +-1 std bands (ledger P-005)",
        "generating_script": SCRIPT,
        "regeneration_argv": [SCRIPT, "data"],
        "inputs": [{"path": CURVE, "sha256": cm.content_hash(CURVE)},
                   {"path": TUNED, "sha256": cm.content_hash(TUNED)}],
        "outputs": [{"path": json_path, "sha256": cm.content_hash(json_path),
                     "repro": repro(json_path, ref_dir)},
                    {"path": png_path, "sha256": cm.content_hash(png_path),
                     "repro": repro(png_path, ref_dir)}],
        "plotting_library": f"matplotlib {matplotlib.__version__}",
        "look_source": "feasibility/paper_hero.py (figsize, fonts, colours, dash-dot first-sub-1% "
                       "markers, 1% guide line, legend) copied, not imported; that file is unchanged",
        "figsize_in": list(FIGSIZE), "dpi": 300,
        "band_alpha": {"escalation": ESC_ALPHA, "missed": MISS_ALPHA},
        "dual_axis_note": "kept the twin y axis of the original Fig. 2 on request (same content and look)",
        "no_new_solves": "re-plotted from data/tradeoff_curve_v2.json; no fit or AC solve",
    }
    man = cm.build_manifest(json_path, out, settings, m2_configs())
    with open(mf.manifest_path(json_path), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {mf.manifest_path(json_path)}")


if __name__ == "__main__":
    main()
