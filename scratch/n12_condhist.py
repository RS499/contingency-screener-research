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

# N12 Part A (scratch/n12_decision_rule.md §1): conditional-history baseline vs the gate. No model is fit.
# Per network and split (seeds 0-4):
#   margin m_b = n0_min_vm - 0.94 per base case; 5 bins = quintiles of m_b over the split's TRAIN base cases
#   (np.quantile at 0.2/0.4/0.6/0.8, default linear method; bin = number of edges <= m_b, so 0..4).
#   COND-HIST score p(e, bin) = (v + a*f_e) / (n + a), a = 10; v, n = violations and rows of element e in that bin
#   over train; f_e = element e's overall train violation frequency (0 if e never appears in train).
#   GLOBAL-STATIC score = f_e.
#   Budget N = round(s_B * n_test), s_B = the gate's rule-B solve share on that split (histgb, held-out; stored).
#   The N test rows with the highest score across all test base cases are solved; ties by element index, then
#   scenario_id (both ascending). Catch = true violations solved / all test true violations.
# GATE-BEATS-CONDHIST per network: mean(gate catch) - mean(COND-HIST catch) > max(std gate, std COND-HIST).
# Primary verdict: case_illinois200.

RULE = "scratch/n12_decision_rule.md"
RULE_SHA = "scratch/n12_decision_rule.sha256"
OUT = "data/sts_n12_condhist.json"
A_SMOOTH = 10.0
N_BINS = 5
QUANTILES = [0.2, 0.4, 0.6, 0.8]
LIMIT = 0.94
PRIMARY = "case_illinois200"


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def budget_catch(score, ek, scen, viol, n_solve):
    # highest score first; ties by element index then scenario_id (np.lexsort: last key is primary)
    order = np.lexsort((scen, ek, -score))
    solved = order[:n_solve]
    return float(viol[solved].sum() / max(int(viol.sum()), 1))


def run_split(d, seed, gate_pt):
    splits = ms.make_splits(d["groups"], seed)
    tr, te = splits["train"], splits["test"]
    df = d["df"]
    ek = d["elem_key"]
    viol_all = d["y"] < LIMIT
    margin = df["n0_min_vm"].to_numpy(np.float64) - LIMIT
    scen_all = df["scenario_id"].to_numpy(np.int64)
    # train base-case margins (one value per base case)
    tr_base = pd.Series(margin[tr], index=scen_all[tr]).groupby(level=0).first()
    edges = np.quantile(tr_base.to_numpy(), QUANTILES)
    bins = np.searchsorted(edges, margin, side="right")
    # f_e over train
    t = pd.DataFrame(dict(e=ek[tr], b=bins[tr], v=viol_all[tr].astype(float)))
    f = t.groupby("e")["v"].mean()
    cell = t.groupby(["e", "b"])["v"].agg(["sum", "count"])
    e_te = ek[te]
    b_te = bins[te]
    f_te = f.reindex(e_te).fillna(0.0).to_numpy()
    idx = pd.MultiIndex.from_arrays([e_te, b_te])
    v_te = cell["sum"].reindex(idx).fillna(0.0).to_numpy()
    n_te = cell["count"].reindex(idx).fillna(0.0).to_numpy()
    p_cond = (v_te + A_SMOOTH * f_te) / (n_te + A_SMOOTH)
    viol = viol_all[te]
    scen = scen_all[te]
    n_test = len(te)
    s_b = float(gate_pt["solve_share_B"])
    n_solve = int(round(s_b * n_test))
    return dict(seed=seed, s_B=s_b, n_test=n_test, n_solve=n_solve, n_test_viol=int(viol.sum()),
                bin_edges=[float(x) for x in edges], train_bases_per_bin=np.bincount(np.searchsorted(edges, tr_base.to_numpy(), side="right"), minlength=N_BINS).tolist(),
                test_rows_per_bin=np.bincount(b_te, minlength=N_BINS).tolist(),
                gate_catch=float(gate_pt["gate_catch"]), static_fixed_catch=float(gate_pt["static_catch_B"]),
                condhist_catch=budget_catch(p_cond, e_te, scen, viol, n_solve),
                global_static_catch=budget_catch(f_te, e_te, scen, viol, n_solve))


def main():
    t0 = time.time()
    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    res = {}
    for name in ld.NETS:
        d = ld.load(name)
        rep = ld.check(d)
        if len([r for r in rep if r["exact"]]) != len(rep):
            res[name] = dict(stopped="reproduction check failed", repro=rep)
            print(f"{name}: STOPPED (reproduction)", flush=True)
            continue
        pts = ld.held_out_points(name, "histgb")
        per = [run_split(d, s, pts[s]) for s in ld.SEEDS]
        s = {}
        for k in ["gate_catch", "static_fixed_catch", "condhist_catch", "global_static_catch", "s_B"]:
            s[k + "_mean"], s[k + "_std"] = ms_([r[k] for r in per])
        s["gap_gate_minus_condhist"] = s["gate_catch_mean"] - s["condhist_catch_mean"]
        s["STD"] = max(s["gate_catch_std"], s["condhist_catch_std"])
        s["gate_beats_condhist"] = bool(s["gap_gate_minus_condhist"] > s["STD"])
        res[name] = dict(per_split=per, summary=s, repro=rep)
        print(f"{name}: gate {100 * s['gate_catch_mean']:.2f}±{100 * s['gate_catch_std']:.2f} | COND-HIST "
              f"{100 * s['condhist_catch_mean']:.2f}±{100 * s['condhist_catch_std']:.2f} | GLOBAL-STATIC "
              f"{100 * s['global_static_catch_mean']:.2f}±{100 * s['global_static_catch_std']:.2f} | fixed static "
              f"{100 * s['static_fixed_catch_mean']:.2f} -> beats {s['gate_beats_condhist']}", flush=True)
    h2 = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h2 != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    done = [n for n in res if "summary" in res[n]]
    verdict = dict(
        GATE_BEATS_CONDHIST_primary=dict(network=PRIMARY, holds=(res[PRIMARY]["summary"]["gate_beats_condhist"]
                                                                 if PRIMARY in done else None)),
        per_network={n: res[n]["summary"]["gate_beats_condhist"] for n in done},
        count_networks_gate_beats_condhist=len([n for n in done if res[n]["summary"]["gate_beats_condhist"]]),
        n_networks_evaluated=len(done),
        rule="histgb, held-out, rule B: mean(gate catch) - mean(COND-HIST catch) > max(std gate, std COND-HIST)")
    out = dict(part="N12 Part A: conditional-history baseline", decision_rule=RULE, decision_rule_sha256=h,
               decision_rule_hash_verified=True, verdict=verdict, networks=res,
               settings=dict(smoothing_a=A_SMOOTH, n_bins=N_BINS, quantiles=QUANTILES, quantile_method="numpy default (linear)",
                             bin_assignment="searchsorted(edges, m, side='right') -> 0..4",
                             tie_break="element index ascending, then scenario_id ascending",
                             budget="N = round(s_B * n_test), s_B from the stored gate (histgb, held-out, rule B)"),
               std_convention="population std (ddof=0) over 5 splits", wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    inputs = [RULE]
    for n in ld.NETS:
        inputs += [ld.NETS[n]["data"], ld.NETS[n]["labels"], ld.NETS[n]["gate"]]
    man = sm.build_manifest([OUT], "scratch/n12_condhist.py", [".venv/bin/python", "scratch/n12_condhist.py"],
                            sorted(set(inputs)), dict(seeds=ld.SEEDS, bins=N_BINS, bin_quantiles=QUANTILES, smoothing_a=A_SMOOTH,
                                                      limit=LIMIT, model_hyperparameters="none: lookup table, no model fit; gate numbers reused from the stored gate JSONs"), "")
    sm.write_manifest(man, OUT)
    print(json.dumps(verdict, indent=1))


if __name__ == "__main__":
    main()
