import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_splits as ms
import gate_eval as ge
import tune_surrogates as T
import classical_manifest as cm

LIMIT = 0.94
CANDIDATE_BUSES = [75, 52, 106]


def m2_configs():
    tm = json.load(open("data/tuned_metrics.json"))
    cfg = {}
    for r in tm["records"]:
        if r["metric"] == "m2":
            cfg[(r["family"], r["seed"])] = r["config"]
    return cfg


def main():
    md = json.load(open("data/missed_depth.json"))

    part1 = {}
    for fam in ("ridge", "histgb"):
        F = md["families"][fam]
        dm = F["deepest_missed"]
        max_depth = dm["depth"]
        qs = [F["per_seed"][str(s)]["0.90"]["q_hat"] for s in range(md["seeds"])]
        q_mean = float(np.mean(qs))
        q_deep = dm["q_hat"]
        part1[fam] = dict(
            max_depth=max_depth,
            q_hat90_per_seed=[float(q) for q in qs],
            q_hat90_mean=q_mean,
            ratio_to_q_hat90_mean=float(max_depth / q_mean),
            deepest_miss_seed=dm["seed"],
            deepest_miss_q_hat=float(q_deep),
            ratio_to_that_seed_q_hat=float(max_depth / q_deep))
        print(f"[part1] {fam}: max_depth={max_depth:.5f} | q_hat90 mean={q_mean:.5f} "
              f"-> ratio {max_depth/q_mean:.1f}x | deepest-seed q_hat={q_deep:.5f} "
              f"-> ratio {max_depth/q_deep:.1f}x", flush=True)

    target_min_vm = LIMIT - md["families"]["ridge"]["deepest_missed"]["depth"]
    df, feature_cols = ms.load_dataset("data/dataset.parquet")
    X, y, groups, _b = ms.build_design_matrix(df, feature_cols)

    diff = np.abs(df["min_vm"].to_numpy(np.float64) - target_min_vm)
    pos = int(np.argmin(diff))
    row = df.iloc[pos]
    scenario_id = int(row["scenario_id"])
    outaged_type = str(row["outaged_type"])
    outaged_idx = int(row["outaged_idx"])
    argmin_bus = int(row["argmin_bus"])
    n0_min_vm = float(row["n0_min_vm"])
    min_vm_n1 = float(row["min_vm"])
    print(f"\n[part2] matched row pos={pos} |min_vm-target|={diff[pos]:.2e}", flush=True)
    print(f"  scenario_id={scenario_id} outaged={outaged_type} idx={outaged_idx} "
          f"argmin_bus={argmin_bus} n0_min_vm={n0_min_vm:.5f} min_vm(N-1)={min_vm_n1:.5f}", flush=True)

    same_scen = df[df["scenario_id"] == scenario_id]
    n_exact = int((np.abs(df["min_vm"].to_numpy(np.float64) - min_vm_n1) < 1e-9).sum())

    base = df[["scenario_id", "n0_min_vm"]].drop_duplicates("scenario_id")
    base_vals = base["n0_min_vm"].to_numpy(np.float64)
    n_base = int(len(base_vals))
    pct = float((base_vals < n0_min_vm).mean() * 100.0)
    base_range = dict(n_scenarios=n_base, min=float(base_vals.min()), p1=float(np.percentile(base_vals, 1)),
                      p5=float(np.percentile(base_vals, 5)), median=float(np.median(base_vals)),
                      max=float(base_vals.max()), this_scenario_n0_min_vm=n0_min_vm,
                      percentile_of_this_base=pct)
    print(f"  base range: min={base_vals.min():.4f} p1={np.percentile(base_vals,1):.4f} "
          f"median={np.median(base_vals):.4f} max={base_vals.max():.4f}; this base at {pct:.1f} pct "
          f"({'near bottom' if pct <= 10 else 'not near bottom'})", flush=True)

    topo = dict(status="not_loaded")
    try:
        import pandapower.networks as pnet
        net = pnet.case118()
        if outaged_type == "line":
            fb = int(net.line.at[outaged_idx, "from_bus"]); tb = int(net.line.at[outaged_idx, "to_bus"])
            topo = dict(element=f"line {outaged_idx}", from_bus=fb, to_bus=tb,
                        vn_kv=float(net.bus.at[fb, "vn_kv"]))
        else:
            hv = int(net.trafo.at[outaged_idx, "hv_bus"]); lv = int(net.trafo.at[outaged_idx, "lv_bus"])
            topo = dict(element=f"trafo {outaged_idx}", hv_bus=hv, lv_bus=lv)
        wb = argmin_bus
        topo["weak_bus_index"] = wb
        topo["weak_bus_vn_kv"] = float(net.bus.at[wb, "vn_kv"]) if wb in net.bus.index else None
        topo["weak_bus_name"] = str(net.bus.at[wb, "name"]) if "name" in net.bus and wb in net.bus.index else None
        print(f"  topology: {topo.get('element')} connects buses "
              f"{topo.get('from_bus', topo.get('hv_bus'))}-{topo.get('to_bus', topo.get('lv_bus'))}; "
              f"weak bus {wb} (vn_kv {topo.get('weak_bus_vn_kv')})", flush=True)
    except Exception as e:
        topo = dict(status=f"pandapower unavailable: {e}")
        print(f"  topology: {topo['status']}", flush=True)

    weak_bus_is_candidate = argmin_bus in CANDIDATE_BUSES

    cfg = m2_configs()
    preds = []
    for seed in range(md["seeds"]):
        sp = ms.make_splits(groups, seed)
        in_test = scenario_id in set(int(s) for s in groups[sp["test"]])
        if not in_test:
            preds.append(dict(seed=seed, in_test=False))
            print(f"  seed {seed}: scenario not in test fold", flush=True)
            continue
        kept = ms.select_features(X, sp["train"]); Xk = X[kept]
        Xtr = Xk.iloc[sp["train"]].to_numpy(np.float32); ytr = y[sp["train"]]
        Xca = Xk.iloc[sp["cal"]].to_numpy(np.float32); yca = y[sp["cal"]]
        xrow = Xk.iloc[[pos]].to_numpy(np.float32)
        rec = dict(seed=seed, in_test=True, true_min_vm=min_vm_n1)
        for fam in ("ridge", "histgb"):
            fitted = T.fit_one(fam, cfg[(fam, seed)], Xtr, ytr, seed)
            pred = float(T.predict(fitted, xrow)[0])
            q = ge.calibrate_qhat(T.predict(fitted, Xca), yca, 0.90)
            lower = pred - q
            rec[fam] = dict(pred=pred, error_pred_minus_true=float(pred - min_vm_n1),
                            q_hat90=float(q), lower_band=float(lower),
                            certified_safe=bool(lower >= LIMIT),
                            depth_below_floor=float(LIMIT - min_vm_n1))
        preds.append(rec)
        print(f"  seed {seed}: ridge pred={rec['ridge']['pred']:.4f} (cert={rec['ridge']['certified_safe']}) "
              f"| histgb pred={rec['histgb']['pred']:.4f} (cert={rec['histgb']['certified_safe']})", flush=True)

    out = dict(
        question="recheck deepest-miss/q_hat ratio and identify the recurring deepest-miss contingency",
        part1_max_depth_vs_qhat90=part1,
        part1_note=("ratio_to_q_hat90_mean is max_depth divided by the family's mean band at coverage "
                    "0.90 over 5 seeds; ratio_to_that_seed_q_hat uses the exact band that certified the "
                    "deepest miss. The earlier '~40x ridge' phrasing was wrong; ridge is ~18x."),
        part2_case=dict(
            scenario_id=scenario_id, outaged_type=outaged_type, outaged_idx=outaged_idx,
            outaged_topology=topo, weak_bus_index=argmin_bus,
            weak_bus_is_one_of_75_52_106=weak_bus_is_candidate,
            n0_base_min_vm=n0_min_vm, min_vm_n1=min_vm_n1,
            depth_below_floor=float(LIMIT - min_vm_n1),
            rows_in_this_scenario=int(len(same_scen)),
            rows_at_this_exact_min_vm=n_exact,
            base_range=base_range,
            model_predictions_by_seed=preds),
        matched_row_pos=pos, target_min_vm=target_min_vm,
        no_new_solves="surrogates refit deterministically; no AC power-flow solve rerun")
    settings = dict(task="deepest-miss ratio recheck + recurring-case identification",
                    source="data/dataset.parquet, data/missed_depth.json, data/tuned_metrics.json",
                    m2_configs={f"{f}_seed{s}": cfg[(f, s)]
                                for (f, s) in sorted(cfg, key=lambda k: (k[0], k[1]))})
    cm.write_with_manifest("data/deepest_miss_case.json", out, settings)
    print("\nwrote data/deepest_miss_case.json")


if __name__ == "__main__":
    main()
