import os, sys, json, random, argparse
import numpy as np
import pandas as pd
import pandapower.networks as nw
import pandapower.plotting as plot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
import manifest as mf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import classical_manifest as cm
import figtools as ft

DATA = "data/dataset.parquet"
LAYOUT = "data/bus_layout.json"
OUT = "data/critical_bus_map.png"
POSTER_OUT = "data/poster/critical_bus_map.png"
LAYOUT_SEED = 0
NORM_GAMMA = 0.5
FS_TITLE, FS_LABEL, FS_ANNOT = 22, 16, 13


def load_or_make_layout(net):
    if os.path.exists(LAYOUT):
        with open(LAYOUT) as f:
            d = json.load(f)
        return {int(k): (v[0], v[1]) for k, v in d["coords"].items()}
    random.seed(LAYOUT_SEED); np.random.seed(LAYOUT_SEED)
    plot.create_generic_coordinates(net, overwrite=True, library="igraph")
    coords = {}
    for b in net.bus.index:
        xy = json.loads(net.bus.at[b, "geo"])["coordinates"]
        coords[int(b)] = [float(xy[0]), float(xy[1])]
    mf.write_with_manifest(LAYOUT, dict(network="case118", library="igraph", seed=LAYOUT_SEED,
                                        coords=coords))
    print(f"generated and froze {LAYOUT} ({len(coords)} buses)")
    return {b: (c[0], c[1]) for b, c in coords.items()}


def critical_frequency(net):
    df = pd.read_parquet(DATA)
    n1 = df[(df.outaged_type != "none") & (df.converged)]
    ab = n1["argmin_bus"].to_numpy()
    counts = np.zeros(len(net.bus), dtype=np.float64)
    for b in ab:
        counts[int(b)] += 1.0
    freq = 100.0 * counts / len(n1)
    return freq, len(n1)


def draw_branches(ax, net, coords):
    lf = net.line["from_bus"].to_numpy(); lt = net.line["to_bus"].to_numpy()
    for i in range(len(lf)):
        a, b = int(lf[i]), int(lt[i])
        ax.plot([coords[a][0], coords[b][0]], [coords[a][1], coords[b][1]],
                color="#bbbbbb", lw=0.6, zorder=1)
    tf = net.trafo["hv_bus"].to_numpy(); tt = net.trafo["lv_bus"].to_numpy()
    for i in range(len(tf)):
        a, b = int(tf[i]), int(tt[i])
        ax.plot([coords[a][0], coords[b][0]], [coords[a][1], coords[b][1]],
                color="#bbbbbb", lw=0.6, ls="--", zorder=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--poster", action="store_true",
                    help="poster panel: identical rendering, writes data/poster/critical_bus_map.png")
    args = ap.parse_args()

    out_path = POSTER_OUT if args.poster else OUT
    if args.poster:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    figsize = (15, 12)
    bbox = "tight"

    net = nw.case118()
    coords = load_or_make_layout(net)
    freq, n_cases = critical_frequency(net)
    buses = list(net.bus.index)

    fig, ax = plt.subplots(figsize=figsize)
    draw_branches(ax, net, coords)
    xs = [coords[b][0] for b in buses]
    ys = [coords[b][1] for b in buses]
    norm = PowerNorm(gamma=NORM_GAMMA, vmin=0.0, vmax=float(freq.max()))
    sc = ax.scatter(xs, ys, c=freq, cmap="YlOrRd", norm=norm, s=130, edgecolor="black",
                    linewidth=0.5, zorder=2)
    cbar = fig.colorbar(sc, ax=ax, shrink=0.85)
    cbar.set_label("share of N-1 cases where this bus has the lowest voltage (%)", fontsize=FS_LABEL)
    cbar.ax.tick_params(labelsize=FS_ANNOT)

    order = np.argsort(freq)[::-1][:5]
    for i in order:
        if freq[i] > 0:
            b = buses[i]
            ax.annotate(f"bus {b + 1} ({freq[i]:.0f}%)", (coords[b][0], coords[b][1]),
                        fontsize=FS_ANNOT, color="black", xytext=(5, 5), textcoords="offset points")

    ax.set_title(f"IEEE 118-bus: critical-bus frequency across {n_cases:,} converged N-1 cases",
                 fontsize=FS_TITLE)
    ax.text(0.5, -0.03, "Topological layout (pandapower igraph); bus positions are NOT geographic.",
            transform=ax.transAxes, ha="center", va="top", fontsize=FS_LABEL, color="#444444")
    ax.set_xticks([]); ax.set_yticks([])
    ft.add_credit(fig)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches=bbox)
    plt.close(fig)
    print(f"wrote {out_path} (buses={len(net.bus)}, N-1 cases={n_cases}, "
          f"top bus freq={freq.max():.1f}% at bus {buses[int(np.argmax(freq))] + 1} (IEEE name))")

    if args.poster:
        meta = dict(figure="poster panel: critical-bus frequency map", figsize_in=list(figsize),
                    n_cases=n_cases, top_bus_ieee=int(buses[int(np.argmax(freq))]) + 1,
                    top_bus_freq_pct=float(freq.max()), source=DATA, model_independent=True)
        settings = dict(task="poster figure regeneration", source=DATA, layout_source=LAYOUT)
        man = cm.build_manifest(out_path, meta, settings)
        with open(mf.manifest_path(out_path), "w") as f:
            json.dump(man, f, indent=2)
        print(f"wrote {mf.manifest_path(out_path)} (sha256 {man['content_sha256'][:12]}...)")


if __name__ == "__main__":
    main()
