"""Out-of-sample test of the escalation identity Esc = F(L + q_hat) - F(L).

Phases, run in strict order per network:
  1a  range sweep + dataset build   (--phase 1a)
  1b  measure the CDF inputs from TEST predictions; NO GATE   (--phase 1bc)
  1c  seal the prediction into notes/preregistration.md, print its sha256 (same call)
  1d  run the gate   (--phase 1d)
  1e  compare, re-print the seal sha   (--phase 1e)

Protocol constants are asserted equal to the committed case30 gate at runtime rather
than retyped, so "nothing about the method changes across networks" is enforced, not
promised.

The identity is ALGEBRAICALLY EXACT given gate_eval.run_gate: escalate is
~(certify | flag) = (pred >= L) & (pred < L + q_hat), which is precisely the share of
test predictions in [L, L + q_hat). A MISS therefore indicates a pipeline defect, not a
falsified physical claim. That is stated in the artifact so the result is not oversold.
"""

import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, HERE)
import generate_dataset as G
import make_splits as ms
import gate_eval as ge
import manifest as mf
import classical_manifest as cm
import tune_surrogates as T
import case30_thermal as H

PREREG = "notes/preregistration.md"
ROOT = "data/netstudy"

SEEDS = 5
LIMIT = 0.94
STRIP_HI = 0.945
STRIP_W = 0.005
COVERAGE_LEVELS = [round(0.90 + 0.01 * i, 2) for i in range(9)]

N_SCENARIOS = 1500
BUILD_SEED = 100
SWEEP_SEED = 100
SWEEP_DRAWS = 200
SWEEP_WINDOW = 0.12
SWEEP_LO_FLOOR = 0.30
SWEEP_N_CONT_BASES = 6
MIN_ACCEPTANCE = 0.20
THERMAL_MAX_PCT = 100.0

APA = ("Thurner, L., Scheidler, A., Schafer, F., Menke, J., Dollichon, J., Meier, F., "
       "Meinecke, S., & Braun, M. (2018). pandapower - an open-source Python tool for "
       "convenient modeling, analysis, and optimization of electric power systems. "
       "IEEE Transactions on Power Systems, 33(6), 6510-6521. "
       "https://doi.org/10.1109/TPWRS.2018.2829021")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_out(args):
    try:
        return subprocess.check_output(["git"] + args, text=True).strip()
    except Exception:
        return None


def outdir(network):
    d = os.path.join(ROOT, network)
    os.makedirs(d, exist_ok=True)
    return d


def assert_protocol():
    import case30_gate as P
    checks = {"SEEDS": (SEEDS, P.SEEDS), "LIMIT": (LIMIT, P.LIMIT),
              "STRIP_HI": (STRIP_HI, P.STRIP_HI), "STRIP_W": (STRIP_W, P.STRIP_W),
              "COVERAGE_LEVELS": (COVERAGE_LEVELS, P.COVERAGE_LEVELS)}
    bad = {k: v for k, v in checks.items() if v[0] != v[1]}
    if bad:
        raise ValueError(f"protocol drift vs scripts/case30_gate.py: {bad}")
    return {k: v[0] for k, v in checks.items()}


def thermal_status(network):
    """Is the thermal N-0 clause DEFINED here? The guard raises when it is not."""
    net = G.build_net(network)
    try:
        ratings = H.assert_ratings_usable(net, network)
        return dict(thermal_defined=True, ratings=ratings, guard_message=None,
                    feasibility="voltage AND thermal")
    except ValueError as e:
        return dict(thermal_defined=False, ratings=None, guard_message=str(e),
                    feasibility="voltage ONLY (thermal predicate UNDEFINED)")


def write_manifest(path, extra):
    man = dict(
        artifact=os.path.basename(path),
        generating_script="scripts/netstudy.py",
        argv=sys.argv,
        seed=extra.get("seed"),
        nproc=os.cpu_count(),
        repo_head_commit=git_out(["rev-parse", "HEAD"]),
        script_git_blob_sha=git_out(["hash-object", "scripts/netstudy.py"]),
        script_tracked_in_git=bool(git_out(["ls-files", "scripts/netstudy.py"])),
        input_file=extra.get("input_file"),
        input_sha256=extra.get("input_sha256"),
        interpreter=sys.version,
        interpreter_short=".".join(str(x) for x in sys.version_info[:3]),
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        pandapower=__import__("pandapower").__version__,
        numpy=np.__version__, pandas=pd.__version__,
        apa_citation=APA,
        content_sha256=sha256_of(path),
        run_settings=extra.get("run_settings"),
    )
    with open(os.path.splitext(path)[0] + ".manifest.json", "w") as f:
        json.dump(man, f, indent=1)
    return man


def write_json(path, doc, extra):
    with open(path, "w") as f:
        json.dump(doc, f, indent=1)
    write_manifest(path, extra)
    return sha256_of(path)


# ----------------------------------------------------------------- 1a


def phase_1a(network):
    t0 = time.time()
    d = outdir(network)
    ts = thermal_status(network)
    thermal = ts["thermal_defined"]
    print(f"[{network}] thermal clause defined: {thermal} -- {ts['feasibility']}", flush=True)
    if not thermal:
        print(f"[{network}] guard fired: {ts['guard_message']}", flush=True)

    rows = []
    lo = 1.00
    while lo >= SWEEP_LO_FLOOR - 1e-9:
        H.NETWORK = network
        r = H.probe_range(lo, lo + SWEEP_WINDOW, SWEEP_DRAWS, SWEEP_SEED, thermal,
                          n_contingency_bases=SWEEP_N_CONT_BASES)
        rows.append(r)
        vp = r["n1_probe"]
        print(f"  lo={r['lo']:.2f} acc={r['acceptance_rate']:.3f} "
              f"maxload={r['max_base_loading_pct']} minvm={r['min_base_vm_pu']} "
              f"viol={vp['violation_rate'] if vp else None} [{time.time()-t0:.0f}s]", flush=True)
        if r["acceptance_rate"] >= MIN_ACCEPTANCE and (
                not thermal or (r["max_base_loading_pct"] is not None
                                and r["max_base_loading_pct"] <= THERMAL_MAX_PCT)):
            break
        lo = round(lo - 0.01, 4)

    chosen = None
    for r in rows:
        if r["acceptance_rate"] >= MIN_ACCEPTANCE and (
                not thermal or (r["max_base_loading_pct"] is not None
                                and r["max_base_loading_pct"] <= THERMAL_MAX_PCT)):
            chosen = r
            break

    sweep_doc = dict(
        network=network, phase="1a range sweep", thermal_status=ts,
        window_width=SWEEP_WINDOW, step=0.01, lo_floor=SWEEP_LO_FLOOR,
        n_draws_per_candidate=SWEEP_DRAWS, seed=SWEEP_SEED,
        selection_rule=(f"highest lo with acceptance >= {MIN_ACCEPTANCE}"
                        + (f" AND max base loading_percent <= {THERMAL_MAX_PCT}"
                           if thermal else " (thermal clause UNDEFINED, not applied)")),
        method_note=("selection rule is unchanged from scripts/case30_thermal.choose_range. "
                     "Only the sweep EXTENT is widened, from case30's lo_floor 0.70 to "
                     f"{SWEEP_LO_FLOOR}, because case57's nominal min_vm is far below 0.94. "
                     "Widening the extent downward cannot change which range is selected for "
                     "a network whose window lies above the old floor, since selection takes "
                     "the highest qualifying lo."),
        sweep=rows, chosen=chosen)
    sweep_path = os.path.join(d, "range_sweep.json")
    write_json(sweep_path, sweep_doc, dict(seed=SWEEP_SEED, input_file=None,
                                           run_settings=dict(phase="1a", network=network)))

    if chosen is None:
        print(f"[{network}] NO FEASIBLE RANGE at acceptance >= {MIN_ACCEPTANCE} "
              f"down to lo={SWEEP_LO_FLOOR}. ABANDON.", flush=True)
        return dict(status="ABANDON", reason="NO FEASIBLE RANGE", sweep=sweep_path,
                    elapsed_s=time.time() - t0)

    lo, hi = chosen["lo"], chosen["hi"]
    print(f"[{network}] chosen range [{lo}, {hi}] acc={chosen['acceptance_rate']:.3f}; "
          f"building n={N_SCENARIOS}", flush=True)

    H.NETWORK = network
    cfg = dict(network=network, stress="fixed", mult_lo=lo, mult_hi=hi,
               reg_lo=lo, reg_hi=hi, pf_lo=0.9, pf_hi=1.15, dvm=0.025)
    G.apply_config(cfg)
    net = G.build_net(network)
    load_region, n_regions = G.region_of_load(net)
    branches = G.branch_list(net)
    rng = np.random.default_rng(BUILD_SEED)
    modes = ("independent", "regional")

    all_rows = []
    accepted, draws = 0, 0
    rejected = dict(nonconvergence=0, voltage=0, thermal=0)
    base_loads, base_vms = [], []
    max_draws = N_SCENARIOS * G.MAX_REJECT_FACTOR
    tb = time.time()
    while accepted < N_SCENARIOS and draws < max_draws:
        draws += 1
        this_mode = modes[accepted % 2]
        params = G.sample_scenario(rng, net, this_mode, load_region, n_regions, stress="fixed")
        n0_conv, vm0, n0_min_vm = G.solve_n0(net, params)
        load_pct = H.max_loading_pct(net) if n0_conv else np.nan
        ok, reason = H.n0_feasible(n0_conv, n0_min_vm, load_pct, thermal=thermal)
        if not ok:
            rejected[reason] += 1
            continue
        scen_id = BUILD_SEED * 1_000_000 + accepted
        rows_s = G.run_scenario(net, branches, params, scen_id, this_mode,
                                n0_conv, vm0, n0_min_vm)
        all_rows.extend(rows_s)
        base_loads.append(load_pct)
        base_vms.append(n0_min_vm)
        accepted += 1
        if accepted % 250 == 0:
            print(f"    accepted {accepted}/{N_SCENARIOS} draws={draws} "
                  f"[{time.time()-tb:.0f}s]", flush=True)

    df = G.rows_to_frame(all_rows)
    ds_path = os.path.join(d, "dataset.parquet")
    df.to_parquet(ds_path, index=False)

    n1 = df[df.outaged_type != "none"]
    n1c = n1[n1.converged]
    stats = dict(
        network=network, phase="1a build", range=dict(lo=lo, hi=hi),
        thermal_status=ts,
        n_accepted=accepted, n_draws=draws, acceptance_rate=accepted / draws,
        rejected_by=rejected,
        max_base_loading_pct=(float(np.max(base_loads)) if base_loads and not
                              np.all(np.isnan(base_loads)) else None),
        median_base_loading_pct=(float(np.nanmedian(base_loads)) if base_loads else None),
        min_base_vm_pu=float(np.min(base_vms)), median_base_vm_pu=float(np.median(base_vms)),
        n_rows=int(len(df)), n_base_rows=int((df.outaged_type == "none").sum()),
        n_n1_rows=int(len(n1)), n_n1_converged=int(len(n1c)),
        n_n1_nonconverged=int(len(n1) - len(n1c)),
        n_branches=len(branches),
        violation_rate=float((n1c.min_vm < LIMIT).mean()),
        boundary_mass=float(((n1c.min_vm >= LIMIT) & (n1c.min_vm < STRIP_HI)).mean()),
        elapsed_s=round(time.time() - tb, 1), seed=BUILD_SEED)
    st_path = os.path.join(d, "build_stats.json")
    write_json(st_path, stats, dict(seed=BUILD_SEED, input_file=ds_path,
                                    input_sha256=sha256_of(ds_path),
                                    run_settings=dict(phase="1a", network=network)))
    print(f"[{network}] built {len(df)} rows, acceptance {accepted/draws:.4f}, "
          f"violation {stats['violation_rate']:.6f}, boundary {stats['boundary_mass']:.6f} "
          f"[{stats['elapsed_s']}s]", flush=True)
    return dict(status="OK", dataset=ds_path, stats=st_path,
                elapsed_s=time.time() - t0)


# ----------------------------------------------------------------- 1b + 1c


def fit_all(network):
    """Train, M2-select and calibrate per (family, seed). Returns per-seed test predictions.

    Runs NO GATE. gate_eval.run_gate is not called anywhere in this function.
    """
    d = outdir(network)
    ds = os.path.join(d, "dataset.parquet")
    ms_solver = mf.load_solve_time()["ms_solver"]
    df, feature_cols = ms.load_dataset(ds)
    X, y, groups, _b = ms.build_design_matrix(df, feature_cols)
    r_cands, h_cands = T.ridge_candidates(), T.histgb_candidates()

    fits, split_info = {}, {}
    for seed in range(SEEDS):
        splits = ms.make_splits(groups, seed)
        split_info[seed] = splits
        kept = ms.select_features(X, splits["train"])
        Xk = X[kept]
        tr, cal = splits["train"], splits["cal"]
        g_tr = groups[tr]
        inner = ms.make_splits(g_tr, T.INNER_SEED_OFFSET + seed)
        i_fit, i_cal, i_score = tr[inner["train"]], tr[inner["cal"]], tr[inner["test"]]
        Xfit = Xk.iloc[i_fit].to_numpy(np.float32); yfit = y[i_fit]
        Xic = Xk.iloc[i_cal].to_numpy(np.float32); yic = y[i_cal]
        Xis = Xk.iloc[i_score].to_numpy(np.float32); yis = y[i_score]
        Xtr = Xk.iloc[tr].to_numpy(np.float32); ytr = y[tr]
        Xca = Xk.iloc[cal].to_numpy(np.float32); yca = y[cal]
        Xte = Xk.iloc[splits["test"]].to_numpy(np.float32); yte = y[splits["test"]]
        for family, cands in (("ridge", r_cands), ("histgb", h_cands)):
            rows = T.search_one_family(family, cands, Xfit, yfit, Xic, yic, Xis, yis,
                                       seed, ms_solver)
            _m1, m2 = T.select_best(rows)
            cfg = T.find_config(cands, m2)
            fitted = T.fit_one(family, cfg, Xtr, ytr, seed)
            fits[(family, seed)] = dict(
                tag=m2, config=cfg, kept_cols=kept, fitted=fitted,
                pred_cal=T.predict(fitted, Xca), yca=yca,
                pred_test=T.predict(fitted, Xte), yte=yte)
            print(f"  [fit] seed={seed} {family:6s} M2={m2}", flush=True)
    return df, fits, split_info, ms_solver


def phase_1bc(network):
    t0 = time.time()
    d = outdir(network)
    assert_protocol()
    df, fits, split_info, ms_solver = fit_all(network)

    per_seed = []
    for family in ("ridge", "histgb"):
        for seed in range(SEEDS):
            e = fits[(family, seed)]
            pte = np.asarray(e["pred_test"], dtype=np.float64)
            yte = np.asarray(e["yte"], dtype=np.float64)
            for cov in COVERAGE_LEVELS:
                q_hat = ge.calibrate_qhat(e["pred_cal"], e["yca"], cov)
                # Empirical predictive CDF of the TEST predictions. No gate is run.
                F_L = float((pte < LIMIT).mean())
                F_Lq = float((pte < LIMIT + q_hat).mean())
                per_seed.append(dict(
                    family=family, seed=seed, coverage_target=cov, q_hat=q_hat,
                    F_at_L=F_L, F_at_L_plus_qhat=F_Lq,
                    identity_escalation=F_Lq - F_L,
                    boundary_mass_pred=float(((pte >= LIMIT) & (pte < LIMIT + q_hat)).mean()),
                    ceiling_p_pred_ge_L=float((pte >= LIMIT).mean()),
                    n_test=int(len(pte)),
                    test_violation_rate=float((yte < LIMIT).mean())))

    ps = pd.DataFrame(per_seed)
    pred = []
    for family in ("ridge", "histgb"):
        for cov in COVERAGE_LEVELS:
            g = ps[(ps.family == family) & (np.isclose(ps.coverage_target, cov))]
            ident = g["identity_escalation"].to_numpy()
            pred.append(dict(
                family=family, coverage_target=cov,
                predicted_escalation=float(ident.mean()),
                predicted_std=float(ident.std(ddof=0)),
                std_of_F_at_L=float(g["F_at_L"].std(ddof=0)),
                std_of_F_at_L_plus_qhat=float(g["F_at_L_plus_qhat"].std(ddof=0)),
                interval_lo=float(ident.mean() - ident.std(ddof=0)),
                interval_hi=float(ident.mean() + ident.std(ddof=0)),
                mean_q_hat=float(g["q_hat"].mean()),
                mean_F_at_L=float(g["F_at_L"].mean()),
                mean_F_at_L_plus_qhat=float(g["F_at_L_plus_qhat"].mean()),
                mean_boundary_mass_pred=float(g["boundary_mass_pred"].mean()),
                mean_ceiling=float(g["ceiling_p_pred_ge_L"].mean()),
                n_seeds=int(len(g))))

    bs = json.load(open(os.path.join(d, "build_stats.json")))
    n1c = df
    doc = dict(
        network=network, phase="1b prediction inputs (gate NOT run)",
        identity="Esc = F_pred(L + q_hat) - F_pred(L), empirical CDF of TEST predictions",
        exactness_note=("ALGEBRAICALLY EXACT given feasibility/gate_eval.py:21, where "
                        "escalate = ~(certify | flag) = (pred >= L) & (pred < L + q_hat). "
                        "The identity therefore tests that the pipeline computes what the "
                        "gate defines; it is NOT an independent physical prediction, and a "
                        "MISS would indicate a pipeline defect rather than a falsified claim."),
        interval_convention=("predicted +/- the seed-to-seed population std (ddof=0) of the "
                             "identity value. The stds of the two CDF terms are reported "
                             "separately as std_of_F_at_L and std_of_F_at_L_plus_qhat."),
        limit=LIMIT, seeds=SEEDS, coverage_levels=COVERAGE_LEVELS,
        dataset_violation_rate=float((n1c.min_vm < LIMIT).mean()),
        dataset_boundary_mass=float(((n1c.min_vm >= LIMIT) & (n1c.min_vm < STRIP_HI)).mean()),
        base_case_statistics=dict(
            n_accepted=bs["n_accepted"], acceptance_rate=bs["acceptance_rate"],
            min_base_vm_pu=bs["min_base_vm_pu"], median_base_vm_pu=bs["median_base_vm_pu"],
            max_base_loading_pct=bs["max_base_loading_pct"],
            median_base_loading_pct=bs["median_base_loading_pct"],
            range=bs["range"], thermal_status=bs["thermal_status"]),
        predictions=pred, per_seed=per_seed)
    path = os.path.join(d, "prediction_inputs.json")
    ds_path = os.path.join(d, "dataset.parquet")
    write_json(path, doc, dict(seed=None, input_file=ds_path,
                               input_sha256=sha256_of(ds_path),
                               run_settings=dict(phase="1b", network=network,
                                                 gate_run=False)))
    print(f"[{network}] 1b done [{time.time()-t0:.0f}s]; sealing", flush=True)
    seal = seal_prediction(network, doc, pred)
    return dict(status="OK", prediction_inputs=path, seal_sha256=seal)


def seal_prediction(network, doc, pred):
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    head = git_out(["rev-parse", "HEAD"])
    lines = []
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"## SEALED PREDICTION — escalation identity on {network}")
    lines.append("")
    lines.append(f"**Sealed:** {stamp}   **git HEAD:** `{head}`")
    lines.append(f"**Identity:** `{doc['identity']}`")
    lines.append(f"**Interval:** {doc['interval_convention']}")
    lines.append(f"**Exactness:** {doc['exactness_note']}")
    lines.append("")
    b = doc["base_case_statistics"]
    lines.append(f"**Inputs.** dataset violation rate `{doc['dataset_violation_rate']!r}`; "
                 f"dataset boundary mass `{doc['dataset_boundary_mass']!r}`; "
                 f"N-0 acceptance `{b['acceptance_rate']!r}` over range "
                 f"`[{b['range']['lo']}, {b['range']['hi']}]`; min base vm "
                 f"`{b['min_base_vm_pu']!r}`; max base loading "
                 f"`{b['max_base_loading_pct']!r}`; feasibility "
                 f"`{b['thermal_status']['feasibility']}`.")
    lines.append("")
    lines.append("| family | target | predicted esc | std | interval lo | interval hi | "
                 "mean q_hat | mean F(L) | mean F(L+q) | boundary mass | ceiling |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for p in pred:
        lines.append(f"| {p['family']} | {p['coverage_target']} | "
                     f"{p['predicted_escalation']!r} | {p['predicted_std']!r} | "
                     f"{p['interval_lo']!r} | {p['interval_hi']!r} | {p['mean_q_hat']!r} | "
                     f"{p['mean_F_at_L']!r} | {p['mean_F_at_L_plus_qhat']!r} | "
                     f"{p['mean_boundary_mass_pred']!r} | {p['mean_ceiling']!r} |")
    lines.append("")
    lines.append(f"**Confidence label:** HIGH for the arithmetic, NONE for physical novelty — "
                 f"the identity is exact by the gate's own definition, so this seal tests the "
                 f"pipeline on {network}, not the theory.")
    lines.append("")
    lines.append(f"gate not yet run on {network} as of {stamp}")
    lines.append("")
    with open(PREREG, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))
    sha = sha256_of(PREREG)
    seal_path = os.path.join(outdir(network), "seal_1c.json")
    with open(seal_path, "w") as f:
        json.dump(dict(network=network, sealed_utc=stamp, git_head=head,
                       preregistration_file=PREREG,
                       preregistration_sha256_at_1c=sha,
                       gate_run_before_seal=False), f, indent=1)
    write_manifest(seal_path, dict(seed=None, input_file=PREREG, input_sha256=sha,
                                   run_settings=dict(phase="1c", network=network)))
    print(f"[{network}] SEAL sha256({PREREG}) = {sha}", flush=True)
    return sha


# ----------------------------------------------------------------- 1d


def phase_1d(network):
    t0 = time.time()
    d = outdir(network)
    protocol = assert_protocol()
    seal_path = os.path.join(d, "seal_1c.json")
    if not os.path.exists(seal_path):
        raise RuntimeError(f"{network}: no 1c seal on disk. The gate must not run first.")
    df, fits, split_info, ms_solver = fit_all(network)

    records = []
    frozen090 = {"ridge": [], "histgb": []}
    for family in ("ridge", "histgb"):
        for seed in range(SEEDS):
            e = fits[(family, seed)]
            pred_te, yte = e["pred_test"], e["yte"]
            n_test, n_viol = int(len(yte)), int((yte < LIMIT).sum())
            for cov in COVERAGE_LEVELS:
                q_hat = ge.calibrate_qhat(e["pred_cal"], e["yca"], cov)
                gate = ge.run_gate(pred_te, q_hat, LIMIT)
                s = ge.score(gate, yte, 1e-6, ms_solver, LIMIT)
                rec = dict(family=family, seed=seed, coverage_target=cov, q_hat=q_hat,
                           escalation=s["escalation"], coverage_emp=s["coverage"],
                           missed_viol=s["missed_viol"], net_speedup=s["net_speedup"],
                           n_test=n_test, n_true_viol=n_viol,
                           n_escalated=s["n_escalated"],
                           n_missed=int((gate["certify"] & (yte < LIMIT)).sum()))
                records.append(rec)
                if abs(cov - 0.90) < 1e-9:
                    frozen090[family].append(rec)

    summary = {}
    for family in ("ridge", "histgb"):
        recs = frozen090[family]
        esc = np.array([r["escalation"] for r in recs])
        cov_emp = np.array([r["coverage_emp"] for r in recs])
        missed = np.array([r["missed_viol"] for r in recs])
        speed = np.array([r["net_speedup"] for r in recs])
        summary[family] = dict(
            escalation_mean=float(esc.mean()), escalation_std=float(esc.std()),
            coverage_emp_mean=float(cov_emp.mean()), coverage_emp_std=float(cov_emp.std()),
            missed_viol_mean=float(missed.mean()), missed_viol_std=float(missed.std()),
            net_speedup_mean=float(speed.mean()), net_speedup_std=float(speed.std()),
            n_test_per_seed=[r["n_test"] for r in recs],
            n_true_viol_per_seed=[r["n_true_viol"] for r in recs])

    crossings = {}
    for family in ("ridge", "histgb"):
        by_cov = {}
        for r in records:
            if r["family"] == family:
                by_cov.setdefault(r["coverage_target"], []).append(r)
        crossing = None
        for cov in COVERAGE_LEVELS:
            mm = float(np.mean([r["missed_viol"] for r in by_cov[cov]]))
            if mm < 0.01:
                crossing = dict(coverage_target=cov, missed_viol=mm,
                                escalation=float(np.mean([r["escalation"] for r in by_cov[cov]])),
                                net_speedup=float(np.mean([r["net_speedup"] for r in by_cov[cov]])))
                break
        crossings[family] = crossing

    violation_rate = float((df.min_vm < LIMIT).mean())
    boundary_mass = float(((df.min_vm >= LIMIT) & (df.min_vm < STRIP_HI)).mean())
    ds_path = os.path.join(d, "dataset.parquet")
    out = dict(network=network, source_dataset=ds_path,
               protocol_source="scripts/case30_gate.py (constants asserted equal at runtime)",
               protocol=protocol, seeds=SEEDS, limit=LIMIT, ms_solver=ms_solver,
               coverage_levels=COVERAGE_LEVELS,
               std_convention="population std (ddof=0) over the five held-out splits",
               violation_rate_pct=round(100 * violation_rate, 4),
               saturation_point_pct=round(100 * (1 - violation_rate), 4),
               boundary_mass_pct=round(100 * boundary_mass, 4),
               four_metrics_at_90pct_coverage=summary,
               crossings_first_below_1pct_missed=crossings,
               records=records)
    path = os.path.join(d, "frozen.json")
    write_json(path, out, dict(seed=None, input_file=ds_path,
                               input_sha256=sha256_of(ds_path),
                               run_settings=dict(phase="1d", network=network)))
    for f in ("ridge", "histgb"):
        s = summary[f]
        print(f"[{network}] {f:6s} esc@0.90={s['escalation_mean']*100:.2f}+-"
              f"{s['escalation_std']*100:.2f}%  missed={s['missed_viol_mean']*100:.3f}%  "
              f"speedup={s['net_speedup_mean']:.2f}", flush=True)
    print(f"[{network}] 1d done [{time.time()-t0:.0f}s]", flush=True)
    return dict(status="OK", frozen=path)


# ----------------------------------------------------------------- 1e


def phase_1e(network):
    d = outdir(network)
    seal = json.load(open(os.path.join(d, "seal_1c.json")))
    sha_now = sha256_of(PREREG)
    intact = bool(sha_now == seal["preregistration_sha256_at_1c"])

    pi = json.load(open(os.path.join(d, "prediction_inputs.json")))
    fr = json.load(open(os.path.join(d, "frozen.json")))
    meas = {}
    for r in fr["records"]:
        meas.setdefault((r["family"], r["coverage_target"]), []).append(r["escalation"])

    comp = []
    for p in pi["predictions"]:
        key = (p["family"], p["coverage_target"])
        vals = np.array(meas[key], dtype=np.float64)
        m = float(vals.mean())
        err = m - p["predicted_escalation"]
        std = p["predicted_std"]
        comp.append(dict(
            family=p["family"], coverage_target=p["coverage_target"],
            predicted=p["predicted_escalation"], predicted_std=std,
            interval_lo=p["interval_lo"], interval_hi=p["interval_hi"],
            measured=m, measured_std=float(vals.std(ddof=0)),
            abs_error=abs(err), signed_error=err,
            error_in_std_units=(None if std == 0 else float(err / std)),
            hit=bool(p["interval_lo"] - 1e-15 <= m <= p["interval_hi"] + 1e-15)))

    doc = dict(network=network, phase="1e comparison",
               seal=dict(preregistration_file=PREREG,
                         sha256_at_1c=seal["preregistration_sha256_at_1c"],
                         sha256_at_1e=sha_now, unchanged=intact,
                         verdict=("SEAL INTACT" if intact else
                                  "SEAL BROKEN - THIS NETWORK'S RESULT IS VOID")),
               exactness_note=pi["exactness_note"],
               n_predictions=len(comp), n_hits=int(sum(c["hit"] for c in comp)),
               mean_abs_error=float(np.mean([c["abs_error"] for c in comp])),
               max_abs_error=float(np.max([c["abs_error"] for c in comp])),
               comparisons=comp)
    path = os.path.join(d, "comparison.json")
    write_json(path, doc, dict(seed=None, input_file=os.path.join(d, "frozen.json"),
                               input_sha256=sha256_of(os.path.join(d, "frozen.json")),
                               run_settings=dict(phase="1e", network=network)))
    print(f"[{network}] SEAL at 1c {seal['preregistration_sha256_at_1c']}")
    print(f"[{network}] SEAL at 1e {sha_now}  -> {doc['seal']['verdict']}")
    print(f"[{network}] hits {doc['n_hits']}/{doc['n_predictions']}  "
          f"mean|err| {doc['mean_abs_error']:.3e}  max|err| {doc['max_abs_error']:.3e}",
          flush=True)
    return doc


if __name__ == "__main__":
    net = sys.argv[sys.argv.index("--network") + 1]
    ph = sys.argv[sys.argv.index("--phase") + 1]
    if ph == "1a":
        print(json.dumps(phase_1a(net), default=str))
    elif ph == "1bc":
        print(json.dumps(phase_1bc(net), default=str))
    elif ph == "1d":
        print(json.dumps(phase_1d(net), default=str))
    elif ph == "1e":
        phase_1e(net)
    else:
        raise SystemExit(f"unknown phase {ph}")
