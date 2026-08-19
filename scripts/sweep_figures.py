import os
import sys
import json
import time
import hashlib
import subprocess
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

SRC = "data/sweep_results_long.parquet"
FIG_A = "data/fig_identity.png"
FIG_B = "data/fig_floor.png"
ND_LIMIT = 0.940
PRED = ["esc_pred_cdf", "esc_pred_rho_local", "esc_pred_rho_outcome"]
PRED_LABEL = {"esc_pred_cdf": "CDF (calibration)",
              "esc_pred_rho_local": r"$\rho_{\hat{p}}\cdot\hat{q}$ (local)",
              "esc_pred_rho_outcome": r"$\rho_{Y}\cdot\hat{q}$ (outcome)"}
PRED_COLOR = {"esc_pred_cdf": "#00798c",
              "esc_pred_rho_local": "#b8860b",
              "esc_pred_rho_outcome": "#d1495b"}
MODEL_MARKER = {"ridge": "o", "histgb": "^"}
APA = ("Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. "
       "Computing in Science & Engineering, 9(3), 90-95. "
       "https://doi.org/10.1109/MCSE.2007.55")


def setup_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 10,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
        "axes.linewidth": 0.8, "savefig.dpi": 300, "figure.dpi": 300,
    })


def r2_identity(obs, pred):
    ss_res = float(np.sum((obs - pred) ** 2))
    ss_tot = float(np.sum((obs - obs.mean()) ** 2))
    return 1.0 - ss_res / ss_tot


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_out(args):
    try:
        return subprocess.run(["git"] + args, capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""


def stats_block(d, cols):
    out = {}
    for c in cols:
        o = d.esc_observed.to_numpy(); p = d[c].to_numpy()
        out[c] = dict(r2=r2_identity(o, p), mae=float(np.mean(np.abs(p - o))), n=int(len(d)))
    return out


def figure_a(d, nd, deg, numbers):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    lim = float(max(nd.esc_observed.max(), max(nd[c].max() for c in PRED)))
    lim = min(lim, 1.05)
    ax.plot([0, lim], [0, lim], color="0.25", lw=1.0, ls="--", zorder=1)
    for c in PRED:
        for m in ("ridge", "histgb"):
            s = nd[nd.model == m]
            ax.scatter(s.esc_observed, s[c], s=3, alpha=0.28, linewidths=0,
                       color=PRED_COLOR[c], marker=MODEL_MARKER[m], zorder=2)
    ax.set_xlim(-0.02, lim); ax.set_ylim(-0.02, lim)
    ax.set_xlabel("observed escalation rate")
    ax.set_ylabel("predicted escalation rate")
    ax.set_title(f"Predicted vs observed escalation, non-degenerate range "
                 f"($L \\leq {ND_LIMIT:.3f}$, n = {numbers['n_nondegenerate']:,})")

    lines = []
    for c in PRED:
        st = numbers["nondegenerate"][c]
        lines.append(f"{PRED_LABEL[c]}:  $R^2$ = {st['r2']:.3f},  MAE = {st['mae']:.4f}")
    ax.text(0.03, 0.97, "\n".join(lines), transform=ax.transAxes, va="top", ha="left",
            fontsize=8, bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="0.7", lw=0.6))

    handles = [Line2D([], [], color=PRED_COLOR[c], marker="s", ls="none", ms=5,
                      label=PRED_LABEL[c]) for c in PRED]
    handles += [Line2D([], [], color="0.35", marker=MODEL_MARKER[m], ls="none", ms=5, label=m)
                for m in ("ridge", "histgb")]
    handles += [Line2D([], [], color="0.25", ls="--", lw=1.0, label="identity")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.015, 0.80),
              frameon=True, framealpha=0.95)

    axi = ax.inset_axes([0.60, 0.07, 0.37, 0.37])
    dlim = float(max(deg.esc_observed.max(), max(deg[c].max() for c in PRED)))
    axi.plot([0, dlim], [0, dlim], color="0.25", lw=0.8, ls="--")
    for c in PRED:
        axi.scatter(deg.esc_observed, deg[c], s=2, alpha=0.30, linewidths=0,
                    color=PRED_COLOR[c])
    axi.set_title(f"degenerate $L > {ND_LIMIT:.3f}$ (n = {numbers['n_degenerate']:,})", fontsize=7)
    axi.tick_params(labelsize=6)
    axi.set_xlabel("observed", fontsize=6, labelpad=1)
    axi.set_ylabel("predicted", fontsize=6, labelpad=1)
    axi.patch.set_alpha(0.97)
    fig.tight_layout()
    fig.savefig(FIG_A, bbox_inches="tight")
    plt.close(fig)


def figure_b(d, nd, numbers):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    sc = None
    for m in ("ridge", "histgb"):
        s = d[d.model == m]
        sc = ax.scatter(s.boundary_mass, s.esc_observed, c=s.L, s=4, alpha=0.45,
                        linewidths=0, marker=MODEL_MARKER[m], cmap="viridis")
    top = float(max(d.boundary_mass.max(), d.esc_observed.max()))
    ax.plot([0, top], [0, top], color="0.25", lw=1.0, ls="--", zorder=1)

    mn = numbers["min_escalation_nondegenerate"]
    ax.scatter([mn["boundary_mass"]], [mn["esc_observed"]], s=70, facecolors="none",
               edgecolors="#d1495b", linewidths=1.4, zorder=5)
    ax.annotate(f"min escalation {mn['esc_observed']*100:.3f}%\n"
                f"$L$ = {mn['L']:.3f}, {mn['model']}, target {mn['target']:.2f}",
                xy=(mn["boundary_mass"], mn["esc_observed"]),
                xytext=(0.055, 0.62), textcoords="axes fraction", fontsize=7.5,
                arrowprops=dict(arrowstyle="->", color="#d1495b", lw=0.9))

    for m in ("ridge", "histgb"):
        p = numbers["at_L094"][m]
        ax.scatter([p["boundary_mass"]], [p["esc_observed"]], s=70, marker="*",
                   color="black", zorder=6)
        ax.annotate(f"$L$=0.940 {m}\nesc {p['esc_observed']*100:.1f}%, "
                    f"bm {p['boundary_mass']*100:.1f}%",
                    xy=(p["boundary_mass"], p["esc_observed"]),
                    xytext=(p["boundary_mass"] + 0.04, p["esc_observed"] - 0.10),
                    fontsize=7.5, arrowprops=dict(arrowstyle="->", color="black", lw=0.8))

    cb = fig.colorbar(sc, ax=ax, pad=0.02)
    cb.set_label("screening limit $L$ (pu)", fontsize=8)
    cb.ax.tick_params(labelsize=7)
    cb.ax.axhline(ND_LIMIT, color="black", lw=1.2)
    cb.ax.text(1.35, ND_LIMIT, "degeneracy\nthreshold", fontsize=6.5,
               va="bottom", ha="left", linespacing=0.95,
               transform=cb.ax.get_yaxis_transform())
    ax.set_xlabel("boundary mass, share of outcomes in $[L,\\, L+\\hat{q})$")
    ax.set_ylabel("observed escalation rate")
    nds = numbers["nondegenerate_fit"]
    ax.set_title(f"Escalation against boundary mass "
                 f"(non-degenerate $L \\leq {ND_LIMIT:.3f}$: slope = {nds['slope']:.3f}, "
                 f"$r$ = {nds['pearson_r']:.3f})")
    handles = [Line2D([], [], color="0.35", marker=MODEL_MARKER[m], ls="none", ms=5, label=m)
               for m in ("ridge", "histgb")]
    handles += [Line2D([], [], color="0.25", ls="--", lw=1.0, label="identity"),
                Line2D([], [], color="black", marker="*", ls="none", ms=9, label="$L$ = 0.940")]
    ax.legend(handles=handles, loc="lower right", frameon=True, framealpha=0.95)
    fig.tight_layout()
    fig.savefig(FIG_B, bbox_inches="tight")
    plt.close(fig)


def write_manifest(fig_path, numbers, src_sha, script_sha, script_commit):
    man = dict(
        figure=os.path.basename(fig_path),
        generating_script="scripts/sweep_figures.py",
        script_git_blob_sha=script_sha,
        script_tracked_in_git=bool(script_commit),
        repo_head_commit=git_out(["rev-parse", "HEAD"]),
        input_file=SRC,
        input_sha256=src_sha,
        interpreter=sys.version,
        interpreter_short=".".join(str(x) for x in sys.version_info[:3]),
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        plotting_library=f"matplotlib {matplotlib.__version__}",
        apa_citation=APA,
        numpy=np.__version__, pandas=pd.__version__,
        rendered_numbers=numbers,
        content_sha256=sha256_of(fig_path),
    )
    out = os.path.splitext(fig_path)[0] + ".manifest.json"
    with open(out, "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {out}")


def main():
    setup_style()
    d = pd.read_parquet(SRC)
    nd = d[d.L <= ND_LIMIT]
    deg = d[d.L > ND_LIMIT]

    i = nd.esc_observed.idxmin()
    row = nd.loc[i]
    mn = dict(esc_observed=float(row.esc_observed), boundary_mass=float(row.boundary_mass),
              L=float(row.L), model=str(row.model), target=float(row.target),
              seed=int(row.seed))

    at94 = {}
    for m in ("ridge", "histgb"):
        s = d[(np.isclose(d.L, 0.940)) & (d.model == m) & (np.isclose(d.target, 0.90))]
        at94[m] = dict(esc_observed=float(s.esc_observed.mean()),
                       boundary_mass=float(s.boundary_mass.mean()),
                       target=0.90, note="mean over 5 seeds at coverage target 0.90")

    slope, intercept = np.polyfit(nd.boundary_mass, nd.esc_observed, 1)
    fit = dict(slope=float(slope), intercept=float(intercept),
               pearson_r=float(np.corrcoef(nd.boundary_mass, nd.esc_observed)[0, 1]))

    numbers = dict(
        nondegenerate_definition=f"L <= {ND_LIMIT}",
        n_nondegenerate=int(len(nd)), n_degenerate=int(len(deg)),
        nondegenerate=stats_block(nd, PRED),
        full_range=stats_block(d, PRED),
        degenerate=stats_block(deg, PRED),
        min_escalation_nondegenerate=mn,
        at_L094=at94,
        nondegenerate_fit=fit,
        requested_6p6pct_floor=dict(
            found=False,
            note=("The request asked to mark a 6.6% minimum. No such minimum exists in this "
                  "parquet: the minimum escalation on L <= 0.940 is "
                  f"{mn['esc_observed']*100:.4f}%. The figure marks the actual minimum instead."),
        ),
    )

    src_sha = sha256_of(SRC)
    script_sha = git_out(["hash-object", "scripts/sweep_figures.py"])
    script_commit = git_out(["log", "-1", "--format=%H", "--", "scripts/sweep_figures.py"])

    figure_a(d, nd, deg, numbers)
    print(f"wrote {FIG_A}")
    figure_b(d, nd, numbers)
    print(f"wrote {FIG_B}")
    write_manifest(FIG_A, numbers, src_sha, script_sha, script_commit)
    write_manifest(FIG_B, numbers, src_sha, script_sha, script_commit)


if __name__ == "__main__":
    main()
