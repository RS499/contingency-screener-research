import os
import sys
import json
import time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import make_splits as ms
import manifest as mf
import tune_surrogates as tu
import sts_manifest as sm
import n5_gate_eval as n5
import n10_gate_illinois as il

# N11 Part 2 (scratch/n11_decision_rule.md §4, descriptive): case30_thermal and case24_ieee_rts (case39 excluded, see
# NETS) on switch-back
# labels (data/sts_n11_relabel_<net>.parquet). The N5 protocol per network, via n10_gate_illinois.run_seed (the N10
# evaluator, checked there against data/netstudy2/case_illinois200/frozen.json): full tune_surrogates search, M2,
# held-out target, refit, q_hat on cal, test at targets 0.90-0.98 + held-out, rules A and B, static at k_B.
# Reported: flips and corrected BM / VR (from the relabel JSON), the gate at 0.90 and at the held-out point,
# the cross-network rho*q_hat points (rho = corrected boundary mass / 0.005, as data/netstudy2/cross_2a_points.json)
# for these three networks plus case118 D94 (N5) and case_illinois200 (N10), and for case30 the abstract's numbers
# recomputed on corrected labels: histgb at 0.97 and the first target with mean missed < 1%.

NETS = {
    "case30_thermal": ("data/case30_thermal/dataset.parquet", 41),
    # case39 excluded: its switch-back relabel failed on 1.09% of rows (> 0.5% ceiling); owner decision to apply
    # the ceiling per dataset (interpretation, not a rule change; see notes/overnight_status.md N11 Step 6)
    "case24_ieee_rts": ("data/netstudy/case24_ieee_rts/dataset.parquet", 33),
}
OUT = "data/sts_n11_smallnets.json"
SEEDS = [0, 1, 2, 3, 4]
TARGETS = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98]
LIMIT = 0.94
STRIP_W = 0.005


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def aggregate(points):
    pts = pd.DataFrame(points)
    pts["tkey"] = np.where(pts["point"] == "grid", pts["target"].round(2), -1.0)
    rows = []
    for (fam, kind, t), m in pts.groupby(["family", "point", "tkey"]):
        r = dict(family=fam, point=kind, target=None if kind == "held_out" else float(t), n_splits=int(len(m)))
        for col in ["target", "q_hat", "escalation", "flag_share", "solve_share_B", "missed", "gate_catch", "speedup_A",
                    "speedup_B", "static_catch_B", "k_B", "coverage_emp", "any_miss_share"]:
            r[col + "_mean"], r[col + "_std"] = ms_(m[col])
        gm, gs = ms_(m["gate_catch"])
        smu, ss = ms_(m["static_catch_B"])
        r["gate_vs_static_B"] = (("gate higher" if gm > smu else "static higher") if abs(gm - smu) > max(gs, ss)
                                 else "tie (gap within larger std)")
        r["splits_missed_le_1pct"] = int((m["missed"] <= 0.01).sum())
        rows.append(r)
    return rows


def rho_points(name, bm, table):
    out = []
    for r in table:
        if r["point"] != "grid":
            continue
        out.append(dict(network=name, family=r["family"], coverage_target=r["target"], boundary_mass=bm,
                        q_hat=r["q_hat_mean"], escalation=r["escalation_mean"],
                        rho_times_qhat=(bm / STRIP_W) * r["q_hat_mean"]))
    return out


def main():
    t0 = time.time()
    ms_solver = mf.load_solve_time()["ms_solver"]
    r_cands = tu.ridge_candidates()
    h_cands = tu.histgb_candidates()
    res = {}
    cross = []
    fits_all = {}
    for name in NETS:
        data_path, n_line = NETS[name]
        lab_path = f"data/sts_n11_relabel_{name}.parquet"
        rel = json.load(open(f"data/sts_n11_relabel_{name}.json"))
        df, feature_cols, info = n5.load_relabeled(data_path, lab_path)
        X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
        ek = il.elem_keys(df, n_line)
        points, fits, sel = [], [], {}
        for seed in SEEDS:
            _s, se, f, p, _c, _co = il.run_seed(df, X, y, groups, seed, ms_solver, r_cands, h_cands, ek)
            sel[str(seed)] = se
            fits.extend(f)
            points.extend(p)
            h = [q for q in p if q["family"] == "histgb" and q["point"] == "held_out"]
            if h:
                print(f"{name} seed {seed}: histgb held-out {h[0]['target']:.2f} esc {100 * h[0]['escalation']:.1f}% "
                      f"missed {100 * h[0]['missed']:.2f}%", flush=True)
        table = aggregate(points)
        bm = rel["summary"]["corrected_boundary_mass"]
        cross.extend(rho_points(name, bm, table))
        first = {}
        for fam in ["ridge", "histgb"]:
            g = [r for r in table if r["family"] == fam and r["point"] == "grid"]
            g = [g[i] for i in np.argsort([r["target"] for r in g])]
            first[fam] = None
            for r in g:
                if r["missed_mean"] < 0.01:
                    first[fam] = r["target"]
                    break
        res[name] = dict(labels=info, relabel_summary=rel["summary"], relabel_checks=rel["checks"], table=table,
                         first_target_mean_missed_below_1pct=first,
                         histgb_at_0p97=[r for r in table if r["family"] == "histgb" and r["point"] == "grid"
                                         and abs(r["target"] - 0.97) < 1e-9][0],
                         selections=sel, points=points)
        fits_all[name] = [dict(seed=f["seed"], family=f["family"], tag=f["tag"], config=f["config"]) for f in fits]
    # the two larger networks, from their corrected-label runs (no refit here)
    v5 = json.load(open("data/sts_n5_verdict.json"))["tables"]["094"]
    n2p = pd.read_parquet("data/sts_n2_label_audit.parquet", columns=["outaged_type", "corrected_status", "corrected_min_vm"])
    n2p = n2p[(n2p.outaged_type != "none") & n2p.corrected_status.isin(["converged", "not_needed"])]
    bm_118 = float(((n2p.corrected_min_vm >= 0.94) & (n2p.corrected_min_vm < 0.945)).mean())
    for r in v5:
        if r["point"] == "grid":
            cross.append(dict(network="case118", family=r["family"], coverage_target=r["target"], boundary_mass=bm_118,
                              q_hat=None, escalation=r["escalation_mean"], rho_times_qhat=None,
                              note="q_hat not stored in data/sts_n5_verdict.json tables; see per-seed points"))
    n5pts = pd.DataFrame([p for p in json.load(open("data/sts_n5_gate_094.json"))["points"] if p["point"] == "grid"])
    for c in cross:
        if c["network"] == "case118":
            q = n5pts[(n5pts.family == c["family"]) & (n5pts.target.round(2) == round(c["coverage_target"], 2))]["q_hat"].mean()
            c["q_hat"] = float(q)
            c["rho_times_qhat"] = (c["boundary_mass"] / STRIP_W) * float(q)
            c.pop("note")
    il_path = "data/sts_n10_illinois.json"
    if os.path.exists(il_path):
        ilj = json.load(open(il_path))
        bm_il = json.load(open("data/sts_n10_relabel_illinois200.json"))["summary"]["corrected_boundary_mass"]
        for r in ilj["table"]:
            if r["point"] == "grid":
                q = float(np.mean([p["q_hat"] for p in ilj["points"] if p["family"] == r["family"] and p["point"] == "grid"
                                   and abs(p["target"] - r["target"]) < 1e-9]))
                cross.append(dict(network="case_illinois200", family=r["family"], coverage_target=r["target"],
                                  boundary_mass=bm_il, q_hat=q, escalation=r["escalation_mean"],
                                  rho_times_qhat=(bm_il / STRIP_W) * q))
    out = dict(part="N11 Part 2: small networks on switch-back labels (descriptive)", networks=res,
               cross_points=dict(strip_width=STRIP_W, density_definition="rho = corrected boundary_mass / strip_width, strip = [0.94, 0.945)",
                                 n_points=len(cross), points=cross),
               std_convention="population std (ddof=0) over 5 splits", ms_solver=ms_solver, wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    inputs = ["data/sts_n5_verdict.json", "data/sts_n5_gate_094.json", "data/sts_n2_label_audit.parquet"]
    for name in NETS:
        inputs += [NETS[name][0], f"data/sts_n11_relabel_{name}.parquet"]
    if os.path.exists(il_path):
        inputs += [il_path, "data/sts_n10_relabel_illinois200.json"]
    man = sm.build_manifest([OUT], "scratch/n11_smallnets.py", [".venv/bin/python", "scratch/n11_smallnets.py"], inputs,
                            dict(seeds=SEEDS, targets=TARGETS, limit=LIMIT, model_hyperparameters=fits_all,
                                 search="scripts/tune_surrogates.py candidates (15 ridge, 26 histgb)",
                                 solver_settings="labels: pinned pandapower + N2 switch-back (scratch/n11_relabel_net.py)"), "")
    man["no_new_solves"] = "No AC solve. Model fits: full tune_surrogates search + M2 refits per network and seed."
    sm.write_manifest(man, OUT)
    for name in res:
        h = [r for r in res[name]["table"] if r["family"] == "histgb" and r["point"] == "held_out"][0]
        print(f"{name}: histgb held-out esc {100 * h['escalation_mean']:.1f}±{100 * h['escalation_std']:.1f} missed "
              f"{100 * h['missed_mean']:.2f}±{100 * h['missed_std']:.2f} [{h['gate_vs_static_B']}] first<1%: "
              f"{res[name]['first_target_mean_missed_below_1pct']}")


if __name__ == "__main__":
    main()
