import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import sts_manifest as sm

# N5 Step 3 summary: mean +/- population std over the 5 splits for every family / dataset / point, and the
# pre-registered rule (scratch/n5_decision_rule.md) applied as written. Reads only the two Step 3 outputs.

RULE = "scratch/n5_decision_rule.md"
RULE_SHA = "scratch/n5_decision_rule.sha256"
IN = {"094": "data/sts_n5_gate_094.json", "095": "data/sts_n5_gate_095.json"}
OUT = "data/sts_n5_verdict.json"
COLS = ["target", "escalation", "flag_share", "solve_share_B", "missed", "gate_catch", "gate_catch_escalate_only",
        "speedup_A", "speedup_B", "static_catch_A", "static_catch_B", "k_A", "k_B"]


def ms(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def main():
    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    recorded = open(RULE_SHA).read().split()[0]
    if h != recorded:
        raise ValueError("decision rule file changed since it was hashed")
    tables = {}
    per_split = {}
    for run in IN:
        d = json.load(open(IN[run]))
        pts = pd.DataFrame([p for p in d["points"] if p["point"] in ("grid", "held_out")])
        pts["tkey"] = np.where(pts["point"] == "grid", pts["target"].round(2), -1.0)
        rows = []
        for (fam, kind, tgt), g in pts.groupby(["family", "point", "tkey"]):
            r = dict(family=fam, point=kind, target=None if kind == "held_out" else float(tgt), n_splits=int(len(g)))
            for c in COLS:
                mu, sd = ms(g[c])
                r[c + "_mean"] = mu
                r[c + "_std"] = sd
            for acc, gc, sc in [("A", "gate_catch", "static_catch_A"), ("B", "gate_catch", "static_catch_B")]:
                gm, gs = ms(g[gc])
                smu, ss = ms(g[sc])
                gap = gm - smu
                r["catch_gap_" + acc] = gap
                r["std_rule_" + acc] = ("gate higher" if gap > 0 else "static higher") if abs(gap) > max(gs, ss) else "tie (gap within larger std)"
            rows.append(r)
        tables[run] = rows
        per_split[run] = [p for p in d["points"] if p["point"] == "held_out"]
        tables[run + "_labels"] = d["labels"]
        tables[run + "_selections"] = d["selections"]

    def held(run, fam):
        return [p for p in per_split[run] if p["family"] == fam]

    verdict = {}
    for run in IN:
        hg = held(run, "histgb")
        n_ok = sum(1 for p in hg if p["missed"] <= 0.01)
        n_missing = 5 - len(hg)
        verdict[f"safer_count_{run}"] = dict(splits_with_missed_le_1pct=n_ok, splits_missing_held_out=n_missing,
                                             missed_per_split=[p["missed"] for p in sorted(hg, key=lambda x: x["seed"])],
                                             passes_4_of_5=bool(n_ok >= 4))
    verdict["SAFER"] = verdict["safer_count_095"]["passes_4_of_5"]
    sb94 = [p["speedup_B"] for p in held("094", "histgb")]
    sb95 = [p["speedup_B"] for p in held("095", "histgb")]
    m94, s94 = ms(sb94)
    m95, s95 = ms(sb95)
    std1 = max(s94, s95)
    c1 = bool((m95 - m94) > std1)
    g95 = [p["gate_catch"] for p in held("095", "histgb")]
    st95 = [p["static_catch_B"] for p in held("095", "histgb")]
    gm, gs = ms(g95)
    sm_, ss = ms(st95)
    std2 = max(gs, ss)
    c2 = bool((gm - sm_) > std2)
    verdict["FASTER_clause1"] = dict(speedup_B_094_mean=m94, speedup_B_094_std=s94, speedup_B_095_mean=m95,
                                     speedup_B_095_std=s95, diff=m95 - m94, STD=std1, holds=c1)
    verdict["FASTER_clause2"] = dict(gate_catch_095_mean=gm, gate_catch_095_std=gs, static_catch_B_095_mean=sm_,
                                     static_catch_B_095_std=ss, diff=gm - sm_, STD=std2, holds=c2)
    verdict["FASTER"] = bool(c1 and c2)
    out = dict(decision_rule=RULE, decision_rule_sha256=h, decision_rule_hash_verified=True,
               verdict=verdict, tables=tables, std_convention="population std (ddof=0) over 5 splits")
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    man = sm.build_manifest([OUT], "scratch/n5_summarize.py", [".venv/bin/python", "scratch/n5_summarize.py"],
                            [IN["094"], IN["095"], RULE], dict(model_hyperparameters="see manifests of the two inputs (M2 configs per split)"), "")
    sm.write_manifest(man, OUT)
    print(json.dumps(verdict, indent=1))
    for run in IN:
        for r in tables[run]:
            t = "held" if r["point"] == "held_out" else f"{r['target']:.2f}"
            print(f"{run} {r['family']:6s} {t:>5s} tgt {r['target_mean']:.3f}±{r['target_std']:.3f} "
                  f"esc {100*r['escalation_mean']:5.1f}±{100*r['escalation_std']:.1f} flag {100*r['flag_share_mean']:4.1f} "
                  f"miss {100*r['missed_mean']:5.2f}±{100*r['missed_std']:.2f} spA {r['speedup_A_mean']:.3f}±{r['speedup_A_std']:.3f} "
                  f"spB {r['speedup_B_mean']:.3f}±{r['speedup_B_std']:.3f} catch {100*r['gate_catch_mean']:6.2f}±{100*r['gate_catch_std']:.2f} "
                  f"stA {100*r['static_catch_A_mean']:6.2f}±{100*r['static_catch_A_std']:.2f} stB {100*r['static_catch_B_mean']:6.2f}±{100*r['static_catch_B_std']:.2f} "
                  f"[A {r['std_rule_A']}; B {r['std_rule_B']}]")


if __name__ == "__main__":
    main()
