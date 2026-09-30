import os
import sys
import json
import time
import platform
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scratch"))
sys.path.insert(0, HERE)
import make_splits as ms
import gate_eval as ge
import manifest as mf
import classical_manifest as cm
import tune_surrogates as tu
import n9_budget_curve as bc

# Paper figures and table bodies rebuilt on the switch-back (corrected) labels, case118 0.94 floor
# (D94 = data/dataset.parquet + data/sts_n2_label_audit.parquet). Model configs, splits and the
# held-out targets are the N5 M2 selections (data/sts_n5_gate_094.json), unchanged.
# Outputs (each with a manifest):
#   data/sts_paper_fig2_tradeoff.png/.json    escalation and missed vs target, +-1 std bands
#   data/sts_paper_fig3_missdepth.png/.json   miss depth at target 0.90, pooled over 5 splits
#   data/sts_paper_fig4_boundary.png/.json    histogram of corrected post-contingency minimum voltage
#   data/sts_paper_fig_budget.png/.json       violations caught vs solve budget (N9 budget curve)
#   data/sts_paper_tables.tex/.json           table bodies: models, ops, floor, gate vs static
# usage: .venv/bin/python scripts/sts_paper_corrected.py

SCRIPT = "scripts/sts_paper_corrected.py"
N5_094 = "data/sts_n5_gate_094.json"
N5_095 = "data/sts_n5_gate_095.json"
N5_VERDICT = "data/sts_n5_verdict.json"
N2 = "data/sts_n2_label_audit.parquet"
SCREENER = "data/screener_metrics.json"
BUDGET = "data/sts_n9_budget_curve.json"
SHIFT = "data/sts_n9_shift.json"
FLOOR = "data/sts_n9_floor_replication.json"
PRED = "scratch/n3_floor_prediction.md"
OUT = "data"
LIMIT = 0.94
STRIP_HI = 0.945
SEEDS = [0, 1, 2, 3, 4]
MODELS = ["ridge", "histgb"]
COLORS = {"persistence": "#d1495b", "ridge": "#b8860b", "histgb": "#00798c"}
C_STATIC = "#555555"
C_ORACLE = "#999999"
OPS_TARGETS = [0.90, 0.94, 0.95, 0.96, 0.97, 0.98]


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def pm(a, scale, nd):
    mu, sd = ms_(np.asarray(a, dtype=float) * scale)
    m = f"{mu:.{nd}f}"
    if m.startswith("-") and float(m) == 0.0:
        m = m[1:]
    if m.startswith("-"):
        return f"${m}\\pm{sd:.{nd}f}$"
    return f"{m}$\\pm${sd:.{nd}f}"


def write_manifest(path_json, outputs, inputs, settings):
    man = dict(generating_script=SCRIPT, regeneration_argv=[".venv/bin/python", SCRIPT],
               inputs=[dict(path=p, sha256=cm.content_hash(p)) for p in inputs],
               outputs=[dict(path=p, sha256=cm.content_hash(p)) for p in outputs],
               settings=settings, labels="switch-back corrected min_vm (N2 method); 1 failed row dropped",
               model_hyperparameters=m2_configs(),
               plotting_library=f"matplotlib {matplotlib.__version__}", python=platform.python_version(),
               packages={p: mf.pkg_version(p) for p in mf.PACKAGES},
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(mf.manifest_path(path_json), "w") as f:
        json.dump(man, f, indent=2)


def m2_configs():
    g = json.load(open(N5_094))
    out = {}
    for f in g["fits"]:
        out[f"{f['family']}_seed{f['seed']}"] = f["config"]
    return out


# ---------------------------------------------------------------- Fig. 2 (trade-off with bands)

def fig2(g):
    sw = pd.DataFrame([p for p in g["points"] if p["point"] == "sweep"])
    sw["t"] = sw["target"].round(2)
    fig, axL = plt.subplots(figsize=(3.5, 2.7))
    axR = axL.twinx()
    vals = {}
    for m in MODELS:
        s = sw[sw.family == m].groupby("t")
        t = np.array(sorted(sw[sw.family == m]["t"].unique()))
        esc = s["escalation"].mean().loc[t].to_numpy() * 100
        esc_sd = s["escalation"].std(ddof=0).loc[t].to_numpy() * 100
        mis = s["missed"].mean().loc[t].to_numpy() * 100
        mis_sd = s["missed"].std(ddof=0).loc[t].to_numpy() * 100
        axL.fill_between(t, esc - esc_sd, esc + esc_sd, color=COLORS[m], alpha=0.20, linewidth=0)
        axR.fill_between(t, np.clip(mis - mis_sd, 0.0, None), mis + mis_sd, color=COLORS[m], alpha=0.12, linewidth=0)
        axL.plot(t, esc, "-", lw=1.6, color=COLORS[m], label=f"{m} escalation")
        axR.plot(t, mis, ":", lw=1.4, color=COLORS[m], label=f"{m} missed")
        vals[m] = [dict(target=float(a), escalation=float(b / 100), escalation_std=float(c / 100),
                        missed=float(d / 100), missed_std=float(e / 100))
                   for a, b, c, d, e in zip(t, esc, esc_sd, mis, mis_sd)]
    axR.axhline(1.0, color="grey", lw=0.9, ls=":")
    axL.set_xlim(0.70, 0.99)
    axL.set_xlabel("target coverage", fontsize=9)
    axL.set_ylabel("escalation (%)", fontsize=9)
    axR.set_ylabel("missed-violation (% of true violations)", fontsize=9)
    axL.tick_params(labelsize=7)
    axR.tick_params(labelsize=7)
    axL.grid(alpha=0.3)
    lL, nL = axL.get_legend_handles_labels()
    lR, nR = axR.get_legend_handles_labels()
    axL.legend(lL + lR, nL + nR, fontsize=6, loc="upper left", ncol=2, framealpha=0.9)
    fig.tight_layout()
    png = f"{OUT}/sts_paper_fig2_tradeoff.png"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    js = png.replace(".png", ".json")
    json.dump(dict(source=N5_094 + " points[point=sweep]", std="population ddof=0 over 5 splits",
                   note="no operating-point markers: the old 0.94/0.97 markers were test-picked", models=vals),
              open(js, "w"), indent=2)
    write_manifest(js, [png, js], [N5_094], dict(figure="Fig. 2 equivalent, corrected labels", figsize_in=[3.5, 2.7], dpi=300,
                                                 grey_dotted_line="1% missed"))
    print("wrote", png)


# ---------------------------------------------------------------- refit for Fig. 3 and Table 1 checks

def refits(d, g):
    out = []
    for seed in SEEDS:
        spl = ms.make_splits(d["groups"], seed)
        kept = ms.select_features(d["X"], spl["train"])
        Xte = d["X"][kept].iloc[spl["test"]].to_numpy(np.float32)
        y_te = d["y"][spl["test"]]
        for fam in MODELS:
            f5 = bc.n5_config(g, seed, fam)
            p_ca, y_ca, p_te = bc.fit_predict(d, seed, fam, f5["config"], Xte, kept)
            q = ge.calibrate_qhat(p_ca, y_ca, 0.90)
            cert = (p_te - q) >= LIMIT
            flag = p_te < LIMIT
            esc = (~cert) & (~flag)
            tv = y_te < LIMIT
            ref = [p for p in g["points"] if p["seed"] == seed and p["family"] == fam and p["point"] == "grid"
                   and round(p["target"], 2) == 0.90][0]
            out.append(dict(seed=seed, family=fam, q_hat=float(q), depths=(LIMIT - y_te[cert & tv]).tolist(),
                            escalation=float(esc.mean()), missed=float((cert & tv).sum() / tv.sum()),
                            d_esc_vs_n5=abs(float(esc.mean()) - ref["escalation"]),
                            d_missed_vs_n5=abs(float((cert & tv).sum() / tv.sum()) - ref["missed"])))
            print(f"  refit seed {seed} {fam}: esc {out[-1]['escalation']:.4f} (N5 {ref['escalation']:.4f})", flush=True)
    return out


def fig3(rf):
    fig, axes = plt.subplots(2, 1, figsize=(3.5, 4.3), sharex=True)
    edges = np.arange(0, 0.095 + 0.001, 0.001)
    vals = {}
    for ax, m in zip(axes, MODELS):
        dep = np.concatenate([np.asarray(r["depths"]) for r in rf if r["family"] == m])
        qmean = float(np.mean([r["q_hat"] for r in rf if r["family"] == m]))
        ax.hist(dep, bins=edges, color=COLORS[m], linewidth=0)
        ax.set_yscale("log")
        ax.axvspan(0, 0.005, color="#cccccc", alpha=0.25, zorder=0)
        for side in ["top", "right"]:
            ax.spines[side].set_visible(False)
        ax.tick_params(labelsize=8)
        ax.set_xlim(0, 0.095)
        ax.axvline(qmean, color="black", lw=1.2, ls="--", zorder=4)
        ax.text(qmean + 0.002, 0.90, f"q̂@0.90 = {qmean:.4f}", transform=ax.get_xaxis_transform(),
                fontsize=7, color="black", va="top", ha="left")
        ax.set_ylabel(f"{m}\nmiss count (log)", fontsize=9)
        vals[m] = dict(n_misses_pooled=int(len(dep)), qhat90_mean=qmean,
                       share_within_qhat=float((dep <= qmean).mean()) if len(dep) else None,
                       share_deeper_than_0p005=float((dep > 0.005).mean()) if len(dep) else None,
                       max_depth=float(dep.max()) if len(dep) else None, p99_depth=float(np.quantile(dep, 0.99)) if len(dep) else None)
    axes[1].set_xlabel("miss depth below the 0.94 pu floor  d = 0.94 − Y  (per unit)", fontsize=9)
    fig.tight_layout()
    png = f"{OUT}/sts_paper_fig3_missdepth.png"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    js = png.replace(".png", ".json")
    rep = dict(max_abs_diff_escalation_vs_n5=max(r["d_esc_vs_n5"] for r in rf),
               max_abs_diff_missed_vs_n5=max(r["d_missed_vs_n5"] for r in rf))
    json.dump(dict(target=0.90, pooled_over_splits=SEEDS, reproduction_of_n5=rep, models=vals), open(js, "w"), indent=2)
    write_manifest(js, [png, js], [N5_094, N2], dict(figure="Fig. 3 equivalent, corrected labels, no deepest-miss annotation",
                                                     figsize_in=[3.5, 4.3], dpi=300, bin_width_pu=0.001, shaded="[0, 0.005) pu"))
    print("wrote", png, rep)


# ---------------------------------------------------------------- Fig. 4 (boundary histogram)

def fig4():
    a = pd.read_parquet(N2, columns=["outaged_type", "corrected_status", "corrected_min_vm"])
    a = a[(a.outaged_type != "none") & a.corrected_status.isin(["converged", "not_needed"])]
    v = a.corrected_min_vm.to_numpy()
    lo, hi, bw, view_lo = 0.715, 0.965, 0.001, 0.87
    edges = np.arange(lo, hi + bw / 2, bw)
    counts, _ = np.histogram(v, bins=edges)
    share = 100.0 * counts / len(v)
    left = edges[:-1]
    colors = [COLORS["persistence"] if e < LIMIT - 1e-9 else COLORS["histgb"] for e in left]
    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    ax.bar(left, share, width=bw, align="edge", color=colors, linewidth=0)
    ax.axvspan(LIMIT, STRIP_HI, color=COLORS["ridge"], alpha=0.20, zorder=0)
    ax.axvline(LIMIT, color="black", lw=1.5, zorder=3)
    ax.set_xlabel("minimum bus voltage after a contingency (per unit)", fontsize=9)
    ax.set_ylabel("share of contingency cases (%)", fontsize=9)
    ax.set_xlim(view_lo, hi)
    ax.tick_params(labelsize=8)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    png = f"{OUT}/sts_paper_fig4_boundary.png"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    js = png.replace(".png", ".json")
    strip = (v >= LIMIT) & (v < STRIP_HI)
    json.dump(dict(n_rows=int(len(v)), boundary_mass_pct=float(100 * strip.mean()),
                   conditional_boundary_pct=float(100 * strip.sum() / (v >= LIMIT).sum()),
                   violation_rate_pct=float(100 * (v < LIMIT).mean()),
                   tallest_bin_left=float(left[share.argmax()]), tallest_bin_share_pct=float(share.max()),
                   share_below_view_lo_pct=float(100 * (v < view_lo).mean()), min=float(v.min()), max=float(v.max())),
              open(js, "w"), indent=2)
    write_manifest(js, [png, js], [N2], dict(figure="Fig. 4 equivalent, corrected labels", figsize_in=[3.5, 2.6], dpi=300,
                                             hist_range=[lo, hi], view=[view_lo, hi], bin_width_pu=bw, shaded="[0.94, 0.945)"))
    print("wrote", png)


# ---------------------------------------------------------------- new: budget-curve figure

def fig_budget():
    b = json.load(open(BUDGET))
    cur = [c for c in b["curves"] if c["family"] == "histgb"]
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.7), sharey=True)
    vals = {}
    for ax, ds, title_key in zip(axes, ["D94", "D95a"], ["0.94", "0.95"]):
        cc = [c for c in cur if c["dataset"] == ds]
        k = np.arange(1, len(cc[0]["surr"]) + 1)
        for key, col, lab, ls in [("surr", COLORS["histgb"], "histgb ranking", "-"),
                                  ("static", C_STATIC, "static history ranking", "--"),
                                  ("oracle", C_ORACLE, "perfect ranking", ":")]:
            arr = np.array([c[key] for c in cc]) * 100
            mu = arr.mean(axis=0)
            sd = arr.std(axis=0)
            if key != "oracle":
                ax.fill_between(k, mu - sd, mu + sd, color=col, alpha=0.18, linewidth=0)
            ax.plot(k, mu, ls, lw=1.4, color=col, label=lab)
        ax.set_xlabel(f"contingencies solved per base case, k\n(generator voltage floor {title_key} pu)", fontsize=8)
        ax.set_xlim(0, 130)
        ax.set_ylim(40, 100.5)
        ax.grid(alpha=0.3)
        ax.tick_params(labelsize=7)
        vals[ds] = dict(n_splits=len(cc), k_max=int(len(k)))
    axes[0].set_ylabel("true violations caught (%)", fontsize=9)
    axes[0].legend(fontsize=6, loc="lower right", framealpha=0.9)
    fig.tight_layout()
    png = f"{OUT}/sts_paper_fig_budget.png"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    js = png.replace(".png", ".json")
    json.dump(dict(source=BUDGET, family="histgb", band="+-1 std (ddof=0) over 5 splits; oracle drawn without band",
                   declared_k_table="see data/sts_n9_budget_curve.json -> table", panels=vals,
                   x_view="k in [0, 130] of 186"), open(js, "w"), indent=2)
    write_manifest(js, [png, js], [BUDGET], dict(figure="new: violations caught vs solve budget", figsize_in=[6.5, 2.7], dpi=300))
    print("wrote", png)


# ---------------------------------------------------------------- tables

def baseline_rows(d):
    sm = json.load(open(SCREENER))
    t_surr = {}
    for r in sm["records"]:
        t_surr.setdefault(r["model"], {})[r["seed"]] = r["ms_surrogate"]
    ms_solver = json.load(open(N5_094))["ms_solver"]
    n0 = d["df"]["n0_min_vm"].to_numpy(np.float64)
    rows = []
    for seed in SEEDS:
        spl = ms.make_splits(d["groups"], seed)
        tr, ca, te = spl["train"], spl["cal"], spl["test"]
        y_ca, y_te = d["y"][ca], d["y"][te]
        for model in ["persistence", "train_mean"]:
            if model == "persistence":
                p_ca, p_te = n0[ca], n0[te]
            else:
                mu = float(d["y"][tr].mean())
                p_ca, p_te = np.full(len(ca), mu), np.full(len(te), mu)
            q = ge.calibrate_qhat(p_ca, y_ca, 0.90)
            cert = (p_te - q) >= LIMIT
            flag = p_te < LIMIT
            esc = (~cert) & (~flag)
            tv = y_te < LIMIT
            n = len(y_te)
            ts = t_surr[model][seed]
            n_solved = int(esc.sum())
            speed = n * ms_solver / (n * ts + n_solved * ms_solver)
            ss = float(np.sum((y_te - p_te) ** 2))
            st = float(np.sum((y_te - y_te.mean()) ** 2))
            rows.append(dict(seed=seed, model=model, mae=float(np.mean(np.abs(p_te - y_te))), r2=1.0 - ss / st,
                             escalation=float(esc.mean()), flag_share=float(flag.mean()),
                             missed=float((cert & tv).sum() / tv.sum()), speedup_A=float(speed),
                             never_calls_solver=bool(n_solved == 0),
                             train_mean_value=(mu if model == "train_mean" else None)))
    return rows


def tables(d, g):
    lines = ["% Table bodies on switch-back (corrected) labels, case118 0.94 floor. Generated by",
             f"% {SCRIPT}. Column layout follows notes/paper_tables_v2.tex; reconcile the tabular spec before",
             "% pasting. Means +- population std (ddof=0) over 5 splits. You write the captions.", ""]
    out = {}
    fits = pd.DataFrame(g["fits"])
    pts = pd.DataFrame([p for p in g["points"] if p["point"] in ("grid", "held_out")])
    pts["t"] = pts["target"].round(2)

    # tab:models
    base = pd.DataFrame(baseline_rows(d))
    lines.append("%%%%%%%%%% tab:models body (target 0.90) %%%%%%%%%%")
    rows_models = []
    for model in ["persistence", "train_mean"]:
        b = base[base.model == model]
        sp = pm(b.speedup_A, 1, 2) if not b.never_calls_solver.all() else "N/A$^{\\dagger}$"
        rows_models.append(f"{'train mean' if model == 'train_mean' else model:11s} & {pm(b.mae, 1000, 1)} & {pm(b.r2, 1, 2)} & "
                           f"{pm(b.escalation, 100, 1)} & {pm(b.missed, 100, 2)} & {sp} \\\\")
    for fam in MODELS:
        f = fits[fits.family == fam]
        p = pts[(pts.family == fam) & (pts.point == "grid") & (pts.t == 0.90)]
        rows_models.append(f"{fam:11s} & {pm(f.mae, 1000, 1)} & {pm(f.r2, 1, 2)} & {pm(p.escalation, 100, 1)} & "
                           f"{pm(p.missed, 100, 2)} & {pm(p.speedup_A, 1, 2)} \\\\")
    lines += rows_models + [""]
    out["tab_models_baselines_per_seed"] = base.to_dict("records")

    # tab:ops (rule A as in the paper) and a variant with rule-B speedup
    lines.append("%%%%%%%%%% tab:ops body: model & target & esc & cov & missed & speedup(A) %%%%%%%%%%")
    ops_rows = []
    for fam in MODELS:
        for t in OPS_TARGETS:
            p = pts[(pts.family == fam) & (pts.point == "grid") & (pts.t == t)]
            ops_rows.append((fam, f"{t:.2f}", p))
        h = pts[(pts.family == fam) & (pts.point == "held_out")]
        ops_rows.append((fam, f"held-out ({pm(h.target, 1, 2)})", h))
    for fam, lab, p in ops_rows:
        lines.append(f"{fam:6s} & {lab} & {pm(p.escalation, 100, 1)} & {pm(p.coverage_emp, 100, 1)} & "
                     f"{pm(p.missed, 100, 2)} & {pm(p.speedup_A, 1, 2)} \\\\")
    lines += ["", "%%%%%%%%%% tab:ops variant: ... & speedup(A) & speedup(B, flagged cases also solved) %%%%%%%%%%"]
    for fam, lab, p in ops_rows:
        lines.append(f"{fam:6s} & {lab} & {pm(p.escalation, 100, 1)} & {pm(p.coverage_emp, 100, 1)} & "
                     f"{pm(p.missed, 100, 2)} & {pm(p.speedup_A, 1, 2)} & {pm(p.speedup_B, 1, 2)} \\\\")
    lines.append("")
    splits_le1 = {fam: int((pts[(pts.family == fam) & (pts.point == "held_out")].missed <= 0.01).sum()) for fam in MODELS}
    out["held_out_splits_missed_le_1pct"] = splits_le1

    # floor experiment table
    fl = json.load(open(FLOOR))
    a = pd.read_parquet(N2, columns=["outaged_type", "corrected_status", "corrected_min_vm", "stored_min_vm"])
    a = a[(a.outaged_type != "none") & a.corrected_status.isin(["converged", "not_needed"])]
    sv = a.stored_min_vm.to_numpy()
    cv = a.corrected_min_vm.to_numpy()

    def bm(v):
        s = (v >= LIMIT) & (v < STRIP_HI)
        return 100 * s.mean(), 100 * s.sum() / (v >= LIMIT).sum(), 100 * (v < LIMIT).mean()
    lines.append("%%%%%%%%%% floor table: build & BM & CBM & VR (stored labels) & BM & VR (corrected) %%%%%%%%%%")
    s94 = bm(sv)
    c94 = bm(cv)
    lines.append(f"floor 0.94 (committed) & {s94[0]:.2f} & {s94[1]:.2f} & {s94[2]:.2f} & {c94[0]:.2f} & {c94[2]:.2f} \\\\")
    out["floor_094"] = dict(stored=dict(bm=s94[0], cbm=s94[1], vr=s94[2]), corrected=dict(bm=c94[0], cbm=c94[1], vr=c94[2]))
    seeds_of = {"D95a": "100-103", "D95b": "200-203", "D95c": "300-303"}
    for r in fl["per_build"]:
        st, co = r["stored"], r["corrected"]
        lines.append(f"floor 0.95, seeds {seeds_of.get(r['build'], r['build'])} & {st['BM']:.2f} & {st['CBM']:.2f} & "
                     f"{st['VR']:.2f} & {co['BM']:.2f} & {co['VR']:.2f} \\\\")
    ab = fl["across_builds"]
    lines.append(f"floor 0.95, mean$\\pm$std & {ab['stored']['BM']['mean']:.2f}$\\pm${ab['stored']['BM']['std_ddof0']:.2f} & "
                 f"{ab['stored']['CBM']['mean']:.2f}$\\pm${ab['stored']['CBM']['std_ddof0']:.2f} & "
                 f"{ab['stored']['VR']['mean']:.2f}$\\pm${ab['stored']['VR']['std_ddof0']:.2f} & "
                 f"{ab['corrected']['BM']['mean']:.2f}$\\pm${ab['corrected']['BM']['std_ddof0']:.2f} & "
                 f"{ab['corrected']['VR']['mean']:.2f}$\\pm${ab['corrected']['VR']['std_ddof0']:.2f} \\\\")
    pr = fl["n3_predicted_ranges_pct"]
    lines.append(f"prediction (hashed before the builds) & {pr['BM'][0]:.0f} [{pr['BM'][1]:.0f}--{pr['BM'][2]:.0f}] & "
                 f"{pr['CBM'][0]:.0f} [{pr['CBM'][1]:.0f}--{pr['CBM'][2]:.0f}] & {pr['VR'][0]:.1f} [{pr['VR'][1]:.0f}--{pr['VR'][2]:.0f}] & -- & -- \\\\")
    lines.append("% std over 3 builds is population (ddof=0); ddof=1 values are in data/sts_n9_floor_replication.json")
    lines.append("")

    # gate vs static
    lines.append("%%%%%%%%%% gate vs static, held-out point, rule B: setting & model & solved & gate catch & static catch %%%%%%%%%%")
    gv = []
    for name, path in [("0.94 floor", N5_094), ("0.95 floor", N5_095)]:
        gj = json.load(open(path))
        for fam in MODELS:
            h = pd.DataFrame([p for p in gj["points"] if p["point"] == "held_out" and p["family"] == fam])
            gm_, gs_ = ms_(h.gate_catch)
            sm_, ss_ = ms_(h.static_catch_B)
            gap = gm_ - sm_
            verdict = "tie" if abs(gap) <= max(gs_, ss_) else ("gate higher" if gap > 0 else "static higher")
            lines.append(f"{name} & {fam} & {pm(h.solve_share_B, 100, 1)} & {pm(h.gate_catch, 100, 2)} & "
                         f"{pm(h.static_catch_B, 100, 2)} \\\\  % {verdict}")
            gv.append(dict(setting=name, family=fam, gate=gm_, gate_std=gs_, static=sm_, static_std=ss_, verdict=verdict))
    sh = json.load(open(SHIFT))
    for s in sh["summary"]:
        if s["source"] == "D94" and s["target"] == "D95a":
            gap = s["gap"]
            verdict = "tie" if abs(gap) <= s["STD"] else ("gate higher" if gap > 0 else "static higher")
            lines.append(f"shift 0.94$\\to$0.95 & {s['family']} & {100 * s['solve_share_B_mean']:.1f}$\\pm${100 * s['solve_share_B_std']:.1f} & "
                         f"{100 * s['gate_catch_mean']:.2f}$\\pm${100 * s['gate_catch_std']:.2f} & "
                         f"{100 * s['static_catch_B_mean']:.2f}$\\pm${100 * s['static_catch_B_std']:.2f} \\\\  % {verdict}")
            gv.append(dict(setting="shift", family=s["family"], gate=s["gate_catch_mean"], static=s["static_catch_B_mean"], verdict=verdict))
    out["gate_vs_static"] = gv

    tex = f"{OUT}/sts_paper_tables.tex"
    open(tex, "w").write("\n".join(lines) + "\n")
    js = f"{OUT}/sts_paper_tables.json"
    json.dump(out, open(js, "w"), indent=2, default=float)
    write_manifest(js, [tex, js], [N5_094, N5_095, N2, SCREENER, FLOOR, SHIFT],
                   dict(tables=["tab:models", "tab:ops (+ rule-B variant)", "floor 0.94 reference row", "gate vs static"],
                        baseline_speedup="Eq. 2 with each baseline's per-seed ms_surrogate from data/screener_metrics.json",
                        persistence_prediction="stored n0_min_vm (an input feature), as in feasibility/run_all.py"))
    print("wrote", tex)


def main():
    t0 = time.time()
    g = json.load(open(N5_094))
    fig2(g)
    fig4()
    fig_budget()
    d = bc.load("094")
    tables(d, g)
    rf = refits(d, g)
    fig3(rf)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
