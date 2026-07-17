import time
import numpy as np
import generate_dataset as gd
import manifest as mf

SEED = 0
N_TIMED = 400
WARMUP = 30
MULT_HI = 1.12


def measure():
    gd.apply_config(dict(mult_hi=MULT_HI))
    net = gd.build_net()
    load_region, n_regions = gd.region_of_load(net)
    branches = gd.branch_list(net)
    rng = np.random.default_rng(SEED)

    times = []
    convs = []
    accepted = 0
    need = N_TIMED + WARMUP
    while len(times) < need:
        mode = "independent" if accepted % 2 == 0 else "regional"
        params = gd.sample_scenario(rng, net, mode, load_region, n_regions, stress="fixed")
        n0_conv, vm0, n0_min_vm = gd.solve_n0(net, params)
        if not n0_conv or n0_min_vm < gd.VMIN_LIMIT:
            continue
        accepted += 1
        for etype, idx in branches:
            table = net[etype]
            table.at[idx, "in_service"] = False
            t0 = time.perf_counter()
            conv, vm = gd.solve(net, init="dc")
            dt = (time.perf_counter() - t0) * 1000.0
            table.at[idx, "in_service"] = True
            times.append(dt)
            convs.append(conv)
            if len(times) >= need:
                break
    return times, convs


def main():
    times, convs = measure()
    kept = np.array(times[WARMUP:])
    kept_conv = convs[WARMUP:]
    warm = np.array(times[:WARMUP])
    mean = float(kept.mean())
    median = float(np.median(kept))
    std = float(kept.std(ddof=0))
    minimum = float(kept.min())
    print("per-case AC solve time (numba on, enforce_q_lims=True, init=dc, stress=fixed mult_hi=1.12)")
    print(f"  n_timed={len(kept)}  warmup_dropped={len(warm)}  converged={sum(kept_conv)}/{len(kept)}")
    print(f"  warm-up first-call max = {warm.max():.1f} ms (numba JIT compile)")
    print(f"  mean   = {mean:.3f} ms/case")
    print(f"  median = {median:.3f} ms/case")
    print(f"  std    = {std:.3f} ms   min = {minimum:.3f} ms  (pinned as ms_solver)")

    out = dict(ms_solver=round(minimum, 2), basis="minimum over N timed solves",
               n_timed=len(kept), warmup_dropped=WARMUP,
               mean_ms=round(mean, 3), median_ms=round(median, 3),
               std_ms=round(std, 3), min_ms=round(minimum, 3))
    mf.write_with_manifest("data/solve_time.json", out)
    print(f"  wrote data/solve_time.json (ms_solver={out['ms_solver']})")


if __name__ == "__main__":
    main()
