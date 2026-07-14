import sys, os, json, time, argparse
import numpy as np
import pandapower as pp
import pandapower.networks as nw
import generate_dataset as G

N_SCEN = int(sys.argv[1]) if len(sys.argv) > 1 else 120
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 7
VMIN = 0.94


def solve(net, enforce, init="dc"):
    try:
        pp.runpp(net, init=init, numba=True, enforce_q_lims=enforce)
        return True, net.res_bus.vm_pu.values.copy()
    except pp.LoadflowNotConverged:
        return False, None
    except Exception:
        return False, None


def old_sampling_scenario(rng, net, nloads):
    m = rng.uniform(1.00, 1.30, size=nloads)
    return m


def run_cell(sampling, oracle, n_scen, seed):
    enforce = (oracle == "new")
    net = G.build_net()
    branches = G.branch_list(net)
    lr, nr = G.region_of_load(net)
    p0 = net["_p0"]; q0 = net["_q0"]
    nloads = len(net.load)
    rng = np.random.default_rng(seed)

    G.GATE_N0 = (sampling == "new")
    if sampling == "new":
        G.MULT_LO, G.MULT_HI = 1.0, 1.12
        G.REG_LO, G.REG_HI = 1.0, 1.12
        G.PF_LO, G.PF_HI = 0.9, 1.15
        G.DVM = 0.025

    argmins = []; n1_min = []; n1_viol = 0; n1_tot = 0; accepted = 0; rejected = 0
    attempts = 0; max_attempts = n_scen * 300
    while accepted < n_scen and attempts < max_attempts:
        attempts += 1
        if sampling == "old":
            m = old_sampling_scenario(rng, net, nloads)
            net.load["p_mw"] = p0 * m
            net.load["q_mvar"] = q0 * m
            n0_conv, vm0 = solve(net, enforce)
            gate_ok = True
        else:
            p = G.sample_scenario(rng, net, "independent" if attempts % 2 else "regional",
                                  lr, nr, stress="fixed")
            G.apply_scenario(net, p)
            n0_conv, vm0 = solve(net, enforce)
            n0mn = float(np.nanmin(vm0)) if (n0_conv and vm0 is not None) else np.nan
            gate_ok = (n0_conv and n0mn >= VMIN) if G.GATE_N0 else True
        if not gate_ok:
            rejected += 1
            if sampling == "new":
                net = G.build_net()
            continue
        accepted += 1
        for etype, idx in branches:
            tbl = net[etype]; loc = tbl.index.get_loc(idx); col = tbl.columns.get_loc("in_service")
            tbl.iat[loc, col] = False
            okc, vmc = solve(net, enforce)
            tbl.iat[loc, col] = True
            n1_tot += 1
            if not okc:
                continue
            mn = float(np.nanmin(vmc)); n1_min.append(mn)
            if mn < VMIN:
                n1_viol += 1; argmins.append(int(np.nanargmin(vmc)))
        if sampling == "new":
            net = G.build_net()
    import collections
    vc = collections.Counter(argmins)
    top2 = sum(c for _, c in vc.most_common(2)) / max(sum(vc.values()), 1) * 100
    n1_min = np.array(n1_min)
    return dict(
        sampling=sampling, oracle=oracle, enforce_q_lims=enforce,
        accepted=accepted, rejected=rejected,
        n1_total=n1_tot, n1_viol=n1_viol, n1_viol_rate=n1_viol / max(n1_tot, 1) * 100,
        distinct_buses=len(vc), top2_share=top2,
        top5=[(int(b), int(c)) for b, c in vc.most_common(5)],
        minvm_min=float(n1_min.min()) if len(n1_min) else np.nan,
        minvm_max=float(n1_min.max()) if len(n1_min) else np.nan,
        minvm_p5=float(np.percentile(n1_min, 5)) if len(n1_min) else np.nan,
        minvm_p50=float(np.percentile(n1_min, 50)) if len(n1_min) else np.nan,
    )


def main():
    t0 = time.time()
    cells = []
    for sampling in ("old", "new"):
        for oracle in ("old", "new"):
            r = run_cell(sampling, oracle, N_SCEN, SEED)
            cells.append(r)
            print(f"sampling={sampling:3s} oracle={oracle:3s} (enforce={r['enforce_q_lims']}): "
                  f"buses={r['distinct_buses']:3d} top2={r['top2_share']:5.1f}% "
                  f"N1viol={r['n1_viol_rate']:5.1f}% minvm[{r['minvm_min']:.3f},{r['minvm_max']:.3f}] "
                  f"(accepted={r['accepted']} rejected={r['rejected']})")
    out = dict(n_scen=N_SCEN, seed=SEED, time_s=time.time() - t0, cells=cells)
    with open("data/experiment_2x2.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote data/experiment_2x2.json ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
