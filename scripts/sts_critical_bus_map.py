import os
import sys
import json
import numpy as np
import pandas as pd
import pandapower.networks as nw
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sts_manifest as sm

# Prose-free critical-bus map for the STS report: the same data and frozen layout as
# feasibility/domain_figure.py (data/critical_bus_map.png), without the in-image title and
# footer, sized for a 0.55-0.6 textwidth column. Bus labels are IEEE 1-based names
# (pandapower index + 1). Logic copied from feasibility/domain_figure.py, which is unchanged.
#
# usage: .venv/bin/python scripts/sts_critical_bus_map.py OUT_DIR [REF_DIR]

DATA = "data/dataset.parquet"
LAYOUT = "data/bus_layout.json"
FROZEN_V2 = "data/frozen_poster_numbers_v2.json"
SCRIPT = "scripts/sts_critical_bus_map.py"
PNG_NAME = "sts_critical_bus_map.png"

N_LABELLED = 3
NORM_GAMMA = 0.5
FIGSIZE = (5.0, 4.2)
NODE_SIZE = 24
FS_LABEL, FS_TICK = 9, 8


def load_layout():
    # the frozen igraph layout written by feasibility/domain_figure.py (seed 0)
    with open(LAYOUT) as f:
        d = json.load(f)
    coords = {}
    for k in d["coords"]:
        coords[int(k)] = (d["coords"][k][0], d["coords"][k][1])
    return coords


def critical_frequency(net):
    df = pd.read_parquet(DATA, columns=["outaged_type", "converged", "argmin_bus"])
    n1 = df[(df["outaged_type"] != "none") & (df["converged"])]
    ab = n1["argmin_bus"].to_numpy()
    counts = np.zeros(len(net.bus), dtype=np.float64)
    for b in ab:
        counts[int(b)] += 1.0
    freq = 100.0 * counts / len(n1)
    return freq, len(n1)


def draw_branches(ax, net, coords):
    lf = net.line["from_bus"].to_numpy()
    lt = net.line["to_bus"].to_numpy()
    for i in range(len(lf)):
        a, b = int(lf[i]), int(lt[i])
        ax.plot([coords[a][0], coords[b][0]], [coords[a][1], coords[b][1]],
                color="#bbbbbb", lw=0.4, zorder=1)
    tf = net.trafo["hv_bus"].to_numpy()
    tt = net.trafo["lv_bus"].to_numpy()
    for i in range(len(tf)):
        a, b = int(tf[i]), int(tt[i])
        ax.plot([coords[a][0], coords[b][0]], [coords[a][1], coords[b][1]],
                color="#bbbbbb", lw=0.4, ls="--", zorder=1)


def verify_top(freq, buses):
    # the labelled shares must match data/frozen_poster_numbers_v2.json -> critical_bus_top5
    with open(FROZEN_V2) as f:
        top5 = json.load(f)["dataset_facts"]["critical_bus_top5"]
    order = np.argsort(freq)[::-1][:5]
    rows = []
    for rank, i in enumerate(order):
        b = int(buses[i])
        ref = top5[rank]
        rows.append({
            "rank": rank + 1,
            "pandapower_index": b,
            "ieee_name": b + 1,
            "share_pct": float(freq[i]),
            "frozen_v2_bus_index": ref["bus"],
            "frozen_v2_share_pct": ref["share_pct"],
            "match": bool(ref["bus"] == b and abs(ref["share_pct"] - round(float(freq[i]), 2)) < 1e-9),
            "labelled": rank < N_LABELLED,
        })
    return rows


def draw(net, coords, freq, out_path):
    buses = list(net.bus.index)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    draw_branches(ax, net, coords)
    xs = [coords[b][0] for b in buses]
    ys = [coords[b][1] for b in buses]
    norm = PowerNorm(gamma=NORM_GAMMA, vmin=0.0, vmax=float(freq.max()))
    sc = ax.scatter(xs, ys, c=freq, cmap="YlOrRd", norm=norm, s=NODE_SIZE, edgecolor="black",
                    linewidth=0.3, zorder=2)
    cbar = fig.colorbar(sc, ax=ax, shrink=0.85)
    cbar.set_label("share of N-1 cases where this bus\nhas the lowest voltage (%)",
                   fontsize=FS_LABEL)
    cbar.ax.tick_params(labelsize=FS_TICK)
    order = np.argsort(freq)[::-1][:N_LABELLED]
    for i in order:
        b = buses[i]
        ax.annotate(f"bus {b + 1}", (coords[b][0], coords[b][1]), fontsize=FS_TICK,
                    color="black", xytext=(4, 3), textcoords="offset points")
    ax.set_xticks([])
    ax.set_yticks([])
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

    net = nw.case118()
    coords = load_layout()
    freq, n_cases = critical_frequency(net)
    top = verify_top(freq, list(net.bus.index))
    for r in top:
        print(f"rank {r['rank']}: IEEE bus {r['ieee_name']} (index {r['pandapower_index']}) "
              f"{r['share_pct']:.4f}% vs frozen {r['frozen_v2_share_pct']} -> match {r['match']}")
    draw(net, coords, freq, png_path)

    params = {
        "n_cases": n_cases,
        "population": "converged N-1 rows of data/dataset.parquet (outaged_type != 'none' and "
                      "converged); share = percent of those rows whose argmin_bus is the bus",
        "layout": "data/bus_layout.json (pandapower igraph, LAYOUT_SEED = 0); positions are "
                  "topological, not geographic",
        "colour_map": "YlOrRd", "colour_norm": f"PowerNorm(gamma={NORM_GAMMA}), vmin 0, vmax = max share",
        "node_size_pt2": NODE_SIZE, "figsize_in": list(FIGSIZE), "dpi": 300,
        "font_sizes": {"label": FS_LABEL, "tick": FS_TICK},
        "branches": "lines solid, transformers dashed, grey #bbbbbb",
        "labels": f"top {N_LABELLED} buses by share, text 'bus <IEEE name>' (index + 1), no percentage",
        "label_choice_reason": "The report caption names buses 76, 53 and 107, so only those are "
                               "labelled. The original figure also labelled bus 1 and bus 21; bus 1 "
                               "(rank 4) is close in share to bus 107 (rank 3), so it shows a "
                               "similar colour without a label. Shares are left to the colour bar "
                               "and the caption, which avoids the integer-rounded '17%' of the "
                               "original disagreeing with the text's 16.81%.",
        "removed_vs_data_critical_bus_map_png": [
            "title: 'IEEE 118-bus: critical-bus frequency across 278,955 converged N-1 cases'",
            "footer: 'Topological layout (pandapower igraph); bus positions are NOT geographic.'",
            "labels 'bus 1 (8%)' and 'bus 21 (4%)'",
            "percentages inside the remaining three labels",
        ],
        "top5_verified_against_frozen_v2": top,
        "bus_numbering": "labels are IEEE 1-based names; argmin_bus and the pandapower_index "
                         "fields are 0-based; IEEE name = index + 1 on case118",
        "logic_source": "feasibility/domain_figure.py (critical_frequency, draw_branches, layout "
                        "loading) copied, not imported; that file is unchanged",
        "in_image_text": "colour-bar label and ticks and three bus labels only; no title, no footer",
    }
    argv = [SCRIPT, "data"]
    man = sm.build_manifest([png_path], SCRIPT, argv, [DATA, LAYOUT, FROZEN_V2], params, ref_dir)
    sm.write_manifest(man, png_path)


if __name__ == "__main__":
    main()
