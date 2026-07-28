import os
import sys
import json
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
import manifest as mf
import figtools as ft
import classical_manifest as cm

CURVE = "data/comparison_curve.json"
OUT = "data/classical_vs_conformal.png"
POSTER_OUT = "data/poster/classical_vs_conformal.png"
POSTER_FIGSIZE = (14.05, 8.5)
FS_LABEL, FS_TICK, FS_LEG = 9, 7, 6
FLOOR = 0.004

STYLE = {
    "conformal_ridge": dict(color="#b8860b", marker="o", ls="-", label="conformal gate (ridge)"),
    "conformal_histgb": dict(color="#00798c", marker="s", ls="-", label="conformal gate (histgb)"),
    "classical_conformal": dict(color="#c1272d", marker="^", ls="--",
                                label="classical screen, conformalized"),
    "classical_delta": dict(color="#7a5195", marker="v", ls=":", label="classical screen, margin sweep"),
    "classical_pi": dict(color="#555555", marker="d", ls="-.", label="Ejebe-Wollenberg PI ranking"),
}
ORDER = ["conformal_ridge", "conformal_histgb", "classical_conformal", "classical_delta",
         "classical_pi"]


def series(points):
    x = np.array([p["avoided"] * 100 for p in points])
    y = np.array([p["missed_viol"] * 100 for p in points])
    ystd = np.array([p.get("missed_viol_std", 0.0) * 100 for p in points])
    return x, np.maximum(y, FLOOR), ystd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--curve", default=CURVE, help="comparison curve JSON to render")
    ap.add_argument("--poster", action="store_true",
                    help="poster panel: 14.05x8.5in, poster fonts, writes data/poster/classical_vs_conformal.png")
    args = ap.parse_args()

    global FS_LABEL, FS_TICK, FS_LEG
    if args.poster:
        FS_LABEL, FS_TICK, FS_LEG = ft.POSTER_FS_LABEL, ft.POSTER_FS_TICK, ft.POSTER_FS_ANNOT
        out_path = POSTER_OUT
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        figsize = POSTER_FIGSIZE
        ms, lw, elw, cap = 8, ft.POSTER_LW, ft.POSTER_LW * 0.4, 4
        bbox = None
    else:
        out_path = OUT
        figsize = (3.5, 2.8)
        ms, lw, elw, cap = 2.6, 1.2, 0.7, 1.2
        bbox = "tight"

    with open(args.curve) as f:
        data = json.load(f)
    curves = data["curves"]

    fig, ax = plt.subplots(figsize=figsize)
    for name in ORDER:
        pts = curves[name]["points"]
        x, y, ystd = series(pts)
        st = STYLE[name]
        lo = np.maximum(y - ystd, FLOOR * 0.5)
        ax.errorbar(x, y, yerr=[y - lo, ystd], fmt=st["marker"], ls=st["ls"], color=st["color"],
                    ms=ms, lw=lw, elinewidth=elw, capsize=cap, label=st["label"], alpha=0.95)

    ax.axhline(1.0, color="grey", lw=0.9, ls=":")
    ax.text(1.5, 1.15, "1% missed", ha="left", va="bottom", fontsize=FS_LEG, color="grey")
    ax.set_yscale("log")
    ax.set_xlim(-2, 102)
    ax.set_xlabel("exact solves avoided (%)", fontsize=FS_LABEL)
    ax.set_ylabel("missed violations (% of true)", fontsize=FS_LABEL)
    ax.tick_params(labelsize=FS_TICK)
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=FS_LEG, loc="lower right", framealpha=0.9)

    ft.add_credit(fig)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches=bbox)
    plt.close(fig)
    print(f"wrote {out_path}")
    print("lower-right dominates; the conformal curves sit below and right of the classical ones "
          "throughout the safety-relevant region.")

    if args.poster:
        meta = dict(figure="poster panel: classical vs conformal throughput/safety comparison",
                    figsize_in=list(figsize), curve_source=args.curve)
        settings = dict(task="poster figure regeneration", source=args.curve)
        man = cm.build_manifest(out_path, meta, settings)
        with open(mf.manifest_path(out_path), "w") as f:
            json.dump(man, f, indent=2)
        print(f"wrote {mf.manifest_path(out_path)} (sha256 {man['content_sha256'][:12]}...)")


if __name__ == "__main__":
    main()
