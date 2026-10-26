import os
import sys
import json
import time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import make_splits as ms
import gate_eval as ge
import tune_surrogates as tu
import sts_manifest as sm

# N15 (POST HOC, exploratory -- not pre-registered). Label every number from this script as post hoc.
# Refits the stored held-out models of an N13/N14 gate run (same splits, features, M2 config, seed), checks that
# the refit reproduces that run's q_hat / missed / escalation / n_test for every seed, and only then computes:
#   (a) miss depth: how far below 0.94 pu each missed violation falls;
#   (b) worst split: its target, band and escalation, then (secondary) the buses and outages its misses come from;
#   (c) three escalation-related quantities, each under its own name:
#       boundary mass [0.94, 0.945): fixed width, model-free, how crowded the test labels are near the limit;
#       labels in [0.94, 0.94 + q_hat): escalation with perfect predictions at this band width (q_hat is model-set);
#       labels + binned calibration residuals: escalation once model error is added back.
# No AC solves. Usage: .venv/bin/python scratch/n15_posthoc_refit.py D94 [histgb|ridge]
# Illinois is left out until the trafo-63 filter used by N14 is wired in here.

LIMIT = 0.94
NETS = {
    "D94": ["data/sts_n13_D94.parquet", "data/sts_n13_gate_D94.json"],
    "C30": ["data/sts_n13_C30.parquet", "data/sts_n13_gate_C30.json"],
    "C24": ["data/sts_n13_C24.parquet", "data/sts_n14_gate_C24.json"],
}
DEPTH_BINS_MV = [0, 0.5, 1, 2, 3, 5, 10, 20, 50, np.inf]
BIN_LO = 0.920
BIN_HI = 0.970
BIN_W = 0.001       # 1 mV label bins near the limit
MIN_BIN_N = 200     # thinner bins use the unconditional residuals


def window_prob(y, e_sorted, q):
    # for each label y: share of residuals e with LIMIT <= y + e < LIMIT + q
    lo = np.searchsorted(e_sorted, LIMIT - y, side="left")
    hi = np.searchsorted(e_sorted, LIMIT + q - y, side="left")
    return (hi - lo) / len(e_sorted)


def label_bins(v):
    edges = np.round(np.arange(BIN_LO, BIN_HI + BIN_W / 2, BIN_W), 6)
    return np.digitize(v, edges), edges   # 0 = below BIN_LO, len(edges) = at/above BIN_HI


def top_counts(df, per_seed, seeds, col, k):
    parts = []
    for sd in seeds:
        s = per_seed[sd]
        sub = df.iloc[s["te"][s["certify"] & s["tv"]]]
        if col == "element":
            parts.append(sub["outaged_type"].astype(str) + ":" + sub["outaged_idx"].astype(str))
        else:
            parts.append(sub[col].astype(str))
    v = pd.concat(parts).value_counts()
    if v.sum() == 0:
        return dict(n=0, top=[])
    return dict(n=int(v.sum()), top=[[str(i), int(n), round(float(n / v.sum()), 4)] for i, n in v.head(k).items()])


def refit_seed(df, X, y, groups, g, seed, family, cands):
    sel = g["selections"][str(seed)][family]
    tgt = sel["m2_inner_cov_at"]
    ref = [p for p in g["points"] if p["seed"] == seed and p["family"] == family and p["point"] == "held_out"][0]
    splits = ms.make_splits(groups, seed)
    kept = ms.select_features(X, splits["train"])
    Xk = X[kept]
    tr, ca, te = splits["train"], splits["cal"], splits["test"]
    fitted = tu.fit_one(family, tu.find_config(cands, sel["m2"]), Xk.iloc[tr].to_numpy(np.float32), y[tr], seed)
    p_ca = np.asarray(tu.predict(fitted, Xk.iloc[ca].to_numpy(np.float32)), dtype=np.float64)
    p_te = np.asarray(tu.predict(fitted, Xk.iloc[te].to_numpy(np.float32)), dtype=np.float64)
    y_ca = y[ca]
    y_te = y[te]
    q = float(ge.calibrate_qhat(p_ca, y_ca, tgt))
    gate = ge.run_gate(p_te, q, LIMIT)
    tv = y_te < LIMIT
    missed = float((gate["certify"] & tv).sum() / max(int(tv.sum()), 1))
    esc = float(gate["escalate"].mean())
    c = dict(seed=seed, tag=sel["m2"], target=tgt, q_hat=q, q_hat_ref=ref["q_hat"], missed=missed,
             missed_ref=ref["missed"], escalation=esc, escalation_ref=ref["escalation"],
             n_test=int(len(te)), n_test_ref=ref["n_test"])
    c["match"] = bool(abs(q - ref["q_hat"]) < 1e-9 and abs(missed - ref["missed"]) < 1e-9
                      and abs(esc - ref["escalation"]) < 1e-9 and len(te) == ref["n_test"])
    s = dict(q=q, p_ca=p_ca, y_ca=y_ca, p_te=p_te, y_te=y_te, te=te, ca=ca, certify=gate["certify"],
             esc=gate["escalate"], tv=tv, target=tgt)
    return c, s


def miss_depth(per_seed):
    rows = []
    pooled = []
    for seed in sorted(per_seed):
        s = per_seed[seed]
        m = s["certify"] & s["tv"]
        d_mv = (LIMIT - s["y_te"][m]) * 1000.0
        pooled.append(d_mv)
        r = dict(seed=seed, n_missed=int(m.sum()), q_hat_mV=s["q"] * 1000)
        if len(d_mv) > 0:
            r.update(median_mV=float(np.median(d_mv)), max_mV=float(d_mv.max()),
                     share_within_1mV=float((d_mv < 1).mean()), share_within_2mV=float((d_mv < 2).mean()),
                     share_within_5mV=float((d_mv < 5).mean()), share_within_qhat=float((d_mv < s["q"] * 1000).mean()))
        rows.append(r)
    pooled = np.concatenate(pooled)
    counts, _ = np.histogram(pooled, bins=DEPTH_BINS_MV)
    out = dict(per_seed=rows, pooled_n=int(len(pooled)),
               pooled_hist_mV=dict(edges=[str(b) for b in DEPTH_BINS_MV], counts=counts.tolist()))
    if len(pooled) > 0:
        out.update(pooled_median_mV=float(np.median(pooled)), pooled_max_mV=float(pooled.max()),
                   pooled_share_within_1mV=float((pooled < 1).mean()), pooled_share_within_2mV=float((pooled < 2).mean()),
                   pooled_share_within_5mV=float((pooled < 5).mean()))
    return out


def escalation_quantities(per_seed):
    rows = []
    for seed in sorted(per_seed):
        s = per_seed[seed]
        q = s["q"]
        y_te = s["y_te"]
        y_ca = s["y_ca"]
        e = np.sort(s["p_ca"] - y_ca)
        b_ca, edges = label_bins(y_ca)
        b_te, _ = label_bins(y_te)
        prob = np.empty(len(y_te))
        n_fallback = 0
        for b in np.unique(np.concatenate([b_ca, b_te])):
            in_ca = b_ca == b
            in_te = b_te == b
            if in_ca.sum() >= MIN_BIN_N:
                eb = np.sort(s["p_ca"][in_ca] - y_ca[in_ca])
            else:
                eb = e
                n_fallback = n_fallback + int(in_te.sum())
            if in_te.any():
                prob[in_te] = window_prob(y_te[in_te], eb, q)
        rows.append(dict(
            seed=seed, target=s["target"], q_hat_mV=q * 1000, measured_escalation=float(s["esc"].mean()),
            boundary_mass_fixed_5mV=float(((y_te >= LIMIT) & (y_te < LIMIT + 0.005)).mean()),
            labels_in_window_perfect_predictions=float(((y_te >= LIMIT) & (y_te < LIMIT + q)).mean()),
            labels_plus_residuals_unconditional=float(window_prob(y_te, e, q).mean()),
            labels_plus_residuals_binned=float(prob.mean()),
            test_rows_using_fallback=n_fallback))
    return rows


def main():
    t0 = time.time()
    net = sys.argv[1]
    family = "histgb"
    if len(sys.argv) > 2:
        family = sys.argv[2]
    data_path = NETS[net][0]
    gate_path = NETS[net][1]
    with open(gate_path) as f:
        g = json.load(f)
    df, feature_cols = ms.load_dataset(data_path)
    n_ref = g["labels"]["n_rows_loaded"]
    print(f"rows loaded {len(df)}; gate run loaded {n_ref}", flush=True)
    if len(df) != n_ref:
        raise SystemExit("STOP: row count differs from the gate run, so the splits would differ.")
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    y = np.asarray(y, dtype=np.float64)
    if family == "histgb":
        cands = tu.histgb_candidates()
    else:
        cands = tu.ridge_candidates()

    checks = []
    per_seed = {}
    frames = []
    for seed in g["seeds"]:
        c, s = refit_seed(df, X, y, groups, g, seed, family, cands)
        checks.append(c)
        per_seed[seed] = s
        print(json.dumps(c), flush=True)
        for role, idx, p, yy in [["cal", s["ca"], s["p_ca"], s["y_ca"]], ["test", s["te"], s["p_te"], s["y_te"]]]:
            f = df.iloc[idx][["scenario_id", "outaged_type", "outaged_idx", "argmin_bus"]].copy()
            f["seed"] = seed
            f["role"] = role
            f["row"] = idx
            f["y"] = yy
            f["p"] = p
            f["q_hat"] = s["q"]
            f["target"] = s["target"]
            frames.append(f)

    out_json = f"data/sts_n15_{net}_{family}.json"
    out_pq = f"data/sts_n15_preds_{net}_{family}.parquet"
    params = dict(network=net, family=family, gate_file=gate_path, limit=LIMIT, depth_bins_mV=[str(b) for b in DEPTH_BINS_MV],
                  label_bins=[BIN_LO, BIN_HI, BIN_W], min_bin_n=MIN_BIN_N, status="POST HOC, exploratory",
                  model_hyperparameters=[dict(seed=c["seed"], tag=c["tag"], target=c["target"]) for c in checks])
    inputs = [data_path, gate_path, "scripts/tune_surrogates.py", "feasibility/gate_eval.py", "feasibility/make_splits.py"]
    all_match = True
    for c in checks:
        all_match = all_match and c["match"]
    if not all_match:
        with open(out_json, "w") as f:
            json.dump(dict(status="REPRODUCTION FAILED: no analysis run", checks=checks), f, indent=2)
        man = sm.build_manifest([out_json], "scratch/n15_posthoc_refit.py",
                                [".venv/bin/python", "scratch/n15_posthoc_refit.py", net, family], inputs, params, "")
        man["no_new_solves"] = "No AC solve. Model fits: M2 refits per seed (no search)."
        sm.write_manifest(man, out_json)
        raise SystemExit(f"STOP: refit does not reproduce the gate run for every seed. Checks in {out_json}.")

    pd.concat(frames, ignore_index=True).to_parquet(out_pq)
    depth = miss_depth(per_seed)
    worst = checks[0]
    for c in checks:
        if c["missed"] > worst["missed"]:
            worst = c
    others = [sd for sd in per_seed if sd != worst["seed"]]
    worst_split = dict(
        seed=worst["seed"], target=worst["target"], q_hat_mV=worst["q_hat"] * 1000, missed=worst["missed"],
        escalation=worst["escalation"], other_targets=[c["target"] for c in checks if c["seed"] != worst["seed"]],
        secondary_breakdown_note="the target choice comes first; buses and outages are secondary",
        worst_buses=top_counts(df, per_seed, [worst["seed"]], "argmin_bus", 5),
        worst_elements=top_counts(df, per_seed, [worst["seed"]], "element", 5),
        other_buses=top_counts(df, per_seed, others, "argmin_bus", 5),
        other_elements=top_counts(df, per_seed, others, "element", 5),
        bus_note="argmin_bus is the 0-based bus index; IEEE number = index + 1 on case118")
    esc = escalation_quantities(per_seed)
    out = dict(status="POST HOC, exploratory; reproduction checks passed for every seed", network=net, family=family,
               gate_file=gate_path, data_file=data_path, checks=checks, miss_depth=depth, worst_split=worst_split,
               escalation_quantities=esc, wall_s=time.time() - t0)
    with open(out_json, "w") as f:
        json.dump(out, f, indent=2, default=str)
    man = sm.build_manifest([out_json, out_pq], "scratch/n15_posthoc_refit.py",
                            [".venv/bin/python", "scratch/n15_posthoc_refit.py", net, family], inputs, params, "")
    man["no_new_solves"] = "No AC solve. Model fits: M2 refits per seed (no search), reproduced against the gate file."
    sm.write_manifest(man, out_json)

    print("\n== miss depth (pooled) ==")
    print(json.dumps({k: v for k, v in depth.items() if k != "per_seed"}))
    for r in depth["per_seed"]:
        print(json.dumps(r))
    print("\n== worst split ==")
    print(json.dumps(worst_split, default=str))
    print("\n== escalation quantities (per seed) ==")
    for r in esc:
        print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}))
    print(f"\nwrote {out_json} and {out_pq}; wall {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
