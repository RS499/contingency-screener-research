import os
import sys
import json
import time
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import sts_manifest as sm

# N14 Step 2 (scratch/n14_decision_rule.md §B): before D94 and C30 primary results are restated from N13, the sha256
# of each N13 dataset file and of each N13 analysis output reused must equal the value recorded in its N13 manifest
# ("outputs"). If any differs, that network is recomputed instead. Output: data/sts_n14_restate_check.json + manifest.

RULE = "scratch/n14_decision_rule.md"
RULE_SHA = "scratch/n14_decision_rule.sha256"
OUT = "data/sts_n14_restate_check.json"
ANALYSES = ["gate_D94", "gate_C30", "condhist", "budget", "guarantee", "crossnet", "n2", "mondrian", "floor", "verdicts"]
PER_NET = {
    "D94": ["data/sts_n13_D94.parquet", "data/sts_n13_gate_D94.json"] + [f"data/sts_n13_{a}.json" for a in ANALYSES if not a.startswith("gate_")],
    "C30": ["data/sts_n13_C30.parquet", "data/sts_n13_gate_C30.json", "data/sts_n13_condhist.json", "data/sts_n13_crossnet.json",
            "data/sts_n13_verdicts.json"],
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def recorded(path):
    man = json.load(open(os.path.splitext(path)[0] + ".manifest.json"))
    for o in man.get("outputs", []):
        if os.path.basename(o["path"]) == os.path.basename(path):
            return o["sha256"]
    return None


def main():
    h = sha(RULE)
    if h != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    res = {}
    for net in PER_NET:
        rows = []
        for p in PER_NET[net]:
            rec = recorded(p)
            now = sha(p)
            rows.append(dict(file=p, recorded_sha256=rec, current_sha256=now, match=bool(rec is not None and rec == now)))
        ok = bool(all([r["match"] for r in rows]))
        res[net] = dict(files=rows, all_match=ok, decision="restated from N13" if ok else "recompute under the N14 primary definition")
        print(f"{net}: {len([r for r in rows if r['match']])}/{len(rows)} hashes match -> {res[net]['decision']}", flush=True)
    out = dict(step="N14 Step 2: D94 / C30 hash check before restating", decision_rule_sha256=h, networks=res,
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    files = sorted(set(PER_NET["D94"] + PER_NET["C30"]))
    man = sm.build_manifest([OUT], "scratch/n14_restate_check.py", [".venv/bin/python", "scratch/n14_restate_check.py"],
                            files + [RULE], dict(model_hyperparameters="none (hash comparison only)"), "")
    sm.write_manifest(man, OUT)


if __name__ == "__main__":
    main()
