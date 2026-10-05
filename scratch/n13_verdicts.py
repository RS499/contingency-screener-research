import os
import sys
import json
import hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import sts_manifest as sm

# N13 Step 5 (scratch/n13_decision_rule.md §4): tier-A verdicts on the rebuilt data, as replications under their
# original definitions. Each definition string below is checked to appear verbatim in the hashed rule file it cites.
# The old-build verdict is read from the old result file and reported beside it. Population std (ddof=0) over 5 splits.
# Missing inputs -> "not run" (never estimated). Output: data/sts_n13_verdicts.json + manifest.

RULE = "scratch/n13_decision_rule.md"
RULE_SHA = "scratch/n13_decision_rule.sha256"
OUT = "data/sts_n13_verdicts.json"
DEFS = {
    "SAFER": ("scratch/n5_decision_rule.md", "histgb missed = certified true violations / true violations <= 0.01 in at least 4 of 5 splits."),
    "BEATS_STATIC": ("scratch/n10_decision_rule.md", "mean(gate catch) − mean(static catch at k_B) > max(std gate, std static)"),
    "SAFER_IL": ("scratch/n10_decision_rule.md", "Histgb held-out missed ≤ 1% in ≥ 4 of 5 splits."),
    "CONDHIST": ("scratch/n12_decision_rule.md", "mean_split(gate catch) − mean_split(COND-HIST catch) > max(std gate, std COND-HIST)"),
    "N2": ("scratch/n11_decision_rule.md", "mean_split(coverage_N2) ≥ 0.90 − max(std_split(coverage_N2), std_split(coverage_N1))"),
    "MONDRIAN": ("scratch/n11_decision_rule.md", "mean(Mondrian gate catch) − mean(static catch at the Mondrian gate's k_B) > max(std gate, std static)"),
    "FLOOR1": ("scratch/n11_decision_rule.md", "1. BM(0.96) < BM(0.95 build D95a) − 5 pp."),
    "FLOOR2": ("scratch/n11_decision_rule.md", "2. |BM(0.93) − BM(0.94)| ≤ 5 pp."),
    "V2": (RULE, "| V2. SAFETY-CHANGED: \\|mean missed (rebuilt) − mean missed (old, `data/sts_n5_gate_094.json`)\\| > max(the two stds), histgb, held-out; unpaired; sign reported |"),
}


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def held(path, fam, key=None):
    if not os.path.exists(path):
        return None
    g = json.load(open(path))
    if key:
        g = g["networks"][key]
    pts = [p for p in g["points"] if p["family"] == fam and p["point"] == "held_out"]
    return [pts[i] for i in np.argsort([p["seed"] for p in pts])]


def catch_rule(h):
    gm, gs = ms_([p["gate_catch"] for p in h])
    sm_, ss = ms_([p["static_catch_B"] for p in h])
    return dict(holds=bool(gm - sm_ > max(gs, ss)), gate_catch_mean=gm, gate_catch_std=gs, static_catch_mean=sm_,
                static_catch_std=ss, gap=gm - sm_, STD=max(gs, ss))


def main():
    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    quotes = {}
    for k in DEFS:
        path, txt = DEFS[k]
        quotes[k] = dict(file=path, text=txt, verbatim_in_file=txt.replace("\\|", "|") in open(path).read() or txt in open(path).read())
    V = {}
    # V1 SAFER-94 and V2 SAFETY-CHANGED (D94)
    new94 = held("data/sts_n13_gate_D94.json", "histgb")
    old94 = held("data/sts_n5_gate_094.json", "histgb")
    if new94:
        n_ok = len([p for p in new94 if p["missed"] <= 0.01])
        V["V1_SAFER_94"] = dict(holds=bool(n_ok >= 4), splits_missed_le_1pct=n_ok, missed_per_split=[p["missed"] for p in new94],
                                old_build=dict(holds=False, splits_missed_le_1pct=len([p for p in old94 if p["missed"] <= 0.01]),
                                               source="data/sts_n5_gate_094.json (N5 reported the 0.94 count; the N5 verdict was on 0.95)"),
                                primary=True, definition="SAFER")
        nm, ns = ms_([p["missed"] for p in new94])
        om, os_ = ms_([p["missed"] for p in old94])
        V["V2_SAFETY_CHANGED"] = dict(holds=bool(abs(nm - om) > max(ns, os_)), rebuilt_mean=nm, rebuilt_std=ns, old_mean=om, old_std=os_,
                                      diff_rebuilt_minus_old=nm - om, STD=max(ns, os_), sign="rebuilt higher" if nm > om else "rebuilt lower",
                                      primary=True, definition="V2", old_build="not applicable (defined by N13)")
    else:
        V["V1_SAFER_94"] = "not run"
        V["V2_SAFETY_CHANGED"] = "not run"
    # BEATS-STATIC per network; SAFER-IL
    old_static = {"D94": ("data/sts_n5_gate_094.json", None), "ILL": ("data/sts_n10_illinois.json", None),
                  "C30": ("data/sts_n11_smallnets.json", "case30_thermal"), "C24": ("data/sts_n11_smallnets.json", "case24_ieee_rts")}
    bs = {}
    for name in ["D94", "ILL", "C30", "C24"]:
        hn = held(f"data/sts_n13_gate_{name}.json", "histgb")
        ho = held(old_static[name][0], "histgb", old_static[name][1])
        if hn:
            r = catch_rule(hn)
            r["old_build"] = catch_rule(ho)
            bs[name] = r
        else:
            bs[name] = "not run"
    V["BEATS_STATIC"] = dict(per_network=bs, primary_network="ILL", definition="BEATS_STATIC")
    hil = held("data/sts_n13_gate_ILL.json", "histgb")
    if hil:
        n_ok = len([p for p in hil if p["missed"] <= 0.01])
        V["SAFER_IL"] = dict(holds=bool(n_ok >= 4), splits_missed_le_1pct=n_ok, missed_per_split=[p["missed"] for p in hil],
                             old_build=dict(holds=bool(len([p for p in held("data/sts_n10_illinois.json", "histgb") if p["missed"] <= 0.01]) >= 4),
                                            splits_missed_le_1pct=len([p for p in held("data/sts_n10_illinois.json", "histgb") if p["missed"] <= 0.01]),
                                            source="data/sts_n10_illinois.json"), definition="SAFER_IL")
    else:
        V["SAFER_IL"] = "not run"
    # GATE-BEATS-CONDHIST
    if os.path.exists("data/sts_n13_condhist.json"):
        chj = json.load(open("data/sts_n13_condhist.json"))["networks"]
        old_ch = json.load(open("data/sts_n12_condhist.json"))["networks"]
        per = {}
        for name, oname in [("D94", "case118"), ("ILL", "case_illinois200"), ("C30", "case30_thermal"), ("C24", "case24_ieee_rts")]:
            if name in chj:
                s = chj[name]["summary"]
                gap = s["gate_catch_mean"] - s["condhist_catch_mean"]
                std = max(s["gate_catch_std"], s["condhist_catch_std"])
                per[name] = dict(holds=bool(gap > std), gap=gap, STD=std, gate_catch_mean=s["gate_catch_mean"],
                                 condhist_catch_mean=s["condhist_catch_mean"], old_build=old_ch[oname]["summary"]["gate_beats_condhist"])
            else:
                per[name] = "not run"
        V["GATE_BEATS_CONDHIST"] = dict(per_network=per, primary_network="ILL",
                                        count=len([n for n in per if isinstance(per[n], dict) and per[n]["holds"]]), definition="CONDHIST")
    else:
        V["GATE_BEATS_CONDHIST"] = "not run"
    # COVERAGE-HOLDS-N2
    if os.path.exists("data/sts_n13_n2.json"):
        s = [x for x in json.load(open("data/sts_n13_n2.json"))["summary"] if x["family"] == "histgb" and x["point"] == "t090"][0]
        thr = 0.90 - max(s["n2_coverage_std"], s["n1_coverage_std"])
        V["COVERAGE_HOLDS_N2"] = dict(holds=bool(s["n2_coverage_mean"] >= thr), coverage_n2_mean=s["n2_coverage_mean"], coverage_n2_std=s["n2_coverage_std"],
                                      coverage_n1_std=s["n1_coverage_std"], threshold=thr, old_build=False, primary=True, definition="N2")
    else:
        V["COVERAGE_HOLDS_N2"] = "not run"
    # MONDRIAN-BEATS-STATIC
    if os.path.exists("data/sts_n13_mondrian.json"):
        s = [x for x in json.load(open("data/sts_n13_mondrian.json"))["summary"] if x["family"] == "histgb"][0]
        gap = s["gate_catch_mean"] - s["static_catch_B_mean"]
        std = max(s["gate_catch_std"], s["static_catch_B_std"])
        V["MONDRIAN_BEATS_STATIC"] = dict(holds=bool(gap > std), gap=gap, STD=std, old_build=False, definition="MONDRIAN")
    else:
        V["MONDRIAN_BEATS_STATIC"] = "not run"
    # FLOOR_DOSE_RESPONSE
    if os.path.exists("data/sts_n13_floor.json"):
        fl = {}
        for r in json.load(open("data/sts_n13_floor.json"))["per_floor"]:
            if r.get("available"):
                fl[r["floor"]] = r["BM"]
        if len(fl) == 4:
            c1 = bool(fl[0.96] < fl[0.95] - 5.0)
            c2 = bool(abs(fl[0.93] - fl[0.94]) <= 5.0)
            V["FLOOR_DOSE_RESPONSE"] = dict(holds=bool(c1 and c2), clause1=c1, clause2=c2, bm=fl, old_build=True, primary=True,
                                            definition=["FLOOR1", "FLOOR2"])
        else:
            V["FLOOR_DOSE_RESPONSE"] = dict(status="not run (missing floors)", available=fl)
    else:
        V["FLOOR_DOSE_RESPONSE"] = "not run"
    h2 = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h2 != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    out = dict(part="N13 Step 5: tier-A verdicts on rebuilt data (replications under the original definitions)",
               decision_rule=RULE, decision_rule_sha256=h, definitions_quoted=quotes, verdicts=V,
               tier_B_verdicts="not part of this file (SAFER/FASTER N5 form on D95a, SHIFT-ADVANTAGE)",
               std_convention="population std (ddof=0) over 5 splits")
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, default=float)
    ins = [RULE] + [p for p in ["data/sts_n13_gate_D94.json", "data/sts_n13_gate_ILL.json", "data/sts_n13_gate_C30.json", "data/sts_n13_gate_C24.json",
                                "data/sts_n13_condhist.json", "data/sts_n13_n2.json", "data/sts_n13_mondrian.json", "data/sts_n13_floor.json",
                                "data/sts_n5_gate_094.json", "data/sts_n10_illinois.json", "data/sts_n11_smallnets.json", "data/sts_n12_condhist.json"]
                    if os.path.exists(p)]
    man = sm.build_manifest([OUT], "scratch/n13_verdicts.py", [".venv/bin/python", "scratch/n13_verdicts.py"], ins,
                            dict(model_hyperparameters="see the input gate manifests"), "")
    sm.write_manifest(man, OUT)
    print(json.dumps(dict(quotes_ok={k: quotes[k]["verbatim_in_file"] for k in quotes}), indent=1))
    for k in V:
        v = V[k]
        if isinstance(v, dict) and "holds" in v:
            print(k, v["holds"])
        else:
            print(k, v if not isinstance(v, dict) else {kk: (vv["holds"] if isinstance(vv, dict) and "holds" in vv else vv) for kk, vv in v.get("per_network", v).items()})


if __name__ == "__main__":
    main()
