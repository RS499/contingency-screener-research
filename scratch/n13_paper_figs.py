import os
import sys
import json
import shutil
import tempfile
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import sts_paper_corrected as spc
import sts_manifest as sm
import matplotlib.pyplot as plt

# Fig. 2 and Fig. 4 on the rebuilt (N13) case118 data. Writes new files only; refuses to overwrite.
# Fig. 2: scripts/sts_paper_corrected.py fig2(), unchanged, on data/sts_n13_gate_D94.json (sweep points, ridge and
#   histgb, 5 splits, mean +/- population std). fig2() hard-codes its output name, so it writes into a temporary
#   folder and the PNG is then moved to data/sts_n13_fig2_tradeoff.png; no existing file is touched.
# Fig. 4: the same style as sts_paper_corrected.py fig4(), built from min_vm of the converged outage rows of
#   data/sts_n13_D94.parquet; [0.94, 0.945) shaded; x view truncated at 0.87 pu.
# --v2: the same two figures, same data, drawn at their printed width (0.45\textwidth = 0.45 x 6.5 in) and saved
#   at exactly that size, so a font size here is its printed size; every text element is 8 pt or larger.
#   Writes the _v2 files; the v1 files are never touched.
# Usage: .venv/bin/python scratch/n13_paper_figs.py [--v2]

SCRIPT = "scratch/n13_paper_figs.py"
GATE = "data/sts_n13_gate_D94.json"
DATA = "data/sts_n13_D94.parquet"
FIG2 = "data/sts_n13_fig2_tradeoff.png"
FIG4 = "data/sts_n13_fig4_boundary.png"
FIG2_V2 = "data/sts_n13_fig2_tradeoff_v2.png"
FIG4_V2 = "data/sts_n13_fig4_boundary_v2.png"
HIST_LO = 0.715
HIST_HI = 0.965
BIN_W = 0.001
VIEW_LO = 0.87
PRINT_W = 0.45 * 6.5
FIG2_LAYOUT_V2 = dict(figsize=(PRINT_W, 2.42), fs_label=9, fs_tick=8, fs_legend=8, legend_above=True,
                      right_label="missed-violation\n(% of true violations)", bbox=None, pad=0.3,
                      tight_passes=2)
FIG4_LAYOUT_V1 = dict(figsize=(3.5, 2.6), fs_label=9, fs_tick=8,
                      xlabel="minimum bus voltage after a contingency (per unit)",
                      ylabel="share of contingency cases (%)", bbox="tight", pad=1.08)
FIG4_LAYOUT_V2 = dict(figsize=(PRINT_W, 2.03), fs_label=9, fs_tick=8,
                      xlabel="minimum bus voltage after a\ncontingency (per unit)",
                      ylabel="share of contingency\ncases (%)", bbox=None, pad=0.3)


def json_of(png):
    return png.replace(".png", ".json")


def fig2_rebuilt(png, layout, argv):
    with open(GATE) as f:
        g = json.load(f)
    tmp = tempfile.mkdtemp()
    spc.OUT = tmp
    spc.N5_094 = GATE
    spc.FIG2_LAYOUT = layout
    spc.fig2(g)
    shutil.move(os.path.join(tmp, "sts_paper_fig2_tradeoff.png"), png)
    with open(os.path.join(tmp, "sts_paper_fig2_tradeoff.json")) as f:
        vals = json.load(f)["models"]
    shutil.rmtree(tmp)
    out = dict(source=GATE + " points[point=sweep]", std="population ddof=0 over 5 splits",
               note="no operating-point markers", models=vals)
    with open(json_of(png), "w") as f:
        json.dump(out, f, indent=2)
    params = dict(figure="Fig. 2, rebuilt case118 (N13)", plotting_function="scripts/sts_paper_corrected.py fig2()",
                  families=spc.MODELS, seeds=spc.SEEDS, grey_dotted_line="1% missed",
                  figsize_in=list(layout["figsize"]), dpi=300, layout=layout)
    man = sm.build_manifest([png, json_of(png)], SCRIPT, argv,
                            [GATE, "scripts/sts_paper_corrected.py"], params, "")
    sm.write_manifest(man, json_of(png))
    return vals


def fig4_rebuilt(png, layout, argv):
    d = pd.read_parquet(DATA, columns=["outaged_type", "converged", "min_vm"])
    v = d.loc[(d["outaged_type"] != "none") & (d["converged"]), "min_vm"].to_numpy(np.float64)
    edges = np.arange(HIST_LO, HIST_HI + BIN_W / 2, BIN_W)
    counts, _ = np.histogram(v, bins=edges)
    share = 100.0 * counts / len(v)
    left = edges[:-1]
    colors = []
    for e in left:
        if e < spc.LIMIT - 1e-9:
            colors.append(spc.COLORS["persistence"])
        else:
            colors.append(spc.COLORS["histgb"])
    fig, ax = plt.subplots(figsize=layout["figsize"])
    ax.bar(left, share, width=BIN_W, align="edge", color=colors, linewidth=0)
    ax.axvspan(spc.LIMIT, spc.STRIP_HI, color=spc.COLORS["ridge"], alpha=0.20, zorder=0)
    ax.axvline(spc.LIMIT, color="black", lw=1.5, zorder=3)
    ax.set_xlabel(layout["xlabel"], fontsize=layout["fs_label"])
    ax.set_ylabel(layout["ylabel"], fontsize=layout["fs_label"])
    ax.set_xlim(VIEW_LO, HIST_HI)
    ax.tick_params(labelsize=layout["fs_tick"])
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    fig.tight_layout(pad=layout["pad"])
    fig.savefig(png, dpi=300, bbox_inches=layout["bbox"])
    plt.close(fig)
    strip = (v >= spc.LIMIT) & (v < spc.STRIP_HI)
    stats = dict(n_rows=int(len(v)), boundary_mass_pct=float(100 * strip.mean()),
                 conditional_boundary_pct=float(100 * strip.sum() / (v >= spc.LIMIT).sum()),
                 violation_rate_pct=float(100 * (v < spc.LIMIT).mean()),
                 tallest_bin_left=float(left[share.argmax()]), tallest_bin_share_pct=float(share.max()),
                 share_below_view_lo_pct=float(100 * (v < VIEW_LO).mean()), min=float(v.min()), max=float(v.max()))
    with open(json_of(png), "w") as f:
        json.dump(stats, f, indent=2)
    params = dict(figure="Fig. 4, rebuilt case118 (N13)", rows="converged outage rows (outaged_type != none)",
                  hist_range=[HIST_LO, HIST_HI], bin_width_pu=BIN_W, view=[VIEW_LO, HIST_HI], shaded="[0.94, 0.945)",
                  style="scripts/sts_paper_corrected.py fig4()", figsize_in=list(layout["figsize"]), dpi=300,
                  layout=layout)
    man = sm.build_manifest([png, json_of(png)], SCRIPT, argv, [DATA], params, "")
    sm.write_manifest(man, json_of(png))
    return stats


def main():
    argv = [".venv/bin/python", SCRIPT]
    fig2_png, fig2_layout, fig4_png, fig4_layout = FIG2, spc.FIG2_LAYOUT, FIG4, FIG4_LAYOUT_V1
    if "--v2" in sys.argv:
        argv = [".venv/bin/python", SCRIPT, "--v2"]
        fig2_png, fig2_layout, fig4_png, fig4_layout = FIG2_V2, FIG2_LAYOUT_V2, FIG4_V2, FIG4_LAYOUT_V2
    for p in [fig2_png, json_of(fig2_png), fig4_png, json_of(fig4_png)]:
        if os.path.exists(p):
            raise SystemExit(f"STOP: {p} already exists; this script never overwrites.")
    vals = fig2_rebuilt(fig2_png, fig2_layout, argv)
    for m in spc.MODELS:
        for r in vals[m]:
            if round(r["target"], 2) in [0.95, 0.98]:
                print(f"Fig. 2 {m} target {r['target']:.2f}: missed {100 * r['missed']:.2f} +/- {100 * r['missed_std']:.2f}%")
    stats = fig4_rebuilt(fig4_png, fig4_layout, argv)
    print(f"Fig. 4 rows {stats['n_rows']:,}; [0.94, 0.945) {stats['boundary_mass_pct']:.2f}%; tallest bin "
          f"[{stats['tallest_bin_left']:.3f}, {stats['tallest_bin_left'] + BIN_W:.3f}) {stats['tallest_bin_share_pct']:.2f}%; "
          f"below {VIEW_LO} {stats['share_below_view_lo_pct']:.2f}%")
    print(f"wrote {fig2_png} and {fig4_png}")


if __name__ == "__main__":
    main()
