import os
import sys
import json
import platform

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import n3_floor_rebuild as nf
import manifest as mf
import sts_manifest as sm

# N11 Part 3 build (scratch/n11_decision_rule.md §3): the scratch/n3_floor_rebuild.py logic (build + summarize,
# imported unchanged) with GEN_VM_LO as an argument and SHARD_DIR inside scratch/. Committed invocation, seeds
# 100-103, 375 accepted each, mixed modes, stress "fixed", N-0 gate at 0.94. Stored (pinned-solver) labels.
# argv: gen_vm_lo  (e.g. 0.93) -> data/sts_n11_floor093.{parquet,json} + manifest

FLOOR = float(sys.argv[1]) if len(sys.argv) > 1 else 0.93
TAG = f"{FLOOR:.2f}".replace("0.", "")
OUT = f"data/sts_n11_floor0{TAG}.parquet" if len(TAG) == 2 else f"data/sts_n11_floor{TAG}.parquet"
OUT_JSON = OUT.replace(".parquet", ".json")


def main():
    nf.SHARD_DIR = f"scratch/n11_floor_shards_{TAG}"
    df, accepted, rejected, wall = nf.build(FLOOR, OUT)
    summ = nf.summarize(df, accepted, rejected)
    summ["wall_s"] = wall
    with open(OUT_JSON, "w") as f:
        json.dump(dict(gen_vm_lo=FLOOR, shard_seeds=[nf.SEED0 + w for w in range(nf.NPROC)], summary=summ), f, indent=2)
    params = dict(gen_vm_lo=FLOOR, config=nf.CFG, n_total=nf.N_TOTAL, shard_seeds=[nf.SEED0 + w for w in range(nf.NPROC)],
                  scenarios_per_shard=nf.N_TOTAL // nf.NPROC, mode="mixed", stress="fixed", solver=mf.SOLVER,
                  model_hyperparameters="none (no model fit)", python=platform.python_version())
    man = sm.build_manifest([OUT, OUT_JSON], "scratch/n11_floor_build.py", [".venv/bin/python", "scratch/n11_floor_build.py", str(FLOOR)],
                            ["scratch/n3_floor_rebuild.py", "feasibility/generate_dataset.py"], params, "")
    man["no_new_solves"] = "FALSE: full dataset build (N-0 and N-1 AC solves, pinned solver)"
    sm.write_manifest(man, OUT)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
