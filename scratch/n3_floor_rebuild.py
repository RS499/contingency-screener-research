import os
import sys
import json
import time
import hashlib
import platform
import subprocess
import multiprocessing
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
import generate_dataset as gd
import manifest as mf

# N3 generator-voltage-floor rebuild. Replays the committed case118 build exactly
# (data/dataset.manifest.json run_settings.invocation; 4 RNG shards, seeds 100-103, 375 accepted
# scenarios each, mixed modes, stress "fixed", N-0 gate at 0.94) and changes ONLY gd.GEN_VM_LO,
# the lower bound on sampled generator voltage setpoints. GEN_VM_LO has no CLI flag, and worker
# processes re-import generate_dataset, so the floor is set inside each worker.
# Prediction written and hashed before this ran: scratch/n3_floor_prediction.md (.sha256).

CFG = dict(mult_lo=1.0, mult_hi=1.12, reg_lo=1.0, reg_hi=1.12, pf_lo=0.9, pf_hi=1.15, dvm=0.025,
           network="case118")
N_TOTAL = 1500
SEED0 = 100
NPROC = 4
PREDICTION = "scratch/n3_floor_prediction.md"
SHARD_DIR = "/Users/rajansaha/.claude/jobs/484f4ac7/tmp/n3_shards"


def floor_worker(task):
    floor, args = task
    gd.GEN_VM_LO = floor
    return gd.worker(args)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build(floor, out):
    modes = np.array(["independent", "regional"])
    mode_list = list(modes[(np.arange(N_TOTAL) % 2)])
    per = [N_TOTAL // NPROC] * NPROC
    tasks = []
    off = 0
    os.makedirs(SHARD_DIR, exist_ok=True)
    tag = f"{floor:.3f}".replace(".", "p")
    for w in range(NPROC):
        shard = os.path.join(SHARD_DIR, f"floor{tag}_shard_{SEED0 + w}.parquet")
        args = (SEED0 + w, per[w], "mixed", mode_list[off:off + per[w]], "fixed", shard, CFG)
        tasks.append((floor, args))
        off += per[w]
    t0 = time.time()
    with multiprocessing.Pool(NPROC, maxtasksperchild=1) as pool:
        paths = pool.map(floor_worker, tasks)
    parts = []
    accepted = 0
    rejected = 0
    for p in paths:
        parts.append(pd.read_parquet(p))
        a, r = open(p + ".reject").read().split(",")
        accepted += int(a)
        rejected += int(r)
    df = pd.concat(parts, ignore_index=True)
    df.to_parquet(out, index=False)
    wall = time.time() - t0
    return df, accepted, rejected, wall


def summarize(df, accepted, rejected):
    conv = df[df.converged]
    n1 = conv[conv.outaged_type != "none"]
    n0 = df[df.outaged_type == "none"]
    v = n1.min_vm.to_numpy()
    strip = (v >= 0.94) & (v < 0.945)
    safe = v >= 0.94
    n0v = n0.n0_min_vm.to_numpy()
    return dict(
        rows=int(len(df)), n1_converged_rows=int(len(n1)),
        nonconverged_rows=int((~df.converged).sum()),
        boundary_mass_pct=100.0 * strip.sum() / len(v),
        boundary_rows=int(strip.sum()),
        conditional_boundary_pct=100.0 * strip.sum() / safe.sum(),
        rows_at_or_above_limit=int(safe.sum()),
        violation_rate_pct=100.0 * (v < 0.94).sum() / len(v),
        violation_rows=int((v < 0.94).sum()),
        n0_bases=int(len(n0)),
        n0_in_strip_pct=100.0 * ((n0v >= 0.94) & (n0v < 0.945)).sum() / len(n0v),
        n0_min_vm_median=float(np.median(n0v)),
        gate_accepted=accepted, gate_rejected=rejected,
        gate_pass_pct=100.0 * accepted / (accepted + rejected),
        min_vm_min=float(v.min()), min_vm_max=float(v.max()))


def main():
    floor = float(sys.argv[1])
    out = sys.argv[2]
    df, accepted, rejected, wall = build(floor, out)
    summ = summarize(df, accepted, rejected)
    summ["wall_s"] = wall
    js = out.replace(".parquet", ".json")
    with open(js, "w") as f:
        json.dump(dict(gen_vm_lo=floor, summary=summ), f, indent=2)
    man = dict(
        artifacts=[out, js],
        generating_script="scratch/n3_floor_rebuild.py",
        regeneration_argv=[".venv/bin/python", "scratch/n3_floor_rebuild.py", str(floor), out],
        script_sha256=sha256_of("scratch/n3_floor_rebuild.py"),
        producer_logic="feasibility/generate_dataset.py (worker, sample_scenario, solve_n0, run_scenario)",
        producer_sha256=sha256_of("feasibility/generate_dataset.py"),
        prediction_file=PREDICTION, prediction_sha256=sha256_of(PREDICTION),
        run_settings=dict(gen_vm_lo=floor, config=CFG, n_total=N_TOTAL, shard_seeds=[SEED0 + w for w in range(NPROC)],
                          scenarios_per_shard=N_TOTAL // NPROC, mode="mixed", stress="fixed",
                          gate_n0=gd.GATE_N0, n0_gate_limit=gd.VMIN_LIMIT, dvm=0.025,
                          qlim_scale=[gd.QLIM_LO, gd.QLIM_HI], p_gen_out=gd.P_GEN_OUT),
        solver=mf.SOLVER,
        packages={p: mf.pkg_version(p) for p in mf.PACKAGES},
        python=platform.python_version(), cpu=mf.cpu_brand(),
        repo_head=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        output_sha256={out: sha256_of(out), js: sha256_of(js)},
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        wall_s=wall)
    with open(out.replace(".parquet", ".manifest.json"), "w") as f:
        json.dump(man, f, indent=2)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
