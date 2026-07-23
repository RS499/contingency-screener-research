import os, sys, json, argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import manifest as mf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import classical_manifest as cm
import figtools as ft

LIMIT = 0.94
STRIP_HI = 0.945
DATA = "data/dataset.parquet"
FROZEN = "data/frozen_poster_numbers.json"
OUT = "data/boundary_mass_hist.png"
POSTER_OUT = "data/poster/boundary_mass_hist.png"
POSTER_FIGSIZE = (7.80, 7.0)

LO, HI, BINW = 0.715, 0.965, 0.001
VIEW_LO = 0.87

COLORS = {"persistence": "#d1495b", "ridge": "#b8860b", "histgb": "#00798c"}
C_VIOL = COLORS["persistence"]
C_SAFE = COLORS["histgb"]
C_STRIP = COLORS["ridge"]

FS_LABEL, FS_ANNOT = 9, 8


def read_boundary_share(path):
    with open(path) as f:
        d = json.load(f)
    return float(d["dataset_facts"]["boundary_0p94_to_0p945_pct"])


def load_min_vm(path):
    df = pd.read_parquet(path, columns=["min_vm", "converged", "outaged_type"])
    n1 = df[(df["outaged_type"] != "none") & (df["converged"])]
    return n1["min_vm"].to_numpy(np.float64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--poster", action="store_true",
                    help="poster panel: 7.80x7.0in, poster fonts, writes data/poster/boundary_mass_hist.png")
    args = ap.parse_args()

    global FS_LABEL, FS_ANNOT
    if args.poster:
        FS_LABEL, FS_ANNOT = ft.POSTER_FS_LABEL, ft.POSTER_FS_TICK
        out_path = POSTER_OUT
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        figsize = POSTER_FIGSIZE
        bbox = "tight"
    else:
        out_path = OUT
        figsize = (3.5, 2.6)
        bbox = "tight"

    boundary_pct = read_boundary_share(FROZEN)
    v = load_min_vm(DATA)

    edges = np.arange(LO, HI + BINW / 2, BINW)
    counts, _ = np.histogram(v, bins=edges)
    share = 100.0 * counts / len(v)
    left = edges[:-1]
    bar_color = [C_VIOL if e < LIMIT - 1e-9 else C_SAFE for e in left]

    tallest = float(share.max())
    below = 100.0 * float(np.mean(v < VIEW_LO))

    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(left, share, width=BINW, align="edge", color=bar_color, linewidth=0)

    ax.axvspan(LIMIT, STRIP_HI, color=C_STRIP, alpha=0.20, zorder=0)
    ymax = tallest
    ax.annotate(f"{boundary_pct:.1f}% of cases fall in this\n0.005 pu strip, yet the tallest\n"
                f"0.001 pu bin holds just {tallest:.1f}%",
                xy=((LIMIT + STRIP_HI) / 2, ymax * 0.5),
                xytext=(0.902, ymax * 0.72), ha="center", va="center", fontsize=FS_ANNOT,
                color="#7a5c00",
                arrowprops=dict(arrowstyle="->", color="#7a5c00", lw=0.8))

    ax.axvline(LIMIT, color="black", lw=1.5, zorder=3)
    ax.text(LIMIT - 0.0015, ymax * 0.99, "under-voltage limit (0.94 pu)", ha="right", va="top",
            fontsize=FS_ANNOT, color="black")

    ax.text(VIEW_LO + 0.001, ymax * 0.13, f"{below:.1f}% of cases fall\nbelow 0.870 pu (not shown)",
            ha="left", va="bottom", fontsize=FS_ANNOT - 1, color="#555555")

    ax.set_xlabel("minimum bus voltage after a contingency (per unit)", fontsize=FS_LABEL)
    ax.set_ylabel("share of contingency cases (%)", fontsize=FS_LABEL)
    ax.set_xlim(VIEW_LO, HI)
    ax.tick_params(labelsize=FS_ANNOT)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    ft.add_credit(fig)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches=bbox)
    plt.close(fig)
    if args.poster:
        ft.pad_to_exact(out_path, figsize)
    print(f"wrote {out_path}")
    print(f"cases={len(v)}  hist=[{LO},{HI}]  view=[{VIEW_LO},{HI}]  bin={BINW} pu  bins={len(edges)-1}")
    print(f"boundary share read = {boundary_pct} % from {FROZEN} "
          f"(dataset_facts/boundary_0p94_to_0p945_pct)")
    print(f"tallest bar = {share.max():.2f}% at min_vm in "
          f"[{left[share.argmax()]:.3f},{left[share.argmax()]+BINW:.3f})")
    print(f"below view (< {VIEW_LO}) = {below:.2f}% of cases (noted on figure)")

    if args.poster:
        meta = dict(figure="poster panel: boundary-mass histogram", figsize_in=list(figsize),
                    boundary_pct=boundary_pct, tallest_bar_pct=float(share.max()),
                    source=DATA, model_independent=True)
        settings = dict(task="poster figure regeneration", source=DATA, frozen_source=FROZEN)
        man = cm.build_manifest(out_path, meta, settings)
        with open(mf.manifest_path(out_path), "w") as f:
            json.dump(man, f, indent=2)
        print(f"wrote {mf.manifest_path(out_path)} (sha256 {man['content_sha256'][:12]}...)")


if __name__ == "__main__":
    main()
