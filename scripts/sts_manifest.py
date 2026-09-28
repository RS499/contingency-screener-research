import os
import sys
import json
import time
import hashlib
import subprocess
from importlib import metadata

# Shared helpers for the scripts/sts_*.py builders: file hashes, library versions, and the
# manifest written beside every new data/sts_* artifact.

PACKAGES = ["pandapower", "numpy", "pandas", "scikit-learn", "pyarrow", "matplotlib"]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def git_out(args):
    try:
        result = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception:
        return ""


def versions():
    out = {}
    for name in PACKAGES:
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            out[name] = "not installed"
    return out


def manifest_path(artifact_path):
    return os.path.splitext(artifact_path)[0] + ".manifest.json"


def input_list(paths):
    out = []
    for p in paths:
        out.append({"path": p, "sha256": sha256_of(p)})
    return out


def repro_check(artifact_path, ref_dir):
    # compare this run's output with the same file written by an earlier run into ref_dir
    if ref_dir == "":
        return {"byte_reproducible": "not checked in this run"}
    ref = os.path.join(ref_dir, os.path.basename(artifact_path))
    if not os.path.exists(ref):
        return {"byte_reproducible": f"not checked: {ref} missing"}
    same = md5_of(ref) == md5_of(artifact_path)
    return {"byte_reproducible": same,
            "byte_reproducible_evidence": f"md5 compared with an independent earlier run of the "
                                          f"same script into {ref}: "
                                          f"{md5_of(ref)} vs {md5_of(artifact_path)}"}


def output_entry(artifact_path, ref_dir):
    entry = {
        "path": artifact_path,
        "sha256": sha256_of(artifact_path),
        "md5": md5_of(artifact_path),
        "bytes": os.path.getsize(artifact_path),
    }
    check = repro_check(artifact_path, ref_dir)
    for k in check:
        entry[k] = check[k]
    return entry


def build_manifest(artifact_paths, script, argv, inputs, params, ref_dir):
    # one manifest per run: it covers every output file the run wrote
    outputs = []
    for p in artifact_paths:
        outputs.append(output_entry(p, ref_dir))
    man = {
        "schema": "B",
        "artifacts": [os.path.basename(p) for p in artifact_paths],
        "generating_script": script,
        "regeneration_argv": argv,
        "script_git_blob_sha": git_out(["hash-object", script]),
        "script_tracked_in_git": git_out(["ls-files", script]) != "",
        "repo_head_commit": git_out(["rev-parse", "HEAD"]),
        "inputs": input_list(inputs),
        "outputs": outputs,
        "interpreter_short": sys.version.split()[0],
        "packages": versions(),
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "parameters": params,
        "no_new_solves": "No AC solve, dataset build, or model fit was run; every output is "
                         "computed from the input files listed above.",
    }
    return man


def write_manifest(man, artifact_path):
    path = manifest_path(artifact_path)
    with open(path, "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {path}")
