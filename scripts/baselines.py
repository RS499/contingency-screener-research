"""Five non-ML comparators for the case118 N-1 screen, plus the conformal gate on the
same budget axis.

Comparison, not demonstration. Every comparator ranks all converged contingencies of a
base scenario; at a budget of k solved contingencies per scenario we report the share of
TRUE under-voltage violations captured. Reads only committed artifacts. Runs NO power
flow solves.

Writes data/baselines.json + Schema-B manifest.
"""

import os
import sys
import json
import time
import hashlib
import subprocess

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
import make_splits as ms
import gate_eval as ge

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor

DATASET = "data/dataset.parquet"
CLASSICAL = "data/classical_predictions.parquet"
TUNED = "data/tuned_metrics.json"
SOLVE_TIME = "data/solve_time.json"
OUT = "data/baselines.json"

LIMIT = 0.94
SEEDS = [0, 1, 2, 3, 4]
K_REPORT = [5, 10, 20, 50, 100]
COVERAGE = 0.90
FAMILIES = ["ridge", "histgb"]

APA = ("Ejebe, G. C., & Wollenberg, B. F. (1979). Automatic contingency selection. "
       "IEEE Transactions on Power Apparatus and Systems, PAS-98(1), 97-109. "
       "https://doi.org/10.1109/TPAS.1979.319518")


# ---------------------------------------------------------------- provenance helpers

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def git_out(args):
    try:
        r = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception:
        return ""


# ---------------------------------------------------------------- ranking machinery

def scenario_offsets(scen_sorted):
    """Start index and length of each scenario block in a scenario-sorted array."""
    uniq, starts, counts = np.unique(scen_sorted, return_index=True, return_counts=True)
    return uniq, starts, counts


def within_scenario_order(scen, score, tiebreak):
    """Row order that sorts by scenario, then ascending score, then ascending tiebreak.

    Lower score == ranked first == solved first. Callers negate for descending indices.
    """
    return np.lexsort((tiebreak, score, scen))


def capture_curve(scen, score, tiebreak, viol, k_max):
    """Share of true violations captured at every budget k = 1..k_max.

    Vectorized key. Returns (curve[k_max], n_viol_total, per_scenario_capture[k_max, n_scen]).
    """
    order = within_scenario_order(scen, score, tiebreak)
    scen_o = scen[order]
    viol_o = viol[order].astype(np.int64)
    uniq, starts, counts = scenario_offsets(scen_o)

    n_scen = len(uniq)
    caught = np.zeros((k_max, n_scen), dtype=np.int64)
    for i in range(n_scen):
        block = viol_o[starts[i]:starts[i] + counts[i]]
        cum = np.cumsum(block)
        take = min(k_max, len(cum))
        caught[:take, i] = cum[:take]
        if take < k_max:
            caught[take:, i] = cum[-1]
    total = int(viol.sum())
    curve = caught.sum(axis=1) / max(total, 1)
    return curve, total, caught


def capture_curve_key2(scen, score, tiebreak, viol, k_list):
    """Independent recompute at selected k using rank comparison instead of cumsum.

    Different mechanism: builds an explicit within-scenario rank vector and masks
    rank < k, rather than accumulating along a sorted block.
    """
    order = within_scenario_order(scen, score, tiebreak)
    rank = np.empty(len(order), dtype=np.int64)
    scen_o = scen[order]
    uniq, starts, counts = scenario_offsets(scen_o)
    pos = np.arange(len(order), dtype=np.int64)
    block_start = np.repeat(starts, counts)
    rank[order] = pos - block_start

    total = max(int(viol.sum()), 1)
    out = {}
    for k in k_list:
        out[int(k)] = float(((rank < k) & viol).sum() / total)
    return out


def at_k(curve, k):
    """Curve is indexed 1..k_max at positions 0..k_max-1."""
    idx = min(int(k), len(curve)) - 1
    return float(curve[idx])


def mean_std(values):
    a = np.asarray(values, dtype=np.float64)
    return float(a.mean()), float(a.std())


# ---------------------------------------------------------------- adjudication

def std_rule(name_a, mean_a, std_a, name_b, mean_b, std_b):
    """Project std rule: a difference smaller than the LARGER of the two stds is noise.

    Returns a verdict dict; never asserts a sub-sigma gap as a real difference.
    """
    gap = mean_a - mean_b
    bar = max(std_a, std_b)
    if abs(gap) <= bar:
        verdict = "indistinguishable"
        ahead = None
    elif gap > 0:
        verdict = "a_ahead"
        ahead = name_a
    else:
        verdict = "b_ahead"
        ahead = name_b
    return dict(a=name_a, a_mean=mean_a, a_std=std_a, b=name_b, b_mean=mean_b, b_std=std_b,
                gap=gap, abs_gap=abs(gap), larger_std=bar, verdict=verdict, ahead=ahead,
                margin_over_std=abs(gap) - bar)


def best_baseline(summary, comparators, k):
    """Highest-mean comparator at budget k, excluding the oracle, plus everything tied to it."""
    pool = []
    for c in comparators:
        if c != "oracle":
            pool.append(c)
    best = pool[0]
    for c in pool:
        if summary[c]["at_k"][str(k)]["mean"] > summary[best]["at_k"][str(k)]["mean"]:
            best = c
    bm = summary[best]["at_k"][str(k)]
    tied = []
    for c in pool:
        cm = summary[c]["at_k"][str(k)]
        if abs(bm["mean"] - cm["mean"]) <= max(bm["std"], cm["std"]):
            tied.append(c)
    return dict(best=best, mean=bm["mean"], std=bm["std"],
                statistically_tied_with_best=tied,
                oracle_mean=summary["oracle"]["at_k"][str(k)]["mean"])


def adjudicate(summary, gate_summary, comparators, k_report, families):
    """Every head-to-head this comparison invites, resolved by the std rule."""
    out = dict(
        rule=("a difference smaller than the larger of the two reported population stds is "
              "NOT stated as real (CLAUDE.md section 8, std rule)"),
        baseline_vs_baseline_at_k={}, gate_vs_baselines={}, best_baseline_at_k={})

    for k in k_report:
        rows = []
        for i in range(len(comparators)):
            for j in range(i + 1, len(comparators)):
                na = comparators[i]
                nb = comparators[j]
                a = summary[na]["at_k"][str(k)]
                b = summary[nb]["at_k"][str(k)]
                rows.append(std_rule(na, a["mean"], a["std"], nb, b["mean"], b["std"]))
        out["baseline_vs_baseline_at_k"][str(k)] = rows
        out["best_baseline_at_k"][str(k)] = best_baseline(summary, comparators, k)

    for fam in families:
        g = gate_summary[fam]
        rows_only = []
        rows_flag = []
        for c in comparators:
            r = g["comparators_at_gate_k"][c]
            rows_only.append(std_rule(
                f"gate_{fam}_escalate_only",
                g["capture_escalate_only"]["mean"], g["capture_escalate_only"]["std"],
                c, r["mean"], r["std"]))
            rows_flag.append(std_rule(
                f"gate_{fam}_escalate_or_flag",
                g["capture_escalate_or_flag"]["mean"], g["capture_escalate_or_flag"]["std"],
                c, r["mean"], r["std"]))
        beat_only = []
        for r in rows_only:
            if r["ahead"] == r["b"]:
                beat_only.append(r["b"])
        beat_flag = []
        tie_flag = []
        for r in rows_flag:
            if r["ahead"] == r["b"] and r["b"] != "oracle":
                beat_flag.append(r["b"])
            if r["verdict"] == "indistinguishable":
                tie_flag.append(r["b"])
        out["gate_vs_baselines"][fam] = dict(
            k_equivalent_mean=g["k_equivalent_mean"],
            vs_capture_escalate_only=rows_only,
            vs_capture_escalate_or_flag=rows_flag,
            baselines_beating_gate_escalate_only=beat_only,
            baselines_beating_gate_escalate_or_flag=beat_flag,
            baselines_tied_with_gate_escalate_or_flag=tie_flag)
    return out


# ---------------------------------------------------------------- surrogate refit

def fit_ridge(cfg, X, y):
    scaler = StandardScaler().fit(X)
    model = Ridge(alpha=cfg["alpha"]).fit(scaler.transform(X), y)
    return dict(kind="ridge", scaler=scaler, model=model)


def fit_histgb(cfg, X, y, seed):
    model = HistGradientBoostingRegressor(
        learning_rate=cfg["learning_rate"], max_iter=cfg["max_iter"],
        max_depth=cfg["max_depth"], max_leaf_nodes=cfg["max_leaf_nodes"],
        min_samples_leaf=cfg["min_samples_leaf"],
        l2_regularization=cfg["l2_regularization"], random_state=seed).fit(X, y)
    return dict(kind="histgb", model=model)


def fit_one(family, cfg, X, y, seed):
    if family == "ridge":
        return fit_ridge(cfg, X, y)
    return fit_histgb(cfg, X, y, seed)


def predict(fitted, X):
    if fitted["kind"] == "ridge":
        return fitted["model"].predict(fitted["scaler"].transform(X))
    return fitted["model"].predict(X)


def m2_config(tuned, seed, family):
    for r in tuned["records"]:
        if r["seed"] == seed and r["family"] == family and r["metric"] == "m2":
            return dict(r["config"]), r
    raise KeyError(f"no M2 record for seed={seed} family={family}")


# ---------------------------------------------------------------- comparator scores

def static_severity_score(df, train_mask, elem_key):
    """Historical violation frequency per element over TRAIN scenarios only.

    Ranking is identical for every scenario; it never reads the current operating point
    and never reads a test label.
    """
    freq = {}
    tr_key = elem_key[train_mask]
    tr_vi = df["violation"].to_numpy()[train_mask].astype(np.float64)
    uniq = np.unique(tr_key)
    for e in uniq:
        m = tr_key == e
        freq[int(e)] = float(tr_vi[m].mean())
    score = np.array([-freq.get(int(e), 0.0) for e in elem_key], dtype=np.float64)
    return score, freq


def static_severity_key2(df, train_mask, elem_key):
    """Independent recompute of the frequency table via pandas groupby."""
    t = pd.DataFrame({"e": elem_key[train_mask],
                      "v": df["violation"].to_numpy()[train_mask].astype(np.float64)})
    g = t.groupby("e")["v"].mean()
    return {int(k): float(v) for k, v in g.items()}


def terminal_base_voltage(df, elem_key, n_line):
    """Min pre-outage voltage at the outaged branch's own terminal buses.

    Topology only (which buses a branch connects) - reads no solved quantity beyond the
    committed vm0_* columns already in the dataset. No power flow is run.
    """
    import pandapower.networks as nw
    net = nw.case118()
    term = {}
    for idx in net.line.index:
        term[int(idx)] = (int(net.line.at[idx, "from_bus"]), int(net.line.at[idx, "to_bus"]))
    for idx in net.trafo.index:
        term[n_line + int(idx)] = (int(net.trafo.at[idx, "hv_bus"]),
                                   int(net.trafo.at[idx, "lv_bus"]))
    n_bus = 118
    vm0 = df[[f"vm0_{i}" for i in range(n_bus)]].to_numpy(np.float64)
    a = np.array([term[int(e)][0] for e in elem_key], dtype=np.int64)
    b = np.array([term[int(e)][1] for e in elem_key], dtype=np.int64)
    rows = np.arange(len(elem_key))
    return np.minimum(vm0[rows, a], vm0[rows, b])


# ---------------------------------------------------------------- main

def main():
    t_start = time.time()

    with open(TUNED) as f:
        tuned = json.load(f)
    with open(SOLVE_TIME) as f:
        solve_time = json.load(f)
    ms_solver = float(tuned["ms_solver"])

    df, feature_cols = ms.load_dataset(DATASET)
    X, y, groups, _branch_cols = ms.build_design_matrix(df, feature_cols)

    clas = pd.read_parquet(CLASSICAL)
    key_cols = ["scenario_id", "outaged_type", "outaged_idx"]
    merged = df[key_cols].merge(clas[key_cols + ["pi", "pred_min_vm"]], on=key_cols,
                                how="left", validate="one_to_one")
    if len(merged) != len(df):
        raise ValueError("classical merge changed row count")
    n_missing_pi = int(merged["pi"].isna().sum())
    pi = merged["pi"].to_numpy(np.float64)
    classical_pred = merged["pred_min_vm"].to_numpy(np.float64)

    n_line = 173
    is_trafo = (df["outaged_type"].to_numpy() == "trafo")
    elem_key = df["outaged_idx"].to_numpy(np.int64) + np.where(is_trafo, n_line, 0)
    scen_all = df["scenario_id"].to_numpy(np.int64)
    viol_all = df["violation"].to_numpy(bool)
    n0_all = df["n0_min_vm"].to_numpy(np.float64)
    term_v_all = terminal_base_voltage(df, elem_key, n_line)

    pi_zero_share = float((pi == 0.0).mean())
    n0_unique_per_scen = int(pd.Series(n0_all).groupby(scen_all).nunique().max())

    k_max = int(pd.Series(scen_all).value_counts().max())
    print(f"rows={len(df)} k_max={k_max} pi_zero_share={pi_zero_share:.4f} "
          f"n0_unique_per_scenario_max={n0_unique_per_scen}", flush=True)

    comparators = [
        "pivq_index_tiebreak", "pivq_random_tiebreak", "pivq_predvm_tiebreak",
        "random", "static_severity",
        "base_proximity_n0_random_tiebreak", "base_proximity_n0_index_tiebreak",
        "base_proximity_terminal_vm",
        "surrogate_point_ridge", "surrogate_point_histgb",
        "classical_point_pred_min_vm",
        "oracle",
    ]
    curves = {c: [] for c in comparators}
    per_seed = {c: {} for c in comparators}
    key2_delta = 0.0

    gate_rows = []
    refit_check = []
    seed_info = []

    for seed in SEEDS:
        print(f"\n=== seed {seed} ===", flush=True)
        splits = ms.make_splits(groups, seed)
        kept = ms.select_features(X, splits["train"])
        Xk = X[kept]
        te = splits["test"]
        tr = splits["train"]
        ca = splits["cal"]

        scen = scen_all[te]
        viol = viol_all[te]
        elem = elem_key[te]
        rng = np.random.default_rng(10_000 + seed)

        train_mask = np.zeros(len(df), dtype=bool)
        train_mask[tr] = True

        # --- surrogate refit (M2 promoted selection, per seed) -----------------
        Xtr = Xk.iloc[tr].to_numpy(np.float32)
        Xca = Xk.iloc[ca].to_numpy(np.float32)
        Xte = Xk.iloc[te].to_numpy(np.float32)
        ytr, yca, yte = y[tr], y[ca], y[te]

        sur_pred = {}
        for fam in FAMILIES:
            cfg, rec = m2_config(tuned, seed, fam)
            cfg.pop("tag", None)
            t0 = time.time()
            fitted = fit_one(fam, cfg, Xtr, ytr, seed)
            p_ca = predict(fitted, Xca)
            p_te = predict(fitted, Xte)
            fit_s = time.time() - t0
            q90 = ge.calibrate_qhat(p_ca, yca, COVERAGE)
            mae = float(np.mean(np.abs(p_te - yte)))
            ss = float(np.sum((yte - p_te) ** 2))
            st = float(np.sum((yte - yte.mean()) ** 2))
            r2 = 1.0 - ss / st
            refit_check.append(dict(
                seed=seed, family=fam, tag=rec["tag"],
                q_hat_90_recomputed=q90, q_hat_90_committed=rec["q_hat_90"],
                q_hat_90_abs_delta=abs(q90 - rec["q_hat_90"]),
                mae_recomputed=mae, mae_committed=rec["mae"],
                mae_abs_delta=abs(mae - rec["mae"]),
                r2_recomputed=r2, r2_committed=rec["r2"],
                r2_abs_delta=abs(r2 - rec["r2"]),
                n_test_recomputed=int(len(yte)), n_test_committed=rec["n_test"],
                fit_seconds=fit_s))
            print(f"  refit {fam:6s} {rec['tag']:16s} q90 d={abs(q90-rec['q_hat_90']):.3e} "
                  f"MAE d={abs(mae-rec['mae']):.3e} R2 d={abs(r2-rec['r2']):.3e} "
                  f"({fit_s:.1f}s)", flush=True)
            sur_pred[fam] = p_te

            # --- the gate on the same axis ------------------------------------
            g = ge.run_gate(p_te, q90, LIMIT)
            s = ge.score(g, yte, rec["ms_surrogate"], ms_solver, LIMIT)
            true_viol = yte < LIMIT
            n_viol = max(int(true_viol.sum()), 1)
            cap_esc = float((g["escalate"] & true_viol).sum() / n_viol)
            cap_esc_flag = float(((g["escalate"] | g["flag"]) & true_viol).sum() / n_viol)
            n_per_scen = float(len(te) / len(np.unique(scen)))
            k_equiv = s["escalation"] * n_per_scen
            gate_rows.append(dict(
                seed=seed, family=fam, coverage_target=COVERAGE,
                escalation=s["escalation"], coverage_emp=s["coverage"],
                missed_viol=s["missed_viol"], net_speedup=s["net_speedup"],
                k_equivalent=k_equiv, n_per_scenario=n_per_scen,
                capture_escalate_only=cap_esc,
                capture_escalate_or_flag=cap_esc_flag,
                capture_escalate_or_flag_key2=float(1.0 - s["missed_viol"]),
                capture_key2_abs_delta=abs(cap_esc_flag - (1.0 - s["missed_viol"])),
                n_test=int(len(yte)), n_true_viol=int(true_viol.sum()),
                flag_share=float(g["flag"].mean()), certify_share=float(g["certify"].mean())))

        # --- scores for every comparator --------------------------------------
        idx_tb = elem.astype(np.float64)
        rand_tb = rng.random(len(te))
        rand_tb2 = rng.random(len(te))
        rand_tb3 = rng.random(len(te))
        zero = np.zeros(len(te))

        stat_score, freq = static_severity_score(df, train_mask, elem_key)
        freq2 = static_severity_key2(df, train_mask, elem_key)
        fdelta = max(abs(freq[k] - freq2[k]) for k in freq)

        scores = {
            "pivq_index_tiebreak": (-pi[te], idx_tb),
            "pivq_random_tiebreak": (-pi[te], rand_tb),
            "pivq_predvm_tiebreak": (-pi[te], classical_pred[te]),
            "random": (rand_tb2, zero),
            "static_severity": (stat_score[te], idx_tb),
            "base_proximity_n0_random_tiebreak": (n0_all[te], rand_tb3),
            "base_proximity_n0_index_tiebreak": (n0_all[te], idx_tb),
            "base_proximity_terminal_vm": (term_v_all[te], idx_tb),
            "surrogate_point_ridge": (sur_pred["ridge"], idx_tb),
            "surrogate_point_histgb": (sur_pred["histgb"], idx_tb),
            "classical_point_pred_min_vm": (classical_pred[te], idx_tb),
            "oracle": (yte, idx_tb),
        }

        for name in comparators:
            sc, tb = scores[name]
            curve, total, _c = capture_curve(scen, sc, tb, viol, k_max)
            k2 = capture_curve_key2(scen, sc, tb, viol, K_REPORT)
            for k in K_REPORT:
                key2_delta = max(key2_delta, abs(at_k(curve, k) - k2[k]))
            curves[name].append(curve)
            per_seed[name][seed] = {str(k): at_k(curve, k) for k in K_REPORT}

        seed_info.append(dict(seed=seed, n_test_rows=int(len(te)),
                              n_test_scenarios=int(len(np.unique(scen))),
                              n_true_viol=int(viol.sum()),
                              viol_rate=float(viol.mean()),
                              static_freq_key2_abs_delta=float(fdelta)))
        print(f"  static-severity freq key2 delta={fdelta:.3e}", flush=True)

    # ---------------------------------------------------------------- summarize
    summary = {}
    for name in comparators:
        arr = np.vstack(curves[name])
        summary[name] = dict(
            curve_mean=[float(v) for v in arr.mean(axis=0)],
            curve_std=[float(v) for v in arr.std(axis=0)],
            at_k={})
        for k in K_REPORT:
            vals = [per_seed[name][s][str(k)] for s in SEEDS]
            m, sd = mean_std(vals)
            summary[name]["at_k"][str(k)] = dict(mean=m, std=sd,
                                                 per_seed={str(s): per_seed[name][s][str(k)]
                                                           for s in SEEDS})

    # analytic key for the random comparator: E[capture at k] = k / n_per_scenario
    n_per = float(np.mean([si["n_test_rows"] / si["n_test_scenarios"] for si in seed_info]))
    random_analytic = {str(k): float(min(k, n_per) / n_per) for k in K_REPORT}
    random_analytic_delta = max(
        abs(summary["random"]["at_k"][str(k)]["mean"] - random_analytic[str(k)])
        for k in K_REPORT)

    # gate placed on the budget axis
    gate_summary = {}
    for fam in FAMILIES:
        rows = [r for r in gate_rows if r["family"] == fam]
        keq = [r["k_equivalent"] for r in rows]
        m_keq, s_keq = mean_std(keq)
        c_esc = mean_std([r["capture_escalate_only"] for r in rows])
        c_ef = mean_std([r["capture_escalate_or_flag"] for r in rows])
        esc = mean_std([r["escalation"] for r in rows])
        # per-seed comparator capture evaluated AT that seed's own k_equivalent
        rival = {}
        for name in comparators:
            vals = []
            for i, s in enumerate(SEEDS):
                kk = int(np.ceil(rows[i]["k_equivalent"]))
                vals.append(at_k(curves[name][i], kk))
            mm, ss = mean_std(vals)
            rival[name] = dict(mean=mm, std=ss,
                               per_seed={str(SEEDS[j]): vals[j] for j in range(len(SEEDS))})
        gate_summary[fam] = dict(
            escalation_mean=esc[0], escalation_std=esc[1],
            k_equivalent_mean=m_keq, k_equivalent_std=s_keq,
            k_equivalent_rounded_up=[int(np.ceil(v)) for v in keq],
            capture_escalate_only=dict(mean=c_esc[0], std=c_esc[1]),
            capture_escalate_or_flag=dict(mean=c_ef[0], std=c_ef[1]),
            comparators_at_gate_k=rival,
            per_seed=rows)

    out = dict(
        task=("five non-ML comparators vs the conformal gate on a common budget axis: "
              "share of true under-voltage violations captured when k contingencies per "
              "base scenario are solved"),
        network="IEEE 118-bus (pandapower case118)",
        limit=LIMIT,
        seeds=SEEDS,
        k_reported=K_REPORT,
        k_max=k_max,
        n_new_power_flow_solves=0,
        std_convention="population std (ddof=0) over the five held-out test splits",
        capture_definition=("pooled: sum over test scenarios of true violations ranked in "
                            "the top-k, divided by the total true violations in the test "
                            "split. Ranking is within each base scenario over its converged "
                            "contingencies."),
        dataset_facts=dict(
            rows_used=int(len(df)),
            filter="outaged_type != 'none' and converged == True (same filter as the ML pipeline)",
            rows_per_scenario_min=int(pd.Series(scen_all).value_counts().min()),
            rows_per_scenario_max=k_max,
            violation_rate=float(viol_all.mean()),
            n_missing_pi_after_merge=n_missing_pi),
        comparator_definitions={
            "pivq": {
                "source_line": ("notes/prior-art.md section 3, lines 99-108: pins Ejebe & "
                                "Wollenberg 1979 and names the PI_VQ family."),
                "exponent_weights_in_notes": "NO SOURCE",
                "no_source_detail": ("notes/prior-art.md section 3 names the method family and "
                                     "the 1979 citation but states neither the exponent n nor "
                                     "the per-bus weights w_i. Reporting NO SOURCE and "
                                     "implementing the most common form."),
                "most_common_form_implemented": ("PI = sum_i (w_i / 2n) * d_i^(2n) with n = 1 "
                                                 "and w_i = 1 for all buses"),
                "as_committed": ("d_i = max(0, (0.94 - V_i_pred) / 0.94), i.e. the most common "
                                 "form rectified one-sided at the under-voltage floor, since "
                                 "this project screens under-voltage only. Implemented at "
                                 "scripts/classical_screen.py:118 (voltage_pi, "
                                 "PI_EXPONENT_2N = 2) and persisted as the 'pi' column of "
                                 "data/classical_predictions.parquet."),
                "V_pred_origin": ("linearized post-outage bus voltages from one base-case AC "
                                  "solve plus a Jacobian factorization per scenario, "
                                  "amortized over its 186 contingencies "
                                  "(scripts/classical_screen.py). Already committed; this "
                                  "script re-solves nothing."),
                "canonical_two_sided_form_NOT_computed": (
                    "The canonical Ejebe-Wollenberg PI_V measures deviation from nominal at "
                    "every bus and would therefore have no ties. It cannot be computed here: "
                    "classical_predictions.parquet persists only pred_min_vm and pi, not the "
                    "per-bus predicted voltage vectors, and rebuilding them requires 1500 base "
                    "AC solves - excluded by the no-new-solves constraint of this task."),
                "tie_mass": dict(
                    share_of_rows_with_pi_exactly_zero=pi_zero_share,
                    consequence=("the one-sided rectification makes PIvq uninformative on this "
                                 "share of rows; below that threshold the ranking is entirely "
                                 "the tie-break rule, so three tie-break variants are reported "
                                 "rather than one number")),
                "variants": {
                    "pivq_index_tiebreak": "ties broken by element index (deterministic, arbitrary)",
                    "pivq_random_tiebreak": "ties broken at random per seed (the honest no-information floor)",
                    "pivq_predvm_tiebreak": "ties broken by ascending linearized pred_min_vm (same classical state vector)"}},
            "random": "uniform random permutation within each scenario, one draw per seed",
            "static_severity": ("elements ranked by violation frequency over TRAIN scenarios of "
                                "that seed only; identical ranking for every scenario; never "
                                "reads the current operating point and never reads a test label"),
            "base_proximity_n0": {
                "as_specified": "rank by pre-outage n0_min_vm alone",
                "DEGENERATE": True,
                "degeneracy_evidence": dict(
                    max_unique_n0_min_vm_per_scenario=n0_unique_per_scen,
                    explanation=("n0_min_vm is the minimum voltage of the pre-outage base case "
                                 "and is therefore constant across all contingencies of a "
                                 "scenario. Ranking by it alone is a total tie within every "
                                 "scenario and carries zero within-scenario information. Its "
                                 "curve under a random tie-break is random selection by "
                                 "construction; under an index tie-break it is a fixed "
                                 "arbitrary order. Both are reported.")),
                "steelman_variant": ("base_proximity_terminal_vm: rank by the minimum PRE-OUTAGE "
                                     "voltage at the outaged branch's own two terminal buses "
                                     "(committed vm0_* columns + case118 topology). No solve. "
                                     "Labelled an addition, not the requested comparator.")},
            "surrogate_point": ("M2 (gate-aware) promoted surrogate, config read per seed from "
                                "data/tuned_metrics.json selections, refit on the full train "
                                "split, ranked by ascending predicted post-outage min_vm. No "
                                "conformal band, no gate."),
            "classical_point_pred_min_vm": ("ADDITION beyond the five requested: the linearized "
                                            "classical pred_min_vm ranked ascending. Included "
                                            "because it is the non-degenerate classical screen "
                                            "that PIvq's tie mass obscures."),
            "oracle": ("ADDITION: ranked by the true post-outage min_vm. Upper bound on any "
                       "ranker at each k. Not a baseline.")},
        gate_definition=dict(
            model="M2 (gate-aware) promoted surrogate, both families",
            coverage_target=COVERAGE,
            k_is_not_free=("every other comparator sweeps k; the gate's budget is DETERMINED by "
                           "its calibrated escalation rate. k_equivalent = escalation * "
                           "rows_per_scenario. The gate cannot be moved along this axis without "
                           "changing its coverage target."),
            capture_escalate_only=("share of true violations that land in the escalate set, i.e. "
                                   "the strict like-for-like number against a budget-k baseline "
                                   "that only learns about what it solves"),
            capture_escalate_or_flag=("share of true violations the gate does not silently "
                                      "certify, i.e. escalated OR flagged. Flagged violations "
                                      "are caught WITHOUT spending solver budget, which no "
                                      "budget-k baseline can do. Equals 1 - missed_viol."),
            asymmetry_warning=("capture_escalate_only and the baselines are the like-for-like "
                               "comparison. capture_escalate_or_flag credits the gate with a "
                               "mechanism the baselines do not have. Do not quote the second "
                               "against the first without saying so.")),
        ms_solver=ms_solver,
        ms_solver_source="data/tuned_metrics.json (minimum over timed solves, data/solve_time.json)",
        solve_time_basis=solve_time.get("note", None),
        seed_info=seed_info,
        surrogate_refit_reproduction_check=dict(
            purpose=("second key on the surrogate and gate rows: the per-seed M2 refit here must "
                     "reproduce the committed q_hat_90, MAE and R2 in data/tuned_metrics.json"),
            max_q_hat_abs_delta=float(max(r["q_hat_90_abs_delta"] for r in refit_check)),
            max_mae_abs_delta=float(max(r["mae_abs_delta"] for r in refit_check)),
            max_r2_abs_delta=float(max(r["r2_abs_delta"] for r in refit_check)),
            rows=refit_check),
        two_key_checks=dict(
            capture_curve_max_abs_delta=float(key2_delta),
            capture_curve_key1="cumulative sum along scenario-sorted blocks",
            capture_curve_key2="within-scenario rank vector masked at rank < k",
            random_comparator_analytic=random_analytic,
            random_comparator_analytic_max_abs_delta=float(random_analytic_delta),
            random_comparator_analytic_note=("E[capture at k] = k / rows_per_scenario for a "
                                             "uniform permutation; compared against the "
                                             "empirical 5-seed mean"),
            static_severity_freq_max_abs_delta=float(
                max(si["static_freq_key2_abs_delta"] for si in seed_info)),
            static_severity_key2="pandas groupby mean vs explicit boolean-mask mean",
            gate_capture_max_abs_delta=float(max(r["capture_key2_abs_delta"] for r in gate_rows)),
            gate_capture_key2="1 - missed_viol from feasibility/gate_eval.score"),
        comparators=summary,
        gate=gate_summary,
        adjudication=adjudicate(summary, gate_summary, comparators, K_REPORT, FAMILIES),
        runtime_seconds=float(time.time() - t_start),
    )

    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)

    man = dict(
        artifact=os.path.basename(OUT),
        generating_script="scripts/baselines.py",
        argv=sys.argv,
        seed=SEEDS,
        seed_note=("five outer GroupShuffleSplit seeds (feasibility/make_splits.make_splits); "
                   "random comparators drawn from numpy default_rng(10000 + seed)"),
        nproc=os.cpu_count(),
        omp_num_threads=os.environ.get("OMP_NUM_THREADS", "unset"),
        script_git_blob_sha=git_out(["hash-object", "scripts/baselines.py"]),
        script_tracked_in_git=bool(git_out(["ls-files", "scripts/baselines.py"])),
        repo_head_commit=git_out(["rev-parse", "HEAD"]),
        input_file=[DATASET, CLASSICAL, TUNED, SOLVE_TIME],
        input_sha256={DATASET: sha256_of(DATASET), CLASSICAL: sha256_of(CLASSICAL),
                      TUNED: sha256_of(TUNED), SOLVE_TIME: sha256_of(SOLVE_TIME)},
        interpreter=sys.version,
        interpreter_short=".".join(str(x) for x in sys.version_info[:3]),
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        numpy=np.__version__,
        pandas=pd.__version__,
        model_hyperparameters=dict(
            note="M2 promoted configs, read verbatim from data/tuned_metrics.json selections",
            per_seed={str(s): {fam: m2_config(tuned, s, fam)[0] for fam in FAMILIES}
                      for s in SEEDS}),
        apa_citation=APA,
        apa_citation_note=("Ejebe & Wollenberg 1979 is the PIvq comparator's source, pinned at "
                           "notes/prior-art.md section 3. It specifies neither exponent nor "
                           "weights in those notes - see comparator_definitions.pivq."),
        content_sha256=sha256_of(OUT),
    )
    with open(os.path.splitext(OUT)[0] + ".manifest.json", "w") as f:
        json.dump(man, f, indent=1)
    print(f"\nwrote {OUT} + manifest (sha256 {man['content_sha256'][:12]}...)")


if __name__ == "__main__":
    main()
