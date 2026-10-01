import os
import sys
import json
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import make_splits as ms
import gate_eval as ge
import manifest as mf
import surrogate as sg
import tune_surrogates as tu
import sts_manifest as sm
import n9_budget_curve as bc

# N10 Part C: paper artifacts on corrected labels (case118 D94 = N2 switch-back labels). No verdict, no prose in
# the images: axis labels, tick labels, legends and value labels only, in the look of the existing STS figures
# (scripts/sts_tradeoff_bands.py, scripts/sts_miss_depth_noannot.py, feasibility/boundary_mass_hist.py --no-prose),
# copied, not imported.
#   (a) data/sts_n10_fig_tradeoff     escalation and missed vs target 0.70-0.99, +-1 std bands (N5 corrected sweep)
#   (b) data/sts_n10_fig_missdepth    miss-depth histogram at 0.90, corrected labels, no deepest-miss annotation
#   (c) data/sts_n10_fig_boundary     histogram of corrected min_vm
#   (d) data/sts_n10_fig_budget       SURR / STATIC / ORACLE catch vs k, D94 and D95a (data/sts_n9_budget_curve.json)
#   (e) data/sts_n10_tables.tex       tab:models and tab:ops bodies, column layout of notes/paper_tables_v2.tex
# The (b) and (e) models are the N5 M2 configs (data/sts_n5_gate_094.json), refit exactly as N9 did.

N5 = "data/sts_n5_gate_094.json"
N9 = "data/sts_n9_budget_curve.json"
N2 = "data/sts_n2_label_audit.parquet"
DATA = "data/dataset.parquet"
LIMIT = 0.94
STRIP_HI = 0.945
MODELS = ["ridge", "histgb"]
COLORS = {"ridge": "#b8860b", "histgb": "#00798c", "persistence": "#d1495b", "oracle": "#555555"}
FS_LABEL, FS_TICK, FS_LEG, FS_ANNOT = 9, 7, 6, 7
OPS_TARGETS = [0.90, 0.94, 0.95, 0.96, 0.97, 0.98]
SEEDS = [0, 1, 2, 3, 4]


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def write_manifest(paths, inputs, params):
    man = sm.build_manifest(paths, "scratch/n10_paper_artifacts.py", [".venv/bin/python", "scratch/n10_paper_artifacts.py"],
                            inputs, params, "")
    man["no_new_solves"] = "No AC solve. Figures (b) and tables (e) refit the N5 M2 configs on D94 corrected labels; persistence and train-mean recomputed."
    sm.write_manifest(man, paths[0])


def n5_configs():
    n5 = json.load(open(N5))
    return [dict(seed=f["seed"], family=f["family"], tag=f["tag"], config=f["config"]) for f in n5["fits"]]


# ---------------------------------------------------------------- (a)

def fig_tradeoff():
    n5 = json.load(open(N5))
    pts = pd.DataFrame([p for p in n5["points"] if p["point"] == "sweep"])
    pts["t"] = pts["target"].round(2)
    vals = {}
    fig, axL = plt.subplots(figsize=(3.5, 2.7))
    axR = axL.twinx()
    ymax = 0.0
    for i, m in enumerate(MODELS):
        g = pts[pts.family == m].groupby("t")
        cov = np.array(sorted(pts[pts.family == m]["t"].unique()))
        esc = np.array([g.get_group(c)["escalation"].mean() for c in cov]) * 100
        esc_sd = np.array([g.get_group(c)["escalation"].std(ddof=0) for c in cov]) * 100
        mis = np.array([g.get_group(c)["missed"].mean() for c in cov]) * 100
        mis_sd = np.array([g.get_group(c)["missed"].std(ddof=0) for c in cov]) * 100
        ymax = max(ymax, esc.max())
        axL.fill_between(cov, esc - esc_sd, esc + esc_sd, color=COLORS[m], alpha=0.20, linewidth=0)
        axR.fill_between(cov, np.clip(mis - mis_sd, 0.0, None), mis + mis_sd, color=COLORS[m], alpha=0.12, linewidth=0)
        axL.plot(cov, esc, "-", lw=1.6, color=COLORS[m], label=f"{m} escalation")
        axR.plot(cov, mis, ":", lw=1.4, color=COLORS[m], label=f"{m} missed")
        safe = [c for c, v in zip(cov, mis) if v < 1.0]
        first = float(min(safe)) if safe else None
        if first is not None:
            axL.axvline(first, color=COLORS[m], lw=1.0, ls="-.")
            axL.text(first + (0.003 if i == 1 else -0.003), ymax * 0.05, f"{first:.2f}",
                     ha="left" if i == 1 else "right", va="bottom", fontsize=FS_ANNOT, color=COLORS[m])
        vals[m] = dict(first_sub_1pct_missed_coverage=first,
                       points=[dict(coverage_target=float(c), escalation=float(e / 100), escalation_std=float(es / 100),
                                    missed_viol=float(v / 100), missed_viol_std=float(vs / 100))
                               for c, e, es, v, vs in zip(cov, esc, esc_sd, mis, mis_sd)])
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
    fig.tight_layout()
    png = "data/sts_n10_fig_tradeoff.png"
    js = "data/sts_n10_fig_tradeoff.json"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    json.dump(dict(source=N5, labels="D94 switch-back (N2) corrected", std_convention="population std (ddof=0) over 5 splits",
                   units="fractions (0-1); the figure plots %", band="mean +- 1 std; missed band clipped at 0",
                   models=vals), open(js, "w"), indent=2)
    write_manifest([js, png], [N5], dict(figure="Fig. 2 equivalent, corrected labels",
                                         model_hyperparameters=n5_configs(), dpi=300, figsize_in=[3.5, 2.7]))


# ---------------------------------------------------------------- shared refit (b, e)

def refit_all():
    n5 = json.load(open(N5))
    d = bc.load("094")
    out = []
    for seed in SEEDS:
        splits = ms.make_splits(d["groups"], seed)
        kept = ms.select_features(d["X"], splits["train"])
        te = splits["test"]
        Xte = d["X"][kept].iloc[te].to_numpy(np.float32)
        y_te = d["y"][te]
        for fam in MODELS:
            f5 = bc.n5_config(n5, seed, fam)
            p_ca, y_ca, p_te = bc.fit_predict(d, seed, fam, f5["config"], Xte, kept)
            mae, r2 = tu.mae_r2(p_te, y_te)
            if mae != f5["mae"]:
                raise ValueError("refit does not reproduce N5 test MAE; stop")
            out.append(dict(seed=seed, family=fam, p_ca=p_ca, y_ca=y_ca, p_te=p_te, y_te=y_te, mae=mae, r2=r2,
                            ms_surrogate=f5["ms_surrogate"]))
        # persistence and train mean, as feasibility/run_all.py, on corrected labels
        n0 = d["df"]["n0_min_vm"].to_numpy(np.float64)
        y_tr = d["y"][splits["train"]]
        y_ca = d["y"][splits["cal"]]
        t0 = time.time()
        p_te = sg.predict_persistence(n0[te])
        dt = time.time() - t0
        mae, r2 = tu.mae_r2(p_te, y_te)
        out.append(dict(seed=seed, family="persistence", p_ca=sg.predict_persistence(n0[splits["cal"]]), y_ca=y_ca,
                        p_te=p_te, y_te=y_te, mae=mae, r2=r2, ms_surrogate=dt / len(y_te) * 1000.0))
        t0 = time.time()
        p_te = sg.predict_mean(y_tr, len(y_te))
        dt = time.time() - t0
        mae, r2 = tu.mae_r2(p_te, y_te)
        out.append(dict(seed=seed, family="train_mean", p_ca=sg.predict_mean(y_tr, len(y_ca)), y_ca=y_ca,
                        p_te=p_te, y_te=y_te, mae=mae, r2=r2, ms_surrogate=dt / len(y_te) * 1000.0))
    return out


# ---------------------------------------------------------------- (b)

def fig_missdepth(fits):
    depths = {}
    qh = {}
    for m in MODELS:
        dl = []
        ql = []
        for f in fits:
            if f["family"] != m:
                continue
            q = ge.calibrate_qhat(f["p_ca"], f["y_ca"], 0.90)
            cert = (f["p_te"] - q) >= LIMIT
            miss = cert & (f["y_te"] < LIMIT)
            dl.extend((LIMIT - f["y_te"][miss]).tolist())
            ql.append(q)
        depths[m] = np.array(dl)
        qh[m] = float(np.mean(ql))
    edges = np.arange(0, 0.095 + 0.001, 0.001)
    fig, axes = plt.subplots(2, 1, figsize=(3.5, 4.3), sharex=True)
    for ax, m in zip(axes, MODELS):
        ax.hist(depths[m], bins=edges, color=COLORS[m], linewidth=0)
        ax.set_yscale("log")
        ax.axvspan(0, 0.005, color="#cccccc", alpha=0.25, zorder=0)
        for side in ["top", "right"]:
            ax.spines[side].set_visible(False)
        ax.tick_params(labelsize=8)
        ax.set_xlim(0, 0.095)
        ax.axvline(qh[m], color="black", lw=1.2, ls="--", zorder=4)
        ax.text(qh[m] + 0.002, 0.90, f"q̂@0.90 = {qh[m]:.4f}", transform=ax.get_xaxis_transform(),
                fontsize=7, color="black", va="top", ha="left")
        ax.set_ylabel(f"{m}\nmiss count (log)", fontsize=9)
    axes[1].set_xlabel("miss depth below the 0.94 pu floor  d = 0.94 − Y  (per unit)", fontsize=9)
    fig.tight_layout()
    png = "data/sts_n10_fig_missdepth.png"
    js = "data/sts_n10_fig_missdepth.json"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    per = {}
    for m in MODELS:
        d = depths[m]
        per[m] = dict(n_misses=int(len(d)), max_depth_pu=float(d.max()) if len(d) else None, qhat90_mean=qh[m],
                      n_beyond_x_max_0p095=int((d > 0.095).sum()),
                      counts_per_bin=np.histogram(d, bins=edges)[0].tolist())
    json.dump(dict(labels="D94 switch-back (N2) corrected", coverage_target=0.90, pooled_over_seeds=SEEDS,
                   bin_edges=edges.tolist(), per_model=per), open(js, "w"), indent=2)
    write_manifest([js, png], [N5, N2, DATA], dict(figure="Fig. 3 equivalent, corrected labels, no deepest-miss annotation",
                                                   model_hyperparameters=n5_configs(), dpi=300, figsize_in=[3.5, 4.3]))


# ---------------------------------------------------------------- (c)

def fig_boundary():
    lab = pd.read_parquet(N2, columns=["outaged_type", "corrected_status", "corrected_min_vm"])
    lab = lab[(lab.outaged_type != "none") & lab.corrected_status.isin(["converged", "not_needed"])]
    v = lab["corrected_min_vm"].to_numpy(np.float64)
    lo, hi, binw, view_lo = 0.715, 0.965, 0.001, 0.87
    edges = np.arange(lo, hi + binw / 2, binw)
    counts, _ = np.histogram(v, bins=edges)
    share = 100.0 * counts / len(v)
    left = edges[:-1]
    col = [COLORS["persistence"] if e < LIMIT - 1e-9 else COLORS["histgb"] for e in left]
    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    ax.bar(left, share, width=binw, align="edge", color=col, linewidth=0)
    ax.axvspan(LIMIT, STRIP_HI, color=COLORS["ridge"], alpha=0.20, zorder=0)
    ax.axvline(LIMIT, color="black", lw=1.5, zorder=3)
    ax.text(LIMIT - 0.0015, share.max() * 0.99, "under-voltage limit (0.94 pu)", ha="right", va="top", fontsize=8)
    ax.set_xlabel("minimum bus voltage after a contingency (per unit)", fontsize=9)
    ax.set_ylabel("share of contingency cases (%)", fontsize=9)
    ax.set_xlim(view_lo, hi)
    ax.tick_params(labelsize=8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    png = "data/sts_n10_fig_boundary.png"
    js = "data/sts_n10_fig_boundary.json"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    json.dump(dict(labels="D94 switch-back (N2) corrected; failed rows dropped", n_rows=int(len(v)),
                   n_below_hist_range=int((v < lo).sum()), n_above_hist_range=int((v >= hi).sum()),
                   boundary_mass_0p94_0p945=float(((v >= LIMIT) & (v < STRIP_HI)).mean()),
                   violation_rate=float((v < LIMIT).mean()), share_below_view_0p87=float((v < view_lo).mean()),
                   tallest_bin_pct=float(share.max()), tallest_bin_left=float(left[share.argmax()]),
                   bin_edges=edges.tolist(), share_pct=share.tolist()), open(js, "w"), indent=2)
    write_manifest([js, png], [N2], dict(figure="Fig. 4 equivalent, corrected labels, no prose",
                                         model_hyperparameters="none (model-independent)", dpi=300, figsize_in=[3.5, 2.6]))


# ---------------------------------------------------------------- (d)

def fig_budget():
    b = json.load(open(N9))
    cv = pd.DataFrame(b["curves"])
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7), sharey=True)
    vals = {}
    for ax, ds in zip(axes, ["D94", "D95a"]):
        vals[ds] = {}
        k = np.arange(1, b["k_max"] + 1)
        for fam in MODELS:
            m = cv[(cv.dataset == ds) & (cv.family == fam)]
            s = np.array(m["surr"].tolist()) * 100
            mu, sd = s.mean(0), s.std(0)
            ax.fill_between(k, mu - sd, mu + sd, color=COLORS[fam], alpha=0.20, linewidth=0)
            ax.plot(k, mu, "-", lw=1.4, color=COLORS[fam], label=f"{fam} ranking")
            vals[ds][f"surr_{fam}"] = dict(mean=mu.tolist(), std=sd.tolist())
        m = cv[(cv.dataset == ds) & (cv.family == "histgb")]
        for kind, style, c in [("static", "--", COLORS["persistence"]), ("oracle", ":", COLORS["oracle"])]:
            s = np.array(m[kind].tolist()) * 100
            mu, sd = s.mean(0), s.std(0)
            ax.fill_between(k, mu - sd, mu + sd, color=c, alpha=0.15, linewidth=0)
            ax.plot(k, mu, style, lw=1.3, color=c, label=f"{kind} ranking")
            vals[ds][kind] = dict(mean=mu.tolist(), std=sd.tolist())
        for kk in b["k_declared"]:
            ax.axvline(kk, color="grey", lw=0.6, ls=":", zorder=0)
        ax.set_xlim(1, 130)
        ax.set_ylim(40, 100.5)
        ax.set_xlabel("solve budget k (contingencies per base case)", fontsize=FS_LABEL)
        ax.set_title(ds, fontsize=FS_LABEL)
        ax.tick_params(labelsize=FS_TICK)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("violations caught (%)", fontsize=FS_LABEL)
    axes[0].legend(fontsize=FS_LEG, loc="lower right", framealpha=0.9)
    fig.tight_layout()
    png = "data/sts_n10_fig_budget.png"
    js = "data/sts_n10_fig_budget.json"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    json.dump(dict(source=N9, labels="switch-back corrected (D94 N2, D95a N5)", k=list(range(1, b["k_max"] + 1)),
                   x_view=[1, 130], declared_k_marked=b["k_declared"], std_convention="population std (ddof=0) over 5 splits",
                   units="percent", curves=vals), open(js, "w"), indent=2)
    write_manifest([js, png], [N9], dict(figure="budget curve SURR/STATIC/ORACLE, D94 and D95a",
                                         model_hyperparameters="N5 M2 configs (see data/sts_n9_budget_curve.manifest.json)",
                                         dpi=300, figsize_in=[7.0, 2.7]))


# ---------------------------------------------------------------- (e)

def gate_stats(f, cov):
    q = ge.calibrate_qhat(f["p_ca"], f["y_ca"], cov)
    g = ge.run_gate(f["p_te"], q, LIMIT)
    return ge.score(g, f["y_te"], f["ms_surrogate"], json.load(open(N5))["ms_solver"], LIMIT)


def tables(fits):
    rows = {}
    for fam in MODELS + ["persistence", "train_mean"]:
        fs = [f for f in fits if f["family"] == fam]
        rows[fam] = {}
        for cov in OPS_TARGETS:
            s = [gate_stats(f, cov) for f in fs]
            rows[fam][cov] = dict(esc=ms_([x["escalation"] * 100 for x in s]), cov=ms_([x["coverage"] * 100 for x in s]),
                                  mis=ms_([x["missed_viol"] * 100 for x in s]), spd=ms_([x["net_speedup"] for x in s]))
        rows[fam]["mae"] = ms_([f["mae"] * 1000 for f in fs])
        rows[fam]["r2"] = ms_([f["r2"] for f in fs])
    ops = []
    for fam in MODELS:
        lab = "ridge " if fam == "ridge" else "histgb"
        for cov in OPS_TARGETS:
            r = rows[fam][cov]
            ops.append(f"{lab} & {cov:.2f} & {r['esc'][0]:.1f}$\\pm${r['esc'][1]:.1f} & {r['cov'][0]:.1f}$\\pm${r['cov'][1]:.1f} & "
                       f"{r['mis'][0]:.2f}$\\pm${r['mis'][1]:.2f} & {r['spd'][0]:.2f}$\\pm${r['spd'][1]:.2f} \\\\")
    mod = []
    for fam, name in [("persistence", "persistence"), ("train_mean", "train mean "), ("ridge", "ridge      "), ("histgb", "histgb     ")]:
        r = rows[fam]
        g = r[0.90]
        spd = f"{g['spd'][0]:.2f}$\\pm${g['spd'][1]:.2f}"
        if g["spd"][0] >= 1000.0:
            ex = int(np.floor(np.log10(g["spd"][0])))
            spd = f"${g['spd'][0] / 10 ** ex:.1f}{{\\times}}10^{{{ex}\\dagger}}$"
        r2 = f"{r['r2'][0]:.2f}$\\pm${r['r2'][1]:.2f}"
        if r["r2"][0] < 0:
            r2 = f"${r['r2'][0]:.2f}\\pm{r['r2'][1]:.2f}$"
        mod.append(f"{name} & {r['mae'][0]:.1f}$\\pm${r['mae'][1]:.1f} & {r2} & {g['esc'][0]:.1f}$\\pm${g['esc'][1]:.1f} & "
                   f"{g['mis'][0]:.2f}$\\pm${g['mis'][1]:.2f} & {spd} \\\\")
    text = ("% N10 Part C: table bodies on CORRECTED labels (D94 = N2 switch-back labels). Generated by\n"
            "% scratch/n10_paper_artifacts.py from the N5 M2 configs (data/sts_n5_gate_094.json), refit exactly as N9.\n"
            "% Column layout of notes/paper_tables_v2.tex. persistence and train-mean are RECOMPUTED on corrected\n"
            "% labels as in feasibility/run_all.py (not copied from the committed stored-label rows); their R2 is\n"
            "% computed, not the hard-coded strings of scripts/emit_v2_tables.py. speedup = paper Eq. 2 (rule A),\n"
            "% t_solve from data/solve_time.json, t_surr measured per model. The surrounding tabular spec must be\n"
            "% reconciled against the paper before pasting; this file guarantees the numbers only.\n\n"
            "%%%%%%%%%% tab:ops body (12 rows) %%%%%%%%%%\n" + "\n".join(ops) + "\n\n"
            "%%%%%%%%%% tab:models body (all rows recomputed on corrected labels) %%%%%%%%%%\n" + "\n".join(mod) + "\n")
    tex = "data/sts_n10_tables.tex"
    with open(tex, "w") as f:
        f.write(text)
    js = "data/sts_n10_tables.json"
    json.dump(dict(labels="D94 switch-back (N2) corrected", std_convention="population std (ddof=0) over 5 splits",
                   rows={fam: {str(k): v for k, v in rows[fam].items()} for fam in rows}), open(js, "w"), indent=2)
    write_manifest([tex, js], [N5, N2, DATA, "data/solve_time.json"],
                   dict(tables="tab:ops and tab:models bodies, corrected labels", model_hyperparameters=n5_configs(),
                        baselines="persistence = n0_min_vm; train mean = mean of train y (feasibility/surrogate.py)"))
    print(text)


def main():
    fig_tradeoff()
    fig_boundary()
    fig_budget()
    fits = refit_all()
    fig_missdepth(fits)
    tables(fits)
    print("done")


if __name__ == "__main__":
    main()
