import os
import sys
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import sts_manifest as sm
import n14_common as cm

# N14 Step 7 (scratch/n14_decision_rule.md §B): verdicts applied word for word.
# Primary: BEATS-STATIC per network, SAFER-IL, GATE-BEATS-CONDHIST per network (primary ILL), count of networks where
# the gate wins. Sensitivity: BEATS-STATIC and GATE-BEATS-CONDHIST per network. Then the ILL outcome (a)/(b)/(c) with
# the rule's fixed wording. N13 verdicts beside. Definitions and wording are checked verbatim against the rule files.
# Output: data/sts_n14_verdicts.json + manifest.

OUT = "data/sts_n14_verdicts.json"
DEFS = {
    "BEATS_STATIC": ("scratch/n10_decision_rule.md", "mean(gate catch) − mean(static catch at k_B) > max(std gate, std static)"),
    "SAFER_IL": ("scratch/n10_decision_rule.md", "Histgb held-out missed ≤ 1% in ≥ 4 of 5 splits."),
    "CONDHIST": ("scratch/n12_decision_rule.md", "mean_split(gate catch) − mean_split(COND-HIST catch) > max(std gate, std COND-HIST)"),
    "OUTCOME_A": (cm.RULE, "the gate's advantage over COND-HIST on Illinois holds with and without islanding outages"),
    "OUTCOME_B": (cm.RULE, "the gate's advantage on Illinois depends on including islanding outages"),
    "OUTCOME_C": (cm.RULE, "on Illinois the gate does not beat COND-HIST once trafo 63 is excluded"),
}
NETS = ["D94", "ILL", "C30", "C24"]


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def held(path):
    g = json.load(open(path))
    pts = [p for p in g["points"] if p["family"] == "histgb" and p["point"] == "held_out"]
    return [pts[i] for i in np.argsort([p["seed"] for p in pts])]


def beats_static(h):
    gm, gs = ms_([p["gate_catch"] for p in h])
    smu, ss = ms_([p["static_catch_B"] for p in h])
    return dict(holds=bool(gm - smu > max(gs, ss)), gate_catch_mean=gm, gate_catch_std=gs, static_catch_mean=smu, static_catch_std=ss,
                gap=gm - smu, STD=max(gs, ss))


def condhist_rule(s):
    gap = s["gate_catch_mean"] - s["condhist_catch_mean"]
    std = max(s["gate_catch_std"], s["condhist_catch_std"])
    return dict(holds=bool(gap > std), gate_catch_mean=s["gate_catch_mean"], condhist_catch_mean=s["condhist_catch_mean"], gap=gap, STD=std)


def gate_primary(name):
    return f"data/sts_n13_gate_{name}.json" if name in ("D94", "C30") else f"data/sts_n14_gate_{name}.json"


def main():
    h = cm.check_hash()
    quotes = {k: dict(file=DEFS[k][0], text=DEFS[k][1], verbatim_in_file=DEFS[k][1] in open(DEFS[k][0]).read()) for k in DEFS}
    n13 = json.load(open("data/sts_n13_verdicts.json"))["verdicts"]
    V = dict(primary={}, sensitivity={})
    bs = {}
    for n in NETS:
        p = gate_primary(n)
        bs[n] = beats_static(held(p)) if os.path.exists(p) else "not run"
        if isinstance(bs[n], dict):
            o = n13["BEATS_STATIC"]["per_network"][n]
            bs[n]["n13"] = o["holds"] if isinstance(o, dict) else o
            bs[n]["source"] = p
    V["primary"]["BEATS_STATIC"] = bs
    hil = held("data/sts_n14_gate_ILL.json") if os.path.exists("data/sts_n14_gate_ILL.json") else None
    if hil:
        n_ok = len([p for p in hil if p["missed"] <= 0.01])
        V["primary"]["SAFER_IL"] = dict(holds=bool(n_ok >= 4), splits_missed_le_1pct=n_ok, missed_per_split=[p["missed"] for p in hil],
                                        n13=n13["SAFER_IL"]["holds"])
    else:
        V["primary"]["SAFER_IL"] = "not run"
    chp = json.load(open("data/sts_n14_condhist.json"))["networks"] if os.path.exists("data/sts_n14_condhist.json") else {}
    ch = {}
    for n in NETS:
        if n in chp:
            ch[n] = condhist_rule(chp[n]["summary"])
            o = n13["GATE_BEATS_CONDHIST"]["per_network"][n]
            ch[n]["n13"] = o["holds"] if isinstance(o, dict) else o
        else:
            ch[n] = "not run"
    V["primary"]["GATE_BEATS_CONDHIST"] = dict(per_network=ch, primary_network="ILL",
                                               count_gate_wins=len([n for n in ch if isinstance(ch[n], dict) and ch[n]["holds"]]),
                                               n_networks=len([n for n in ch if isinstance(ch[n], dict)]))
    sens = json.load(open("data/sts_n14_sensitivity.json"))["networks"] if os.path.exists("data/sts_n14_sensitivity.json") else {}
    sb, sc = {}, {}
    for n in NETS:
        if n in sens and isinstance(sens[n], dict):
            sb[n] = beats_static(held(f"data/sts_n14_gate_{n}_sens.json"))
            sc[n] = condhist_rule(sens[n]["condhist"]["summary"])
        else:
            sb[n] = "not run"
            sc[n] = "not run"
    V["sensitivity"]["BEATS_STATIC"] = sb
    V["sensitivity"]["GATE_BEATS_CONDHIST"] = sc
    prim = ch.get("ILL")
    sen = sc.get("ILL")
    outcome = None
    if isinstance(prim, dict):
        if not prim["holds"]:
            outcome = dict(case="c", wording=DEFS["OUTCOME_C"][1], note="the cross-network count of networks where the gate wins drops by one")
        elif isinstance(sen, dict) and sen["holds"]:
            outcome = dict(case="a", wording=DEFS["OUTCOME_A"][1])
        elif isinstance(sen, dict):
            outcome = dict(case="b", wording=DEFS["OUTCOME_B"][1])
        else:
            outcome = dict(case="sensitivity not run", wording=None)
    V["ILL_outcome"] = outcome if outcome else "not run"
    cm.check_hash()
    out = dict(part="N14 verdicts (replications on the rebuilt N13 data, N14 primary and sensitivity)", decision_rule_sha256=h,
               definitions_quoted=quotes, verdicts=V, std_convention="population std (ddof=0) over 5 splits")
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, default=float)
    ins = [cm.RULE, "data/sts_n13_verdicts.json"] + [p for p in [gate_primary(n) for n in NETS] + [f"data/sts_n14_gate_{n}_sens.json" for n in NETS]
                                                      + ["data/sts_n14_condhist.json", "data/sts_n14_sensitivity.json"] if os.path.exists(p)]
    man = sm.build_manifest([OUT], "scratch/n14_verdicts.py", [".venv/bin/python", "scratch/n14_verdicts.py"], ins,
                            dict(model_hyperparameters="see the input gate manifests"), "")
    sm.write_manifest(man, OUT)
    print(json.dumps(dict(quotes_ok={k: quotes[k]["verbatim_in_file"] for k in quotes}, ILL_outcome=V["ILL_outcome"]), indent=1))


if __name__ == "__main__":
    main()
