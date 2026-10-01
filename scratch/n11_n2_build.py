import os
import sys
import json
import time
import multiprocessing
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import generate_dataset as gd
import sts_n2_label_audit as n2
import sts_manifest as sm

# N11 Part 1 build (scratch/n11_decision_rule.md §1): N-2 rows on the D94 base cases.
# - Base cases: replayed exactly with scripts/sts_n2_label_audit.py replay_shard (seeds 100-103, 375 each);
#   every replayed N-0 minimum must equal the stored one.
# - Pairs: for every accepted base case, in scenario_id order, 50 unordered pairs of distinct in-service branches
#   drawn uniformly without replacement from all C(186, 2) pairs, one numpy stream seeded 20261001. Drawn once.
# - Each pair: both branches out; pinned_solve, gen_check and corrected_solve from scripts/sts_n2_label_audit.py
#   (the N2 switch-back); state restored after each row. Pinned nonconverged rows are kept and marked.
# 4 workers (one per shard seed); one parquet per shard in SHARD_DIR, finished shards skipped on restart.

DATASET = "data/dataset.parquet"
OUT = "data/sts_n11_n2_rows.parquet"
SHARD_DIR = "scratch/n11_n2_shards"
PAIR_SEED = 20261001
N_PAIRS = 50
NPROC = 4
LIMIT = 0.94


def branch_buses(net, branches):
    out = []
    for etype, idx in branches:
        if etype == "line":
            out.append((int(net.line.at[idx, "from_bus"]), int(net.line.at[idx, "to_bus"])))
        else:
            out.append((int(net.trafo.at[idx, "hv_bus"]), int(net.trafo.at[idx, "lv_bus"])))
    return out


def draw_pairs(scen_ids, n_branch):
    rng = np.random.default_rng(PAIR_SEED)
    iu = np.triu_indices(n_branch, k=1)
    n_all = len(iu[0])
    pairs = {}
    for sid in scen_ids:
        pick = np.sort(rng.choice(n_all, N_PAIRS, replace=False))
        pairs[int(sid)] = [(int(iu[0][p]), int(iu[1][p])) for p in pick]
    return pairs


def solve_shard(task):
    path, scen_list, pairs = task
    if os.path.exists(path):
        return path
    gd.apply_config(n2.CFG)
    recs = []
    for scen in scen_list:
        net = gd.build_net("case118")
        branches = gd.branch_list(net)
        buses = branch_buses(net, branches)
        gd.apply_scenario(net, scen["params"])
        n2.add_pq_sgens(net)
        gen_on = net.gen.in_service.values.copy()
        for a, b in pairs[scen["scenario_id"]]:
            (ta, ia), (tb, ib) = branches[a], branches[b]
            net[ta].at[ia, "in_service"] = False
            net[tb].at[ib, "in_service"] = False
            ok = n2.pinned_solve(net)
            rec = dict(scenario_id=scen["scenario_id"], a_pos=a, b_pos=b, a_type=ta, a_idx=ia, b_type=tb, b_idx=ib,
                       adjacent=bool(len(set(buses[a]) & set(buses[b])) > 0), pinned_converged=ok)
            if ok:
                vm = net.res_bus.vm_pu.values
                rec["pinned_min_vm"] = float(np.nanmin(vm))
                chk = n2.gen_check(net, {}, gen_on)
                n_bad = int((chk["bad_abs"] | chk["bad_inj"]).sum())
                rec["n_inconsistent"] = n_bad
                if n_bad > 0:
                    cs = n2.corrected_solve(net, chk, gen_on)
                    n2.apply_fixed(net, {}, gen_on)
                    rec["corrected_status"] = cs["status"]
                    rec["corrected_min_vm"] = cs["min_vm"]
                    rec["n_outer_iter"] = cs["n_outer"]
                else:
                    rec["corrected_status"] = "not_needed"
                    rec["corrected_min_vm"] = rec["pinned_min_vm"]
                    rec["n_outer_iter"] = 0
            else:
                rec["pinned_min_vm"] = np.nan
                rec["n_inconsistent"] = -1
                rec["corrected_status"] = "pinned_nonconverged"
                rec["corrected_min_vm"] = np.nan
                rec["n_outer_iter"] = 0
            net[ta].at[ia, "in_service"] = True
            net[tb].at[ib, "in_service"] = True
            recs.append(rec)
    pd.DataFrame(recs).to_parquet(path, index=False)
    return path


def main():
    t0 = time.time()
    os.makedirs(SHARD_DIR, exist_ok=True)
    df = pd.read_parquet(DATASET, columns=["scenario_id", "outaged_type", "n0_min_vm"])
    stored_n0 = df[df.outaged_type == "none"].set_index("scenario_id")["n0_min_vm"]
    per = n2.N_TOTAL // len(n2.SHARD_SEEDS)
    ml = n2.mode_lists()
    tasks = [(s, per, ml[w]) for w, s in enumerate(n2.SHARD_SEEDS)]
    with multiprocessing.Pool(NPROC) as pool:
        shards = pool.map(n2.replay_shard, tasks)
    diffs = [abs(sc["n0_min_vm"] - float(stored_n0.loc[sc["scenario_id"]])) for sh in shards for sc in sh["scenarios"]]
    print(f"replay: {len(diffs)} scenarios, max |n0 diff| {max(diffs):.3e} [{time.time() - t0:.0f}s]", flush=True)
    if max(diffs) != 0.0 or len(diffs) != len(stored_n0):
        raise ValueError("replay does not reproduce D94; stop")
    net = gd.build_net("case118")
    n_branch = len(gd.branch_list(net))
    scen_ids = sorted([sc["scenario_id"] for sh in shards for sc in sh["scenarios"]])
    pairs = draw_pairs(scen_ids, n_branch)
    stasks = []
    for sh in shards:
        stasks.append((os.path.join(SHARD_DIR, f"shard_{sh['seed0']}.parquet"), sh["scenarios"],
                       {sc["scenario_id"]: pairs[sc["scenario_id"]] for sc in sh["scenarios"]}))
    with multiprocessing.Pool(NPROC) as pool:
        paths = []
        for i, p in enumerate(pool.imap(solve_shard, stasks)):
            paths.append(p)
            print(f"shard {i + 1}/{len(stasks)} done [{time.time() - t0:.0f}s]", flush=True)
    res = pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True)
    res = res.sort_values(["scenario_id", "a_pos", "b_pos"]).reset_index(drop=True)
    res.to_parquet(OUT, index=False)
    conv = res["pinned_converged"]
    ok = res["corrected_status"].isin(["converged", "not_needed"])
    v = res.loc[ok, "corrected_min_vm"].to_numpy()
    summ = dict(n_rows=int(len(res)), n_pinned_nonconverged=int((~conv).sum()),
                pinned_nonconverged_share=float((~conv).mean()),
                n_corrected_failed_among_converged=int((conv & ~ok).sum()),
                corrected_failed_share_of_converged=float((conv & ~ok).sum() / max(int(conv.sum()), 1)),
                status_counts={str(k): int(c) for k, c in res["corrected_status"].value_counts().items()},
                corrected_violation_rate=float((v < LIMIT).mean()),
                pinned_violation_rate=float((res.loc[conv, "pinned_min_vm"] < LIMIT).mean()),
                adjacent_share=float(res["adjacent"].mean()), n_branch=n_branch)
    with open(OUT.replace(".parquet", ".json"), "w") as f:
        json.dump(dict(part="N11 Part 1 build: N-2 rows on D94 base cases", pair_seed=PAIR_SEED, n_pairs_per_base=N_PAIRS,
                       replay_n0_max_abs_diff=float(max(diffs)), summary=summ, wall_s=time.time() - t0), f, indent=2)
    params = dict(pair_seed=PAIR_SEED, n_pairs_per_base=N_PAIRS, pair_sampling="uniform without replacement over all C(186,2) pairs, per base in scenario_id order",
                  base_replay="scripts/sts_n2_label_audit.py replay_shard, seeds 100-103", nproc=NPROC,
                  switchback_tol_q=n2.TOL_Q, switchback_tol_v=n2.TOL_V, switchback_max_outer=n2.MAX_OUTER,
                  solver="pandapower runpp enforce_q_lims=True init=dc numba=True (pinned) + N2 switch-back",
                  model_hyperparameters="none (no model fit)")
    man = sm.build_manifest([OUT, OUT.replace(".parquet", ".json")], "scratch/n11_n2_build.py",
                            [".venv/bin/python", "scratch/n11_n2_build.py"],
                            [DATASET, "scripts/sts_n2_label_audit.py", "feasibility/generate_dataset.py"], params, "")
    man["no_new_solves"] = "FALSE: pinned + switch-back AC solves of every N-2 pair"
    sm.write_manifest(man, OUT)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
