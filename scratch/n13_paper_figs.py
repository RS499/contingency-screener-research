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
# Usage: .venv/bin/python scratch/n13_paper_figs.py

SCRIPT = "scratch/n13_paper_figs.py"
GATE = "data/sts_n13_gate_D94.json"
DATA = "data/sts_n13_D94.parquet"
FIG2 = "data/sts_n13_fig2_tradeoff.png"
FIG4 = "data/sts_n13_fig4_boundary.png"
HIST_LO = 0.715
HIST_HI = 0.965
BIN_W = 0.001
VIEW_LO = 0.87


def json_of(png):
    return png.replace(".png", ".json")


def fig2_rebuilt():
    with open(GATE) as f:
        g = json.load(f)
    tmp = tempfile.mkdtemp()
    spc.OUT = tmp
    spc.N5_094 = GATE
    spc.fig2(g)
    shutil.move(os.path.join(tmp, "sts_paper_fig2_tradeoff.png"), FIG2)
    with open(os.path.join(tmp, "sts_paper_fig2_tradeoff.json")) as f:
        vals = json.load(f)["models"]
    shutil.rmtree(tmp)
    out = dict(source=GATE + " points[point=sweep]", std="population ddof=0 over 5 splits",
               note="no operating-point markers", models=vals)
    with open(json_of(FIG2), "w") as f:
        json.dump(out, f, indent=2)
    params = dict(figure="Fig. 2, rebuilt case118 (N13)", plotting_function="scripts/sts_paper_corrected.py fig2()",
                  families=spc.MODELS, seeds=spc.SEEDS, grey_dotted_line="1% missed", figsize_in=[3.5, 2.7], dpi=300)
    man = sm.build_manifest([FIG2, json_of(FIG2)], SCRIPT, [".venv/bin/python", SCRIPT],
                            [GATE, "scripts/sts_paper_corrected.py"], params, "")
    sm.write_manifest(man, json_of(FIG2))
    return vals


def fig4_rebuilt():
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
    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    ax.bar(left, share, width=BIN_W, align="edge", color=colors, linewidth=0)
    ax.axvspan(spc.LIMIT, spc.STRIP_HI, color=spc.COLORS["ridge"], alpha=0.20, zorder=0)
    ax.axvline(spc.LIMIT, color="black", lw=1.5, zorder=3)
    ax.set_xlabel("minimum bus voltage after a contingency (per unit)", fontsize=9)
    ax.set_ylabel("share of contingency cases (%)", fontsize=9)
    ax.set_xlim(VIEW_LO, HIST_HI)
    ax.tick_params(labelsize=8)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG4, dpi=300, bbox_inches="tight")
    plt.close(fig)
    strip = (v >= spc.LIMIT) & (v < spc.STRIP_HI)
    stats = dict(n_rows=int(len(v)), boundary_mass_pct=float(100 * strip.mean()),
                 conditional_boundary_pct=float(100 * strip.sum() / (v >= spc.LIMIT).sum()),
                 violation_rate_pct=float(100 * (v < spc.LIMIT).mean()),
                 tallest_bin_left=float(left[share.argmax()]), tallest_bin_share_pct=float(share.max()),
                 share_below_view_lo_pct=float(100 * (v < VIEW_LO).mean()), min=float(v.min()), max=float(v.max()))
    with open(json_of(FIG4), "w") as f:
        json.dump(stats, f, indent=2)
    params = dict(figure="Fig. 4, rebuilt case118 (N13)", rows="converged outage rows (outaged_type != none)",
                  hist_range=[HIST_LO, HIST_HI], bin_width_pu=BIN_W, view=[VIEW_LO, HIST_HI], shaded="[0.94, 0.945)",
                  style="scripts/sts_paper_corrected.py fig4()", figsize_in=[3.5, 2.6], dpi=300)
    man = sm.build_manifest([FIG4, json_of(FIG4)], SCRIPT, [".venv/bin/python", SCRIPT], [DATA], params, "")
    sm.write_manifest(man, json_of(FIG4))
    return stats


def main():
    for p in [FIG2, json_of(FIG2), FIG4, json_of(FIG4)]:
        if os.path.exists(p):
            raise SystemExit(f"STOP: {p} already exists; this script never overwrites.")
    vals = fig2_rebuilt()
    for m in spc.MODELS:
        for r in vals[m]:
            if round(r["target"], 2) in [0.95, 0.98]:
                print(f"Fig. 2 {m} target {r['target']:.2f}: missed {100 * r['missed']:.2f} +/- {100 * r['missed_std']:.2f}%")
    stats = fig4_rebuilt()
    print(f"Fig. 4 rows {stats['n_rows']:,}; [0.94, 0.945) {stats['boundary_mass_pct']:.2f}%; tallest bin "
          f"[{stats['tallest_bin_left']:.3f}, {stats['tallest_bin_left'] + BIN_W:.3f}) {stats['tallest_bin_share_pct']:.2f}%; "
          f"below {VIEW_LO} {stats['share_below_view_lo_pct']:.2f}%")
    print(f"wrote {FIG2} and {FIG4}")


if __name__ == "__main__":
    main()
