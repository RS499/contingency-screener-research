import os
import sys
import json
import time
import copy
import multiprocessing
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import n13_common as c
import generate_dataset as gd
import case30_thermal as H
import sts_n2_label_audit as n2
import n10_relabel_illinois as n10r
import n11_relabel_net as n11r
import sts_manifest as sm

# N13 §5 (descriptive): for each original build, replay its draws with the original pinned acceptance (the check-1
# replay functions), and for every draw the original build REJECTED, solve its corrected N-0 state (pinned solve +
# switch-back, n13_common.corrected_pf) and count how many would now pass the corrected check (converged, min >= 0.94,
# and, where the build had a thermal check, loading of the corrected state <= 100%). The corrected solve runs on a deep
# copy of the net, so the replay's own net and acceptance are untouched; the stored n0_min_vm are re-checked exactly.
# (Code fix, N13 rule 3: the first version solved on the replay net itself and kept its log across pool tasks.)
# Output: data/sts_n13_old_rejects.json + manifest.

OUT = "data/sts_n13_old_rejects.json"
NPROC = 8
LOG = []


def wrapped_solve_n0(net, params):
    n0_conv, vm0, n0_min_vm = c.ORIG_SOLVE_N0(net, params)
    thermal = c.STATE["kind"] != "case118"
    load = H.max_loading_pct(net) if n0_conv else np.nan
    if thermal:
        ok, reason = H.n0_feasible(n0_conv, n0_min_vm, load, thermal=True)
    else:
        ok = bool(n0_conv and n0_min_vm >= gd.VMIN_LIMIT)
        reason = "accepted" if ok else ("nonconvergence" if not n0_conv else "voltage")
    if not ok:
        # corrected solve on a deep copy, so the replay's own net (and every later pinned solve) is untouched
        net2 = copy.deepcopy(net)
        cok, vmc, info = c.corrected_pf(net2)
        cmin = float(np.nanmin(vmc)) if cok else np.nan
        cload = H.max_loading_pct(net2) if cok else np.nan
        if thermal:
            cpass, creason = H.n0_feasible(cok, cmin, cload, thermal=True)
        else:
            cpass = bool(cok and cmin >= gd.VMIN_LIMIT)
            creason = "accepted" if cpass else ("correction_failed_or_nonconv" if not cok else "voltage")
        LOG.append(dict(pinned_reason=reason, corrected_pass=bool(cpass), corrected_reason=creason, corrected_status=info["status"],
                        pinned_min=float(n0_min_vm) if n0_conv else np.nan, corrected_min=cmin))
    return n0_conv, vm0, n0_min_vm


def task_fn(task):
    name, seed = task
    spec = c.DATASETS[name]
    LOG.clear()
    if spec["kind"] == "case118":
        c.STATE["kind"] = "case118"
        gd.solve_n0 = wrapped_solve_n0
        gd.GEN_VM_LO = spec["floor"]
        w = spec["seeds"].index(seed)
        rep = n2.replay_shard((seed, n2.N_TOTAL // len(n2.SHARD_SEEDS), n2.mode_lists()[w]))
        scen = rep["scenarios"]
    elif name == "ILL":
        c.STATE["kind"] = "other"
        gd.solve_n0 = wrapped_solve_n0
        scen, draws, rejected, cfg = n10r.replay()
    else:
        c.STATE["kind"] = "other"
        gd.solve_n0 = wrapped_solve_n0
        n11r.NETWORK = spec["network"]
        n11r.DATASET = spec["file"]
        n11r.BUILD_STATS = spec["stats"]
        scen, draws, rejected, cfg = n11r.replay()
    stored = c.stored_n0(spec["file"])
    d = np.abs(np.array([sc["n0_min_vm"] for sc in scen]) - stored.reindex([int(sc["scenario_id"]) for sc in scen]).to_numpy())
    lg = pd.DataFrame(LOG)
    by = lg.groupby("pinned_reason")["corrected_pass"].agg(["sum", "count"]) if len(lg) else None
    return dict(name=name, shard_seed=seed, replay_exact=bool(np.nanmax(d) == 0.0 and not np.isnan(d).any()),
                n_rejected=int(len(lg)), n_would_pass=int(lg["corrected_pass"].sum()) if len(lg) else 0,
                by_pinned_reason={str(k): dict(would_pass=int(by.loc[k, "sum"]), rejected=int(by.loc[k, "count"])) for k in by.index} if by is not None else {},
                corrected_status_counts={str(k): int(v) for k, v in lg["corrected_status"].value_counts().items()} if len(lg) else {})


def main():
    t0 = time.time()
    tasks = []
    for name in c.DATASETS:
        spec = c.DATASETS[name]
        if spec["kind"] == "case118":
            for s in spec["seeds"]:
                tasks.append((name, s))
        else:
            tasks.append((name, 100))
    with multiprocessing.Pool(NPROC) as pool:
        res = pool.map(task_fn, tasks)
    summ = {}
    for name in c.DATASETS:
        rows = [r for r in res if r["name"] == name]
        summ[name] = dict(replay_exact=bool(all([r["replay_exact"] for r in rows])),
                          old_rejected_draws=sum([r["n_rejected"] for r in rows]),
                          would_pass_corrected=sum([r["n_would_pass"] for r in rows]))
        summ[name]["share"] = summ[name]["would_pass_corrected"] / max(summ[name]["old_rejected_draws"], 1)
        print(f"{name}: replay exact {summ[name]['replay_exact']} | old rejected {summ[name]['old_rejected_draws']} | "
              f"would pass corrected {summ[name]['would_pass_corrected']} ({100 * summ[name]['share']:.2f}%)", flush=True)
    out = dict(part="N13 §5: old rejected draws that pass the corrected N-0 check", summary=summ, per_shard=res,
               wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    ins = ["scratch/n13_decision_rule.md"] + [c.DATASETS[n]["file"] for n in c.DATASETS]
    man = sm.build_manifest([OUT], "scratch/n13_old_rejects.py", [".venv/bin/python", "scratch/n13_old_rejects.py"], ins,
                            dict(datasets=c.DATASETS, solver="pinned replay; corrected N-0 (pinned + N2 switch-back) on rejected draws",
                                 model_hyperparameters="none (no model fit)"), "")
    man["no_new_solves"] = "FALSE: replay N-0 solves plus corrected N-0 solves of rejected draws"
    sm.write_manifest(man, OUT)


if __name__ == "__main__":
    main()
