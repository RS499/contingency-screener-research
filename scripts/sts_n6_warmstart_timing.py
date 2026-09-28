import os
import sys
import json
import time
import hashlib
import platform
import subprocess
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
import generate_dataset as gd
import manifest as mf

# N6: warm-start solver timing, a sensitivity number only. The pinned config (enforce_q_lims=True,
# numba on, init="dc", Newton-Raphson) is unchanged everywhere; this script times it against the same
# solve started from the pre-outage (N-0) solution (init="results" with net.res_bus restored to the
# N-0 result before every warm solve). Everything else is identical.

OUT_JSON = "data/sts_n6_warmstart_timing.json"
# committed generator flags (data/dataset.manifest.json run_settings.invocation), stress "fixed"
CFG = dict(mult_lo=1.0, mult_hi=1.12, reg_lo=1.0, reg_hi=1.12, pf_lo=0.9, pf_hi=1.15, dvm=0.025,
           network="case118")
SEED = 2026
N_BASES = 12
N_WARMUP = 30
LIMIT = 0.94


def timed_solve(net, init):
    t0 = time.perf_counter()
    conv, vm = gd.solve(net, init=init)
    dt = (time.perf_counter() - t0) * 1000.0
    return conv, vm, dt


def paired_loop(net, branches, res0, flip_order):
    # per outage: one cold and one warm solve, order alternating to cancel any ordering effect
    rows = []
    for k, (etype, idx) in enumerate(branches):
        table = net[etype]
        table.at[idx, "in_service"] = False
        cold_first = (k % 2 == 0) != flip_order
        if cold_first:
            c_conv, c_vm, c_dt = timed_solve(net, "dc")
            net["res_bus"] = res0.copy()
            w_conv, w_vm, w_dt = timed_solve(net, "results")
        else:
            net["res_bus"] = res0.copy()
            w_conv, w_vm, w_dt = timed_solve(net, "results")
            c_conv, c_vm, c_dt = timed_solve(net, "dc")
        table.at[idx, "in_service"] = True
        rows.append(dict(etype=etype, idx=int(idx), cold_ms=c_dt, warm_ms=w_dt,
                         cold_conv=bool(c_conv), warm_conv=bool(w_conv),
                         cold_min_vm=(float(np.nanmin(c_vm)) if c_conv else None),
                         warm_min_vm=(float(np.nanmin(w_vm)) if w_conv else None)))
    return rows


def sweep(net, branches, res0, init):
    # full N-1 sweep of one base case, wall time including outage toggles (and, for the warm
    # start, restoring the N-0 result before each solve)
    t0 = time.perf_counter()
    for etype, idx in branches:
        table = net[etype]
        table.at[idx, "in_service"] = False
        if init == "results":
            net["res_bus"] = res0.copy()
        gd.solve(net, init=init)
        table.at[idx, "in_service"] = True
    return (time.perf_counter() - t0) * 1000.0


def stats(a):
    a = np.array(a, dtype=np.float64)
    return dict(n=int(len(a)), min_ms=float(a.min()), median_ms=float(np.median(a)),
                mean_ms=float(a.mean()), std_ms=float(a.std()), p90_ms=float(np.percentile(a, 90)))


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def git_head():
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip()


def load_average():
    try:
        return list(os.getloadavg())
    except OSError:
        return None


def main():
    t_start = time.time()
    load_before = load_average()
    gd.apply_config(CFG)
    net = gd.build_net("case118")
    load_region, n_regions = gd.region_of_load(net)
    branches = gd.branch_list(net)
    rng = np.random.default_rng(SEED)

    bases = []
    n_reject = 0
    while len(bases) < N_BASES + 1:
        mode = "independent" if len(bases) % 2 == 0 else "regional"
        params = gd.sample_scenario(rng, net, mode, load_region, n_regions, stress="fixed")
        n0_conv, vm0, n0_min_vm = gd.solve_n0(net, params)
        if not n0_conv or n0_min_vm < gd.VMIN_LIMIT:
            n_reject += 1
            continue
        bases.append(params)

    # warm-up base (not reported): numba JIT compile and cache fill, both inits
    gd.solve_n0(net, bases[0])
    res0 = net["res_bus"].copy()
    paired_loop(net, branches[:N_WARMUP], res0, False)

    all_rows = []
    sweeps = []
    for b in range(1, N_BASES + 1):
        n0_conv, vm0, n0_min_vm = gd.solve_n0(net, bases[b])
        res0 = net["res_bus"].copy()
        rows = paired_loop(net, branches, res0, b % 2 == 0)
        for r in rows:
            r["base"] = b
        all_rows.extend(rows)
        cold_sweep = sweep(net, branches, res0, "dc")
        warm_sweep = sweep(net, branches, res0, "results")
        sweeps.append(dict(base=b, n0_min_vm=float(n0_min_vm), n_outages=len(branches),
                           cold_sweep_ms=cold_sweep, warm_sweep_ms=warm_sweep))
        print(f"  base {b}: cold sweep {cold_sweep:.0f} ms, warm sweep {warm_sweep:.0f} ms", flush=True)

    cold = [r["cold_ms"] for r in all_rows]
    warm = [r["warm_ms"] for r in all_rows]
    both = [r for r in all_rows if r["cold_conv"] and r["warm_conv"]]
    dmin = np.array([abs(r["cold_min_vm"] - r["warm_min_vm"]) for r in both])
    label_diff = sum(1 for r in both if (r["cold_min_vm"] < LIMIT) != (r["warm_min_vm"] < LIMIT))
    cs = np.array([s["cold_sweep_ms"] for s in sweeps])
    ws = np.array([s["warm_sweep_ms"] for s in sweeps])
    wall = time.time() - t_start
    out = dict(
        question="sensitivity of the per-solve cost to a warm start from the pre-outage solution",
        pinned_config_unchanged=True,
        configs=dict(
            cold=dict(enforce_q_lims=True, numba=True, init="dc", algorithm="nr", note="pinned (data/solve_time.json basis)"),
            warm=dict(enforce_q_lims=True, numba=True, init="results", algorithm="nr",
                      note="net.res_bus reset to the N-0 solution before every warm solve (reset not timed in per-solve numbers)")),
        sampling=dict(generator_flags=CFG, stress="fixed", seed=SEED, n_bases=N_BASES,
                      n_rejected_draws=n_reject, outages_per_base=len(branches),
                      warmup=f"one extra base, first {N_WARMUP} outages, both inits, discarded",
                      order="paired per outage; cold/warm order alternates by outage and base"),
        per_solve=dict(cold=stats(cold), warm=stats(warm),
                       median_ratio_cold_over_warm=float(np.median(cold) / np.median(warm)),
                       min_ratio_cold_over_warm=float(np.min(cold) / np.min(warm)),
                       paired_median_of_cold_minus_warm_ms=float(np.median(np.array(cold) - np.array(warm)))),
        full_sweep_one_base=dict(first_base=sweeps[0],
                                 cold_ms=dict(median=float(np.median(cs)), min=float(cs.min()), max=float(cs.max())),
                                 warm_ms=dict(median=float(np.median(ws)), min=float(ws.min()), max=float(ws.max())),
                                 median_ratio_cold_over_warm=float(np.median(cs / ws)),
                                 per_base=sweeps),
        agreement=dict(n_pairs=len(all_rows), n_both_converged=len(both),
                       n_cold_only_converged=sum(1 for r in all_rows if r["cold_conv"] and not r["warm_conv"]),
                       n_warm_only_converged=sum(1 for r in all_rows if r["warm_conv"] and not r["cold_conv"]),
                       max_abs_min_vm_diff=float(dmin.max()) if len(dmin) else None,
                       n_min_vm_diff_gt_1e6=int((dmin > 1e-6).sum()),
                       n_violation_label_differs=int(label_diff)),
        committed_reference=dict(path="data/solve_time.json", note=(
            "committed ms_solver is the min over 400 cold solves drawn with feasibility/measure_solve.py "
            "(seed 0, only --mult-hi 1.12 set, about 2-3 base cases); this run uses the full committed "
            "generator flags, seed 2026, 12 base cases, so its cold min is an independent re-measurement")),
        load_average_before=load_before, load_average_after=load_average(),
        hardware=mf.hardware(),
        wall_time_s=wall)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    man = dict(
        schema="sts-new-analysis",
        artifacts=[OUT_JSON],
        generating_script="scripts/sts_n6_warmstart_timing.py",
        regeneration_argv=[".venv/bin/python", "scripts/sts_n6_warmstart_timing.py"],
        script_sha256=sha256_of("scripts/sts_n6_warmstart_timing.py"),
        repo_head_commit=git_head(),
        inputs=[dict(path="feasibility/generate_dataset.py", sha256=sha256_of("feasibility/generate_dataset.py")),
                dict(path="data/solve_time.json", sha256=sha256_of("data/solve_time.json"))],
        output_sha256=sha256_of(OUT_JSON),
        model_hyperparameters=None,
        seeds=[SEED],
        solver=dict(cold=out["configs"]["cold"], warm=out["configs"]["warm"]),
        cpu=mf.cpu_brand(), machine=platform.machine(), numba=mf.numba_state(),
        environment=mf.build_manifest(),
        wall_time_s=wall,
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(mf.manifest_path(OUT_JSON), "w") as f:
        json.dump(man, f, indent=2)
    print(f"cold per-solve min {np.min(cold):.2f} median {np.median(cold):.2f} | warm min {np.min(warm):.2f} "
          f"median {np.median(warm):.2f} | sweep cold {np.median(cs):.0f} warm {np.median(ws):.0f} ms", flush=True)
    print(f"wrote {OUT_JSON} + manifest; wall {wall:.0f}s", flush=True)


if __name__ == "__main__":
    main()
