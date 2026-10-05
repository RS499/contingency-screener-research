import os
import sys
import json
import hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import sts_manifest as sm

# N13 Step 7 (scratch/n13_decision_rule.md §4, tier-B rows): SAFER and FASTER (N5 form) on rebuilt D94 + D95a, and
# SHIFT-ADVANTAGE (N9 Part 2) on rebuilt D94 -> D95a, as replications under their original definitions (quoted and
# checked verbatim). Old-build verdicts beside. Output: data/sts_n13_verdicts_tierB.json + manifest.

RULE = "scratch/n13_decision_rule.md"
RULE_SHA = "scratch/n13_decision_rule.sha256"
OUT = "data/sts_n13_verdicts_tierB.json"
DEFS = {
    "SAFER": ("scratch/n5_decision_rule.md", "histgb missed = certified true violations / true violations <= 0.01 in at least 4 of 5 splits."),
    "FASTER1": ("scratch/n5_decision_rule.md", "10. **FASTER, clause 1.** mean_split(speedup_B, 0.95) - mean_split(speedup_B, 0.94) >"),
    "FASTER2": ("scratch/n5_decision_rule.md", "Clause 2 holds if mean(gate catch) - mean(static catch) > max(std(gate catch), std(static catch))."),
    "SHIFT": ("scratch/n9_decision_rule.md", "mean_split(gate catch) − mean_split(static catch) > max(std_split(gate catch), std_split(static catch))"),
}


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def held(path):
    g = json.load(open(path))
    pts = [p for p in g["points"] if p["family"] == "histgb" and p["point"] == "held_out"]
    return [pts[i] for i in np.argsort([p["seed"] for p in pts])]


def main():
    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    quotes = {k: dict(file=DEFS[k][0], text=DEFS[k][1], verbatim_in_file=DEFS[k][1] in open(DEFS[k][0]).read()) for k in DEFS}
    V = {}
    if os.path.exists("data/sts_n13_gate_D95a.json"):
        h95 = held("data/sts_n13_gate_D95a.json")
        h94 = held("data/sts_n13_gate_D94.json")
        n_ok = len([p for p in h95 if p["missed"] <= 0.01])
        V["SAFER_N5"] = dict(holds=bool(n_ok >= 4), splits_missed_le_1pct=n_ok, missed_per_split=[p["missed"] for p in h95],
                             old_build=dict(holds=False, splits_missed_le_1pct=1, source="data/sts_n5_verdict.json"))
        m95, s95 = ms_([p["speedup_B"] for p in h95])
        m94, s94 = ms_([p["speedup_B"] for p in h94])
        gm, gs = ms_([p["gate_catch"] for p in h95])
        smu, ss = ms_([p["static_catch_B"] for p in h95])
        c1 = bool(m95 - m94 > max(s94, s95))
        c2 = bool(gm - smu > max(gs, ss))
        V["FASTER_N5"] = dict(holds=bool(c1 and c2), clause1=dict(holds=c1, speedup_B_095=m95, std_095=s95, speedup_B_094=m94, std_094=s94,
                                                                 diff=m95 - m94, STD=max(s94, s95)),
                              clause2=dict(holds=c2, gate_catch=gm, gate_std=gs, static_catch=smu, static_std=ss, diff=gm - smu, STD=max(gs, ss)),
                              old_build=dict(holds=False, clause1=True, clause2=False, source="data/sts_n5_verdict.json"))
    else:
        V["SAFER_N5"] = "not run"
        V["FASTER_N5"] = "not run"
    if os.path.exists("data/sts_n13_shift.json"):
        prim = [s for s in json.load(open("data/sts_n13_shift.json"))["summary"] if s["source"] == "D94" and s["target"] == "D95a" and s["family"] == "histgb"][0]
        V["SHIFT_ADVANTAGE"] = dict(holds=prim["gate_higher_by_std_rule"], gate_catch_mean=prim["gate_catch_mean"], gate_catch_std=prim["gate_catch_std"],
                                    static_catch_mean=prim["static_catch_B_mean"], static_catch_std=prim["static_catch_B_std"], gap=prim["gap"], STD=prim["STD"],
                                    old_build=dict(holds=False, source="data/sts_n9_shift.json"))
    else:
        V["SHIFT_ADVANTAGE"] = "not run"
    h2 = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h2 != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    out = dict(part="N13 tier-B verdicts on rebuilt data (replications)", decision_rule=RULE, decision_rule_sha256=h,
               definitions_quoted=quotes, verdicts=V, std_convention="population std (ddof=0) over 5 splits")
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, default=float)
    ins = [RULE] + [p for p in ["data/sts_n13_gate_D94.json", "data/sts_n13_gate_D95a.json", "data/sts_n13_shift.json",
                                "data/sts_n5_verdict.json", "data/sts_n9_shift.json"] if os.path.exists(p)]
    man = sm.build_manifest([OUT], "scratch/n13_verdicts_B.py", [".venv/bin/python", "scratch/n13_verdicts_B.py"], ins,
                            dict(model_hyperparameters="see the input gate manifests"), "")
    sm.write_manifest(man, OUT)
    print(json.dumps(dict(quotes_ok={k: quotes[k]["verbatim_in_file"] for k in quotes},
                          verdicts={k: (V[k]["holds"] if isinstance(V[k], dict) else V[k]) for k in V}), indent=1))


if __name__ == "__main__":
    main()
