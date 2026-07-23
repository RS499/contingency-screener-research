import os, sys, argparse
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import manifest as mf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import classical_manifest as cm
import figtools as ft

LIMIT = 0.94
CURVE = "data/tradeoff_curve.json"
OUT = "data/gate_schematic.png"
POSTER_OUT = "data/poster/gate_schematic.png"

COLORS = {"persistence": "#d1495b", "ridge": "#b8860b", "histgb": "#00798c"}
C_CERTIFY = COLORS["histgb"]
C_ESCALATE = COLORS["ridge"]
C_FLAG = COLORS["persistence"]

FS_TITLE, FS_LABEL, FS_ANNOT = 13, 10, 9


def read_qhat(path):
    with open(path) as f:
        d = json.load(f)
    for r in d["records"]:
        if r["model"] == "histgb" and abs(r["coverage_target"] - 0.90) < 1e-9:
            return float(r["q_hat"])
    raise ValueError("histgb q_hat at coverage 0.90 not found in " + path)


def draw_case(ax, x, pred, band, color, role, note):
    low = pred - band
    ax.plot([x, x], [low, pred], color=color, lw=4, solid_capstyle="butt", zorder=3)
    ax.plot([x - 0.09, x + 0.09], [low, low], color=color, lw=2.5, zorder=3)
    ax.plot([x], [pred], marker="o", color=color, markersize=8, markeredgecolor="white",
            markeredgewidth=0.8, zorder=4)
    ax.text(x, pred + 0.0012, role, ha="center", va="bottom", fontsize=FS_ANNOT + 1,
            color=color, fontweight="bold")
    ax.text(x, low - 0.0008, note, ha="center", va="top", fontsize=FS_ANNOT, color="black")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--curve", default=CURVE, help="tradeoff curve JSON used to SIZE the strip")
    ap.add_argument("--out", default=OUT, help="output PNG path")
    ap.add_argument("--font-bump", type=float, default=0.0,
                    help="add this many points to every font size (v3 uses 2)")
    ap.add_argument("--poster", action="store_true",
                    help="poster panel: identical rendering, writes data/poster/gate_schematic.png")
    args = ap.parse_args()
    qhat = read_qhat(args.curve)

    global FS_TITLE, FS_LABEL, FS_ANNOT
    FS_TITLE += args.font_bump
    FS_LABEL += args.font_bump
    FS_ANNOT += args.font_bump
    out_path = (POSTER_OUT if args.poster and args.out == OUT else args.out)
    if args.poster:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    figsize = (7.16, 2.8)
    bbox = "tight"

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_ylim(0.930, 0.950)
    ax.set_xlim(0.3, 4.9)

    ax.axhspan(LIMIT, LIMIT + qhat, color=C_ESCALATE, alpha=0.14, zorder=0)
    ax.axhline(LIMIT, color="black", lw=1.5, zorder=2)

    draw_case(ax, 1, LIMIT + qhat + 0.0045, qhat, C_CERTIFY, "Certify",
              "certify safe,\nskip the solver")
    draw_case(ax, 2, LIMIT - 0.0028, qhat, C_FLAG, "Flag",
              "flag violation,\nskip the solver")
    draw_case(ax, 3, LIMIT + qhat * 0.45, qhat, C_ESCALATE, "Escalate",
              "band straddles the limit,\ncall the exact solver")

    ax.text(3.7, LIMIT - 0.0004, "under-voltage limit (0.94 pu)", ha="left", va="top",
            fontsize=FS_ANNOT)
    ax.text(3.7, LIMIT + qhat / 2, "escalation strip,\none band width", ha="left",
            va="center", fontsize=FS_ANNOT, color="#7a5c00")

    ax.annotate("band extends downward only, because the\nrisk is the true voltage sitting below the prediction",
                xy=(1.1, LIMIT + qhat + 0.0045 - qhat / 2), xytext=(1.35, 0.9482),
                fontsize=FS_ANNOT, va="top", ha="left",
                arrowprops=dict(arrowstyle="->", color="0.4", lw=0.8))

    ax.set_ylabel("minimum bus voltage after a\ncontingency (per unit)", fontsize=FS_LABEL)
    ax.set_yticks([0.93, 0.935, 0.94, 0.945, 0.95])
    ax.tick_params(axis="y", labelsize=FS_ANNOT)
    ax.set_xticks([])
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)

    ax.set_title("The three-way gate",
                 fontsize=FS_TITLE)
    ft.add_credit(fig)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches=bbox)
    plt.close(fig)
    print(f"wrote {out_path}")
    print(f"strip sized from q_hat={qhat} pu read from {args.curve} "
          f"(histgb, coverage_target 0.90); annotation prints no number")

    if args.poster:
        meta = dict(figure="poster panel: the three-way conformal gate schematic",
                    figsize_in=list(figsize), curve_source=args.curve, q_hat=qhat)
        settings = dict(task="poster figure regeneration", source=args.curve)
        man = cm.build_manifest(out_path, meta, settings)
        with open(mf.manifest_path(out_path), "w") as f:
            json.dump(man, f, indent=2)
        print(f"wrote {mf.manifest_path(out_path)} (sha256 {man['content_sha256'][:12]}...)")


if __name__ == "__main__":
    main()
