import sys, os, time, json, argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import make_splits as ms
import surrogate as sg
import gate_eval as ge
import manifest as mf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import classical_manifest as cm
import figtools as ft

LIMIT = 0.94
SEEDS = 5
MODELS = ("persistence", "ridge", "histgb")
COVERAGE_LEVELS = [round(0.70 + 0.01 * i, 2) for i in range(30)]
REPRESENTATIVE = (0.99, 0.95, 0.90, 0.85, 0.80, 0.70)
OPERATING = 0.90
COLORS = {"persistence": "#d1495b", "ridge": "#b8860b", "histgb": "#00798c"}
FS_TITLE, FS_LABEL, FS_TICK, FS_LEG, FS_ANNOT = 22, 19, 15, 16, 14


def build_cache(X, y, n0, groups):
    cache = {}
    ycal, ytest = {}, {}
    for seed in range(SEEDS):
        splits = ms.make_splits(groups, seed)
        kept = ms.select_features(X, splits["train"])
        Xk = X[kept]
        Xtr = Xk.iloc[splits["train"]].to_numpy(np.float32)
        Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
        Xte = Xk.iloc[splits["test"]].to_numpy(np.float32)
        ytr = y[splits["train"]]
        ycal[seed] = y[splits["cal"]]
        ytest[seed] = y[splits["test"]]
        n0ca, n0te = n0[splits["cal"]], n0[splits["test"]]
        for model in MODELS:
            if model == "persistence":
                pca, pte = sg.predict_persistence(n0ca), sg.predict_persistence(n0te)
                dt = 1e-6
            elif model == "ridge":
                fitted = sg.train_ridge(Xtr, ytr)
                pca = sg.predict(fitted, Xca)
                t0 = time.time(); pte = sg.predict(fitted, Xte); dt = time.time() - t0
            else:
                fitted = sg.train_histgb(Xtr, ytr, seed=seed)
                pca = sg.predict(fitted, Xca)
                t0 = time.time(); pte = sg.predict(fitted, Xte); dt = time.time() - t0
            cache[(seed, model)] = dict(pred_cal=pca, pred_test=pte,
                                        ms_surrogate=dt / len(ytest[seed]) * 1000.0)
        print(f"  cached seed={seed} (cal={len(ycal[seed])} test={len(ytest[seed])})")
    return cache, ycal, ytest


def sweep(cache, ycal, ytest, ms_solver):
    records = []
    for cov in COVERAGE_LEVELS:
        for model in MODELS:
            qh, esc, cvg, mis, spd, flr, gap = [], [], [], [], [], [], []
            for seed in range(SEEDS):
                c = cache[(seed, model)]
                yte = ytest[seed]
                q_hat = ge.calibrate_qhat(c["pred_cal"], ycal[seed], cov)
                gate = ge.run_gate(c["pred_test"], q_hat, LIMIT)
                s = ge.score(gate, yte, c["ms_surrogate"], ms_solver, LIMIT)
                floor = float(np.mean((yte >= LIMIT) & (yte < LIMIT + q_hat)))
                qh.append(q_hat); esc.append(s["escalation"]); cvg.append(s["coverage"])
                mis.append(s["missed_viol"]); spd.append(s["net_speedup"]); flr.append(floor)
                gap.append(floor - s["escalation"])
            records.append(dict(
                coverage_target=cov, model=model,
                q_hat=float(np.mean(qh)), q_hat_std=float(np.std(qh)),
                escalation=float(np.mean(esc)), escalation_std=float(np.std(esc)),
                coverage_emp=float(np.mean(cvg)), coverage_emp_std=float(np.std(cvg)),
                missed_viol=float(np.mean(mis)), missed_viol_std=float(np.std(mis)),
                net_speedup=float(np.mean(spd)), net_speedup_std=float(np.std(spd)),
                floor=float(np.mean(flr)), floor_std=float(np.std(flr)),
                gap=float(np.mean(gap))))
    return records


def rows_for(records, model):
    rows = [r for r in records if r["model"] == model]
    order = np.argsort([r["coverage_target"] for r in rows])
    return [rows[i] for i in order]


def invert_floor(y_all, target_esc):
    grid = np.linspace(0.0, 0.02, 4001)
    for q in grid:
        if np.mean((y_all >= LIMIT) & (y_all < LIMIT + q)) >= target_esc:
            return float(q)
    return float("nan")


def qhat_sensitivity(records, cache, ytest, y_all):
    q20 = invert_floor(y_all, 0.20)
    q10 = invert_floor(y_all, 0.10)
    out = {"q_for_esc_20": q20, "q_for_esc_10": q10, "per_model": {}}
    for model in ("ridge", "histgb"):
        rows = rows_for(records, model)
        cov = np.array([r["coverage_target"] for r in rows])
        qh = np.array([r["q_hat"] for r in rows])
        es = np.array([r["escalation"] for r in rows])
        i = int(np.argmin(np.abs(cov - OPERATING)))
        lo, hi = max(i - 1, 0), min(i + 1, len(rows) - 1)
        slope = float((es[hi] - es[lo]) / (qh[hi] - qh[lo]))
        q_cur = float(qh[i])
        mae_cur = float(np.mean([np.mean(np.abs(cache[(s, model)]["pred_test"] - ytest[s]))
                                 for s in range(SEEDS)]))
        out["per_model"][model] = dict(
            q_hat_current=q_cur, escalation_current=float(es[i]), mae_current=mae_cur,
            d_esc_d_qhat=slope,
            shrink_for_20=q_cur / q20 if q20 > 0 else float("inf"),
            shrink_for_10=q_cur / q10 if q10 > 0 else float("inf"),
            mae_target_20=mae_cur * q20 / q_cur, mae_target_10=mae_cur * q10 / q_cur)
    return out


def first_safe_coverage(rows, max_missed=0.01):
    safe = [r["coverage_target"] for r in rows if r["missed_viol"] < max_missed]
    return min(safe) if safe else None


def fig_hero(records, suffix="", figsize=(14, 9), fs_title=FS_TITLE, fs_label=FS_LABEL,
             fs_tick=FS_TICK, fs_leg=FS_LEG, fs_annot=FS_ANNOT, lw=3.0, out_path=None):
    FS_TITLE, FS_LABEL, FS_TICK, FS_LEG, FS_ANNOT = fs_title, fs_label, fs_tick, fs_leg, fs_annot
    hero_models = ["ridge", "histgb"]
    fig, axL = plt.subplots(figsize=figsize)
    axR = axL.twinx()

    cross = {}
    all_cov = []
    for model in hero_models:
        rows = rows_for(records, model)
        cov = [r["coverage_target"] for r in rows]
        all_cov = cov
        axL.plot(cov, [r["escalation"] * 100 for r in rows], "-", lw=lw, color=COLORS[model],
                 label=f"{model} escalation")
        axR.plot(cov, [r["missed_viol"] * 100 for r in rows], ":", lw=lw, color=COLORS[model],
                 label=f"{model} missed-violation")
        cross[model] = first_safe_coverage(rows)

    lo = min(all_cov)
    ytop = axL.get_ylim()[1]
    named = [(m, cross[m]) for m in hero_models if cross[m] is not None]
    if named:
        min_cross = min([c for _, c in named])
        max_cross = max([c for _, c in named])
        safer_model = named[0][0]
        for m, c in named:
            if c == min_cross:
                safer_model = m
        axL.axvspan(lo, min_cross, color="#d1495b", alpha=0.14, zorder=0)
        axL.text((lo + min_cross) / 2, ytop * 0.55, "missed-violation > 1%\n(unusable for both)",
                 ha="center", va="center", fontsize=FS_ANNOT, color="#a03040")
        if max_cross > min_cross:
            axL.axvspan(min_cross, max_cross, color="#d1495b", alpha=0.05, zorder=0)
            axL.text((min_cross + max_cross) / 2, ytop * 0.30, f"{safer_model}\nonly",
                     ha="center", va="center", fontsize=FS_ANNOT - 2, color="#a03040")
    for i, model in enumerate(hero_models):
        c = cross[model]
        if c is not None:
            axL.axvline(c, color=COLORS[model], lw=1.6, ls="-.")
            axL.text(c, ytop * (0.995 - 0.055 * i), f"{model} <1% missed at cov {c:.2f}",
                     ha="right", va="top", fontsize=FS_ANNOT, color=COLORS[model])
    axR.axhline(1.0, color="grey", lw=1.2, ls=":")
    axR.text(max(all_cov), 1.0, "1% missed ", ha="right", va="bottom", fontsize=FS_ANNOT - 1,
             color="grey")

    axL.set_xlabel("target coverage", fontsize=FS_LABEL)
    axL.set_ylabel("escalation  (%)", fontsize=FS_LABEL)
    axR.set_ylabel("missed-violation  (% of true violations)", fontsize=FS_LABEL)
    axL.tick_params(labelsize=FS_TICK); axR.tick_params(labelsize=FS_TICK)
    axL.set_title("Safety vs throughput: below ~1% missed-violation, escalation stays high",
                  fontsize=FS_TITLE)
    axL.grid(alpha=0.3)
    lL, nL = axL.get_legend_handles_labels(); lR, nR = axR.get_legend_handles_labels()
    axL.legend(lL + lR, nL + nR, fontsize=FS_LEG, loc="center left")
    ft.add_credit(fig)
    fig.tight_layout()
    bbox = None if out_path else "tight"
    fig.savefig(out_path or f"data/tradeoff_hero{suffix}.png", dpi=300, bbox_inches=bbox)
    plt.close(fig)


def fig_record(records, suffix=""):
    fig, axes = plt.subplots(3, 1, figsize=(8, 11), sharex=True)
    for ax, model in zip(axes, MODELS):
        rows = rows_for(records, model)
        cov = [r["coverage_target"] for r in rows]
        axr = ax.twinx()
        ax.plot(cov, [r["escalation"] * 100 for r in rows], "-", lw=2, color=COLORS[model], label="escalation")
        ax.plot(cov, [r["floor"] * 100 for r in rows], "--", lw=2, color=COLORS[model], alpha=0.6, label="floor")
        axr.plot(cov, [r["missed_viol"] * 100 for r in rows], ":", lw=2, color="black", label="missed")
        ax.axvline(OPERATING, color="grey", lw=1, ls="-.")
        ax.set_ylabel(f"{model}\nesc / floor (%)", fontsize=12)
        axr.set_ylabel("missed (%)", fontsize=11)
        ax.grid(alpha=0.3)
        if model == MODELS[0]:
            lL, nL = ax.get_legend_handles_labels(); lR, nR = axr.get_legend_handles_labels()
            ax.legend(lL + lR, nL + nR, fontsize=10, loc="center right", framealpha=0.9)
    axes[-1].set_xlabel("target coverage", fontsize=13)
    ft.add_credit(fig)
    fig.tight_layout(); fig.savefig(f"data/tradeoff_record{suffix}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_qhat(records, suffix=""):
    fig, ax = plt.subplots(figsize=(14, 8.5))
    for model in MODELS:
        rows = rows_for(records, model)
        qh = [r["q_hat"] for r in rows]
        ax.plot(qh, [r["escalation"] * 100 for r in rows], "-", lw=3.0, color=COLORS[model], label=f"{model} escalation")
        ax.plot(qh, [r["floor"] * 100 for r in rows], "--", lw=2.2, color=COLORS[model], alpha=0.6, label=f"{model} floor")
    ax.set_xscale("log")
    ax.set_xlabel("conformal band half-width  (pu; log scale)", fontsize=FS_LABEL)
    ax.set_ylabel("escalation / perfect-model floor  (%)", fontsize=FS_LABEL)
    ax.set_title("Escalation vs band width: saturation plateaus confirm the ceilings", fontsize=FS_TITLE)
    ax.tick_params(labelsize=FS_TICK); ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=FS_LEG)
    ax.text(0.5, -0.14, "Plateaus confirm the predicted escalation ceilings: persistence 100%, "
            "persistence floor ~82.6%, histgb ~84%, ridge ~75%.",
            transform=ax.transAxes, ha="center", va="top", fontsize=FS_ANNOT - 1, color="#333333")
    ft.add_credit(fig)
    fig.tight_layout(); fig.savefig(f"data/tradeoff_qhat{suffix}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def print_table(records):
    print("\nrepresentative operating points (mean over seeds)")
    print(f"{'cov':>5} {'model':11s} {'q_hat':>8} {'esc%':>7} {'covEmp%':>8} "
          f"{'floor%':>8} {'gap%':>7} {'missed%':>8} {'speedup':>8}")
    for cov in REPRESENTATIVE:
        for model in MODELS:
            r = next(x for x in records if x["model"] == model and abs(x["coverage_target"] - cov) < 1e-9)
            print(f"{cov:>5.2f} {model:11s} {r['q_hat']:8.5f} {r['escalation']*100:7.1f} "
                  f"{r['coverage_emp']*100:8.1f} {r['floor']*100:8.1f} {r['gap']*100:7.1f} "
                  f"{r['missed_viol']*100:8.2f} {r['net_speedup']:7.2f}x")


def print_sensitivity(sens):
    print("\nq_hat sensitivity (floor is conditional on band width; perfect model -> q_hat 0 -> esc 0)")
    print(f"  q_hat needed for 20% escalation: {sens['q_for_esc_20']:.5f}  |  for 10%: {sens['q_for_esc_10']:.5f}")
    for model, d in sens["per_model"].items():
        print(f"  {model}: current q_hat={d['q_hat_current']:.5f} (esc {d['escalation_current']*100:.1f}%), "
              f"MAE={d['mae_current']:.5f}")
        print(f"     d(esc)/d(q_hat) at operating point = {d['d_esc_d_qhat']:.1f} per pu "
              f"({d['d_esc_d_qhat']/100:.3f} %/micro-pu)")
        print(f"     -> 20% esc needs q_hat {d['shrink_for_20']:.2f}x smaller "
              f"(MAE ~{d['mae_current']:.5f} -> {d['mae_target_20']:.5f})")
        print(f"     -> 10% esc needs q_hat {d['shrink_for_10']:.2f}x smaller "
              f"(MAE ~{d['mae_current']:.5f} -> {d['mae_target_10']:.5f})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="data/dataset.parquet")
    ap.add_argument("--suffix", default="")
    ap.add_argument("--figs-only", action="store_true")
    ap.add_argument("--poster", action="store_true",
                    help="with --figs-only: render ONLY the poster hero panel (14.05x10.5in, poster "
                         "fonts) to data/poster/tradeoff_hero.png instead of the 3 paper figures")
    args = ap.parse_args()

    if args.figs_only:
        with open(f"data/tradeoff_curve{args.suffix}.json") as f:
            records = json.load(f)["records"]
        if args.poster:
            out_path = "data/poster/tradeoff_hero.png"
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            fig_hero(records, args.suffix, figsize=(14.05, 10.5), fs_title=ft.POSTER_FS_BASE,
                     fs_label=ft.POSTER_FS_LABEL, fs_tick=ft.POSTER_FS_TICK, fs_leg=ft.POSTER_FS_ANNOT,
                     fs_annot=ft.POSTER_FS_ANNOT, lw=ft.POSTER_LW, out_path=out_path)
            print(f"wrote {out_path} (poster mode, no refit, from data/tradeoff_curve{args.suffix}.json)")
            meta = dict(figure="poster panel: safety vs throughput hero", figsize_in=[14.05, 10.5],
                        curve_source=f"data/tradeoff_curve{args.suffix}.json")
            settings = dict(task="poster figure regeneration",
                            source=f"data/tradeoff_curve{args.suffix}.json")
            man = cm.build_manifest(out_path, meta, settings)
            with open(mf.manifest_path(out_path), "w") as f:
                json.dump(man, f, indent=2)
            print(f"wrote {mf.manifest_path(out_path)} (sha256 {man['content_sha256'][:12]}...)")
        else:
            fig_hero(records, args.suffix); fig_record(records, args.suffix); fig_qhat(records, args.suffix)
            print(f"re-rendered 3 figures from data/tradeoff_curve{args.suffix}.json (no refit)")
        return

    t0 = time.time()
    df, feature_cols = ms.load_dataset(args.path)
    X, y, groups, _b = ms.build_design_matrix(df, feature_cols)
    n0 = df["n0_min_vm"].to_numpy(np.float64)
    ms_solver = mf.load_solve_time()["ms_solver"]

    cache, ycal, ytest = build_cache(X, y, n0, groups)
    n_cal = len(ycal[0])
    records = sweep(cache, ycal, ytest, ms_solver)
    sens = qhat_sensitivity(records, cache, ytest, y)

    fig_hero(records, args.suffix); fig_record(records, args.suffix); fig_qhat(records, args.suffix)

    out = dict(seeds=SEEDS, coverage_levels=COVERAGE_LEVELS, limit=LIMIT,
               ms_solver=ms_solver, n_cal=n_cal, operating_point=OPERATING,
               sensitivity=sens, records=records)
    os.makedirs("data", exist_ok=True)
    json_path = f"data/tradeoff_curve{args.suffix}.json"
    mf.write_with_manifest(json_path, out)
    print(f"wrote {json_path} and 3 figures")

    print_table(records)
    print_sensitivity(sens)
    print(f"time_s={time.time()-t0:.1f}")


if __name__ == "__main__":
    main()
