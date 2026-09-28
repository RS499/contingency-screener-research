import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sts_manifest as sm

# Cross-network check of the escalation approximation: measured escalation against
# rho * q_hat (rho = boundary mass / strip width) for every network and coverage target in
# data/netstudy2/cross_2a_points.json. Log-log scatter with the identity line y = x.
#
# usage: .venv/bin/python scripts/sts_crossnet_scatter.py OUT_DIR [REF_DIR]

SRC = "data/netstudy2/cross_2a_points.json"
SRC_MANIFEST = "data/netstudy2/cross_2a_points.manifest.json"
SUMMARY = "data/netstudy2/summary.json"
SCRIPT = "scripts/sts_crossnet_scatter.py"
PNG_NAME = "sts_crossnet_scatter.png"
JSON_NAME = "sts_crossnet_scatter.json"

MODELS = ["ridge", "histgb"]
MARKERS = {"ridge": "o", "histgb": "^"}
# Okabe-Ito blue / vermillion / green / orange plus Tol wine; checked with the dataviz
# palette validator (all-pairs CVD separation >= 8.6, normal-vision floor 15.6)
NET_COLORS = ["#0072B2", "#D55E00", "#009E73", "#E69F00", "#882255"]
FIGSIZE = (3.5, 3.9)
FS_LABEL, FS_TICK = 9, 8
MARKER_SIZE = 20
LOW_RATIO = 0.5


def load_points():
    with open(SRC) as f:
        cp = json.load(f)
    return cp


def check_rho(cp):
    # rho * q_hat stored in the file must equal boundary_mass / strip_width * q_hat
    worst = 0.0
    for p in cp["points"]:
        x = p["boundary_mass"] / cp["strip_width"] * p["q_hat"]
        worst = max(worst, abs(x - p["rho_times_qhat"]))
    return worst


def arrays(points):
    x = np.array([p["rho_times_qhat"] for p in points])
    y = np.array([p["escalation"] for p in points])
    return x, y


def correlations(points):
    x, y = arrays(points)
    return {
        "n_points": int(len(x)),
        "pearson_r_linear": float(np.corrcoef(x, y)[0, 1]),
        "pearson_r_loglog": float(np.corrcoef(np.log(x), np.log(y))[0, 1]),
    }


def group_stats(cp):
    out = []
    for net in cp["networks"]:
        for m in MODELS:
            sel = [p for p in cp["points"] if p["network"] == net and p["family"] == m]
            if len(sel) == 0:
                continue
            x, y = arrays(sel)
            ratio = y / x
            out.append({
                "network": net,
                "family": m,
                "n_points": int(len(sel)),
                "boundary_mass": float(sel[0]["boundary_mass"]),
                "coverage_targets": [p["coverage_target"] for p in sel],
                "median_ratio_esc_over_rho_qhat": float(np.median(ratio)),
                "min_ratio": float(ratio.min()),
                "max_ratio": float(ratio.max()),
                "n_ratio_below_0p5": int((ratio < LOW_RATIO).sum()),
                "n_rho_qhat_above_1": int((x > 1.0).sum()),
                "source": sel[0]["source"],
            })
    return out


def flag_group(groups, cp):
    # the group whose median ratio is furthest from 1 on a log scale
    dist = np.array([abs(np.log(g["median_ratio_esc_over_rho_qhat"])) for g in groups])
    g = groups[int(np.argmax(dist))]
    rest = [p for p in cp["points"]
            if not (p["network"] == g["network"] and p["family"] == g["family"])]
    return {
        "rule": "group (network, family) whose median escalation / (rho * q_hat) is furthest "
                "from 1 in |log ratio|",
        "network": g["network"],
        "family": g["family"],
        "median_ratio": g["median_ratio_esc_over_rho_qhat"],
        "n_points": g["n_points"],
        "n_ratio_below_0p5": g["n_ratio_below_0p5"],
        "sensitivity_without_this_group": correlations(rest),
    }


def draw(cp, out_path):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    x_all, y_all = arrays(cp["points"])
    lo = 0.8 * min(x_all.min(), y_all.min())
    hi = 1.25 * max(x_all.max(), y_all.max())
    ax.plot([lo, hi], [lo, hi], color="0.35", lw=0.9, ls="--", zorder=1)
    for i, net in enumerate(cp["networks"]):
        for m in MODELS:
            sel = [p for p in cp["points"] if p["network"] == net and p["family"] == m]
            x, y = arrays(sel)
            ax.scatter(x, y, s=MARKER_SIZE, marker=MARKERS[m], color=NET_COLORS[i],
                       edgecolors="white", linewidths=0.4, zorder=2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$\rho \cdot \hat{q}$ (boundary density $\times$ band width)", fontsize=FS_LABEL)
    ax.set_ylabel("measured escalation rate", fontsize=FS_LABEL)
    ax.tick_params(labelsize=FS_TICK)
    ax.grid(True, which="major", color="#e5e5e5", lw=0.5)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)

    handles = []
    for i, net in enumerate(cp["networks"]):
        handles.append(Line2D([], [], color=NET_COLORS[i], marker="s", ls="none", ms=5, label=net))
    for m in MODELS:
        handles.append(Line2D([], [], color="0.35", marker=MARKERS[m], ls="none", ms=5, label=m))
    handles.append(Line2D([], [], color="0.35", ls="--", lw=0.9, label="y = x"))
    ax.legend(handles=handles, fontsize=FS_TICK - 1, frameon=False, ncol=2,
              loc="upper center", bbox_to_anchor=(0.5, -0.2))
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

    cp = load_points()
    with open(SRC_MANIFEST) as f:
        src_man = json.load(f)
    with open(SUMMARY) as f:
        summ = json.load(f)
    groups = group_stats(cp)
    out = {
        "source": SRC,
        "source_sha256_matches_its_manifest": src_man["content_sha256"] == sm.sha256_of(SRC),
        "source_n_points_field": cp["n_points"],
        "strip_width": cp["strip_width"],
        "density_definition": cp["density_definition"],
        "max_abs_rho_qhat_recompute_error": check_rho(cp),
        "x": "rho_times_qhat as stored in the source (= boundary_mass / strip_width * q_hat)",
        "y": "escalation as stored in the source (seed-mean measured escalation rate)",
        "all_points": correlations(cp["points"]),
        "per_network_family": groups,
        "flagged_group": flag_group(groups, cp),
        "netstudy2_cross_network_context": summ["cross_network"],
    }
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {json_path}")
    draw(cp, png_path)

    params = {
        "axes": "log-log, equal aspect, limits [0.8 * min, 1.25 * max] over both variables",
        "identity_line": "y = x, dashed",
        "network_colors": dict(zip(cp["networks"], NET_COLORS)),
        "model_markers": MARKERS,
        "marker_size_pt2": MARKER_SIZE,
        "figsize_in": list(FIGSIZE), "dpi": 300,
        "font_sizes": {"label": FS_LABEL, "tick": FS_TICK},
        "correlation": "numpy.corrcoef (Pearson) on raw values and on natural-log values",
        "low_ratio_threshold": LOW_RATIO,
        "in_image_text": "axis labels, tick labels and legend only; no title, no annotation",
        "upstream": "points assembled by scripts/netstudy2_cross.py phase_2a() from each "
                    "network's frozen results (inner-split M2 selection); q_hat and escalation are "
                    "seed means; the point 'source' field names the file",
    }
    inputs = [SRC, SRC_MANIFEST, SUMMARY]
    argv = [SCRIPT, "data"]
    man = sm.build_manifest([json_path, png_path], SCRIPT, argv, inputs, params, ref_dir)
    sm.write_manifest(man, json_path)


if __name__ == "__main__":
    main()
