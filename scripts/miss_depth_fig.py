import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import tune_surrogates as T
import classical_manifest as cm
import manifest as mf

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figtools as ft

LIMIT = 0.94
SEEDS = 5
COV = 0.90
STRIP = 0.005
XHI = 0.095
DEEPEST = 0.09146
COLORS = {"ridge": "#b8860b", "histgb": "#00798c"}
C_DEEP = "#d1495b"
FS_LABEL, FS_ANNOT = 9, 8


def m2_configs():
    tm = json.load(open("data/tuned_metrics.json"))
    cfg = {}
    for r in tm["records"]:
        if r["metric"] == "m2":
            cfg[(r["family"], r["seed"])] = r["config"]
    return cfg


def collect_depths(cfg):
    df, feature_cols = ms.load_dataset("data/dataset.parquet")
    X, y, groups, _b = ms.build_design_matrix(df, feature_cols)
    depths = {"ridge": [], "histgb": []}
    qrows = {"ridge": [], "histgb": []}
    qhat90 = {"ridge": [], "histgb": []}
    for seed in range(SEEDS):
        sp = ms.make_splits(groups, seed)
        kept = ms.select_features(X, sp["train"]); Xk = X[kept]
        Xtr = Xk.iloc[sp["train"]].to_numpy(np.float32); ytr = y[sp["train"]]
        Xca = Xk.iloc[sp["cal"]].to_numpy(np.float32); yca = y[sp["cal"]]
        Xte = Xk.iloc[sp["test"]].to_numpy(np.float32); yte = y[sp["test"]]
        tv = yte < LIMIT
        for fam in ("ridge", "histgb"):
            fitted = T.fit_one(fam, cfg[(fam, seed)], Xtr, ytr, seed)
            q = ge.calibrate_qhat(T.predict(fitted, Xca), yca, COV)
            qhat90[fam].append(float(q))
            gate = ge.run_gate(T.predict(fitted, Xte), q, LIMIT)
            missed = gate["certify"] & tv
            d = LIMIT - yte[missed]
            depths[fam].extend(list(d))
            qrows[fam].extend([float(q)] * len(d))
        print(f"seed {seed} done", flush=True)
    for fam in ("ridge", "histgb"):
        depths[fam] = np.asarray(depths[fam], dtype=np.float64)
        qrows[fam] = np.asarray(qrows[fam], dtype=np.float64)
    return depths, qrows, qhat90


def verify(depths, qrows, qhat90):
    md = json.load(open("data/missed_depth.json"))
    printed = {}
    for fam in ("ridge", "histgb"):
        d = depths[fam]; q = qrows[fam]
        ref = md["families"][fam]["pooled"]["0.90"]
        got = dict(count=int(len(d)), mean=float(d.mean()), median=float(np.median(d)),
                   p90=float(np.percentile(d, 90)), p99=float(np.percentile(d, 99)),
                   max=float(d.max()), share_below_qhat=float((d < q).mean()),
                   share_below_strip=float((d < STRIP).mean()))
        qmean = float(np.mean(qhat90[fam]))
        got["qhat90_mean"] = qmean
        got["share_left_of_mean_line"] = float((d < qmean).mean())
        printed[fam] = dict(regen=got, json_ref=ref)
        ok = (got["count"] == ref["count"] and abs(got["max"] - ref["max"]) < 1e-9
              and abs(got["share_below_qhat"] - ref["share_below_qhat"]) < 1e-9)
        print(f"[verify] {fam}: count {got['count']} vs {ref['count']} | max {got['max']:.5f} vs "
              f"{ref['max']:.5f} | share<qhat {got['share_below_qhat']*100:.1f}% vs "
              f"{ref['share_below_qhat']*100:.1f}% | MATCH={ok}", flush=True)
    return printed


def panel_common(ax, fam):
    ax.axvspan(0, STRIP, color="#cccccc", alpha=0.25, zorder=0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=FS_ANNOT)
    ax.set_xlim(0, XHI)


def make_hist(depths, printed, out_path):
    fig, axes = plt.subplots(2, 1, figsize=(3.5, 4.3), sharex=True)
    edges = np.arange(0, XHI + 0.001, 0.001)
    for ax, fam in zip(axes, ("ridge", "histgb")):
        d = depths[fam]
        ax.hist(d, bins=edges, color=COLORS[fam], linewidth=0)
        ax.set_yscale("log")
        panel_common(ax, fam)
        trans = ax.get_xaxis_transform()
        qm = printed[fam]["regen"]["qhat90_mean"]
        share = printed[fam]["regen"]["share_below_qhat"] * 100
        ax.axvline(qm, color="black", lw=1.2, ls="--", zorder=4)
        ax.text(qm + 0.002, 0.90, f"q̂@0.90 = {qm:.4f}\n{share:.0f}% of misses within band",
                transform=trans, fontsize=FS_ANNOT - 1, color="black", va="top", ha="left")
        ax.plot([DEEPEST], [1], marker="v", color=C_DEEP, ms=6, clip_on=False, zorder=5)
        ax.set_ylabel(f"{fam}\nmiss count (log)", fontsize=FS_LABEL)
    axes[0].annotate(f"deepest miss {DEEPEST:.4f} pu\n(scen 101000025, line 78 out)",
                     xy=(DEEPEST, 0.06), xycoords=axes[0].get_xaxis_transform(),
                     xytext=(0.42, 0.55), textcoords="axes fraction",
                     fontsize=FS_ANNOT - 1, color=C_DEEP, ha="center", va="center",
                     arrowprops=dict(arrowstyle="->", color=C_DEEP, lw=0.8))
    axes[1].set_xlabel("miss depth below the 0.94 pu floor  d = 0.94 − Y  (per unit)",
                       fontsize=FS_LABEL)
    ft.add_credit(fig)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_cdf(depths, printed, out_path):
    fig, axes = plt.subplots(2, 1, figsize=(3.5, 4.3), sharex=True)
    for ax, fam in zip(axes, ("ridge", "histgb")):
        d = np.sort(depths[fam])
        cdf = np.arange(1, len(d) + 1) / len(d)
        ax.plot(d, cdf, color=COLORS[fam], lw=1.6)
        panel_common(ax, fam)
        ax.set_ylim(0, 1.02)
        qm = printed[fam]["regen"]["qhat90_mean"]
        share = printed[fam]["regen"]["share_below_qhat"] * 100
        ax.axvline(qm, color="black", lw=1.2, ls="--", zorder=4)
        ax.axhline(share / 100, color="black", lw=0.6, ls=":", zorder=3)
        ax.text(qm + 0.002, 0.42, f"q̂@0.90 = {qm:.4f}\n{share:.0f}% within band",
                fontsize=FS_ANNOT - 1, color="black", va="center", ha="left")
        ax.plot([DEEPEST], [1.0], marker="v", color=C_DEEP, ms=6, clip_on=False, zorder=5)
        ax.set_ylabel(f"{fam}\ncumulative share", fontsize=FS_LABEL)
    axes[0].annotate(f"deepest miss {DEEPEST:.4f} pu\n(scen 101000025, line 78 out)",
                     xy=(DEEPEST, 1.0), xytext=(0.60, 0.70), textcoords="axes fraction",
                     fontsize=FS_ANNOT - 1, color=C_DEEP, ha="center", va="center",
                     arrowprops=dict(arrowstyle="->", color=C_DEEP, lw=0.8))
    axes[1].set_xlabel("miss depth below the 0.94 pu floor  d = 0.94 − Y  (per unit)",
                       fontsize=FS_LABEL)
    ft.add_credit(fig)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    cfg = m2_configs()
    depths, qrows, qhat90 = collect_depths(cfg)
    printed = verify(depths, qrows, qhat90)
    pool = dict(coverage_target=COV, families={fam: dict(
        depths=[float(x) for x in depths[fam]], qhat90_per_seed=qhat90[fam],
        stats=printed[fam]["regen"]) for fam in ("ridge", "histgb")})
    with open("data/miss_depth_pool.json", "w") as f:
        json.dump(pool, f)
    make_hist(depths, printed, "data/miss_depth_v2.png")
    make_cdf(depths, printed, "data/miss_depth_v2_cdf.png")

    meta = dict(figure="miss-depth distribution of v2 M2 missed violations, coverage target 0.90",
                coverage_target=COV, x_axis="depth d = 0.94 - Y (pu), 0..0.095",
                boundary_strip=STRIP, deepest_miss_pu=DEEPEST,
                deepest_miss_case="scenario 101000025, line 78 out (IEEE bus 54)",
                families={fam: printed[fam]["regen"] for fam in ("ridge", "histgb")},
                chosen="data/miss_depth_v2.png (log-y histogram; tail visible)",
                variants=["data/miss_depth_v2.png (log-y histogram, CHOSEN)",
                          "data/miss_depth_v2_cdf.png (empirical CDF, alternative — plateau hides tail)"],
                no_new_solves="surrogates refit deterministically; no AC solve rerun")
    settings = dict(task="miss-depth figure (chosen histogram + CDF alternative)",
                    source="data/dataset.parquet, data/tuned_metrics.json, data/missed_depth.json")
    for png in ("data/miss_depth_v2.png", "data/miss_depth_v2_cdf.png"):
        man = cm.build_manifest(png, dict(meta, artifact=png), settings)
        mpath = mf.manifest_path(png)
        with open(mpath, "w") as f:
            json.dump(man, f, indent=2)
        print(f"wrote {png} + {mpath} (sha256 {man['content_sha256'][:12]}...)")


if __name__ == "__main__":
    main()
