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
import manifest as mf
import baselines as bl
import tune_surrogates as tu
import sts_manifest as sm
import n5_gate_eval as n5
import n9_budget_curve as bc

# N10 Part B evaluation (scratch/n10_decision_rule.md, Part B) on case_illinois200 with switch-back labels.
# Protocol = N5 (scratch/n5_gate_eval.py): per split (seeds 0-4) the full scripts/tune_surrogates.py search on the
# inner split, M2 selection, held-out target = M2 inner_cov_at, refit on train, q_hat on cal, evaluate on test at
# targets 0.90-0.98 and the held-out point (n5_gate_eval.evaluate_point: rules A and B, static at matched budget).
# Also: budget curve at the declared k, violation concentration (top-5 / top-10 elements by train frequency), and
# the operator any-miss metric; the last two also for case118 D94 (corrected labels, N5 M2 configs refit).
#
# argv[1]:
#   "check"  stored labels, seed 0 only: must reproduce data/netstudy2/case_illinois200/frozen.json
#            (escalation and missed at 0.90, both families, and the test index hash) exactly, else stop
#   "full"   corrected labels, seeds 0-4, then the verdicts

NETWORK = "case_illinois200"
DATASET = "data/netstudy/case_illinois200/dataset.parquet"
LABELS = "data/sts_n10_relabel_illinois200.parquet"
FROZEN = "data/netstudy2/case_illinois200/frozen.json"
RULE = "scratch/n10_decision_rule.md"
RULE_SHA = "scratch/n10_decision_rule.sha256"
OUT = "data/sts_n10_illinois.json"
LIMIT = 0.94
TARGETS = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98]
SEEDS = [0, 1, 2, 3, 4]
N_LINE_IL = 179
N_BRANCH_IL = 245
K_IL = [26, 53, 75, 117, 158]
K_SHARES = [0.108, 0.215, 0.306, 0.478, 0.645]
TOP = [5, 10]


def idx_hash(a):
    a = np.ascontiguousarray(np.asarray(a).astype(np.int64))
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def elem_keys(df, n_line):
    is_trafo = df["outaged_type"].to_numpy() == "trafo"
    return df["outaged_idx"].to_numpy(np.int64) + np.where(is_trafo, n_line, 0)


def concentration(df, tr, te, ek):
    # share of all test violations that come from the top-n elements ranked by train violation frequency
    viol = df["violation"].to_numpy(bool)
    t = pd.DataFrame(dict(e=ek[tr], v=viol[tr].astype(float)))
    freq = t.groupby("e")["v"].mean().sort_values(ascending=False, kind="stable")
    out = {}
    tv = viol[te]
    for n in TOP:
        top = freq.index[:n].to_numpy()
        out[f"top{n}"] = float((np.isin(ek[te], top) & tv).sum() / max(int(tv.sum()), 1))
    return out


def any_miss(scen, certify, true_v):
    # share of test base cases with at least one certified true violation
    m = pd.Series(certify & true_v).groupby(scen).any()
    return float(m.mean())


def run_seed(df, X, y, groups, seed, ms_solver, r_cands, h_cands, ek):
    splits = ms.make_splits(groups, seed)
    kept = ms.select_features(X, splits["train"])
    Xk = X[kept]
    tr = splits["train"]
    inner = ms.make_splits(groups[tr], tu.INNER_SEED_OFFSET + seed)
    i_fit, i_cal, i_score = tr[inner["train"]], tr[inner["cal"]], tr[inner["test"]]
    Xfit = Xk.iloc[i_fit].to_numpy(np.float32)
    Xic = Xk.iloc[i_cal].to_numpy(np.float32)
    Xis = Xk.iloc[i_score].to_numpy(np.float32)
    search, sel = [], {}
    for family, cands in (("ridge", r_cands), ("histgb", h_cands)):
        rows = tu.search_one_family(family, cands, Xfit, y[i_fit], Xic, y[i_cal], Xis, y[i_score], seed, ms_solver)
        search.extend(rows)
        m1, m2 = tu.select_best(rows)
        m2r = [r for r in rows if r["tag"] == m2][0]
        sel[family] = dict(m1=m1, m2=m2, m2_inner_cov_at=m2r["inner_cov_at"], m2_inner_avoided=m2r["inner_avoided"])
        print(f"  seed {seed} -> {family}: M2 {m2}, held-out target {m2r['inner_cov_at']}", flush=True)
    te = splits["test"]
    train_mask = np.zeros(len(df), dtype=bool)
    train_mask[tr] = True
    stat_score, _ = bl.static_severity_score(df, train_mask, ek)
    scen = df["scenario_id"].to_numpy(np.int64)[te]
    y_te = y[te]
    viol = y_te < LIMIT
    tb = ek[te].astype(float)
    rows_per_scen = len(te) / len(np.unique(scen))
    c_static, _, _ = bl.capture_curve(scen, stat_score[te], tb, viol, N_BRANCH_IL)
    c_oracle, _, _ = bl.capture_curve(scen, y_te, tb, viol, N_BRANCH_IL)
    Xtr = Xk.iloc[tr].to_numpy(np.float32)
    Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
    Xte = Xk.iloc[te].to_numpy(np.float32)
    y_ca = y[splits["cal"]]
    points, fits, curve_rows = [], [], []
    for family, cands in (("ridge", r_cands), ("histgb", h_cands)):
        cfg = tu.find_config(cands, sel[family]["m2"])
        fitted = tu.fit_one(family, cfg, Xtr, y[tr], seed)
        p_ca = tu.predict(fitted, Xca)
        t0 = time.time()
        p_te = tu.predict(fitted, Xte)
        ms_surr = (time.time() - t0) / len(y_te) * 1000.0
        mae, r2 = tu.mae_r2(p_te, y_te)
        fits.append(dict(seed=seed, family=family, tag=sel[family]["m2"], config=dict(cfg), mae=mae, r2=r2,
                         ms_surrogate=ms_surr))
        tlist = [(t, "grid") for t in TARGETS]
        if sel[family]["m2_inner_cov_at"] is not None:
            tlist.append((sel[family]["m2_inner_cov_at"], "held_out"))
        for tgt, kind in tlist:
            r = n5.evaluate_point(p_ca, y_ca, p_te, y_te, tgt, ms_surr, ms_solver, c_static, rows_per_scen)
            q = r["q_hat"]
            r["any_miss_share"] = any_miss(scen, (p_te - q) >= LIMIT, viol)
            r.update(seed=seed, family=family, point=kind, tag=sel[family]["m2"], test_index_hash=idx_hash(te))
            points.append(r)
        c_surr, _, _ = bl.capture_curve(scen, p_te, tb, viol, N_BRANCH_IL)
        cr = dict(seed=seed, family=family)
        for k in K_IL:
            cr[f"surr_{k}"] = float(c_surr[k - 1])
            cr[f"static_{k}"] = float(c_static[k - 1])
            cr[f"oracle_{k}"] = float(c_oracle[k - 1])
        curve_rows.append(cr)
    conc = concentration(df, tr, te, ek)
    conc["seed"] = seed
    return search, sel, fits, points, curve_rows, conc


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def check_mode(ms_solver, r_cands, h_cands):
    fr = json.load(open(FROZEN))
    df, feature_cols = ms.load_dataset(DATASET)
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    ek = elem_keys(df, N_LINE_IL)
    s, sel, fits, pts, _, _ = run_seed(df, X, y, groups, 0, ms_solver, r_cands, h_cands, ek)
    res = []
    for fam in ["ridge", "histgb"]:
        ref = [r for r in fr["records"] if r["family"] == fam and r["seed"] == 0 and abs(r["coverage_target"] - 0.90) < 1e-9][0]
        mine = [p for p in pts if p["family"] == fam and p["point"] == "grid" and abs(p["target"] - 0.90) < 1e-9][0]
        exact = bool(mine["escalation"] == ref["escalation"] and mine["missed"] == ref["missed_viol"]
                     and mine["test_index_hash"] == ref["test_index_hash"])
        res.append(dict(family=fam, m2_tag=sel[fam]["m2"], esc_n10=mine["escalation"], esc_frozen=ref["escalation"],
                        missed_n10=mine["missed"], missed_frozen=ref["missed_viol"],
                        test_index_hash_n10=mine["test_index_hash"], test_index_hash_frozen=ref["test_index_hash"],
                        exact=exact))
        print(f"CHECK {fam}: exact={exact} esc {mine['escalation']!r} vs {ref['escalation']!r}; "
              f"missed {mine['missed']!r} vs {ref['missed_viol']!r}", flush=True)
    out = dict(check="N10 Step 4 stored-label reproduction of frozen.json, seed 0, target 0.90", results=res,
               all_exact=bool(all(r["exact"] for r in res)),
               m2_tags_recorded_in_frozen=False)
    with open("scratch/n10_gate_illinois_check.json", "w") as f:
        json.dump(out, f, indent=2)
    if not out["all_exact"]:
        print("STOP: stored-label reproduction failed", flush=True)


def case118_extras():
    # D94 corrected labels, N5 M2 configs and held-out targets, refit (as in N9): concentration and any-miss
    n5json = json.load(open("data/sts_n5_gate_094.json"))
    d = bc.load("094")
    out = []
    for seed in SEEDS:
        splits = ms.make_splits(d["groups"], seed)
        kept = ms.select_features(d["X"], splits["train"])
        te = splits["test"]
        Xte = d["X"][kept].iloc[te].to_numpy(np.float32)
        y_te = d["y"][te]
        scen = d["df"]["scenario_id"].to_numpy(np.int64)[te]
        viol = y_te < LIMIT
        r = dict(seed=seed)
        r.update(concentration(d["df"], splits["train"], te, d["elem_key"]))
        for fam in ["ridge", "histgb"]:
            f5 = bc.n5_config(n5json, seed, fam)
            h5 = bc.n5_held_out(n5json, seed, fam)
            p_ca, y_ca, p_te = bc.fit_predict(d, seed, fam, f5["config"], Xte, kept)
            g = bc.gate_point(p_ca, y_ca, p_te, y_te, h5["target"])
            if g["missed"] != h5["missed"]:
                raise ValueError("case118 refit does not reproduce N5 held-out missed; stop")
            r[f"any_miss_{fam}"] = any_miss(scen, (p_te - g["q_hat"]) >= LIMIT, viol)
        out.append(r)
    return out


def full_mode(ms_solver, r_cands, h_cands):
    t0 = time.time()
    df, feature_cols, info = n5.load_relabeled(DATASET, LABELS)
    print(json.dumps(info), flush=True)
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    ek = elem_keys(df, N_LINE_IL)
    search, sel, fits, points, curves, conc = [], {}, [], [], [], []
    for seed in SEEDS:
        s, se, f, p, c, co = run_seed(df, X, y, groups, seed, ms_solver, r_cands, h_cands, ek)
        search.extend(s)
        sel[str(seed)] = se
        fits.extend(f)
        points.extend(p)
        curves.extend(c)
        conc.append(co)
        ho = [q for q in p if q["family"] == "histgb" and q["point"] == "held_out"]
        if ho:
            h = ho[0]
            print(f"  TEST histgb held-out {h['target']:.2f}: esc {100*h['escalation']:.1f}% missed {100*h['missed']:.2f}% "
                  f"spB {h['speedup_B']:.3f} catch {100*h['gate_catch']:.2f} static_B {100*h['static_catch_B']:.2f}", flush=True)
    c118 = case118_extras()

    pts = pd.DataFrame([p for p in points])
    table = []
    for fam in ["ridge", "histgb"]:
        for kind in ["grid", "held_out"]:
            m0 = pts[(pts.family == fam) & (pts.point == kind)]
            keys = sorted(m0["target"].round(2).unique()) if kind == "grid" else [None]
            for t in keys:
                m = m0 if t is None else m0[m0["target"].round(2) == t]
                r = dict(family=fam, point=kind, target=t, n_splits=int(len(m)))
                for col in ["target", "escalation", "flag_share", "solve_share_B", "missed", "gate_catch", "speedup_A",
                            "speedup_B", "static_catch_A", "static_catch_B", "k_A", "k_B", "any_miss_share", "coverage_emp"]:
                    mu, sd = ms_(m[col])
                    r[col + "_mean"] = mu
                    r[col + "_std"] = sd
                for acc in ["A", "B"]:
                    gm, gs = ms_(m["gate_catch"])
                    smu, ss = ms_(m[f"static_catch_{acc}"])
                    gap = gm - smu
                    r[f"std_rule_{acc}"] = (("gate higher" if gap > 0 else "static higher") if abs(gap) > max(gs, ss)
                                            else "tie (gap within larger std)")
                table.append(r)

    cv = pd.DataFrame(curves)
    budget = []
    for fam in ["ridge", "histgb"]:
        m = cv[cv.family == fam]
        crossover = None
        rows = []
        for k, share in zip(K_IL, K_SHARES):
            r = dict(family=fam, k=k, declared_share=share)
            for kind in ["surr", "static", "oracle"]:
                r[kind + "_mean"], r[kind + "_std"] = ms_(m[f"{kind}_{k}"])
            r["verdict"] = bc.verdict(m[f"surr_{k}"], m[f"static_{k}"])
            if crossover is None and r["verdict"] != "SURR higher":
                crossover = k
            rows.append(r)
        for r in rows:
            r["crossover_k"] = crossover
        budget.extend(rows)

    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise ValueError("decision rule changed since hashing; stop")
    ho = pts[(pts.family == "histgb") & (pts.point == "held_out")].sort_values("seed")
    gm, gs = ms_(ho["gate_catch"])
    smu, ss = ms_(ho["static_catch_B"])
    beats = bool((gm - smu) > max(gs, ss))
    n_ok = int((ho["missed"] <= 0.01).sum())
    verdict = dict(
        BEATS_STATIC_IL=dict(holds=beats, gate_catch_mean=gm, gate_catch_std=gs, static_catch_B_mean=smu,
                             static_catch_B_std=ss, gap=gm - smu, STD=max(gs, ss), n_splits=int(len(ho))),
        SAFER_IL=dict(holds=bool(n_ok >= 4), splits_missed_le_1pct=n_ok, n_splits_with_held_out=int(len(ho)),
                      missed_per_split=[float(v) for v in ho["missed"]]))
    cc = pd.DataFrame(conc)
    c1 = pd.DataFrame(c118)
    descriptive = dict(
        labels=info,
        violation_concentration=dict(
            illinois={f"top{n}": dict(zip(["mean", "std"], ms_(cc[f"top{n}"]))) for n in TOP},
            case118_D94_corrected={f"top{n}": dict(zip(["mean", "std"], ms_(c1[f"top{n}"]))) for n in TOP},
            per_seed_illinois=conc, per_seed_case118=c118),
        operator_any_miss_held_out=dict(
            illinois={fam: dict(zip(["mean", "std"], ms_(pts[(pts.family == fam) & (pts.point == "held_out")]["any_miss_share"])))
                      for fam in ["ridge", "histgb"]},
            case118_D94_corrected={fam: dict(zip(["mean", "std"], ms_(c1[f"any_miss_{fam}"]))) for fam in ["ridge", "histgb"]}),
        budget_curve=budget)
    out = dict(part="N10 Part B: case_illinois200 on switch-back labels", decision_rule=RULE, decision_rule_sha256=h,
               decision_rule_hash_verified=True, verdict=verdict, table=table, descriptive=descriptive,
               selections=sel, fits=fits, points=points, curves_at_declared_k=curves, search=search,
               std_convention="population std (ddof=0) over 5 splits", ms_solver=ms_solver,
               ms_solver_provenance="data/solve_time.json (case118); not re-timed on Illinois, as in netstudy2",
               wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    params = dict(network=NETWORK, seeds=SEEDS, targets=TARGETS, limit=LIMIT, k_declared=K_IL,
                  k_declared_shares=K_SHARES, top_n=TOP,
                  model_hyperparameters=dict(search="scripts/tune_surrogates.py candidates (15 ridge, 26 histgb)",
                                             selected_m2=[dict(seed=f["seed"], family=f["family"], tag=f["tag"], config=f["config"]) for f in fits],
                                             case118_extras="N5 M2 configs from data/sts_n5_gate_094.json, refit"),
                  solver_settings="labels from data/sts_n10_relabel_illinois200.parquet (pinned pandapower + N2 switch-back); no solve here",
                  omp_num_threads=os.environ.get("OMP_NUM_THREADS", "unset"))
    man = sm.build_manifest([OUT], "scratch/n10_gate_illinois.py", [".venv/bin/python", "scratch/n10_gate_illinois.py", "full"],
                            [DATASET, LABELS, FROZEN, RULE, "data/sts_n5_gate_094.json", "data/dataset.parquet",
                             "data/sts_n2_label_audit.parquet", "scripts/tune_surrogates.py", "scripts/baselines.py"], params, "")
    man["no_new_solves"] = "No AC solve. Model fits: full tune_surrogates search + M2 refits per seed; case118 N5 configs refit."
    sm.write_manifest(man, OUT)
    print(json.dumps(verdict, indent=1))


def main():
    ms_solver = mf.load_solve_time()["ms_solver"]
    r_cands = tu.ridge_candidates()
    h_cands = tu.histgb_candidates()
    if sys.argv[1] == "check":
        check_mode(ms_solver, r_cands, h_cands)
    else:
        full_mode(ms_solver, r_cands, h_cands)


if __name__ == "__main__":
    main()
