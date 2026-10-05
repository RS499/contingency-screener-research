import os
import sys
import json
import time
import hashlib
import multiprocessing
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import n13_common as c
import n13_build as nb
import generate_dataset as gd
import sts_n2_label_audit as n2
import n10_relabel_illinois as n10r
import n11_relabel_net as n11r
import make_splits as ms
import gate_eval as ge
import tune_surrogates as tu
import manifest as mf
import sts_manifest as sm
import n5_gate_eval as n5
import n9_budget_curve as bc

# N13 Step 6, arm F (scratch/n13_decision_rule.md §3-§4, diagnostic): the ORIGINAL base sets with corrected inputs only.
# (1) For each original base of D94, ILL, C30, C24 (replayed with the check-1 replay functions), solve the corrected
#     N-0 state (n13_common.corrected_pf: pinned + switch-back) and write a copy of the original dataset with only
#     vm0_* and n0_min_vm replaced: data/sts_n13_armF_<name>.parquet (original schema; same bases, rows, labels, splits).
# (2) Per split and family: the existing M2 config and held-out target (original gate results) refit on train
#     (select_features re-run). The refit on the ORIGINAL inputs must reproduce the existing held-out missed rate
#     exactly before the corrected inputs are used; then refit on the corrected inputs. Labels are the original
#     analyses' (switch-back relabels), applied at load as before.
# (3) V3 (D94, histgb, held-out): bins of each base's drift |corrected - stored N-0 minimum| with the edges of
#     data/sts_n0drift_check.json; pinned-input rate = that file's per-split missed in the > 1e-3 bin; corrected-input
#     rate = the same from arm F. Holds iff mean(pinned) - mean(corrected) > max(std pinned, std corrected).
#     Reported: ridge, all 4 bins both families and both inputs, a second binning by max per-bus |delta vm0|, and paired
#     per-split differences (missed, escalation, speedup B).
# Output: data/sts_n13_armF_<name>.parquet (+ manifests), data/sts_n13_armF.json + manifest.

NETS = {
    "D94": dict(gate="data/sts_n5_gate_094.json", gate_key=None, labels="data/sts_n2_label_audit.parquet", n_line=173),
    "ILL": dict(gate="data/sts_n10_illinois.json", gate_key=None, labels="data/sts_n10_relabel_illinois200.parquet", n_line=179),
    "C30": dict(gate="data/sts_n11_smallnets.json", gate_key="case30_thermal", labels="data/sts_n11_relabel_case30_thermal.parquet", n_line=41),
    "C24": dict(gate="data/sts_n11_smallnets.json", gate_key="case24_ieee_rts", labels="data/sts_n11_relabel_case24_ieee_rts.parquet", n_line=33),
}
SEEDS = [0, 1, 2, 3, 4]
FAMILIES = ["histgb", "ridge"]
LIMIT = 0.94
BINS = [0.0, 1e-6, 1e-4, 1e-3, 1.0]
BIN_NAMES = ["none (<=1e-6)", "1e-6..1e-4", "1e-4..1e-3", ">1e-3"]
DRIFT = "data/sts_n0drift_check.json"
RULE = "scratch/n13_decision_rule.md"
RULE_SHA = "scratch/n13_decision_rule.sha256"
NPROC = 8


def ms_(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(a.std())


def replay_bases(name):
    spec = c.DATASETS[name]
    out = []
    if spec["kind"] == "case118":
        c.install("pinned", "case118")
        gd.GEN_VM_LO = spec["floor"]
        for w, s in enumerate(spec["seeds"]):
            rep = n2.replay_shard((s, n2.N_TOTAL // len(n2.SHARD_SEEDS), n2.mode_lists()[w]))
            out.extend(rep["scenarios"])
    elif name == "ILL":
        c.install("pinned", "other")
        out, _d, _r, _c = n10r.replay()
    else:
        c.install("pinned", "other")
        n11r.NETWORK = spec["network"]
        n11r.DATASET = spec["file"]
        n11r.BUILD_STATS = spec["stats"]
        out, _d, _r, _c = n11r.replay()
    return out


def corrected_n0(task):
    name, sid, params_json = task
    spec = c.DATASETS[name]
    if spec["kind"] == "case118":
        c.STATE["kind"] = "case118"
        gd.apply_config(n2.CFG)
        net = gd.build_net("case118")
    else:
        c.STATE["kind"] = "other"
        gd.apply_config(nb.cfg_other(spec))
        net = gd.build_net(spec["network"])
    gd.apply_scenario(net, c.params_from_json(params_json))
    ok, vm, info = c.corrected_pf(net)
    return dict(scenario_id=sid, ok=bool(ok), status=info["status"], vm=vm.tolist() if ok else None)


def build_armF(name):
    path = f"data/sts_n13_armF_{name}.parquet"
    spec = c.DATASETS[name]
    if os.path.exists(path):
        return path, json.load(open(f"scratch/n13_armF_{name}_build.json"))
    scen = replay_bases(name)
    tasks = [(name, int(s["scenario_id"]), c.params_jsonable(s["params"])) for s in scen]
    with multiprocessing.Pool(NPROC) as pool:
        res = pool.map(corrected_n0, tasks, chunksize=8)
    df = pd.read_parquet(spec["file"])
    vm_cols = [col for col in df.columns if col.startswith("vm0_")]
    n_bus = len(vm_cols)
    vmap = {}
    fails = []
    for r in res:
        if r["ok"]:
            vmap[r["scenario_id"]] = np.asarray(r["vm"], dtype=np.float64)
        else:
            fails.append(r["scenario_id"])
    sids = df["scenario_id"].to_numpy()
    new_vm = df[vm_cols].to_numpy(np.float64).copy()
    new_min = df["n0_min_vm"].to_numpy(np.float64).copy()
    stored_min = {}
    stored_vec = {}
    for sid in np.unique(sids):
        msk = sids == sid
        stored_min[int(sid)] = float(df.loc[msk, "n0_min_vm"].iloc[0])
        stored_vec[int(sid)] = df.loc[msk, vm_cols].iloc[0].to_numpy(np.float64)
        if int(sid) in vmap:
            v = vmap[int(sid)]
            new_vm[msk, :] = v[:n_bus]
            new_min[msk] = float(np.nanmin(v))
    out = df.copy()
    out[vm_cols] = new_vm.astype(df[vm_cols[0]].dtype)
    out["n0_min_vm"] = new_min.astype(df["n0_min_vm"].dtype)
    same = list(out.columns) == list(df.columns) and all([out[col].dtype == df[col].dtype for col in df.columns])
    out.to_parquet(path, index=False)
    drift = {}
    vecdrift = {}
    for sid in stored_min:
        if sid in vmap:
            drift[sid] = abs(float(np.nanmin(vmap[sid])) - stored_min[sid])
            vecdrift[sid] = float(np.nanmax(np.abs(vmap[sid][:n_bus] - stored_vec[sid])))
    info = dict(name=name, n_bases=len(stored_min), n_correction_failed=len(fails), failed_bases=fails[:50],
                schema_same=bool(same), n_bases_min_changed_gt_1e6=int(sum([1 for s in drift if drift[s] > 1e-6])),
                drift=drift, vecdrift=vecdrift)
    with open(f"scratch/n13_armF_{name}_build.json", "w") as f:
        json.dump(info, f)
    man = sm.build_manifest([path], "scratch/n13_armF.py", [".venv/bin/python", "scratch/n13_armF.py"],
                            [spec["file"], RULE], dict(dataset=name, replaced=["vm0_*", "n0_min_vm"],
                                                       solver="corrected N-0: pinned + N2 switch-back (n13_common.corrected_pf)",
                                                       model_hyperparameters="none (dataset file)"), "")
    man["no_new_solves"] = "FALSE: corrected N-0 solve of every original base"
    sm.write_manifest(man, path)
    return path, info


def gate_json(name):
    g = json.load(open(NETS[name]["gate"]))
    if NETS[name]["gate_key"]:
        g = g["networks"][NETS[name]["gate_key"]]
    return g


def fit_info(gj, seed, fam, held_pt, ms_solver):
    # config and per-row surrogate time of the existing M2 model. N5/N10 store them under "fits"; N11's smallnets
    # file stores only the M2 tag per split ("selections"), so the config is looked up in the unchanged candidate
    # list and t_surr is recovered from the stored held-out speedup B: t_surr = t_solve * (1/speedup_B - solve_share_B).
    # (Code fix, N13 rule 3.)
    if "fits" in gj:
        f = [x for x in gj["fits"] if x["seed"] == seed and x["family"] == fam][0]
        return f["config"], f["ms_surrogate"], f["tag"]
    tag = gj["selections"][str(seed)][fam]["m2"]
    cands = tu.ridge_candidates() if fam == "ridge" else tu.histgb_candidates()
    cfg = tu.find_config(cands, tag)
    ms_surr = ms_solver * (1.0 / held_pt["speedup_B"] - held_pt["solve_share_B"])
    return cfg, ms_surr, tag


def load(path, name):
    df, feature_cols, info = n5.load_relabeled(path, NETS[name]["labels"])
    X, y, groups, _ = ms.build_design_matrix(df, feature_cols)
    is_trafo = df["outaged_type"].to_numpy() == "trafo"
    ek = df["outaged_idx"].to_numpy(np.int64) + np.where(is_trafo, NETS[name]["n_line"], 0)
    return dict(name=name, df=df, X=X, y=y, groups=groups, elem_key=ek, info=info)


def eval_split(d, seed, fam, cfg, tgt, ms_surr, ms_solver):
    splits = ms.make_splits(d["groups"], seed)
    kept = ms.select_features(d["X"], splits["train"])
    te = splits["test"]
    Xte = d["X"][kept].iloc[te].to_numpy(np.float32)
    p_ca, y_ca, p_te = bc.fit_predict(d, seed, fam, cfg, Xte, kept)
    y_te = d["y"][te]
    g = bc.gate_point(p_ca, y_ca, p_te, y_te, tgt)
    n = len(y_te)
    g["speedup_B"] = float(n * ms_solver / (n * ms_surr + g["solve_share_B"] * n * ms_solver))
    q = g["q_hat"]
    certify = (p_te - q) >= LIMIT
    tv = y_te < LIMIT
    sid = d["df"]["scenario_id"].to_numpy()[te]
    return g, certify, tv, sid


def by_bin(certify, tv, sid, drift_map):
    out = []
    dvals = np.array([drift_map.get(int(s), np.nan) for s in sid])
    for i in range(4):
        msk = (dvals > BINS[i]) & (dvals <= BINS[i + 1]) if i > 0 else (dvals <= BINS[1])
        nt = int((tv & msk).sum())
        out.append(dict(bin=BIN_NAMES[i], n_rows=int(msk.sum()), n_true_viol=nt,
                        missed=float((certify & tv & msk).sum() / nt) if nt else None))
    return out


def main():
    t0 = time.time()
    h = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
    if h != open(RULE_SHA).read().split()[0]:
        raise SystemExit("decision rule hash does not verify; stop the whole run")
    ms_solver = mf.load_solve_time()["ms_solver"]
    res = {}
    for name in NETS:
        path, binfo = build_armF(name)
        gj = gate_json(name)
        d_orig = load(c.DATASETS[name]["file"], name)
        d_f = load(path, name)
        per = []
        stopped = None
        for fam in FAMILIES:
            pts = {}
            for p in gj["points"]:
                if p["family"] == fam and p["point"] == "held_out":
                    pts[int(p["seed"])] = p
            for seed in SEEDS:
                p = pts[seed]
                cfg, ms_surr, _tag = fit_info(gj, seed, fam, p, ms_solver)
                go, cert_o, tv_o, sid_o = eval_split(d_orig, seed, fam, cfg, p["target"], ms_surr, ms_solver)
                if go["missed"] != p["missed"]:
                    stopped = dict(seed=seed, family=fam, missed_refit=go["missed"], missed_stored=p["missed"])
                    break
                gf, cert_f, tv_f, sid_f = eval_split(d_f, seed, fam, cfg, p["target"], ms_surr, ms_solver)
                rec = dict(seed=seed, family=fam, target=p["target"], original=dict(missed=go["missed"], escalation=go["escalation"], speedup_B=go["speedup_B"]),
                           corrected_inputs=dict(missed=gf["missed"], escalation=gf["escalation"], speedup_B=gf["speedup_B"]),
                           diff=dict(missed=gf["missed"] - go["missed"], escalation=gf["escalation"] - go["escalation"], speedup_B=gf["speedup_B"] - go["speedup_B"]))
                rec["bins_minimum"] = dict(original=by_bin(cert_o, tv_o, sid_o, {int(k): v for k, v in binfo["drift"].items()}),
                                           corrected=by_bin(cert_f, tv_f, sid_f, {int(k): v for k, v in binfo["drift"].items()}))
                rec["bins_vector"] = dict(original=by_bin(cert_o, tv_o, sid_o, {int(k): v for k, v in binfo["vecdrift"].items()}),
                                          corrected=by_bin(cert_f, tv_f, sid_f, {int(k): v for k, v in binfo["vecdrift"].items()}))
                per.append(rec)
                print(f"armF {name} {fam} seed {seed}: missed {100 * go['missed']:.2f} -> {100 * gf['missed']:.2f}", flush=True)
            if stopped is not None:
                break
        if stopped is not None:
            res[name] = dict(stopped="refit on the original inputs does not reproduce the stored held-out missed rate", detail=stopped,
                             build=dict(n_correction_failed=binfo["n_correction_failed"], schema_same=binfo["schema_same"]))
            print(f"armF {name}: STOPPED {stopped}", flush=True)
            continue
        summ = {}
        for fam in FAMILIES:
            m = [r for r in per if r["family"] == fam]
            s = {}
            for k in ["missed", "escalation", "speedup_B"]:
                s[f"diff_{k}_mean"], s[f"diff_{k}_std"] = ms_([r["diff"][k] for r in m])
                s[f"original_{k}_mean"], s[f"original_{k}_std"] = ms_([r["original"][k] for r in m])
                s[f"corrected_{k}_mean"], s[f"corrected_{k}_std"] = ms_([r["corrected_inputs"][k] for r in m])
            summ[fam] = s
        res[name] = dict(per_split=per, summary=summ, build=dict(n_bases=binfo["n_bases"], n_correction_failed=binfo["n_correction_failed"],
                                                                 schema_same=binfo["schema_same"], n_bases_min_changed_gt_1e6=binfo["n_bases_min_changed_gt_1e6"]))
    # V3 on D94
    v3 = None
    if "summary" in res.get("D94", {}):
        dj = json.load(open(DRIFT))
        pinned = []
        for r in dj["per_split"]:
            if r["family"] == "histgb":
                pinned.append([b for b in r["missed_by_n0_drift"] if b["bin"] == ">1e-3"][0]["missed"])
        corr = []
        consist = []
        for r in res["D94"]["per_split"]:
            if r["family"] == "histgb":
                corr.append([b for b in r["bins_minimum"]["corrected"] if b["bin"] == ">1e-3"][0]["missed"])
                orig_b = [b for b in r["bins_minimum"]["original"] if b["bin"] == ">1e-3"][0]
                dj_b = [b for b in [x for x in dj["per_split"] if x["family"] == "histgb" and x["seed"] == r["seed"]][0]["missed_by_n0_drift"] if b["bin"] == ">1e-3"][0]
                consist.append(dict(seed=r["seed"], n_rows_armF=orig_b["n_rows"], n_rows_drift_file=dj_b["n_rows"],
                                    missed_armF_original=orig_b["missed"], missed_drift_file=dj_b["missed"]))
        pm, ps = ms_(pinned)
        cm_, cs_ = ms_(corr)
        h2 = hashlib.sha256(open(RULE, "rb").read()).hexdigest()
        if h2 != open(RULE_SHA).read().split()[0]:
            raise SystemExit("decision rule hash does not verify; stop the whole run")
        v3 = dict(MISMATCH_DRIVES_DRIFT_GAP=bool(pm - cm_ > max(ps, cs_)), pinned_mean=pm, pinned_std=ps, corrected_mean=cm_,
                  corrected_std=cs_, gap=pm - cm_, STD=max(ps, cs_), pinned_per_split=pinned, corrected_per_split=corr,
                  consistency_with_drift_file=consist,
                  rule="histgb held-out, > 1e-3 drift bin: mean_split(pinned) - mean_split(corrected) > max(std pinned, std corrected)")
        print(f"V3: pinned {100 * pm:.2f}±{100 * ps:.2f} corrected {100 * cm_:.2f}±{100 * cs_:.2f} -> {v3['MISMATCH_DRIVES_DRIFT_GAP']}", flush=True)
    out = dict(part="N13 arm F diagnostic (original bases, corrected inputs only; never replaces paper numbers)",
               decision_rule=RULE, decision_rule_sha256=h, V3=v3, networks=res, bins=BINS, bin_names=BIN_NAMES,
               std_convention="population std (ddof=0) over 5 splits", wall_s=time.time() - t0)
    with open("data/sts_n13_armF.json", "w") as f:
        json.dump(out, f, indent=2, default=float)
    hp = {}
    for name in NETS:
        gj = gate_json(name)
        hp[name] = []
        for fam in FAMILIES:
            for seed in SEEDS:
                p = [x for x in gj["points"] if x["family"] == fam and x["point"] == "held_out" and x["seed"] == seed][0]
                cfg, _ms, tag = fit_info(gj, seed, fam, p, ms_solver)
                hp[name].append(dict(seed=seed, family=fam, tag=tag, config=cfg))
    ins = [RULE, DRIFT] + [NETS[n]["gate"] for n in NETS] + [NETS[n]["labels"] for n in NETS] + [c.DATASETS[n]["file"] for n in NETS]
    man = sm.build_manifest(["data/sts_n13_armF.json"], "scratch/n13_armF.py", [".venv/bin/python", "scratch/n13_armF.py"], sorted(set(ins)),
                            dict(seeds=SEEDS, bins=BINS, model_hyperparameters=hp, note="existing M2 configs and held-out targets, refit (no search)"), "")
    man["no_new_solves"] = "FALSE: corrected N-0 solves of the original bases; model refits"
    sm.write_manifest(man, "data/sts_n13_armF.json")


if __name__ == "__main__":
    main()
