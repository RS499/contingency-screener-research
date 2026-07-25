import argparse
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figtools as ft

CURVE = "data/tradeoff_curve.json"
OUT = "data/tradeoff_hero_col.png"
MODELS = ["ridge", "histgb"]
COLORS = {"ridge": "#b8860b", "histgb": "#00798c"}
FS_LABEL, FS_TICK, FS_LEG, FS_ANNOT = 9, 7, 6, 7


def rows_for(records, model):
    rows = [r for r in records if r["model"] == model]
    order = np.argsort([r["coverage_target"] for r in rows])
    return [rows[i] for i in order]


def first_safe_coverage(rows):
    safe = [r["coverage_target"] for r in rows if r["missed_viol"] < 0.01]
    return min(safe) if safe else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--curve", default=CURVE, help="tradeoff curve JSON to render")
    ap.add_argument("--out", default=OUT, help="output PNG path")
    args = ap.parse_args()

    with open(args.curve) as f:
        records = json.load(f)["records"]

    fig, axL = plt.subplots(figsize=(3.5, 2.7))
    axR = axL.twinx()

    ymax_esc = 0.0
    for i, model in enumerate(MODELS):
        rows = rows_for(records, model)
        cov = [r["coverage_target"] for r in rows]
        esc = [r["escalation"] * 100 for r in rows]
        mis = [r["missed_viol"] * 100 for r in rows]
        ymax_esc = max(ymax_esc, max(esc))
        axL.plot(cov, esc, "-", lw=1.6, color=COLORS[model], label=f"{model} escalation")
        axR.plot(cov, mis, ":", lw=1.4, color=COLORS[model], label=f"{model} missed")
        c = first_safe_coverage(rows)
        if c is not None:
            axL.axvline(c, color=COLORS[model], lw=1.0, ls="-.")
            side = "right" if i == 0 else "left"
            dx = -0.003 if i == 0 else 0.003
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

    ft.add_credit(fig)
    fig.tight_layout()
    fig.savefig(args.out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {args.out}")
    for model in MODELS:
        c = first_safe_coverage(rows_for(records, model))
        print(f"  {model}: first sub-1% missed coverage = {c}")


if __name__ == "__main__":
    main()
