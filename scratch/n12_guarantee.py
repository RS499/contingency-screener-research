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
import gate_eval as ge
import tune_surrogates as tu
import manifest as mf
import sts_manifest as sm
import n12_loaders as ld

# N12 Part B (scratch/n12_decision_rule.md §2, descriptive): the price of a guarantee. case118 (0.94) and
# case_illinois200; histgb and ridge. The N5 / N10 M2 configs are refit per split on train (no re-search); each
# refit must reproduce the stored held-out escalation and missed exactly (else that network/family is stopped).
# Two calibrations of the certify threshold t on the cal split (certify iff pred >= L + t; flag iff pred < L;
# escalate otherwise; gate_eval.run_gate precedence: a row both certified and flagged counts as certified):
#   row-level, alpha = 0.01: t = ceil((n_v + 1)(1 - alpha))-th smallest (pred - L) over the n_v cal violation rows
#   base-level any-miss, alpha = 0.10: m_b = max over a cal base's violation rows of (pred - L), for bases with >= 1
#     violation; t = ceil((n_b + 1)(1 - alpha))-th smallest m_b. If the rank exceeds n, t = +inf (certify nothing).
# Reported on test: escalation, flag share, missed, any-miss share of base cases, speedup A and B, next to the
# held-out global-q_hat gate (recomputed from the same refit, which reproduces the stored numbers).

NETS = ["case118", "case_illinois200"]
FAMILIES = ["histgb", "ridge"]
OUT = "data/sts_n12_guarantee.json"
RULE = "scratch/n12_decision_rule.md"
RULE_SHA = "scratch/n12_decision_rule.sha256"
LIMIT = 0.94
ALPHA_ROW = 0.01
ALPHA_BASE = 0.10


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def kth(values, alpha):
    v = np.sort(np.asarray(values, dtype=np.float64))
    n = len(v)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    if n == 0 or k > n:
        return float("inf"), n, k
    return float(v[k - 1]), n, k


def gate_metrics(pred, y, scen, t, ms_surr, ms_solver):
    certify = pred >= LIMIT + t
    flag = pred < LIMIT
    esc = ~(certify | flag)
    tv = y < LIMIT
    n = len(y)
    miss_rows = certify & tv
    any_miss = pd.Series(miss_rows).groupby(scen).any()
    return dict(t=float(t), escalation=float(esc.mean()), flag_share=float(flag.mean()),
                certify_share=float(certify.mean()), overlap_certify_and_flag=int((certify & flag).sum()),
                missed=float(miss_rows.sum() / max(int(tv.sum()), 1)), any_miss_share=float(any_miss.mean()),
                speedup_A=float(n * ms_solver / (n * ms_surr + esc.sum() * ms_solver)),
                speedup_B=float(n * ms_solver / (n * ms_surr + (esc.sum() + flag.sum()) * ms_solver)))


def main():
    t0 = time.time()
    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    ms_solver = mf.load_solve_time()["ms_solver"]
    res = {}
    configs = {}
    for name in NETS:
        d = ld.load(name)
        gj = ld.gate_json(name)
        res[name] = {}
        configs[name] = []
        for fam in FAMILIES:
            pts = ld.held_out_points(name, fam)
            per = []
            stop = None
            for seed in ld.SEEDS:
                f = [x for x in gj["fits"] if x["seed"] == seed and x["family"] == fam][0]
                configs[name].append(dict(seed=seed, family=fam, tag=f["tag"], config=f["config"]))
                splits = ms.make_splits(d["groups"], seed)
                kept = ms.select_features(d["X"], splits["train"])
                Xk = d["X"][kept]
                fitted = tu.fit_one(fam, f["config"], Xk.iloc[splits["train"]].to_numpy(np.float32), d["y"][splits["train"]], seed)
                ca, te = splits["cal"], splits["test"]
                p_ca = tu.predict(fitted, Xk.iloc[ca].to_numpy(np.float32))
                p_te = tu.predict(fitted, Xk.iloc[te].to_numpy(np.float32))
                y_ca, y_te = d["y"][ca], d["y"][te]
                scen_ca = d["df"]["scenario_id"].to_numpy(np.int64)[ca]
                scen_te = d["df"]["scenario_id"].to_numpy(np.int64)[te]
                p = pts[seed]
                q = ge.calibrate_qhat(p_ca, y_ca, p["target"])
                glob = gate_metrics(p_te, y_te, scen_te, q, f["ms_surrogate"], ms_solver)
                if glob["escalation"] != p["escalation"] or glob["missed"] != p["missed"]:
                    stop = dict(seed=seed, esc=glob["escalation"], esc_stored=p["escalation"], missed=glob["missed"],
                                missed_stored=p["missed"])
                    break
                v_ca = y_ca < LIMIT
                t_row, n_v, k_v = kth(p_ca[v_ca] - LIMIT, ALPHA_ROW)
                mb = pd.Series(p_ca[v_ca] - LIMIT).groupby(scen_ca[v_ca]).max().to_numpy()
                t_base, n_b, k_b = kth(mb, ALPHA_BASE)
                per.append(dict(seed=seed, target=float(p["target"]), q_hat_global=float(q),
                                global_gate=glob,
                                row_level=dict(gate_metrics(p_te, y_te, scen_te, t_row, f["ms_surrogate"], ms_solver),
                                               n_cal_violation_rows=n_v, rank=k_v),
                                base_level=dict(gate_metrics(p_te, y_te, scen_te, t_base, f["ms_surrogate"], ms_solver),
                                                n_cal_bases_with_violation=n_b, rank=k_b)))
                print(f"{name} {fam} seed {seed}: reproduced; t_row {t_row:.5f} t_base {t_base:.5f} | missed "
                      f"global {100 * glob['missed']:.2f}% row {100 * per[-1]['row_level']['missed']:.2f}% base "
                      f"{100 * per[-1]['base_level']['missed']:.2f}% | any-miss base-level "
                      f"{100 * per[-1]['base_level']['any_miss_share']:.1f}%", flush=True)
            if stop is not None:
                res[name][fam] = dict(stopped="refit does not reproduce stored held-out numbers", detail=stop)
                print(f"{name} {fam}: STOPPED {stop}", flush=True)
                continue
            summ = {}
            for cal in ["global_gate", "row_level", "base_level"]:
                summ[cal] = {}
                for k in ["t", "escalation", "flag_share", "missed", "any_miss_share", "speedup_A", "speedup_B",
                          "overlap_certify_and_flag"]:
                    summ[cal][k + "_mean"], summ[cal][k + "_std"] = ms_([r[cal][k] for r in per])
            summ["base_level"]["splits_any_miss_le_alpha"] = len([r for r in per if r["base_level"]["any_miss_share"] <= ALPHA_BASE])
            summ["row_level"]["splits_missed_le_alpha"] = len([r for r in per if r["row_level"]["missed"] <= ALPHA_ROW])
            res[name][fam] = dict(per_split=per, summary=summ)
    h2 = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h2 != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    out = dict(part="N12 Part B: price of a guarantee (descriptive)", decision_rule=RULE, decision_rule_sha256=h,
               networks=res, alpha_row=ALPHA_ROW, alpha_base=ALPHA_BASE,
               caveat_row_level="rows within a base case are not exchangeable, so the row-level alpha is not a guarantee per row",
               guarantee_base_level="under base-case exchangeability, P(a new base case has any certified violation) <= alpha",
               certify_rule="certify iff pred >= L + t (as written in the rule); flag iff pred < L; certify takes precedence where both hold (gate_eval convention)",
               std_convention="population std (ddof=0) over 5 splits", ms_solver=ms_solver, wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    inputs = [RULE, "data/solve_time.json"]
    for n in NETS:
        inputs += [ld.NETS[n]["data"], ld.NETS[n]["labels"], ld.NETS[n]["gate"]]
    man = sm.build_manifest([OUT], "scratch/n12_guarantee.py", [".venv/bin/python", "scratch/n12_guarantee.py"], inputs,
                            dict(seeds=ld.SEEDS, alpha_row=ALPHA_ROW, alpha_base=ALPHA_BASE, limit=LIMIT,
                                 model_hyperparameters=configs, search="none: N5/N10 M2 configs refit"), "")
    man["no_new_solves"] = "No AC solve. Model fits: N5/N10 M2 configs refit per split (no search)."
    sm.write_manifest(man, OUT)
    for n in res:
        for fam in res[n]:
            if "summary" in res[n][fam]:
                s = res[n][fam]["summary"]
                parts = []
                for c in ["global_gate", "row_level", "base_level"]:
                    parts.append(f"{c}: esc {100 * s[c]['escalation_mean']:.1f} missed {100 * s[c]['missed_mean']:.2f} "
                                 f"anymiss {100 * s[c]['any_miss_share_mean']:.1f} spB {s[c]['speedup_B_mean']:.2f}")
                print(f"{n} {fam}: " + " | ".join(parts))


if __name__ == "__main__":
    main()
