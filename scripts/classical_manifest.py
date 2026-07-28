import os
import sys
import json
import hashlib
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "feasibility"))
import manifest as mf


def git_commit():
    try:
        full = subprocess.run(["git", "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=5).stdout.strip()
        short = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                               capture_output=True, text=True, timeout=5).stdout.strip()
        if full:
            return dict(full=full, short=short)
        return dict(full="unknown", short="unknown")
    except Exception:
        return dict(full="unknown", short="unknown")


def content_hash(results_path):
    h = hashlib.sha256()
    with open(results_path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def artifact_shape(out):
    records = out.get("records", None)
    if isinstance(records, list) and len(records) > 0 and isinstance(records[0], dict):
        return dict(n_records=len(records), n_fields=len(records[0]))
    return dict(n_records=None, n_fields=None)


def build_manifest(results_path, out, run_settings, model_config=None):
    base = mf.build_manifest()
    base["git_commit"] = git_commit()
    base["artifact"] = artifact_shape(out)
    base["content_sha256"] = content_hash(results_path)
    base["run_settings"] = run_settings
    base["model_hyperparameters"] = model_config
    return base


def write_with_manifest(results_path, out, run_settings, model_config=None):
    with open(results_path, "w") as f:
        json.dump(out, f, indent=2)
    man = build_manifest(results_path, out, run_settings, model_config)
    with open(mf.manifest_path(results_path), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {results_path} + {mf.manifest_path(results_path)} "
          f"(sha256 {man['content_sha256'][:12]}..., git {man['git_commit']['short']})")
