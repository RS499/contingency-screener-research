import os
import sys
import json
import time
import multiprocessing as mp
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

N_SCEN = 6          # scenarios per configuration (first is warm-up, discarded)
MULT_HI = 1.12
SEED = 0


def worker(args):
    """Solve an assigned slice of branches for N_SCEN scenarios. Returns (n_solves, seconds)."""
    wid, n_workers = args
    import generate_dataset as gd
    gd.apply_config(dict(mult_hi=MULT_HI))
    net = gd.build_net()
    load_region, n_regions = gd.region_of_load(net)
    branches = gd.branch_list(net)
    mine = [b for i, b in enumerate(branches) if i % n_workers == wid]
    rng = np.random.default_rng(SEED)

    n_solves = 0
    elapsed = 0.0
    accepted = 0
    while accepted < N_SCEN:
        mode = "independent" if accepted % 2 == 0 else "regional"
        params = gd.sample_scenario(rng, net, mode, load_region, n_regions, stress="fixed")
        n0_conv, vm0, n0_min_vm = gd.solve_n0(net, params)
        if not n0_conv or n0_min_vm < gd.VMIN_LIMIT:
            continue
        accepted += 1
        warm = (accepted == 1)          # discard the JIT-compile scenario
        t0 = time.perf_counter()
        for etype, idx in mine:
            table = net[etype]
            table.at[idx, "in_service"] = False
            gd.solve(net, init="dc")
            table.at[idx, "in_service"] = True
        dt = time.perf_counter() - t0
        if not warm:
            elapsed += dt
            n_solves += len(mine)
    return n_solves, elapsed


def run(n_workers):
    """Wall-clock for the same total workload spread over n_workers processes."""
    t0 = time.perf_counter()
    if n_workers == 1:
        res = [worker((0, 1))]
    else:
        with mp.Pool(n_workers) as pool:
            res = pool.map(worker, [(w, n_workers) for w in range(n_workers)])
    wall = time.perf_counter() - t0
    total_solves = sum(r[0] for r in res)
    busy = sum(r[1] for r in res)
    return dict(n_workers=n_workers, total_solves=total_solves,
                wall_s=wall, worker_busy_s=busy,
                ms_per_case_wall=1000.0 * busy / total_solves if total_solves else float("nan"))


def main():
    mp.set_start_method("spawn", force=True)
    cores = os.cpu_count()
    plan = [p for p in (1, 2, 4, 8, cores) if p <= cores]
    plan = sorted(set(plan))
    out = []
    for p in plan:
        r = run(p)
        out.append(r)
        print(f"  workers={p:2d} solves={r['total_solves']:5d} "
              f"busy={r['worker_busy_s']:7.2f}s ms/case={r['ms_per_case_wall']:.3f}", flush=True)
    json.dump(dict(cores=cores, runs=out), open(sys.argv[1], "w"), indent=2)
    print("done")


if __name__ == "__main__":
    main()
