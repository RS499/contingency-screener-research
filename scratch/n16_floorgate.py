import os
import sys
import json
import time
import hashlib
import subprocess
from datetime import datetime, timezone
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import make_splits as ms
import manifest as mf
import baselines as bl
import tune_surrogates as tu
import sts_manifest as sm
import n5_gate_eval as n5

# N16 (scratch/n16_decision_rule.md): the gate across generator-setpoint floors on the N13 rebuilt builds
# D93 / D94 / D95a / D96. The N5 protocol is scratch/n5_gate_eval.py run_seed, imported unchanged (full
# tune_surrogates search, M2, held-out target, targets 0.90-0.98, rule B, static at k_B). D94 and D95a are not
# re-searched: their points come from data/sts_n13_gate_D94.json / D95a.json. D93 and D96 are run here.
# Family isolation (rule §4): run_seed is called unchanged; only if ridge raises in a split is that split rerun
# through run_seed_histgb_only below, which is run_seed's histgb steps in the same order.
#
# argv[1] = mode:
#   step1      rule hash, ms_solver and dataset-level BM/VR checks; D94 split 0 through run_seed and through the
#              histgb-only path, compared with data/sts_n13_gate_D94.json split 0 -> scratch/n16_step1.json
#   build D93  (or D96) 5 splits -> scratch/n16_raw_<name>.json; refuses to start unless step1 passed
#   summarize  per floor, split, family and point + summaries + verdicts -> data/sts_n16_floorgate.json,
#              data/sts_n16_verdicts.json (each with a manifest) and scratch/n16_result.md

RULE = "scratch/n16_decision_rule.md"
RULE_SHA_FILE = "scratch/n16_decision_rule.sha256"
RULE_COMMIT = "a2102bbe656d74ab943b06ca826b4d6d0ad0b242"
FLOORS = [(0.93, "D93"), (0.94, "D94"), (0.95, "D95a"), (0.96, "D96")]
NEW = ["D93", "D96"]
REUSED = ["D94", "D95a"]
SEEDS = [0, 1, 2, 3, 4]
N_LINE = 173
LIMIT = 0.94
STEP1 = "scratch/n16_step1.json"
OUT = "data/sts_n16_floorgate.json"
OUT_V = "data/sts_n16_verdicts.json"
RESULT = "scratch/n16_result.md"
METRICS = ["BM", "VR", "target", "q_hat", "escalation", "flag_share", "solve_share_B", "missed", "gate_catch",
           "speedup_B"]
EXTRA = ["speedup_A", "coverage_emp", "static_catch_B"]
CHECK_KEYS = ["q_hat", "escalation", "flag_share", "missed", "k_B", "static_catch_B"]
# the owner's predictions, copied from the rule's "Predictions (owner)" table: histgb, target 0.90,
# (point, low, high); escalation in percent
PRED = {"D93": {"speedup_B": (2.4, 2.1, 2.7), "escalation_pct": (24.9, 21.0, 29.0)},
        "D96": {"speedup_B": (4.5, 3.3, 5.5), "escalation_pct": (8.4, 5.0, 14.0)}}


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def git_text(args):
    return subprocess.run(["git"] + args, capture_output=True, text=True).stdout.strip()


def rule_info():
    # the working copy must be byte-identical to the committed, pushed rule
    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    committed = subprocess.run(["git", "show", f"{RULE_COMMIT}:{RULE}"], capture_output=True).stdout
    if hashlib.sha256(committed).hexdigest() != h:
        raise SystemExit("the rule file differs from the committed version: stop")
    if os.path.exists(RULE_SHA_FILE) and open(RULE_SHA_FILE).read().split()[0] != h:
        raise SystemExit("the rule file does not match the recorded sha256: stop")
    commit_time = git_text(["log", "-1", "--format=%cI", RULE_COMMIT])
    on_origin = RULE_COMMIT in git_text(["ls-remote", "origin", "refs/heads/main"])
    return dict(path=RULE, sha256=h, commit=RULE_COMMIT, commit_time=commit_time, on_origin_main=on_origin)


def check_ms_solver():
    t = mf.load_solve_time()["ms_solver"]
    for name in REUSED:
        g = json.load(open(f"data/sts_n13_gate_{name}.json"))
        if g["ms_solver"] != t:
            raise SystemExit(f"ms_solver {t} differs from {g['ms_solver']} in sts_n13_gate_{name}.json: stop")
    return t


def elem_key(df):
    is_trafo = df["outaged_type"].to_numpy() == "trafo"
    return df["outaged_idx"].to_numpy(np.int64) + np.where(is_trafo, N_LINE, 0)


def dataset_check(name, df, floor_ref):
    # same formula as scratch/n13_analyses.py a_floor, on the rows the gate loads
    v = df["min_vm"].to_numpy(np.float64)
    strip = (v >= 0.94) & (v < 0.945)
    bm = 100.0 * strip.mean()
    vr = 100.0 * (v < 0.94).mean()
    ref = [r for r in floor_ref["per_floor"] if r["dataset"] == name][0]
    ok = (len(v) == ref["n_rows"]) and (bm == ref["BM"]) and (vr == ref["VR"])
    return dict(dataset=name, n_rows=int(len(v)), BM=bm, VR=vr, ref_n_rows=ref["n_rows"], ref_BM=ref["BM"],
                ref_VR=ref["VR"], equal=bool(ok))


def split_bm_vr(df, seed):
    groups = df[ms.GROUP_COL].to_numpy()
    te = ms.make_splits(groups, seed)["test"]
    v = df[ms.TARGET_COL].to_numpy(np.float64)[te]
    return dict(seed=seed, n_test=int(len(te)), BM=float(((v >= 0.94) & (v < 0.945)).mean()),
                VR=float((v < LIMIT).mean()))


def run_seed_histgb_only(df, X, y, groups, seed, ms_solver, h_cands, elem_key):
    # scratch/n5_gate_eval.py run_seed, step for step, with its two family loops limited to histgb
    print(f"\n=== seed {seed} (histgb-only path) ===", flush=True)
    splits = ms.make_splits(groups, seed)
    kept = ms.select_features(X, splits["train"])
    Xk = X[kept]
    tr = splits["train"]
    inner = ms.make_splits(groups[tr], tu.INNER_SEED_OFFSET + seed)
    i_fit, i_cal, i_score = tr[inner["train"]], tr[inner["cal"]], tr[inner["test"]]
    Xfit = Xk.iloc[i_fit].to_numpy(np.float32)
    Xic = Xk.iloc[i_cal].to_numpy(np.float32)
    Xis = Xk.iloc[i_score].to_numpy(np.float32)

    family = "histgb"
    search_rows = tu.search_one_family(family, h_cands, Xfit, y[i_fit], Xic, y[i_cal], Xis, y[i_score], seed,
                                       ms_solver)
    m1_tag, m2_tag = tu.select_best(search_rows)
    m2_row = [r for r in search_rows if r["tag"] == m2_tag][0]
    sel = {family: dict(m1=m1_tag, m2=m2_tag, m2_inner_cov_at=m2_row["inner_cov_at"],
                        m2_inner_avoided=m2_row["inner_avoided"])}

    te = splits["test"]
    train_mask = np.zeros(len(df), dtype=bool)
    train_mask[tr] = True
    stat_score, _ = bl.static_severity_score(df, train_mask, elem_key)
    scen = df["scenario_id"].to_numpy(np.int64)[te]
    viol = df["violation"].to_numpy(bool)[te]
    k_max = int(pd.Series(scen).value_counts().max())
    curve, _, _ = bl.capture_curve(scen, stat_score[te], elem_key[te].astype(float), viol, k_max)
    rows_per_scen = len(te) / len(np.unique(scen))

    Xtr = Xk.iloc[tr].to_numpy(np.float32)
    Xca = Xk.iloc[splits["cal"]].to_numpy(np.float32)
    Xte = Xk.iloc[te].to_numpy(np.float32)
    y_ca, y_te = y[splits["cal"]], y[te]
    points = []
    cfg = tu.find_config(h_cands, sel[family]["m2"])
    fitted = tu.fit_one(family, cfg, Xtr, y[tr], seed)
    p_ca = tu.predict(fitted, Xca)
    t0 = time.time()
    p_te = tu.predict(fitted, Xte)
    ms_surr = (time.time() - t0) / len(y_te) * 1000.0
    mae, r2 = tu.mae_r2(p_te, y_te)
    fits = [dict(seed=seed, family=family, tag=sel[family]["m2"], config=dict(cfg), mae=mae, r2=r2,
                 ms_surrogate=ms_surr)]
    tlist = [(t, "grid") for t in n5.TARGETS]
    if sel[family]["m2_inner_cov_at"] is not None:
        tlist.append((sel[family]["m2_inner_cov_at"], "held_out"))
    for tgt, kind in tlist:
        r = n5.evaluate_point(p_ca, y_ca, p_te, y_te, tgt, ms_surr, ms_solver, curve, rows_per_scen)
        r.update(seed=seed, family=family, point=kind, tag=sel[family]["m2"])
        points.append(r)
    for sw in tu.coverage_sweep(p_ca, y_ca, p_te, y_te, ms_surr, ms_solver):
        points.append(dict(seed=seed, family=family, point="sweep", tag=sel[family]["m2"],
                           target=sw["coverage_target"], escalation=sw["escalation"], missed=sw["missed_viol"]))
    return search_rows, sel, fits, points


def failing_family(err):
    # which family loop of n5_gate_eval.run_seed was running when the error was raised ("none" if neither)
    fam = "none"
    tb = err.__traceback__
    while tb is not None:
        fr = tb.tb_frame
        if fr.f_code.co_name == "run_seed" and fr.f_code.co_filename.endswith("n5_gate_eval.py"):
            fam = fr.f_locals.get("family", "none")
        tb = tb.tb_next
    return fam


def run_split(df, X, y, groups, seed, ms_solver, r_cands, h_cands, ek):
    ridge_error = ""
    try:
        s, se, f, p = n5.run_seed(df, X, y, groups, seed, ms_solver, r_cands, h_cands, ek)
        return dict(seed=seed, path="run_seed", search=s, selections=se, fits=f, points=p, ridge_error="", error="")
    except Exception as err:
        fam = failing_family(err)
        if fam != "ridge":
            return dict(seed=seed, path="crashed", failing_family=fam, error=repr(err), search=[], selections={},
                        fits=[], points=[], ridge_error="")
        ridge_error = repr(err)
    print(f"seed {seed}: ridge raised {ridge_error}; rerunning this split histgb-only (rule §4)", flush=True)
    try:
        s, se, f, p = run_seed_histgb_only(df, X, y, groups, seed, ms_solver, h_cands, ek)
    except Exception as err:
        return dict(seed=seed, path="crashed", failing_family="histgb", error=repr(err), search=[], selections={},
                    fits=[], points=[], ridge_error=ridge_error)
    return dict(seed=seed, path="histgb_only", search=s, selections=se, fits=f, points=p, ridge_error=ridge_error,
                error="")


def compare_split0(ref, sel, fits, points, families):
    # exact comparison with data/sts_n13_gate_D94.json split 0 (rule §4 Step 1); speedups excluded (t_surr timing)
    bad = []
    n_cmp = 0
    info = []
    for fam in families:
        rs = ref["selections"]["0"][fam]
        for k in ["m1", "m2", "m2_inner_cov_at"]:
            n_cmp += 1
            if rs[k] != sel[fam][k]:
                bad.append(f"{fam} selection {k}: {rs[k]} vs {sel[fam][k]}")
        rf = [x for x in ref["fits"] if x["seed"] == 0 and x["family"] == fam][0]
        nf = [x for x in fits if x["family"] == fam][0]
        n_cmp += 1
        if rf["mae"] != nf["mae"]:
            bad.append(f"{fam} test MAE: {rf['mae']} vs {nf['mae']}")
        info.append(dict(family=fam, r2_equal=bool(rf["r2"] == nf["r2"]), ms_surrogate_ref=rf["ms_surrogate"],
                         ms_surrogate_now=nf["ms_surrogate"]))
        for kind in ["grid", "held_out"]:
            rp = [x for x in ref["points"] if x["seed"] == 0 and x["family"] == fam and x["point"] == kind]
            npt = [x for x in points if x["family"] == fam and x["point"] == kind]
            if len(rp) != len(npt):
                bad.append(f"{fam} {kind}: {len(rp)} vs {len(npt)} points")
                continue
            for a, b in zip(rp, npt):
                n_cmp += 1
                if a["target"] != b["target"]:
                    bad.append(f"{fam} {kind} target {a['target']} vs {b['target']}")
                for k in CHECK_KEYS:
                    n_cmp += 1
                    if a[k] != b[k]:
                        bad.append(f"{fam} {kind} @{a['target']} {k}: {a[k]} vs {b[k]}")
        rsw = [x for x in ref["points"] if x["seed"] == 0 and x["family"] == fam and x["point"] == "sweep"]
        nsw = [x for x in points if x["family"] == fam and x["point"] == "sweep"]
        sweep_equal = len(rsw) == len(nsw)
        for a, b in zip(rsw, nsw):
            if a["escalation"] != b["escalation"] or a["missed"] != b["missed"]:
                sweep_equal = False
        info.append(dict(family=fam, sweep_escalation_missed_equal_info_only=bool(sweep_equal)))
    return dict(n_compared=n_cmp, mismatches=bad, equal=len(bad) == 0, info=info)


def step1():
    start = utc_now()
    t0 = time.time()
    rule = rule_info()
    if not rule["on_origin_main"]:
        raise SystemExit("rule commit is not origin/main: stop")
    with open(RULE_SHA_FILE, "w") as f:
        f.write(f"{rule['sha256']}  {RULE}  recorded {start}  (committed in {RULE_COMMIT}, {rule['commit_time']}; "
                f"origin/main = this commit: yes; working copy identical to that commit: yes)\n")
    ms_solver = check_ms_solver()
    floor_ref = json.load(open("data/sts_n13_floor.json"))
    checks = []
    for floor, name in FLOORS:
        df, _fc, _info = n5.load_relabeled(f"data/sts_n13_{name}.parquet", "")
        checks.append(dataset_check(name, df, floor_ref))
        print(f"dataset check {name}: {checks[-1]}", flush=True)
    out = dict(step="N16 Step 1", rule=rule, run_start_utc=start, ms_solver=ms_solver,
               omp_num_threads=os.environ.get("OMP_NUM_THREADS", "unset"), dataset_checks=checks)
    if not all([c["equal"] for c in checks]):
        out["passed"] = False
        out["stop_reason"] = "dataset-level BM/VR differ from data/sts_n13_floor.json"
        json.dump(out, open(STEP1, "w"), indent=2)
        raise SystemExit(out["stop_reason"])

    ref = json.load(open("data/sts_n13_gate_D94.json"))
    df, feature_cols, _info = n5.load_relabeled("data/sts_n13_D94.parquet", "")
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    ek = elem_key(df)
    r_cands = tu.ridge_candidates()
    h_cands = tu.histgb_candidates()
    t1 = time.time()
    _s, se, f, p = n5.run_seed(df, X, y, groups, 0, ms_solver, r_cands, h_cands, ek)
    wall_full = time.time() - t1
    cmp_full = compare_split0(ref, se, f, p, ["ridge", "histgb"])
    print(f"run_seed split 0 vs N13: {cmp_full['n_compared']} compared, mismatches {cmp_full['mismatches']}", flush=True)
    t2 = time.time()
    _s2, se2, f2, p2 = run_seed_histgb_only(df, X, y, groups, 0, ms_solver, h_cands, ek)
    wall_h = time.time() - t2
    cmp_h = compare_split0(ref, se2, f2, p2, ["histgb"])
    print(f"histgb-only split 0 vs N13: {cmp_h['n_compared']} compared, mismatches {cmp_h['mismatches']}", flush=True)
    out.update(run_seed_split0=cmp_full, histgb_only_split0=cmp_h, wall_s=dict(run_seed=wall_full, histgb_only=wall_h,
                                                                               total=time.time() - t0))
    out["passed"] = bool(cmp_full["equal"] and cmp_h["equal"])
    if not out["passed"]:
        out["stop_reason"] = "D94 split 0 does not reproduce data/sts_n13_gate_D94.json exactly"
    json.dump(out, open(STEP1, "w"), indent=2)
    print(f"Step 1 passed: {out['passed']}; wrote {STEP1}", flush=True)
    if not out["passed"]:
        raise SystemExit(out["stop_reason"])


def build(name):
    start = utc_now()
    t0 = time.time()
    rule = rule_info()
    s1 = json.load(open(STEP1))
    if not s1["passed"] or s1["rule"]["sha256"] != rule["sha256"]:
        raise SystemExit("Step 1 has not passed under this rule: stop")
    ms_solver = check_ms_solver()
    path = f"data/sts_n13_{name}.parquet"
    df, feature_cols, info = n5.load_relabeled(path, "")
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    ek = elem_key(df)
    r_cands = tu.ridge_candidates()
    h_cands = tu.histgb_candidates()
    splits = []
    histgb_status = "ok"
    for seed in SEEDS:
        r = run_split(df, X, y, groups, seed, ms_solver, r_cands, h_cands, ek)
        splits.append(r)
        print(f"{name} seed {seed}: path {r['path']} {r['error']}", flush=True)
        if r["path"] == "crashed" and r["failing_family"] != "ridge":
            # rule §4: a histgb crash is not retried; the build's histgb results are "not run"
            histgb_status = "not run"
            break
    op = f"scratch/n16_raw_{name}.json"
    out = dict(run=f"N16 gate, {name}", dataset=path, labels=info, seeds=SEEDS, limit=LIMIT, ms_solver=ms_solver,
               procedure="scratch/n5_gate_eval.py run_seed (histgb-only path only after a ridge error)",
               rule=rule, run_start_utc=start, omp_num_threads=os.environ.get("OMP_NUM_THREADS", "unset"),
               histgb_status=histgb_status, splits=splits, wall_s=time.time() - t0)
    with open(op, "w") as f:
        json.dump(out, f, indent=2)
    hyper = []
    for r in splits:
        for x in r["fits"]:
            hyper.append(dict(seed=x["seed"], family=x["family"], tag=x["tag"], config=x["config"]))
    params = dict(seeds=SEEDS, invocation=f"scratch/n16_floorgate.py build {name}", model_hyperparameters=hyper,
                  candidate_grids="scripts/tune_surrogates.py ridge_candidates (15) and histgb_candidates (26)",
                  inner_seed_offset=tu.INNER_SEED_OFFSET, inner_missed_ceiling=tu.INNER_MISSED_CEIL,
                  omp_num_threads=os.environ.get("OMP_NUM_THREADS", "unset"))
    man = sm.build_manifest([op], "scratch/n16_floorgate.py", [".venv/bin/python", "scratch/n16_floorgate.py", "build", name],
                            [path, "data/solve_time.json", "scripts/tune_surrogates.py", RULE], params, "")
    man["no_new_solves"] = "No AC solve. Model fits: full tune_surrogates search + M2 refits per split."
    sm.write_manifest(man, op)
    print(f"wrote {op}; histgb {histgb_status}; wall {time.time() - t0:.0f}s", flush=True)


def floor_points(name):
    # (points, fits, selections, source, histgb_status, deviations) for one build
    if name in REUSED:
        g = json.load(open(f"data/sts_n13_gate_{name}.json"))
        return g["points"], g["fits"], g["selections"], f"data/sts_n13_gate_{name}.json (N13, reused)", "ok", []
    raw = json.load(open(f"scratch/n16_raw_{name}.json"))
    points, fits, sel, dev = [], [], {}, []
    for r in raw["splits"]:
        points.extend(r["points"])
        fits.extend(r["fits"])
        sel[str(r["seed"])] = r["selections"]
        if r["path"] == "histgb_only":
            dev.append(f"{name} split {r['seed']}: ridge raised {r['ridge_error']}; split rerun histgb-only (rule §4)")
        if r["path"] == "crashed":
            dev.append(f"{name} split {r['seed']}: {r['failing_family']} crashed: {r['error']}")
    return points, fits, sel, f"scratch/n16_raw_{name}.json (N16)", raw["histgb_status"], dev


def per_split_rows(name, points, bmvr):
    rows = []
    for fam in ["histgb", "ridge"]:
        for point in ["target_0.90", "held_out"]:
            for seed in SEEDS:
                if point == "target_0.90":
                    hit = [p for p in points if p["seed"] == seed and p["family"] == fam and p["point"] == "grid"
                           and abs(p["target"] - 0.90) < 1e-9]
                else:
                    hit = [p for p in points if p["seed"] == seed and p["family"] == fam and p["point"] == "held_out"]
                b = [x for x in bmvr if x["seed"] == seed][0]
                row = dict(dataset=name, family=fam, point=point, seed=seed, BM=b["BM"], VR=b["VR"], available=len(hit) == 1)
                if len(hit) == 1:
                    if hit[0]["n_test"] != b["n_test"]:
                        raise SystemExit(f"{name} seed {seed}: test rows {b['n_test']} vs gate n_test {hit[0]['n_test']}")
                    for k in METRICS[2:] + EXTRA:
                        row[k] = hit[0][k]
                rows.append(row)
    return rows


def summarize_rows(rows):
    out = {}
    have = [r for r in rows if r["available"]]
    for k in METRICS + EXTRA:
        m, s = ms_([r[k] for r in have]) if have else (None, None)
        out[k] = dict(mean=m, std=s)
    out["n_splits"] = len(have)
    out["n_missing"] = len(rows) - len(have)
    out["splits_missed_le_1pct"] = len([r for r in have if r["missed"] <= 0.01])
    return out


def gap(summ, a, b, k):
    # mean(a) - mean(b) and the larger std
    if summ[a] is None or summ[b] is None:
        return None
    return dict(diff=summ[a][k]["mean"] - summ[b][k]["mean"], max_std=max(summ[a][k]["std"], summ[b][k]["std"]),
                mean_a=summ[a][k]["mean"], std_a=summ[a][k]["std"], mean_b=summ[b][k]["mean"], std_b=summ[b][k]["std"])


def verdicts(summary, status):
    t90 = {}
    ho = {}
    for _floor, name in FLOORS:
        ok = status[name] == "ok"
        t90[name] = summary[name]["histgb"]["target_0.90"] if ok else None
        ho[name] = summary[name]["histgb"]["held_out"] if ok else None
    v = {}
    g = gap(t90, "D94", "D96", "escalation")
    v["d_primary"] = dict(form="escalation(0.94) - escalation(0.96) > max(the two stds), target 0.90, histgb",
                          numbers=g, holds=None if g is None else bool(g["diff"] > g["max_std"]),
                          result=("not computable" if g is None else
                                  ("holds" if g["diff"] > g["max_std"] else "not supported")))
    g = gap(t90, "D96", "D94", "speedup_B")
    v["a_secondary"] = dict(form="speedup B(0.96) - speedup B(0.94) > max(the two stds), target 0.90, histgb",
                            numbers=g, holds=None if g is None else bool(g["diff"] > g["max_std"]),
                            reported_with=dict(flag_share=gap(t90, "D96", "D94", "flag_share"),
                                               escalation=gap(t90, "D96", "D94", "escalation")))
    g = gap(t90, "D96", "D94", "missed")
    v["c_secondary"] = dict(form="mean missed(0.96) - mean missed(0.94) <= max(the two stds), target 0.90, histgb",
                            numbers=g, holds=None if g is None else bool(g["diff"] <= g["max_std"]))
    g = gap(ho, "D96", "D94", "speedup_B")
    v["e_secondary"] = dict(form="speedup B(0.96) - speedup B(0.94) > max(the two stds), held-out target, histgb",
                            numbers=g, holds=None if g is None else bool(g["diff"] > g["max_std"]),
                            held_out_points=None if g is None else dict(D96=ho["D96"]["n_splits"], D94=ho["D94"]["n_splits"]))
    pred = {}
    for name in PRED:
        if t90[name] is None:
            pred[name] = "not computable"
            continue
        sp = t90[name]["speedup_B"]
        es = t90[name]["escalation"]
        p_sp, lo_sp, hi_sp = PRED[name]["speedup_B"]
        p_es, lo_es, hi_es = PRED[name]["escalation_pct"]
        pred[name] = dict(speedup_B=dict(predicted=p_sp, range=[lo_sp, hi_sp], observed_mean=sp["mean"], observed_std=sp["std"],
                                         mean_in_range=bool(lo_sp <= sp["mean"] <= hi_sp)),
                          escalation_pct=dict(predicted=p_es, range=[lo_es, hi_es], observed_mean=100 * es["mean"],
                                              observed_std=100 * es["std"],
                                              mean_in_range=bool(lo_es <= 100 * es["mean"] <= hi_es)))
    v["predictions_vs_observed"] = dict(note="descriptive; the rule defines no verdict on the predictions", per_floor=pred)
    return v


def fmt(s, k, scale):
    # scale 100 = percent, 1000 = 10^-3 pu, 1 = as stored
    if s[k]["mean"] is None:
        return "—"
    if scale != 1:
        return f"{scale * s[k]['mean']:.2f} ± {scale * s[k]['std']:.2f}"
    return f"{s[k]['mean']:.3f} ± {s[k]['std']:.3f}"


def write_result(summary, status, v, deviations, rule, start, commit_before):
    cols = [("BM", "BM %", 100), ("VR", "VR %", 100), ("target", "target", 1), ("q_hat", "q̂ (× 10⁻³ pu)", 1000),
            ("escalation", "esc %", 100), ("flag_share", "flag %", 100), ("solve_share_B", "solve %", 100),
            ("missed", "missed %", 100), ("gate_catch", "catch %", 100), ("speedup_B", "speedup B", 1)]
    L = ["# N16 result — gate across generator-setpoint floors", "",
         f"Rule: `{RULE}`, sha256 `{rule['sha256']}`, commit `{RULE_COMMIT}` ({rule['commit_time']}).",
         f"Run start (Step 1): {start}. Rule committed before the run started: {'yes' if commit_before else 'NO'}.",
         "Population std (ddof=0) over 5 splits. D94 and D95a points: `data/sts_n13_gate_D94.json`, "
         "`data/sts_n13_gate_D95a.json` (N13, reused). D93 and D96: this run.", "",
         "| Floor | Build | Family | Point | " + " | ".join([c[1] for c in cols]) + " | splits missed ≤ 1% |",
         "|" + "---|" * (len(cols) + 5)]
    for floor, name in FLOORS:
        for fam in ["histgb", "ridge"]:
            for point in ["target_0.90", "held_out"]:
                if status[name] != "ok" and fam == "histgb":
                    L.append(f"| {floor:.2f} | {name} | {fam} | {point} | " + " | ".join(["not run"] * len(cols)) + " | — |")
                    continue
                s = summary[name][fam][point]
                L.append(f"| {floor:.2f} | {name} | {fam} | {point} | " + " | ".join([fmt(s, c[0], c[2]) for c in cols])
                         + f" | {s['splits_missed_le_1pct']} / 5 |")
    d = v["d_primary"]
    L += ["", "## Verdict (rule: Verdict (owner))", "",
          f"- **Primary (d):** {d['form']}: **{d['result']}**."]
    if d["numbers"] is not None:
        n = d["numbers"]
        L.append(f"  - escalation 0.94: {100 * n['mean_a']:.2f} ± {100 * n['std_a']:.2f}%; 0.96: {100 * n['mean_b']:.2f} ± "
                 f"{100 * n['std_b']:.2f}%; gap {100 * n['diff']:.2f} pp vs max std {100 * n['max_std']:.2f} pp.")
    for key, label, scale, unit in [("a_secondary", "(a)", 1.0, ""), ("c_secondary", "(c)", 100.0, " pp"),
                                    ("e_secondary", "(e)", 1.0, "")]:
        x = v[key]
        if x["numbers"] is None:
            L.append(f"- **Secondary {label}:** {x['form']}: not computable.")
            continue
        n = x["numbers"]
        L.append(f"- **Secondary {label}:** {x['form']}: **{'holds' if x['holds'] else 'does not hold'}** "
                 f"(0.96 {scale * n['mean_a']:.3f} ± {scale * n['std_a']:.3f}; 0.94 {scale * n['mean_b']:.3f} ± "
                 f"{scale * n['std_b']:.3f}; difference {scale * n['diff']:.3f}{unit} vs max std {scale * n['max_std']:.3f}{unit}).")
        if key == "a_secondary":
            fs = x["reported_with"]["flag_share"]
            es = x["reported_with"]["escalation"]
            L.append(f"  - Reported with it (rule): flag share 0.96 − 0.94 = {100 * fs['diff']:.2f} pp (max std "
                     f"{100 * fs['max_std']:.2f}); escalation 0.96 − 0.94 = {100 * es['diff']:.2f} pp (max std "
                     f"{100 * es['max_std']:.2f}).")
    L += ["", "## Predictions vs observed (histgb, target 0.90; descriptive, no verdict defined)", "",
          "| Floor | Speedup B: predicted [range] | observed | Escalation %: predicted [range] | observed |", "|---|---|---|---|---|"]
    for name in PRED:
        p = v["predictions_vs_observed"]["per_floor"][name]
        fl = [f for f, n_ in FLOORS if n_ == name][0]
        if p == "not computable":
            L.append(f"| {fl:.2f} | — | not run | — | not run |")
            continue
        sp, es = p["speedup_B"], p["escalation_pct"]
        L.append(f"| {fl:.2f} | {sp['predicted']} [{sp['range'][0]}–{sp['range'][1]}] | {sp['observed_mean']:.3f} ± "
                 f"{sp['observed_std']:.3f} (mean in range: {'yes' if sp['mean_in_range'] else 'no'}) | {es['predicted']} "
                 f"[{es['range'][0]}–{es['range'][1]}] | {es['observed_mean']:.2f} ± {es['observed_std']:.2f} "
                 f"(mean in range: {'yes' if es['mean_in_range'] else 'no'}) |")
    L += ["", "## Deviations", ""]
    if deviations:
        for x in deviations:
            L.append(f"- {x}")
    else:
        L.append("- None.")
    with open(RESULT, "w") as f:
        f.write("\n".join(L) + "\n")


def summarize():
    t0 = time.time()
    rule = rule_info()
    s1 = json.load(open(STEP1))
    if not s1["passed"] or s1["rule"]["sha256"] != rule["sha256"]:
        raise SystemExit("Step 1 has not passed under this rule: stop")
    start = s1["run_start_utc"]
    commit_dt = datetime.fromisoformat(rule["commit_time"])
    start_dt = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    commit_before = bool(commit_dt < start_dt)
    per_split, summary, status, sources, deviations, hyper = [], {}, {}, {}, [], {}
    inputs = [RULE, STEP1, "data/sts_n13_floor.json", "data/solve_time.json"]
    for floor, name in FLOORS:
        points, fits, sel, src, hst, dev = floor_points(name)
        status[name] = hst
        sources[name] = src
        deviations.extend(dev)
        inputs.append(src.split(" ")[0])
        inputs.append(f"data/sts_n13_{name}.parquet")
        df, _fc, _info = n5.load_relabeled(f"data/sts_n13_{name}.parquet", "")
        bmvr = [split_bm_vr(df, seed) for seed in SEEDS]
        rows = per_split_rows(name, points, bmvr)
        per_split.extend(rows)
        summary[name] = {}
        for fam in ["histgb", "ridge"]:
            summary[name][fam] = {}
            for point in ["target_0.90", "held_out"]:
                summary[name][fam][point] = summarize_rows([r for r in rows if r["family"] == fam and r["point"] == point])
        hyper[name] = [dict(seed=x["seed"], family=x["family"], tag=x["tag"], config=x["config"], mae=x["mae"], r2=x["r2"])
                       for x in fits]
        summary[name]["selections"] = sel
        print(f"{name}: histgb t0.90 esc {fmt(summary[name]['histgb']['target_0.90'], 'escalation', 100)} "
              f"spB {fmt(summary[name]['histgb']['target_0.90'], 'speedup_B', 1)}", flush=True)
        for fam in ["histgb", "ridge"]:
            n_no_ho = 0
            for seed in SEEDS:
                fixed = [r for r in rows if r["family"] == fam and r["seed"] == seed and r["point"] == "target_0.90"][0]
                hold = [r for r in rows if r["family"] == fam and r["seed"] == seed and r["point"] == "held_out"][0]
                if fixed["available"] and not hold["available"]:
                    n_no_ho += 1
            if n_no_ho > 0:
                deviations.append(f"{name} {fam}: {n_no_ho} split(s) without a held-out point (counted as not <= 1%; "
                                  "held-out means over the remaining splits)")
    v = verdicts(summary, status)
    prov = dict(rule=rule, rule_commit_time=rule["commit_time"], run_start_utc=start,
                rule_committed_before_run_start=commit_before, step1=STEP1)
    out = dict(run="N16: the gate across generator-setpoint floors", provenance=prov, sources=sources,
               histgb_status=status, units="shares in 0-1 (BM, VR, escalation, flag_share, solve_share_B, missed, "
               "gate_catch); q_hat in pu; speedups as ratios", std_convention="population std (ddof=0) over 5 splits",
               per_split=per_split, summary=summary, deviations=deviations)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    outv = dict(run="N16 verdicts", provenance=prov, verdict_section="scratch/n16_decision_rule.md 'Verdict (owner)'",
                verdicts=v, deviations=deviations, with_deviation=len(deviations) > 0)
    with open(OUT_V, "w") as f:
        json.dump(outv, f, indent=2)
    params = dict(seeds=SEEDS, model_hyperparameters=hyper, std="ddof=0")
    for p in [OUT, OUT_V]:
        man = sm.build_manifest([p], "scratch/n16_floorgate.py", [".venv/bin/python", "scratch/n16_floorgate.py", "summarize"],
                                sorted(set(inputs)), params, "")
        man["no_new_solves"] = "No AC solve and no model fit in this step: computed from the input files listed."
        sm.write_manifest(man, p)
    write_result(summary, status, v, deviations, rule, start, commit_before)
    print(f"wrote {OUT}, {OUT_V}, {RESULT}; primary (d): {v['d_primary']['result']}; wall {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "step1":
        step1()
    elif mode == "build":
        build(sys.argv[2])
    elif mode == "summarize":
        summarize()
    else:
        raise SystemExit(f"unknown mode {mode}")
