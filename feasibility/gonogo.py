import sys, os, time, json
import numpy as np
import pandapower as pp
import pandapower.networks as nw

ENFORCE_QLIM = os.environ.get("GONOGO_QLIM", "0") == "1"

VMIN_LIMIT, VMAX_LIMIT = 0.94, 1.06
NEAR_V_LO = (0.94, 0.95)
NEAR_V_HI = (1.05, 1.06)
THERM_NEAR = (95.0, 100.0)
THERM_VIOL = 100.0
LEVELS = [100, 120, 140, 160, 180]

def build_net():
    net = nw.case118()
    net["_p0"] = net.load.p_mw.values.copy()
    net["_q0"] = net.load.q_mvar.values.copy()
    return net

def branch_list(net):
    b = [("line", int(i)) for i in net.line.index]
    b += [("trafo", int(i)) for i in net.trafo.index]
    return b

def classify(net):
    vm = net.res_bus.vm_pu.values
    mn, mx = float(np.nanmin(vm)), float(np.nanmax(vm))
    load = net.res_line.loading_percent.values
    th = float(np.nanmax(load)) if len(load) else 0.0
    viol = (mn < VMIN_LIMIT) or (mx > VMAX_LIMIT) or (th > THERM_VIOL)
    near = (not viol) and (
        (NEAR_V_LO[0] <= mn <= NEAR_V_LO[1]) or
        (NEAR_V_HI[0] <= mx <= NEAR_V_HI[1]) or
        (THERM_NEAR[0] <= th <= THERM_NEAR[1])
    )
    return mn, mx, th, viol, near

def run_level(net, branches, pct):
    factor = pct / 100.0
    net.load["p_mw"] = net["_p0"] * factor
    net.load["q_mvar"] = net["_q0"] * factor
    times = []
    min_vs = []
    cases = near = viol = nonconv = 0
    for c in [None] + branches:
        if c is not None:
            net[c[0]].at[c[1], "in_service"] = False
        cases += 1
        t = time.perf_counter()
        ok = True
        try:
            pp.runpp(net, init="flat", numba=False, enforce_q_lims=ENFORCE_QLIM)
        except pp.LoadflowNotConverged:
            ok = False
        except Exception:
            ok = False
        dt = (time.perf_counter() - t) * 1000.0
        if c is not None:
            net[c[0]].at[c[1], "in_service"] = True
        times.append(dt)
        if not ok:
            nonconv += 1
            continue
        mn, mx, th, v, n = classify(net)
        min_vs.append(mn)
        viol += int(v)
        near += int(n)
    times = np.array(times)
    return dict(
        loading=pct, cases=cases, near=near, viol=viol, nonconv=nonconv,
        nonconv_rate=100.0 * nonconv / cases,
        mean_ms=float(times.mean()), median_ms=float(np.median(times)),
        p95_ms=float(np.percentile(times, 95)),
        min_v=float(min(min_vs)) if min_vs else float("nan"),
    )

if __name__ == "__main__":
    outfile = sys.argv[1] if len(sys.argv) > 1 else None
    net = build_net()
    branches = branch_list(net)
    print(f"ORACLE: enforce_q_lims={ENFORCE_QLIM}")
    print(f"base load MW={net['_p0'].sum():.1f} buses={len(net.bus)} "
          f"lines={len(net.line)} trafos={len(net.trafo)} branches={len(branches)}")
    hdr = ("Loading", "Cases", "Near", "Viol", "NonConv", "NonConv%",
           "mean_ms", "median_ms", "p95_ms", "MinV")
    print("| " + " | ".join(hdr) + " |")
    rows = []
    for pct in LEVELS:
        r = run_level(net, branches, pct)
        rows.append(r)
        print(f"| {r['loading']}% | {r['cases']} | {r['near']} | {r['viol']} | "
              f"{r['nonconv']} | {r['nonconv_rate']:.1f}% | {r['mean_ms']:.2f} | "
              f"{r['median_ms']:.2f} | {r['p95_ms']:.2f} | {r['min_v']:.3f} |")
    if outfile:
        with open(outfile, "w") as f:
            json.dump(rows, f, indent=2)
