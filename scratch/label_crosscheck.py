import os
import sys
import json
import time
import hashlib
import platform
import numpy as np
import pandas as pd
import pandapower as pp
from scipy.stats import beta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import generate_dataset as gd
import manifest as mf
import sts_n2_label_audit as n2

# Label cross-check for the N2 audit with an INDEPENDENT method.
# N2 corrected labels with an outer loop around pandapower (PV->PQ by pandapower, PQ->PV by the loop).
# Here: a from-scratch AC power flow (own Newton iteration) that solves the generator reactive-limit
# rule SIMULTANEOUSLY as a complementarity condition, one equation per PV bus:
#     F = Qg - mid(Qmin, Qmax, Qg - c * (Vm - Vset)) = 0
# interior -> Vm = Vset (voltage control); at Qmax -> Vm <= Vset; at Qmin -> Vm >= Vset.
# A generator at a limit returns to voltage control whenever the voltage condition demands it.
# Solved by semismooth Newton with backtracking. Shared with pandapower: only the network model
# (internal bus/gen data and the bus admittance matrix after pandapower's element conversion).
# Validation: with the limit rule replaced by Vm = Vset, the solver must reproduce pandapower's
# enforce_q_lims=False solution.

N2_PARQUET = "data/sts_n2_label_audit.parquet"
OUT = "data/sts_label_crosscheck.json"
OUT_ROWS = "data/sts_label_crosscheck_rows.parquet"
LIMIT = 0.94
N_PER_STRATUM = 100
SAMPLE_SEED = 20260927
C_SCALE = 1.0
TOL = 1e-10
MAX_IT = 60
WORST = (101000025, "line", 78)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def network_model(net):
    # internal pandapower model after an unconstrained (no Q-limit) solve; returns arrays in p.u.
    pp.runpp(net, enforce_q_lims=False, init="dc", numba=True)
    ppci = net._ppc["internal"]
    base = float(ppci["baseMVA"])
    bus = ppci["bus"]
    gen = ppci["gen"]
    nb = bus.shape[0]
    ref = np.asarray(ppci["ref"], dtype=int)
    on = gen[:, 7] > 0
    gbus = gen[on, 0].astype(int)
    pg = np.zeros(nb)
    qmax = np.zeros(nb)
    qmin = np.zeros(nb)
    vset = np.full(nb, np.nan)
    np.add.at(pg, gbus, gen[on, 1] / base)
    np.add.at(qmax, gbus, gen[on, 3] / base)
    np.add.at(qmin, gbus, gen[on, 4] / base)
    vset[gbus] = gen[on, 5]
    pv = np.array(sorted(set(gbus.tolist()) - set(ref.tolist())), dtype=int)
    return dict(Y=ppci["Ybus"].toarray(), nb=nb, ref=ref, pv=pv,
                pspec=pg - bus[:, 2] / base, qd=bus[:, 3] / base,
                qmin=qmin, qmax=qmax, vset=vset, V0=ppci["V"].copy(),
                pp_nolim_min=float(np.abs(ppci["V"]).min()))


def residual(m, x, nr, mode):
    nb = m["nb"]
    va = np.zeros(nb)
    vm = np.abs(m["V0"]).copy()
    va[m["ref"]] = np.angle(m["V0"][m["ref"]])
    n = len(nr)
    va[nr] = x[:n]
    vm[nr] = x[n:2 * n]
    qg = x[2 * n:]
    V = vm * np.exp(1j * va)
    I = m["Y"] @ V
    S = V * np.conj(I)
    qspec = -m["qd"].copy()
    qspec[m["pv"]] += qg
    fp = S.real[nr] - m["pspec"][nr]
    fq = S.imag[nr] - qspec[nr]
    dv = vm[m["pv"]] - m["vset"][m["pv"]]
    if mode == "pv":
        fc = dv
        state = np.zeros(len(qg), dtype=int)
    else:
        z = qg - C_SCALE * dv
        lo = m["qmin"][m["pv"]]
        hi = m["qmax"][m["pv"]]
        mid = np.minimum(np.maximum(z, lo), hi)
        fc = qg - mid
        state = np.where(z >= hi, 1, np.where(z <= lo, -1, 0))
    return np.concatenate([fp, fq, fc]), V, I, vm, state


def jacobian(m, V, I, nr, state, mode):
    Y = m["Y"]
    Vn = V / np.abs(V)
    dS_dVm = np.diag(V) @ np.conj(Y @ np.diag(Vn)) + np.conj(np.diag(I)) @ np.diag(Vn)
    dS_dVa = 1j * np.diag(V) @ np.conj(np.diag(I) - Y @ np.diag(V))
    n = len(nr)
    npv = len(m["pv"])
    J = np.zeros((2 * n + npv, 2 * n + npv))
    J[:n, :n] = dS_dVa[np.ix_(nr, nr)].real
    J[:n, n:2 * n] = dS_dVm[np.ix_(nr, nr)].real
    J[n:2 * n, :n] = dS_dVa[np.ix_(nr, nr)].imag
    J[n:2 * n, n:2 * n] = dS_dVm[np.ix_(nr, nr)].imag
    pos = {b: i for i, b in enumerate(nr)}
    for k, b in enumerate(m["pv"]):
        J[n + pos[b], 2 * n + k] = -1.0
        if mode == "pv" or state[k] == 0:
            J[2 * n + k, n + pos[b]] = 1.0 if mode == "pv" else C_SCALE
        else:
            J[2 * n + k, 2 * n + k] = 1.0
    return J


def solve(m, mode):
    nb = m["nb"]
    nr = np.array([b for b in range(nb) if b not in set(m["ref"].tolist())], dtype=int)
    V0 = m["V0"]
    S0 = V0 * np.conj(m["Y"] @ V0)
    qg0 = S0.imag[m["pv"]] + m["qd"][m["pv"]]
    x = np.concatenate([np.angle(V0[nr]), np.abs(V0[nr]), qg0])
    for it in range(1, MAX_IT + 1):
        F, V, I, vm, state = residual(m, x, nr, mode)
        nf = float(np.max(np.abs(F)))
        if nf < TOL:
            return dict(converged=True, it=it, vm=vm, state=state, qg=x[2 * len(nr):], resid=nf)
        J = jacobian(m, V, I, nr, state, mode)
        try:
            dx = np.linalg.solve(J, -F)
        except np.linalg.LinAlgError:
            return dict(converged=False, it=it, vm=vm, state=state, qg=None, resid=nf)
        t = 1.0
        f0 = float(F @ F)
        while t > 1e-6:
            F1 = residual(m, x + t * dx, nr, mode)[0]
            if float(F1 @ F1) <= (1 - 1e-4 * t) * f0:
                break
            t *= 0.5
        x = x + t * dx
    F, V, I, vm, state = residual(m, x, nr, mode)
    return dict(converged=False, it=MAX_IT, vm=vm, state=state, qg=None, resid=float(np.max(np.abs(F))))


def consistency(m, res):
    # every PV bus either holds Vset inside its limits, or sits at a limit on the correct side
    pv = m["pv"]
    vm = res["vm"][pv]
    vs = m["vset"][pv]
    qg = res["qg"]
    lo = m["qmin"][pv]
    hi = m["qmax"][pv]
    in_lim = (qg >= lo - 1e-8) & (qg <= hi + 1e-8)
    at_hi = np.abs(qg - hi) < 1e-8
    at_lo = np.abs(qg - lo) < 1e-8
    ok_int = (~at_hi) & (~at_lo) & (np.abs(vm - vs) < 1e-7)
    ok_hi = at_hi & (vm <= vs + 1e-7)
    ok_lo = at_lo & (vm >= vs - 1e-7)
    return bool(np.all(in_lim & (ok_int | ok_hi | ok_lo))), int((at_hi | at_lo).sum())


def clopper_pearson(k, n):
    if n == 0:
        return [float("nan"), float("nan")]
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return [lo, hi]


def main():
    t0 = time.time()
    a = pd.read_parquet(N2_PARQUET)
    a = a[a.outaged_type != "none"]
    rng = np.random.default_rng(SAMPLE_SEED)
    v2s = a[a.flip_viol_to_safe.astype(bool)]
    s2v = a[a.flip_safe_to_viol.astype(bool)]
    pick_a = v2s.iloc[np.sort(rng.choice(len(v2s), N_PER_STRATUM, replace=False))].assign(stratum="viol_to_safe")
    pick_b = s2v.iloc[np.sort(rng.choice(len(s2v), N_PER_STRATUM, replace=False))].assign(stratum="safe_to_viol")
    sample = pd.concat([pick_a, pick_b], ignore_index=True)
    w = a[(a.scenario_id == WORST[0]) & (a.outaged_type == WORST[1]) & (a.outaged_idx == WORST[2])].assign(stratum="named_worst_case")
    rows = pd.concat([sample, w], ignore_index=True)

    # replay the committed generator RNG for the shards we need (exact; see scripts/sts_n2_label_audit.py)
    gd.apply_config(n2.CFG)
    mlists = n2.mode_lists()
    need = sorted(set((rows.scenario_id // 1_000_000).astype(int).tolist()))
    scen_params = {}
    for s0 in need:
        w_idx = n2.SHARD_SEEDS.index(s0)
        rep = n2.replay_shard((s0, n2.N_TOTAL // len(n2.SHARD_SEEDS), mlists[w_idx]))
        for sc in rep["scenarios"]:
            scen_params[sc["scenario_id"]] = sc["params"]

    out_rows = []
    pv_check = []
    for _, r in rows.iterrows():
        net = gd.build_net("case118")
        gd.apply_scenario(net, scen_params[int(r.scenario_id)])
        net[r.outaged_type].at[int(r.outaged_idx), "in_service"] = False
        rec = dict(scenario_id=int(r.scenario_id), outaged_type=r.outaged_type, outaged_idx=int(r.outaged_idx),
                   stratum=r.stratum, stored_min_vm=float(r.stored_min_vm), n2_min_vm=float(r.corrected_min_vm),
                   stored_violation=bool(r.stored_violation), n2_violation=bool(r.corrected_violation))
        try:
            m = network_model(net)
        except Exception:
            rec.update(model_ok=False)
            out_rows.append(rec)
            continue
        v = solve(m, "pv")
        pv_check.append(abs(float(v["vm"].min()) - m["pp_nolim_min"]) if v["converged"] else np.nan)
        res = solve(m, "cc")
        rec.update(model_ok=True, pv_mode_converged=v["converged"],
                   pv_mode_minvm_diff_vs_pandapower=pv_check[-1],
                   indep_converged=res["converged"], indep_iterations=res["it"], indep_residual=res["resid"])
        if res["converged"]:
            ok, n_lim = consistency(m, res)
            mv = float(res["vm"].min())
            rec.update(indep_min_vm=mv, indep_violation=bool(mv < LIMIT), indep_consistent=ok,
                       indep_n_at_limit=n_lim, indep_minus_n2=mv - float(r.corrected_min_vm))
        out_rows.append(rec)

    df = pd.DataFrame(out_rows)
    df.to_parquet(OUT_ROWS, index=False)

    def agree(sub):
        s = sub[sub.indep_converged.fillna(False).astype(bool)]
        n = len(s)
        k_orig = int((s.indep_violation == s.stored_violation).sum())
        k_n2 = int((s.indep_violation == s.n2_violation).sum())
        return dict(n_rows=int(len(sub)), n_converged=n,
                    agree_with_original=k_orig, agree_with_original_share=k_orig / n if n else float("nan"),
                    agree_with_original_ci95=clopper_pearson(k_orig, n),
                    agree_with_n2=k_n2, agree_with_n2_share=k_n2 / n if n else float("nan"),
                    agree_with_n2_ci95=clopper_pearson(k_n2, n),
                    n_consistent_state=int(s.indep_consistent.sum()),
                    median_abs_minvm_diff_vs_n2=float(np.median(np.abs(s.indep_minus_n2))) if n else float("nan"),
                    max_abs_minvm_diff_vs_n2=float(np.max(np.abs(s.indep_minus_n2))) if n else float("nan"))

    main_sample = df[df.stratum != "named_worst_case"]
    summary = dict(
        viol_to_safe=agree(df[df.stratum == "viol_to_safe"]),
        safe_to_viol=agree(df[df.stratum == "safe_to_viol"]),
        pooled_200_unweighted=agree(main_sample))
    # population-weighted agreement (strata weighted by their size in N2)
    wts = dict(viol_to_safe=len(v2s), safe_to_viol=len(s2v))
    tot = sum(wts.values())
    summary["population_weighted_agree_with_n2_share"] = sum(
        wts[k] / tot * summary[k]["agree_with_n2_share"] for k in wts)
    wc = df[df.stratum == "named_worst_case"].to_dict("records")
    out = dict(
        question="Do N2's flipped labels hold under an independent solver that lets a limited generator return to voltage control?",
        method="own semismooth-Newton AC power flow with a per-PV-bus complementarity condition (see script header); "
               "shared with pandapower: internal network model and Ybus only",
        sample=dict(population_viol_to_safe=len(v2s), population_safe_to_viol=len(s2v),
                    n_per_stratum=N_PER_STRATUM, sample_seed=SAMPLE_SEED),
        validation=dict(pv_mode_max_abs_minvm_diff_vs_pandapower_nolimits=float(np.nanmax(pv_check)),
                        rows_model_ok=int(df.model_ok.sum()),
                        rows_indep_converged=int(df.indep_converged.fillna(False).astype(bool).sum())),
        summary=summary,
        named_worst_case=wc,
        interval="Clopper-Pearson exact 95%",
        wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, default=float)
    man = dict(artifacts=[OUT, OUT_ROWS], generating_script="scratch/label_crosscheck.py",
               regeneration_argv=[".venv/bin/python", "scratch/label_crosscheck.py"],
               script_sha256=sha256_of("scratch/label_crosscheck.py"),
               inputs={N2_PARQUET: sha256_of(N2_PARQUET), "scripts/sts_n2_label_audit.py": sha256_of("scripts/sts_n2_label_audit.py"),
                       "feasibility/generate_dataset.py": sha256_of("feasibility/generate_dataset.py")},
               parameters=dict(limit=LIMIT, n_per_stratum=N_PER_STRATUM, sample_seed=SAMPLE_SEED, c_scale=C_SCALE,
                               tol=TOL, max_it=MAX_IT, generator_config=n2.CFG, shard_seeds=n2.SHARD_SEEDS),
               network_model_solve=dict(enforce_q_lims=False, init="dc", numba=True, purpose="build internal model + start point only"),
               packages={p: mf.pkg_version(p) for p in mf.PACKAGES}, python=platform.python_version(),
               output_sha256={OUT: sha256_of(OUT), OUT_ROWS: sha256_of(OUT_ROWS)},
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(OUT.replace(".json", ".manifest.json"), "w") as f:
        json.dump(man, f, indent=2)
    print(json.dumps(dict(validation=out["validation"], summary=summary, worst=wc), indent=1, default=float))


if __name__ == "__main__":
    main()
