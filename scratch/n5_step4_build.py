import os
import sys
import json
import time
import platform

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import n3_floor_rebuild as nf
import manifest as mf
import sts_manifest as sm

# N5 Step 4: a second 0.95-floor case118 dataset with a NEW RNG seed, for error bars on boundary mass and
# violation rate. Same build as scratch/n3_floor_rebuild.py (committed invocation, 1,500 scenarios, 4 shards,
# 375 each, mixed modes, stress "fixed", N-0 gate at 0.94, GEN_VM_LO = 0.95); only the shard seeds change:
# 200-203 instead of 100-103 (scenario_id = seed * 1_000_000 + k, so ids never collide with build 1).
# Labels are pandapower's pinned-solver labels, as in N3 build B (no switch-back relabel in this step).

FLOOR = 0.95
SEED0 = 200
OUT = "data/sts_n5_floor095_seed200.parquet"
OUT_JSON = "data/sts_n5_floor095_seed200.json"


def main():
    nf.SEED0 = SEED0
    nf.SHARD_DIR = "scratch/n5_step4_shards"
    df, accepted, rejected, wall = nf.build(FLOOR, OUT)
    summ = nf.summarize(df, accepted, rejected)
    summ["wall_s"] = wall
    b1 = json.load(open("data/sts_n3_floor095.json"))["summary"]
    with open(OUT_JSON, "w") as f:
        json.dump(dict(gen_vm_lo=FLOOR, shard_seeds=[SEED0 + w for w in range(nf.NPROC)], summary=summ,
                       build1_summary_for_comparison=b1), f, indent=2)
    params = dict(gen_vm_lo=FLOOR, config=nf.CFG, n_total=nf.N_TOTAL, shard_seeds=[SEED0 + w for w in range(nf.NPROC)],
                  scenarios_per_shard=nf.N_TOTAL // nf.NPROC, mode="mixed", stress="fixed", solver=mf.SOLVER,
                  model_hyperparameters="none (no model fit)", python=platform.python_version())
    man = sm.build_manifest([OUT, OUT_JSON], "scratch/n5_step4_build.py", [".venv/bin/python", "scratch/n5_step4_build.py"],
                            ["scratch/n3_floor_rebuild.py", "feasibility/generate_dataset.py", "data/sts_n3_floor095.json"], params, "")
    man["no_new_solves"] = "FALSE: full dataset build (N-0 and N-1 AC solves, pinned solver)"
    sm.write_manifest(man, OUT)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
