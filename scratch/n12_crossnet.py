import os
import sys
import json
import time
import hashlib
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import make_splits as ms
import sts_manifest as sm
import n12_loaders as ld

# N12 Part C (scratch/n12_decision_rule.md §3, descriptive): one table over the 4 networks.
# Columns: corrected boundary mass [0.94, 0.945) and violation rate (all converged N-1 rows with a corrected label);
# spread of risk = std (ddof=0) over test base cases of the per-base violation share, per split, then mean +- std
# over splits; violation concentration = share of test violations from the top-10 elements ranked by train
# violation frequency (n10_gate_illinois.concentration definition), per split; gate catch, fixed-budget static
# catch, COND-HIST catch and GLOBAL-STATIC catch from data/sts_n12_condhist.json. n = 4: no correlation or law.

RULE = "scratch/n12_decision_rule.md"
RULE_SHA = "scratch/n12_decision_rule.sha256"
CONDHIST = "data/sts_n12_condhist.json"
OUT = "data/sts_n12_crossnet.json"
LIMIT = 0.94
TOP = 10


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def top_share(df_viol, ek, tr, te):
    t = pd.DataFrame(dict(e=ek[tr], v=df_viol[tr].astype(float)))
    freq = t.groupby("e")["v"].mean().sort_values(ascending=False, kind="stable")
    top = freq.index[:TOP].to_numpy()
    tv = df_viol[te]
    return float((np.isin(ek[te], top) & tv).sum() / max(int(tv.sum()), 1))


def main():
    t0 = time.time()
    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    ch = json.load(open(CONDHIST))["networks"]
    rows = []
    for name in ld.NETS:
        d = ld.load(name)
        y = d["y"]
        viol = y < LIMIT
        scen = d["df"]["scenario_id"].to_numpy(np.int64)
        spread, conc = [], []
        for seed in ld.SEEDS:
            sp = ms.make_splits(d["groups"], seed)
            te = sp["test"]
            per_base = pd.Series(viol[te].astype(float)).groupby(scen[te]).mean()
            spread.append(float(per_base.std(ddof=0)))
            conc.append(top_share(viol, d["elem_key"], sp["train"], te))
        r = dict(network=name, n_rows=int(len(y)), boundary_mass=float(((y >= LIMIT) & (y < 0.945)).mean()),
                 violation_rate=float(viol.mean()))
        r["risk_spread_mean"], r["risk_spread_std"] = ms_(spread)
        r["top10_concentration_mean"], r["top10_concentration_std"] = ms_(conc)
        if "summary" in ch.get(name, {}):
            s = ch[name]["summary"]
            for k in ["gate_catch", "static_fixed_catch", "condhist_catch", "global_static_catch"]:
                r[k + "_mean"] = s[k + "_mean"]
                r[k + "_std"] = s[k + "_std"]
        else:
            r["catch_columns"] = "not available: Part A stopped for this network"
        rows.append(r)
        print(f"{name}: BM {100 * r['boundary_mass']:.2f}% VR {100 * r['violation_rate']:.2f}% spread "
              f"{r['risk_spread_mean']:.3f} top10 {100 * r['top10_concentration_mean']:.1f}% | gate "
              f"{100 * r.get('gate_catch_mean', float('nan')):.2f} static {100 * r.get('static_fixed_catch_mean', float('nan')):.2f} "
              f"cond {100 * r.get('condhist_catch_mean', float('nan')):.2f} global {100 * r.get('global_static_catch_mean', float('nan')):.2f}",
              flush=True)
    out = dict(part="N12 Part C: cross-network summary (descriptive, n = 4, no correlation or law claimed)",
               decision_rule=RULE, decision_rule_sha256=h, table=rows, top_n=TOP,
               definitions=dict(boundary_mass="share of corrected-label N-1 rows in [0.94, 0.945)",
                                violation_rate="share < 0.94", risk_spread="std (ddof=0) over test base cases of per-base violation share; mean +- std over 5 splits",
                                concentration="share of test violations from the top-10 elements by train violation frequency"),
               std_convention="population std (ddof=0) over 5 splits", wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    inputs = [RULE, CONDHIST]
    for n in ld.NETS:
        inputs += [ld.NETS[n]["data"], ld.NETS[n]["labels"]]
    man = sm.build_manifest([OUT], "scratch/n12_crossnet.py", [".venv/bin/python", "scratch/n12_crossnet.py"], inputs,
                            dict(seeds=ld.SEEDS, top_n=TOP, limit=LIMIT,
                                 model_hyperparameters="none here; catch columns read from data/sts_n12_condhist.json (gate = stored histgb held-out results)"), "")
    man["no_new_solves"] = "No AC solve and no model fit."
    sm.write_manifest(man, OUT)


if __name__ == "__main__":
    main()
