import sys, os, json, time
import numpy as np
import pandas as pd
import generate_dataset as G

N_ACCEPT = int(sys.argv[1]) if len(sys.argv) > 1 else 60
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 11

SETTINGS = [
    dict(mult_hi=1.02, pf=(0.95, 1.05), dvm=0.015),
    dict(mult_hi=1.05, pf=(0.90, 1.10), dvm=0.02),
    dict(mult_hi=1.08, pf=(0.90, 1.10), dvm=0.02),
    dict(mult_hi=1.12, pf=(0.90, 1.15), dvm=0.025),
    dict(mult_hi=1.18, pf=(0.90, 1.15), dvm=0.03),
    dict(mult_hi=1.25, pf=(0.90, 1.20), dvm=0.03),
]


def run_setting(st, n_accept, seed):
    net = G.build_net()
    lr, nr = G.region_of_load(net)
    branches = G.branch_list(net)
    G.MULT_LO, G.MULT_HI = 1.0, st["mult_hi"]
    G.REG_LO, G.REG_HI = 1.0, st["mult_hi"]
    G.PF_LO, G.PF_HI = st["pf"]
    G.DVM = st["dvm"]
    G.GATE_N0 = True
    rng = np.random.default_rng(seed)

    accepted = 0; rejected = 0
    n1_min = []; n1_viol = 0; n1_strad = 0; n1_tot = 0; n1_collapse = 0
    argmins = []; n0_min = []
    max_rej = n_accept * G.MAX_REJECT_FACTOR
    while accepted < n_accept and rejected <= max_rej:
        mode = "independent" if (accepted + rejected) % 2 == 0 else "regional"
        p = G.sample_scenario(rng, net, mode, lr, nr, stress="fixed")
        n0_conv, vm0, n0mn = G.solve_n0(net, p)
        if not n0_conv or n0mn < 0.94:
            rejected += 1; continue
        accepted += 1; n0_min.append(n0mn)
        for etype, idx in branches:
            tbl = net[etype]; loc = tbl.index.get_loc(idx); col = tbl.columns.get_loc("in_service")
            tbl.iat[loc, col] = False
            okc, vmc = G.solve(net, init="dc")
            tbl.iat[loc, col] = True
            n1_tot += 1
            if not okc:
                continue
            mn = float(np.nanmin(vmc)); n1_min.append(mn)
            if mn < 0.94:
                n1_viol += 1; argmins.append(int(np.nanargmin(vmc)))
            elif mn <= 0.95:
                n1_strad += 1
            if mn < G.COLLAPSE_FLOOR:
                n1_collapse += 1
    n1_min = np.array(n1_min)
    import collections
    vc = collections.Counter(argmins)
    top2 = sum(c for _, c in vc.most_common(2)) / max(sum(vc.values()), 1) * 100
    return dict(
        mult_hi=st["mult_hi"], pf=st["pf"], dvm=st["dvm"],
        accepted=accepted, rejected=rejected,
        n0_pass_rate=accepted / (accepted + rejected) * 100,
        n1_total=n1_tot, n1_viol_rate=n1_viol / max(n1_tot, 1) * 100,
        n1_strad=n1_strad, n1_strad_share=n1_strad / max(n1_tot, 1) * 100,
        n1_collapse=n1_collapse, n1_collapse_share=n1_collapse / max(n1_tot, 1) * 100,
        distinct_buses=len(vc), top2_share=top2,
        n1_min_p1=float(np.percentile(n1_min, 1)) if len(n1_min) else np.nan,
        n1_min_p5=float(np.percentile(n1_min, 5)) if len(n1_min) else np.nan,
        n1_min_p50=float(np.percentile(n1_min, 50)) if len(n1_min) else np.nan,
        n1_min_min=float(n1_min.min()) if len(n1_min) else np.nan,
        n1_min_max=float(n1_min.max()) if len(n1_min) else np.nan,
        n0_min_p50=float(np.median(n0_min)) if n0_min else np.nan,
        _hist=n1_min,
    )


def main():
    t0 = time.time()
    results = []
    for st in SETTINGS:
        r = run_setting(st, N_ACCEPT, SEED)
        results.append(r)
        print(f"mult_hi={r['mult_hi']:.2f} pf={r['pf']} dvm={r['dvm']}: "
              f"N0pass={r['n0_pass_rate']:5.1f}% N1viol={r['n1_viol_rate']:5.1f}% "
              f"strad={r['n1_strad_share']:5.1f}% collapse={r['n1_collapse_share']:4.1f}% "
              f"buses={r['distinct_buses']} top2={r['top2_share']:4.1f}% "
              f"minvm[{r['n1_min_min']:.3f},{r['n1_min_max']:.3f}] p5={r['n1_min_p5']:.3f}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figtools as ft
    n = len(results)
    fig, axes = plt.subplots(2, (n + 1) // 2, figsize=(4 * ((n + 1) // 2), 6.5))
    axes = np.array(axes).ravel()
    for ax, r in zip(axes, results):
        h = r["_hist"]
        ax.hist(h, bins=80, range=(0.70, 0.96), color="#2166AC", alpha=0.85)
        ax.axvline(0.94, color="crimson", ls="--", lw=1.2)
        ax.axvspan(0.94, 0.95, color="orange", alpha=0.25)
        ax.set_title(f"mult_hi={r['mult_hi']:.2f}\nN1viol={r['n1_viol_rate']:.0f}% "
                     f"strad={r['n1_strad_share']:.0f}% top2={r['top2_share']:.0f}%", fontsize=8)
        ax.set_xlabel("N-1 minimum bus voltage (pu)", fontsize=7)
        ax.set_ylabel("cases", fontsize=7)
        ax.tick_params(labelsize=6)
    for ax in axes[len(results):]:
        ax.axis("off")
    fig.suptitle(f"N-1 minimum-voltage distribution vs load ceiling (feasible base, reactive "
                 f"limits enforced, n={N_ACCEPT} accepted/setting)", fontsize=9)
    ft.add_credit(fig)
    fig.tight_layout()
    fig.savefig("tune_sweep_hist.png", dpi=170, bbox_inches="tight")

    for r in results:
        r.pop("_hist", None)
        r["pf"] = list(r["pf"])
    with open("data/tune_sweep.json", "w") as f:
        json.dump(dict(n_accept=N_ACCEPT, seed=SEED, time_s=time.time() - t0,
                       settings=results), f, indent=2)
    print(f"\nwrote data/tune_sweep.json and tune_sweep_hist.png  ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
