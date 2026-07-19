import sys
import numpy as np
import generate_dataset as gd

N_SCEN = int(sys.argv[1]) if len(sys.argv) > 1 else 150
MAX_ATTEMPTS = N_SCEN * 20
L = 0.94
CFG = dict(mult_lo=1.0, mult_hi=1.12, reg_lo=1.0, reg_hi=1.12, pf_lo=0.9, pf_hi=1.15, dvm=0.025)


def resample_gen_vm(gen_vm0, rng):
    out = gen_vm0.copy()
    for i in range(len(gen_vm0)):
        v = gen_vm0[i] + rng.uniform(-gd.DVM, gd.DVM)
        while not (gd.VMIN_LIMIT <= v <= gd.VMAX_LIMIT):
            v = gen_vm0[i] + rng.uniform(-gd.DVM, gd.DVM)
        out[i] = v
    return out


def run_arm(resample, n_scen, seed):
    gd.apply_config(CFG)
    net = gd.build_net()
    load_region, n_regions = gd.region_of_load(net)
    branches = gd.branch_list(net)
    rng = np.random.default_rng(seed)
    minv, argb = [], []
    accepted, attempts = 0, 0
    while accepted < n_scen and attempts < MAX_ATTEMPTS:
        attempts += 1
        mode = "independent" if accepted % 2 == 0 else "regional"
        params = gd.sample_scenario(rng, net, mode, load_region, n_regions, stress="fixed")
        if resample:
            params["gen_vm"] = resample_gen_vm(net["_gen_vm0"], rng)
        n0_conv, vm0, n0_min = gd.solve_n0(net, params)
        if not n0_conv or n0_min < L:
            continue
        accepted += 1
        for etype, idx in branches:
            tbl = net[etype]
            tbl.at[idx, "in_service"] = False
            conv, vm = gd.solve(net, init="dc")
            tbl.at[idx, "in_service"] = True
            if conv:
                minv.append(float(np.nanmin(vm)))
                argb.append(int(np.nanargmin(vm)))
    return dict(minv=np.array(minv), argb=np.array(argb),
                accepted=accepted, attempts=attempts)


def stats(name, arm):
    y = arm["minv"]; ab = arm["argb"]; n = len(y)
    exact = float(np.mean(y == L))
    band = float(np.mean((y >= L) & (y < L + 0.005)))
    near = float(np.mean(np.abs(y - L) < 0.005))
    viol = float(np.mean(y < L))
    gate = 100.0 * arm["accepted"] / max(arm["attempts"], 1)
    u, c = np.unique(ab, return_counts=True)
    order = np.argsort(c)[::-1][:5]
    top5 = [(int(u[i]), round(100 * c[i] / n, 1)) for i in order]
    sh_75_106 = 100 * float(np.mean(np.isin(ab, [75, 106])))
    print(f"\n=== {name}  (N-1 cases={n}) ===")
    print(f"  N-0 gate pass       : {gate:5.1f}%  ({arm['accepted']}/{arm['attempts']})")
    print(f"  min_vm == 0.94 exact: {100*exact:5.1f}%")
    print(f"  in [0.94, 0.945)    : {100*band:5.1f}%")
    print(f"  within +/-0.005     : {100*near:5.1f}%")
    print(f"  N-1 violation rate  : {100*viol:5.1f}%   (committed dataset = 28.6%)")
    print(f"  argmin top5 (bus,%) : {top5}")
    print(f"  argmin at bus 75/106: {sh_75_106:5.1f}%")


def main():
    print(f"probe: {N_SCEN} accepted scenarios per arm, matched config {CFG}")
    clip = run_arm(resample=False, n_scen=N_SCEN, seed=100)
    resamp = run_arm(resample=True, n_scen=N_SCEN, seed=100)
    stats("CLIP (current behavior)", clip)
    stats("RESAMPLE (fix: no point mass, same support)", resamp)


if __name__ == "__main__":
    main()
