import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import figtools as ft

OUT = "data/pipeline_schematic.png"

COLORS = {"persistence": "#d1495b", "ridge": "#b8860b", "histgb": "#00798c"}
C_TRAIN = COLORS["histgb"]
C_CAL = COLORS["ridge"]
C_TEST = COLORS["persistence"]
C_DATA = "#3b3b3b"
C_NOTE = "#00798c"

FS_BOX, FS_SIDE, FS_NOTE = 8, 6, 7

CX = 3.7
W = 5.6
H = 1.2


def draw_box(ax, cy, text, edge, fill="white", weight="normal", grow=0.0):
    h = H + grow
    box = FancyBboxPatch((CX - W / 2, cy - h / 2), W, h,
                         boxstyle="round,pad=0.02,rounding_size=0.12",
                         fc=fill, ec=edge, lw=1.3, zorder=2)
    ax.add_patch(box)
    ax.text(CX, cy, text, ha="center", va="center", fontsize=FS_BOX, color="black",
            weight=weight, zorder=3)


def draw_arrow(ax, y_top, y_bot, color="0.35"):
    ax.annotate("", xy=(CX, y_bot), xytext=(CX, y_top),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.4), zorder=1)


def side_count(ax, cy, text):
    ax.text(CX + W / 2 + 0.25, cy, text, ha="left", va="center", fontsize=FS_SIDE, color="0.3",
            style="italic")


def main():
    fig, ax = plt.subplots(figsize=(3.5, 6.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 20)
    ax.axis("off")

    y_a, y_b, y_c, y_d, y_e = 18.8, 16.9, 15.0, 13.1, 11.2
    y_note = 9.3
    y_f, y_g, y_h = 7.0, 5.2, 3.4

    draw_box(ax, y_a, "Sample base\noperating point", C_DATA)
    draw_box(ax, y_b, "N-0 feasibility gate\n(reject if base < 0.94 pu)", C_DATA, grow=0.15)
    draw_box(ax, y_c, "Apply 186 single-\nelement contingencies", C_DATA, grow=0.15)
    draw_box(ax, y_d, "Exact AC power-flow\nsolve; record min. voltage", C_DATA, grow=0.15)
    draw_box(ax, y_e, "Split BY SCENARIO into\ntrain / calibration / test", C_DATA,
             fill="#f3f3f3", weight="bold", grow=0.15)

    draw_arrow(ax, y_a - H / 2, y_b + (H + 0.15) / 2)
    draw_arrow(ax, y_b - (H + 0.15) / 2, y_c + (H + 0.15) / 2)
    draw_arrow(ax, y_c - (H + 0.15) / 2, y_d + (H + 0.15) / 2)
    draw_arrow(ax, y_d - (H + 0.15) / 2, y_e + (H + 0.15) / 2)

    side_count(ax, y_a, "1,500\nscenarios")
    side_count(ax, y_c, "173 lines +\n13 transformers")
    side_count(ax, y_d, "278,955\nconverged\nN-1 rows")

    note = ("Grouped by scenario, not by row:\n"
            "no scenario's rows land in two\n"
            "partitions, which keeps the\n"
            "calibration and test sets exchangeable.")
    ax.text(CX, y_note, note, ha="center", va="center", fontsize=FS_NOTE, color=C_NOTE,
            style="italic",
            bbox=dict(boxstyle="round,pad=0.35", fc="#eef6f7", ec=C_NOTE, lw=0.9), zorder=2)

    draw_box(ax, y_f, "Fit surrogate on TRAIN", C_TRAIN)
    draw_box(ax, y_g, "Calibrate one-sided\nband on CALIBRATION", C_CAL, grow=0.15)
    draw_box(ax, y_h, "Three-way gate on TEST\n(certify/flag/escalate)", C_TEST, grow=0.15)

    draw_arrow(ax, y_e - (H + 0.15) / 2, y_note + 1.15, color="0.6")
    draw_arrow(ax, y_note - 1.15, y_f + H / 2, color="0.6")
    draw_arrow(ax, y_f - H / 2, y_g + (H + 0.15) / 2)
    draw_arrow(ax, y_g - (H + 0.15) / 2, y_h + (H + 0.15) / 2)

    for yy, col, lab in [(y_f, C_TRAIN, "train"), (y_g, C_CAL, "calib."), (y_h, C_TEST, "test")]:
        ax.text(CX - W / 2 - 0.2, yy, lab, ha="right", va="center", fontsize=FS_SIDE,
                color=col, weight="bold")

    ft.add_credit(fig)
    fig.tight_layout()
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT}")
    print("counts: 1,500 scenarios / 278,955 converged rows from data/frozen_poster_numbers.json; "
          "186 = 173 lines + 13 transformers from CLAUDE.md section 5")


if __name__ == "__main__":
    main()
