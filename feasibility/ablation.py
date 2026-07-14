import sys, json
import numpy as np
import generate_dataset as G

def run_config(disable, n, seed):
    net = G.build_net()
    load_region, n_regions = G.region_of_load(net)
    branches = G.branch_list(net)
    rng = np.random.default_rng(seed)
    argmins = []; mins = []; nconv = 0; ntot = 0
    for s in range(n):
        mode = "independent" if s % 2 == 0 else "regional"
        stress = "fixed" if "load" in disable else "perscenario"
        if "load" in disable:
            G.MULT_LO = G.MULT_HI = 1.0; G.REG_LO = G.REG_HI = 1.0
        else:
            G.MULT_LO, G.MULT_HI = 1.0, 1.5; G.REG_LO, G.REG_HI = 1.0, 1.5
        p = G.sample_scenario(rng, net, mode, load_region, n_regions, stress=stress)
        if "reactive" in disable:
            p["q_new"] = net["_q0"] * (p["p_new"] / net["_p0"])
        if "setpoint" in disable:
            p["gen_vm"] = net["_gen_vm0"].copy()
        if "qlim" in disable:
            p["gen_qmin"] = net["_gen_qmin0"].copy(); p["gen_qmax"] = net["_gen_qmax0"].copy()
        if "genout" in disable:
            p["gen_out"] = -1
        rows = G.run_scenario(net, branches, p, s, mode)
        for r in rows:
            ntot += 1
            if not r["converged"]:
                continue
            nconv += 1; mins.append(r["min_vm"])
            if r["violation"]:
                argmins.append(r["argmin_bus"])
    import collections
    vc = collections.Counter(argmins)
    tot = sum(vc.values())
    mins = np.array(mins)
    return dict(
        distinct_buses=len(vc),
        top2_pct=(sum(c for _, c in vc.most_common(2)) / tot * 100) if tot else float("nan"),
        n_viol=tot, nonconv_pct=(ntot - nconv) / ntot * 100,
        minvm_min=float(mins.min()), minvm_max=float(mins.max()),
        minvm_width=float(mins.max() - mins.min()),
    )

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    axes = ["load", "reactive", "setpoint", "qlim", "genout"]

    base = run_config(set(), n, seed)
    out = {"full": base, "ablations": {}}
    print(f"FULL (all axes): distinct={base['distinct_buses']} top2={base['top2_pct']:.1f}% "
          f"width={base['minvm_width']:.3f} nonconv={base['nonconv_pct']:.1f}%")
    for ax in axes:
        r = run_config({ax}, n, seed)
        d_distinct = r["distinct_buses"] - base["distinct_buses"]
        d_top2 = r["top2_pct"] - base["top2_pct"]
        d_width = r["minvm_width"] - base["minvm_width"]
        out["ablations"][ax] = dict(r, d_distinct=d_distinct, d_top2=d_top2, d_width=d_width)
        print(f"  -{ax:9s}: distinct={r['distinct_buses']:3d} (Δ{d_distinct:+d})  "
              f"top2={r['top2_pct']:5.1f}% (Δ{d_top2:+.1f})  width={r['minvm_width']:.3f} (Δ{d_width:+.3f})")
    def impact(ax):
        a = out["ablations"][ax]
        return abs(a["d_top2"]) + abs(a["d_distinct"])
    ranked = sorted(axes, key=impact)
    out["least_impactful"] = ranked[0]
    out["impact_ranking"] = ranked
    print(f"\nLeast impactful axis (moved bus-spread least): {ranked[0]}")
    print(f"Impact ranking (least->most): {ranked}")
    with open("data/ablation.json", "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
