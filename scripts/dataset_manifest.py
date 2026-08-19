import json
import os
import sys

import pandas as pd
import pyarrow.parquet as pq
import pandapower.networks as pn

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manifest as mf
import classical_manifest as cm

# Emit the missing manifest for data/dataset.parquet.
#
# WHY IT WAS MISSING: feasibility/generate_dataset.py writes the parquet (line 360) and
# never writes a manifest. Neither network's dataset got one from the generator;
# data/case30_dataset.manifest.json was written after the fact by a later task. This
# script does the same for case118, and is committed so the artifact comes from repo code.
#
# THIS MANIFEST IS RETROACTIVE, AND SAYS SO IN ITS OWN BODY.
# mf.build_manifest() reads the CURRENT interpreter, package versions and hardware. The
# dataset was generated earlier, and nothing in this repository records the environment
# at generation time. Emitting those fields unlabelled would assert provenance this
# script cannot establish, so every field is tagged with how it was obtained:
#   observed_now             - true of this machine at emit time, NOT of the build
#   recovered_from_docs      - read from a committed document, cited
#   derived_from_artifact    - recomputed from the parquet itself (the only fields that
#                              are genuinely about the build)
#   UNKNOWN                  - not recorded anywhere; not guessed
#
# CONFIG SOURCE: README.md lines 94-95, the committed invocation. Deliberately NOT
# feasibility/case57_gonogo.py:COMMITTED_CFG, which is what
# data/case30_dataset.manifest.json cites - that script is a go/no-go for a different
# network and may mirror the build without being it.

DATASET = "data/dataset.parquet"
README = "README.md"

INVOCATION = (
    "feasibility/generate_dataset.py --n 1500 --mult-lo 1.0 --mult-hi 1.12 "
    "--reg-lo 1.0 --reg-hi 1.12 --pf-lo 0.9 --pf-hi 1.15 --dvm 0.025"
)


def parquet_shape(path):
    meta = pq.ParquetFile(path).metadata
    return dict(n_rows=int(meta.num_rows), n_columns=int(meta.num_columns))


def derived_checks(path):
    """Recompute, from the parquet, the invocation parameters that leave a trace in it.

    These are the only manifest fields that are evidence about the BUILD rather than
    about this machine. Each is a two-key check on the README invocation.
    """
    cols = ["scenario_id", "outaged_type", "converged", "agg_loading", "gen_out",
            "min_vm", "max_vm"]
    gen_cols = [f"genvm_{i}" for i in range(3)]
    d = pd.read_parquet(path, columns=cols + gen_cols)
    base = d[d.outaged_type == "none"]
    n1 = d[d.outaged_type != "none"]

    net = pn.case118()
    vm0 = net.gen.vm_pu.values
    devs = []
    for i in range(3):
        col = f"genvm_{i}"
        devs.append(max(abs(base[col].min() - vm0[i]), abs(base[col].max() - vm0[i])))

    return dict(
        n_base_scenarios=int(len(base)),
        n_n1_rows=int(len(n1)),
        n_n1_converged=int(n1.converged.sum()),
        n_nonconverged=int((~d.converged).sum()),
        agg_loading_min=float(base.agg_loading.min()),
        agg_loading_max=float(base.agg_loading.max()),
        gen_out_share_of_bases=float((base.gen_out >= 0).mean()),
        max_abs_gen_vm_deviation=float(max(devs)),
        n_scenarios_declared_by_invocation=1500,
        checks=dict(
            n_matches_invocation=bool(len(base) == 1500),
            dvm_consistent_with_0p025=bool(max(devs) <= 0.0251),
            agg_loading_within_mult_range=bool(base.agg_loading.max() <= 1.13),
        ),
        note_agg_loading=(
            "agg_loading max exceeds 1.12 slightly (regional mode applies a block "
            "multiplier plus +/-10% per-load jitter, so the aggregate can land just "
            "above the stated hi). Recorded, not corrected."
        ),
    )


def main():
    if not os.path.exists(DATASET):
        print(f"FAIL: {DATASET} absent")
        return 1

    shape = parquet_shape(DATASET)
    derived = derived_checks(DATASET)

    run_settings = dict(
        task="N-1 contingency dataset, IEEE 118-bus",
        invocation=INVOCATION,
        config_source=(
            f"{README}:94-95 (committed invocation). NOT taken from "
            "feasibility/case57_gonogo.py:COMMITTED_CFG, which describes a different "
            "network's go/no-go and may mirror the build without being it."
        ),
        producer_script="feasibility/generate_dataset.py",
        producer_writes_manifest=False,
    )

    man = cm.build_manifest(DATASET, {}, run_settings, None)
    man["artifact"] = shape

    man["provenance_class"] = dict(
        retroactive=True,
        emitted_by="scripts/dataset_manifest.py",
        why=("feasibility/generate_dataset.py writes the parquet and no manifest. This "
             "manifest was emitted after the fact and does NOT witness the build "
             "environment."),
        field_provenance=dict(
            python="observed_now",
            packages="observed_now",
            hardware="observed_now",
            numba="observed_now",
            measurement="observed_now (read from data/solve_time.json; a separate "
                        "measurement, unrelated to dataset generation)",
            solver="recovered_from_docs (feasibility/manifest.py SOLVER constant; the "
                   "pinned config this project uses throughout)",
            tuned_generator_settings="recovered_from_docs (feasibility/manifest.py TUNED)",
            git_commit="observed_now - this is HEAD at emit time, NOT the commit the "
                       "dataset was built at",
            content_sha256="derived_from_artifact",
            artifact="derived_from_artifact",
            run_settings="recovered_from_docs (README.md:94-95)",
            derived_verification="derived_from_artifact",
        ),
        unknown=[
            "interpreter and package versions at generation time",
            "hardware at generation time",
            "wall-clock generation date",
            "the RNG seed used for the case118 build (the invocation in README.md:94-95 "
            "passes no --seed; case30's recorded invocation passes --seed 100)",
            "the git commit at which the dataset was generated",
        ],
    )

    man["derived_verification"] = derived

    out_path = mf.manifest_path(DATASET)
    with open(out_path, "w") as f:
        json.dump(man, f, indent=2)

    print(f"wrote {out_path}")
    print(f"  artifact: {shape['n_rows']} rows x {shape['n_columns']} columns")
    print(f"  content_sha256: {man['content_sha256']}")
    print(f"  git HEAD at emit: {man['git_commit']['short']} (NOT the build commit)")
    for name, ok in derived["checks"].items():
        print(f"  check {name}: {'PASS' if ok else 'FAIL'}")
    print(f"  max |gen vm deviation| = {derived['max_abs_gen_vm_deviation']:.6f} "
          f"(invocation --dvm 0.025)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
