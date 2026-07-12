import sys, os, time, json
import numpy as np
import pandapower as pp
import pandapower.networks as nw

ENFORCE_QLIM = os.environ.get("STRADDLE_QLIM", "0") == "1"

VMIN_LIMIT = 0.94
VMAX_LIMIT = 1.06
NEAR_LO = (0.94, 0.95)
NEAR_HI = (1.05, 1.06)
MULT_LO, MULT_HI = 1.00, 1.30

def build_net():
    net = nw.case118()
    net["_p0"] = net.load.p_mw.values.copy()
    net["_q0"] = net.load.q_mvar.values.copy()
    pp.runpp(net)
    return net

def branch_list(net):
    b = [("line", int(i)) for i in net.line.index]
    b += [("trafo", int(i)) for i in net.trafo.index]
    return b

def run_scenario(net, branches, mults):
    net.load["p_mw"] = net["_p0"] * mults
    net.load["q_mvar"] = net["_q0"] * mults
    out = []
    for etype, idx in branches:
        tbl = net[etype]
        tbl.at[idx, "in_service"] = False
        conv = True
        try:
            pp.runpp(net, init="dc", enforce_q_lims=ENFORCE_QLIM)
        except pp.LoadflowNotConverged:
            conv = False
        except Exception:
            conv = False
        tbl.at[idx, "in_service"] = True
        if not conv:
            out.append(dict(etype=etype, idx=idx, converged=False,
                            min_vm=None, max_vm=None, viol=None, near=False))
            continue
        vm = net.res_bus.vm_pu.values
        mn, mx = float(np.nanmin(vm)), float(np.nanmax(vm))
        viol = (mn < VMIN_LIMIT) or (mx > VMAX_LIMIT)
        near_lo = (NEAR_LO[0] <= mn <= NEAR_LO[1])
        near_hi = (NEAR_HI[0] <= mx <= NEAR_HI[1])
        near = (near_lo or near_hi) and (not viol)
        argmin_bus = int(net.res_bus.vm_pu.idxmin())
        argmax_bus = int(net.res_bus.vm_pu.idxmax())
        out.append(dict(etype=etype, idx=idx, converged=True,
                        min_vm=mn, max_vm=mx, viol=bool(viol),
                        near=bool(near), near_lo=bool(near_lo), near_hi=bool(near_hi),
                        min_bus=argmin_bus, max_bus=argmax_bus))
    return out

def worker(args):
    seed0, n_scen = args
    net = build_net()
    branches = branch_list(net)
    rng = np.random.default_rng(seed0)
    nloads = len(net.load)
    rows = []
    for s in range(n_scen):
        mults = rng.uniform(MULT_LO, MULT_HI, size=nloads)
        cases = run_scenario(net, branches, mults)
        for c in cases:
            c["scen"] = seed0 * 1_000_000 + s
        rows.extend(cases)
    return rows

if __name__ == "__main__":
    import multiprocessing as mp
    n_scen = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    nproc = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    outfile = sys.argv[3] if len(sys.argv) > 3 else None

    t0 = time.time()
    if nproc == 1:
        rows = worker((1, n_scen))
    else:
        per = [n_scen // nproc] * nproc
        for i in range(n_scen % nproc):
            per[i] += 1
        tasks = [(seed + 1, cnt) for seed, cnt in enumerate(per)]
        with mp.Pool(nproc) as pool:
            parts = pool.map(worker, tasks)
        rows = [r for p in parts for r in p]
    dt = time.time() - t0

    tot = len(rows)
    conv = [r for r in rows if r["converged"]]
    nonconv = tot - len(conv)
    viol = [r for r in conv if r["viol"]]
    near = [r for r in conv if r["near"]]
    near_lo = [r for r in near if r.get("near_lo")]
    near_hi = [r for r in near if r.get("near_hi")]

    scens = len(set(r["scen"] for r in rows))
    elems = len(set((r["etype"], r["idx"]) for r in near))
    near_buses = len(set(r["min_bus"] for r in near_lo) | set(r["max_bus"] for r in near_hi))

    print(f"time_s={dt:.1f} scenarios={scens} total_cases={tot}")
    print(f"nonconverged={nonconv} converged={len(conv)}")
    print(f"violation_cases={len(viol)} ({100*len(viol)/max(len(conv),1):.1f}% of converged)")
    print(f"near_limit_straddle={len(near)} (near_lo={len(near_lo)} near_hi={len(near_hi)})")
    print(f"distinct_contingency_elements_in_near={elems}/186 distinct_critical_buses={near_buses}")

    if outfile:
        summary = dict(time_s=dt, scenarios=scens, total_cases=tot,
                       nonconverged=nonconv, converged=len(conv),
                       violation_cases=len(viol), near_limit=len(near),
                       near_lo=len(near_lo), near_hi=len(near_hi),
                       distinct_elements=elems, distinct_buses=near_buses,
                       mult_lo=MULT_LO, mult_hi=MULT_HI,
                       vmin_limit=VMIN_LIMIT, vmax_limit=VMAX_LIMIT,
                       near_lo_band=NEAR_LO, near_hi_band=NEAR_HI)
        with open(outfile, "w") as f:
            json.dump(dict(summary=summary,
                           near_cases=[{k: r[k] for k in ("scen","etype","idx","min_vm","max_vm","near_lo","near_hi","min_bus","max_bus")} for r in near]),
                      f)
