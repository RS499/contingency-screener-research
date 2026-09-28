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

# Fig. 3 (miss-depth histogram) without the deepest-miss annotation: the same data, bins,
# colours, strip and q_hat markers as data/miss_depth_v3.png (scripts/miss_depth_fig.py,
# unchanged), minus the "deepest miss" text, arrow and red triangle markers. The labels are
# NOT corrected here; the pooled depths are exactly those in data/miss_depth_pool.json.
#
# usage: .venv/bin/python scripts/sts_miss_depth_noannot.py OUT_DIR [REF_DIR]

POOL = "data/miss_depth_pool.json"
N2 = "data/sts_n2_label_audit.json"
SCRIPT = "scripts/sts_miss_depth_noannot.py"
PNG_NAME = "sts_miss_depth_noannot.png"
MODELS = ["ridge", "histgb"]
COLORS = {"ridge": "#b8860b", "histgb": "#00798c"}
STRIP = 0.005
XHI = 0.095
BINW = 0.001
FIGSIZE = (3.5, 4.3)
FS_LABEL, FS_ANNOT = 9, 8


def load_pool():
    with open(POOL) as f:
        pool = json.load(f)
    depths = {}
    qmean = {}
    for m in MODELS:
        depths[m] = np.asarray(pool["families"][m]["depths"], dtype=np.float64)
        qmean[m] = pool["families"][m]["stats"]["qhat90_mean"]
    return pool, depths, qmean


def draw(depths, qmean, out_path):
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE, sharex=True)
    edges = np.arange(0, XHI + BINW, BINW)
    for ax, m in zip(axes, MODELS):
        ax.hist(depths[m], bins=edges, color=COLORS[m], linewidth=0)
        ax.set_yscale("log")
        ax.axvspan(0, STRIP, color="#cccccc", alpha=0.25, zorder=0)
        for side in ["top", "right"]:
            ax.spines[side].set_visible(False)
        ax.tick_params(labelsize=FS_ANNOT)
        ax.set_xlim(0, XHI)
        ax.axvline(qmean[m], color="black", lw=1.2, ls="--", zorder=4)
        ax.text(qmean[m] + 0.002, 0.90, f"q̂@0.90 = {qmean[m]:.4f}", transform=ax.get_xaxis_transform(),
                fontsize=FS_ANNOT - 1, color="black", va="top", ha="left")
        ax.set_ylabel(f"{m}\nmiss count (log)", fontsize=FS_LABEL)
    axes[1].set_xlabel("miss depth below the 0.94 pu floor  d = 0.94 − Y  (per unit)",
                       fontsize=FS_LABEL)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")


def n2_note():
    # what the label audit says about the case the old annotation named (read, not recomputed)
    with open(N2) as f:
        w = json.load(f)["worst_case_0p8485"]
    return {"scenario_id": w["scenario_id"], "outaged_type": w["outaged_type"],
            "outaged_idx": w["outaged_idx"], "stored_min_vm": w["stored_min_vm"],
            "corrected_min_vm": w["corrected_min_vm"], "flips_to_safe": w["flips_to_safe"]}


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

    pool, depths, qmean = load_pool()
    draw(depths, qmean, png_path)

    counts = {}
    for m in MODELS:
        counts[m] = {"n_misses": int(len(depths[m])), "max_depth_pu": float(depths[m].max()),
                     "qhat90_mean": qmean[m],
                     "n_deeper_than_0p09": int((depths[m] > 0.09).sum())}
    settings = {
        "task": "Fig. 3 without the deepest-miss annotation (N2 shows that case is a solver artifact)",
        "generating_script": SCRIPT,
        "regeneration_argv": [SCRIPT, "data"],
        "inputs": [{"path": POOL, "sha256": cm.content_hash(POOL)},
                   {"path": N2, "sha256": cm.content_hash(N2)}],
        "outputs": [{"path": png_path, "sha256": cm.content_hash(png_path),
                     "repro": repro(png_path, ref_dir)}],
        "plotting_library": f"matplotlib {matplotlib.__version__}",
        "coverage_target": pool["coverage_target"],
        "look_source": "scripts/miss_depth_fig.py make_hist() with prose off (figsize, colours, "
                       "log y, 0.001 pu bins to 0.095, grey 0.005 pu strip, dashed q_hat line and "
                       "its value label) copied, not imported; that file is unchanged",
        "figsize_in": list(FIGSIZE), "dpi": 300, "bin_width": BINW, "x_max": XHI, "strip": STRIP,
        "removed_vs_miss_depth_v3": [
            "annotation 'deepest miss 0.0915 pu' with arrow (ridge panel)",
            "red triangle marker at d = 0.09146 in both panels",
        ],
        "kept_in_image_text": "axis labels, tick labels, and the per-panel q_hat value label",
        "labels_not_corrected": "the pooled depths are the stored pandapower labels; the bin that "
                                "holds the artifact case is still drawn. A corrected-label version "
                                "waits on the author's N2b decision.",
        "per_model": counts,
        "artifact_case_per_n2": n2_note(),
        "no_new_solves": "re-plotted from data/miss_depth_pool.json; no fit or AC solve",
    }
    man = cm.build_manifest(png_path, {}, settings)
    with open(mf.manifest_path(png_path), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {mf.manifest_path(png_path)}")


if __name__ == "__main__":
    main()
