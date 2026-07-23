import os, sys, json, argparse
import numpy as np
import pandapower.networks as nw
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import manifest as mf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import classical_manifest as cm
import figtools as ft

LAYOUT = "data/bus_layout.json"
OUT = "data/network_anatomy_map.png"
POSTER_OUT = "data/poster/network_diagram.png"

C_BUS = "#1f6fb2"
C_LINE = "#bbbbbb"
C_TRAFO = "#d1495b"
FIGW, FIGH = 8.25, 5.4
FS_TITLE, FS_LABEL, FS_ANNOT, FS_NOTE = 18, 13.5, 13, 12


def load_layout():
    if not os.path.exists(LAYOUT):
        raise FileNotFoundError(
            f"{LAYOUT} not found. Run feasibility/domain_figure.py first to freeze the layout.")
    with open(LAYOUT) as f:
        d = json.load(f)
    return {int(k): (v[0], v[1]) for k, v in d["coords"].items()}


def callout(ax, xy, text, anchor, ha, va):
    ax.annotate(text, xy=xy, xycoords="data", xytext=anchor, textcoords=ax.transAxes,
                fontsize=FS_ANNOT, ha=ha, va=va, zorder=5,
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#333333", lw=1.0),
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.2,
                                connectionstyle="arc3,rad=0.15"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--poster", action="store_true",
                    help="poster panel: identical rendering, writes data/poster/network_diagram.png")
    args = ap.parse_args()

    global OUT
    if args.poster:
        OUT = POSTER_OUT
        os.makedirs(os.path.dirname(OUT), exist_ok=True)

    net = nw.case118()
    coords = load_layout()
    n_bus, n_line, n_trafo = len(net.bus), len(net.line), len(net.trafo)
    n_branch = int(net.line.in_service.sum() + net.trafo.in_service.sum())

    fig, ax = plt.subplots(figsize=(FIGW, FIGH))
    fig.subplots_adjust(left=0.015, right=0.985, top=0.90, bottom=0.02)

    lf = net.line["from_bus"].to_numpy(); lt = net.line["to_bus"].to_numpy()
    for i in range(len(lf)):
        a, b = int(lf[i]), int(lt[i])
        ax.plot([coords[a][0], coords[b][0]], [coords[a][1], coords[b][1]],
                color=C_LINE, lw=0.55, zorder=1)
    tf = net.trafo["hv_bus"].to_numpy(); tt = net.trafo["lv_bus"].to_numpy()
    for i in range(len(tf)):
        a, b = int(tf[i]), int(tt[i])
        ax.plot([coords[a][0], coords[b][0]], [coords[a][1], coords[b][1]],
                color=C_TRAFO, lw=1.5, ls="--", zorder=2)
    buses = list(net.bus.index)
    xs = [coords[b][0] for b in buses]; ys = [coords[b][1] for b in buses]
    ax.scatter(xs, ys, c=C_BUS, s=42, edgecolor="black", linewidth=0.4, zorder=3)

    xlo, xhi = min(xs), max(xs); ylo, yhi = min(ys), max(ys)
    px, py = 0.06 * (xhi - xlo), 0.06 * (yhi - ylo)
    ax.set_xlim(xlo - px, xhi + px); ax.set_ylim(ylo - py, yhi + py)
    fx = lambda x: (x - (xlo - px)) / ((xhi + px) - (xlo - px))
    fy = lambda y: (y - (ylo - py)) / ((yhi + py) - (ylo - py))

    tmids = [((coords[int(tf[i])][0] + coords[int(tt[i])][0]) / 2,
              (coords[int(tf[i])][1] + coords[int(tt[i])][1]) / 2) for i in range(len(tf))]
    def mid_of(i):
        return ((coords[int(lf[i])][0] + coords[int(lt[i])][0]) / 2,
                (coords[int(lf[i])][1] + coords[int(lt[i])][1]) / 2)
    def min_dist_to_trafo(m):
        return min((m[0] - t[0]) ** 2 + (m[1] - t[1]) ** 2 for t in tmids)
    lengths = [(coords[int(lf[i])][0] - coords[int(lt[i])][0]) ** 2
               + (coords[int(lf[i])][1] - coords[int(lt[i])][1]) ** 2 for i in range(len(lf))]

    ex_bus = buses[int(np.argmin(xs))]
    bus_xy = (coords[ex_bus][0], coords[ex_bus][1])
    ti = max(range(len(tmids)), key=lambda i: fx(tmids[i][0]) + fy(tmids[i][1]))
    tmid = tmids[ti]; ta, tb = int(tf[ti]), int(tt[ti])
    longest = list(np.argsort(lengths)[::-1][:30])
    trafo_scale = np.median([min_dist_to_trafo(mid_of(i)) for i in longest])
    clear = [i for i in longest if min_dist_to_trafo(mid_of(i)) >= trafo_scale] or longest
    li = max(clear, key=lambda i: fx(mid_of(i)[0]) + (1 - fy(mid_of(i)[1])))
    la, lb = int(lf[li]), int(lt[li]); lmid = mid_of(li)

    callout(ax, bus_xy,
            r"$\mathbf{Bus}$" + "\na network node (substation):\nwhere lines, transformers,\ngenerators and loads meet",
            anchor=(0.015, 0.34), ha="left", va="center")
    callout(ax, tmid,
            r"$\mathbf{Transformer}$" + "\nlinks two buses that operate\nat different voltage levels",
            anchor=(0.985, 0.975), ha="right", va="top")
    callout(ax, lmid,
            r"$\mathbf{Line}$" + "\nan AC transmission line\ncarrying power between two buses",
            anchor=(0.985, 0.03), ha="right", va="bottom")

    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=C_BUS, markeredgecolor="black",
               markersize=8, label=f"Bus  —  {n_bus} total"),
        Line2D([0], [0], color=C_LINE, lw=1.8, label=f"Line  —  {n_line} total"),
        Line2D([0], [0], color=C_TRAFO, lw=1.8, ls="--", label=f"Transformer  —  {n_trafo} total"),
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=FS_LABEL, frameon=True,
              framealpha=0.95, edgecolor="#333333", borderpad=0.6, labelspacing=0.5)

    ax.text(0.015, 0.02, "Topological layout; positions are not geographic.",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=FS_NOTE, color="#666666")

    ax.set_title("IEEE 118-bus test network", fontsize=FS_TITLE, pad=8)
    ax.set_xticks([]); ax.set_yticks([])
    ft.add_credit(fig)
    fig.savefig(OUT, dpi=300)
    plt.close(fig)
    print(f"wrote {OUT}  ({FIGW}x{FIGH} in; buses={n_bus}, lines={n_line}, transformers={n_trafo})")
    print(f"labeled examples: bus {ex_bus}, line {la}-{lb}, transformer {ta}-{tb}")

    if args.poster:
        meta = dict(figure="poster panel: IEEE 118-bus anatomy (bus/line/transformer)",
                    figsize_in=[FIGW, FIGH], source="pandapower case118 topology + data/bus_layout.json",
                    model_independent=True)
        settings = dict(task="poster figure regeneration", source=LAYOUT)
        man = cm.build_manifest(OUT, meta, settings)
        with open(mf.manifest_path(OUT), "w") as f:
            json.dump(man, f, indent=2)
        print(f"wrote {mf.manifest_path(OUT)} (sha256 {man['content_sha256'][:12]}...)")


if __name__ == "__main__":
    main()
