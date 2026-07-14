import sys, os, time, argparse
import numpy as np
import pandas as pd
import pandapower as pp
import pandapower.networks as nw
import pandapower.topology as top

VMIN_LIMIT = 0.94
VMAX_LIMIT = 1.06
GEN_VM_LO = 0.94
STRADDLE_BAND = (0.94, 0.95)
LOADING_CAP = 1.60
COLLAPSE_FLOOR = 0.80

GATE_N0 = True
MAX_REJECT_FACTOR = 200

STRESS_LO, STRESS_HI = 1.05, 1.50
MULT_LO, MULT_HI = 1.00, 1.50
REG_LO, REG_HI = 1.00, 1.50
REG_JITTER = 0.10

PF_LO, PF_HI = 0.80, 1.50

DVM = 0.03
QLIM_LO, QLIM_HI = 0.60, 1.40

P_GEN_OUT = 0.30

N_REGIONS_TARGET = 8

N_BUS = 118


def apply_config(cfg):
    g = globals()
    mapping = dict(stress_lo="STRESS_LO", stress_hi="STRESS_HI",
                   mult_lo="MULT_LO", mult_hi="MULT_HI",
                   reg_lo="REG_LO", reg_hi="REG_HI",
                   pf_lo="PF_LO", pf_hi="PF_HI", dvm="DVM",
                   qlim_lo="QLIM_LO", qlim_hi="QLIM_HI",
                   p_gen_out="P_GEN_OUT", gate_n0="GATE_N0",
                   loading_cap="LOADING_CAP")
    for k, v in cfg.items():
        if k in mapping and v is not None:
            g[mapping[k]] = v


def build_net(network="case118"):
    net = getattr(nw, network)()
    net["_p0"] = net.load.p_mw.values.copy()
    net["_q0"] = net.load.q_mvar.values.copy()
    net["_load_bus"] = net.load.bus.values.copy()
    net["_gen_vm0"] = net.gen.vm_pu.values.copy()
    net["_gen_qmin0"] = net.gen.min_q_mvar.values.copy()
    net["_gen_qmax0"] = net.gen.max_q_mvar.values.copy()
    net["_gen_p0"] = net.gen.p_mw.values.copy()
    net["_base_p_total"] = float(net["_p0"].sum())
    return net


def region_of_load(net):
    from networkx.algorithms.community import greedy_modularity_communities
    g = top.create_nxgraph(net, respect_switches=False)
    comms = list(greedy_modularity_communities(g))
    bus2region = {}
    for r, c in enumerate(comms):
        for b in c:
            bus2region[int(b)] = r
    load_region = np.array([bus2region.get(int(b), 0) for b in net["_load_bus"]])
    return load_region, len(comms)


def branch_list(net):
    b = [("line", int(i)) for i in net.line.index if net.line.at[i, "in_service"]]
    b += [("trafo", int(i)) for i in net.trafo.index if net.trafo.at[i, "in_service"]]
    return b


def draw_gen_vm(gen_vm0, rng, max_redraws=1000):
    out = gen_vm0.copy()
    redraws = np.ones(len(gen_vm0), dtype=np.int64)
    for i in range(len(gen_vm0)):
        v = gen_vm0[i] + rng.uniform(-DVM, DVM)
        while not (GEN_VM_LO <= v <= VMAX_LIMIT):
            redraws[i] += 1
            if redraws[i] > max_redraws:
                raise RuntimeError(
                    f"draw_gen_vm: gen {i} (base vm {gen_vm0[i]:.4f}) could not be sampled into "
                    f"[{GEN_VM_LO}, {VMAX_LIMIT}] within {max_redraws} redraws; never clip silently.")
            v = gen_vm0[i] + rng.uniform(-DVM, DVM)
        out[i] = v
    return out, redraws


def sample_scenario(rng, net, mode, load_region, n_regions, stress="perscenario"):
    if mode not in ("independent", "regional"):
        raise ValueError(
            f"sample_scenario: unknown mode {mode!r}; expected 'independent' or 'regional'. "
            f"The 'mixed' option is expanded per scenario in main(); it must not reach here.")
    nloads = len(net["_p0"])
    if stress == "perscenario":
        hi = rng.uniform(STRESS_LO, STRESS_HI)
        lo_i, hi_i = 1.0, hi
        lo_r, hi_r = 1.0, hi
    else:
        lo_i, hi_i = MULT_LO, MULT_HI
        lo_r, hi_r = REG_LO, REG_HI
    if mode == "regional":
        block = rng.uniform(lo_r, hi_r, size=n_regions)
        jit = rng.uniform(1.0 - REG_JITTER, 1.0 + REG_JITTER, size=nloads)
        mp = block[load_region] * jit
    else:
        mp = rng.uniform(lo_i, hi_i, size=nloads)
    mp = np.clip(mp, 0.5, None)
    agg = float((net["_p0"] * mp).sum()) / net["_base_p_total"]
    if agg > LOADING_CAP:
        mp *= LOADING_CAP / agg
    pf = rng.uniform(PF_LO, PF_HI, size=nloads)
    p_new = net["_p0"] * mp
    q_new = net["_q0"] * mp * pf
    ngen = len(net["_gen_vm0"])
    gen_vm, _ = draw_gen_vm(net["_gen_vm0"], rng)
    qscale = rng.uniform(QLIM_LO, QLIM_HI, size=ngen)
    gen_qmin = net["_gen_qmin0"] * qscale
    gen_qmax = net["_gen_qmax0"] * qscale
    gen_out = -1
    if rng.random() < P_GEN_OUT:
        candidates = [i for i in range(ngen) if not net.gen.iloc[i]["slack"]]
        gen_out = int(rng.choice(candidates))
    return dict(mp=mp, pf=pf, p_new=p_new, q_new=q_new,
                gen_vm=gen_vm, gen_qmin=gen_qmin, gen_qmax=gen_qmax,
                gen_out=gen_out, agg_loading=min(agg, LOADING_CAP))


def apply_scenario(net, params):
    net.load["p_mw"] = params["p_new"]
    net.load["q_mvar"] = params["q_new"]
    net.gen["vm_pu"] = params["gen_vm"]
    net.gen["min_q_mvar"] = params["gen_qmin"]
    net.gen["max_q_mvar"] = params["gen_qmax"]
    net.gen["in_service"] = True
    if params["gen_out"] >= 0:
        net.gen.iat[params["gen_out"], net.gen.columns.get_loc("in_service")] = False


def solve(net, init="dc"):
    try:
        pp.runpp(net, enforce_q_lims=True, init=init, numba=True)
        return True, net.res_bus.vm_pu.values.copy()
    except pp.LoadflowNotConverged:
        return False, None
    except Exception:
        return False, None


def scenario_features(net, params, vm0, n0_conv):
    feat = {}
    n_bus = len(net.bus)
    pbus = np.zeros(n_bus); qbus = np.zeros(n_bus)
    for b, p, q in zip(net["_load_bus"], params["p_new"], params["q_new"]):
        pbus[int(b)] += p; qbus[int(b)] += q
    for i in range(n_bus):
        feat[f"pload_{i}"] = pbus[i]
        feat[f"qload_{i}"] = qbus[i]
    for gi in range(len(net["_gen_vm0"])):
        feat[f"genvm_{gi}"] = params["gen_vm"][gi]
        feat[f"genp_{gi}"] = net["_gen_p0"][gi]
        feat[f"genqmin_{gi}"] = params["gen_qmin"][gi]
        feat[f"genqmax_{gi}"] = params["gen_qmax"][gi]
        feat[f"genon_{gi}"] = 0 if gi == params["gen_out"] else 1
    if n0_conv:
        for i in range(n_bus):
            feat[f"vm0_{i}"] = float(vm0[i])
    else:
        for i in range(n_bus):
            feat[f"vm0_{i}"] = np.nan
    return feat


def solve_n0(net, params):
    apply_scenario(net, params)
    n0_conv, vm0 = solve(net, init="dc")
    n0_min_vm = float(np.nanmin(vm0)) if (n0_conv and vm0 is not None) else np.nan
    return n0_conv, vm0, n0_min_vm


def run_scenario(net, branches, params, scen_id, mode, n0_conv, vm0, n0_min_vm):
    feat = scenario_features(net, params, vm0, n0_conv)

    def make_row(otype, oidx, conv, vm):
        r = dict(scenario_id=scen_id, sampling_mode=mode,
                 outaged_type=otype, outaged_idx=oidx,
                 gen_out=params["gen_out"], agg_loading=params["agg_loading"],
                 n0_converged=n0_conv, n0_min_vm=n0_min_vm, converged=conv)
        if conv and vm is not None:
            mn = float(np.nanmin(vm)); mx = float(np.nanmax(vm))
            amn = int(np.nanargmin(vm))
            r.update(min_vm=mn, max_vm=mx, argmin_bus=amn,
                     violation=bool(mn < VMIN_LIMIT),
                     straddle=bool((not (mn < VMIN_LIMIT)) and STRADDLE_BAND[0] <= mn <= STRADDLE_BAND[1]),
                     deep_collapse=bool(mn < COLLAPSE_FLOOR))
        else:
            r.update(min_vm=np.nan, max_vm=np.nan, argmin_bus=-1,
                     violation=False, straddle=False, deep_collapse=False)
        r.update(feat)
        return r

    rows = [make_row("none", -1, n0_conv, vm0)]
    for etype, idx in branches:
        tbl = net[etype]
        col = tbl.columns.get_loc("in_service")
        tbl.iat[tbl.index.get_loc(idx), col] = False
        conv, vm = solve(net, init="dc")
        tbl.iat[tbl.index.get_loc(idx), col] = True
        rows.append(make_row(etype, idx, conv, vm))
    return rows


_KEEP_COLS = {"scenario_id", "sampling_mode", "outaged_type", "outaged_idx",
              "gen_out", "n0_converged", "converged", "argmin_bus",
              "violation", "straddle", "deep_collapse"}

_FLOAT64_COLS = {"min_vm", "max_vm", "n0_min_vm"} | {f"vm0_{i}" for i in range(200)}


def rows_to_frame(rows):
    df = pd.DataFrame(rows)
    float_cols = [c for c in df.columns
                  if c not in _KEEP_COLS and c not in _FLOAT64_COLS
                  and df[c].dtype == "float64"]
    df[float_cols] = df[float_cols].astype("float32")
    return df


FLUSH_EVERY = 25


def worker(args):
    seed0, n_scen, mode, mode_list, stress, shard_path, cfg = args
    if cfg:
        apply_config(cfg)
    net = build_net((cfg or {}).get("network") or "case118")
    load_region, n_regions = region_of_load(net)
    branches = branch_list(net)
    rng = np.random.default_rng(seed0)
    buf = []
    frames = []
    n_reject = 0
    accepted = 0
    max_rejects = n_scen * MAX_REJECT_FACTOR
    while accepted < n_scen and n_reject <= max_rejects:
        this_mode = mode_list[accepted] if mode_list is not None else mode
        params = sample_scenario(rng, net, this_mode, load_region, n_regions, stress=stress)
        n0_conv, vm0, n0_min_vm = solve_n0(net, params)
        if GATE_N0 and (not n0_conv or n0_min_vm < VMIN_LIMIT):
            n_reject += 1
            continue
        scen_id = seed0 * 1_000_000 + accepted
        buf.extend(run_scenario(net, branches, params, scen_id, this_mode,
                                n0_conv, vm0, n0_min_vm))
        accepted += 1
        if accepted % FLUSH_EVERY == 0:
            frames.append(rows_to_frame(buf)); buf = []
    if buf:
        frames.append(rows_to_frame(buf))
    df = pd.concat(frames, ignore_index=True) if frames else rows_to_frame([])
    if shard_path is not None:
        df.to_parquet(shard_path, index=False)
        with open(shard_path + ".reject", "w") as f:
            f.write(f"{accepted},{n_reject}")
        del df, frames
        return shard_path
    df.attrs["accepted"] = accepted
    df.attrs["n_reject"] = n_reject
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50, help="number of scenarios")
    ap.add_argument("--network", type=str, default="case118",
                    help="pandapower.networks name (default case118; feature block adapts to bus count)")
    ap.add_argument("--mode", choices=["independent", "regional", "mixed"], default="mixed")
    ap.add_argument("--stress", choices=["perscenario", "fixed"], default="fixed")
    ap.add_argument("--out", type=str, default="data/dataset.parquet")
    ap.add_argument("--nproc", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--stress-lo", type=float, default=None)
    ap.add_argument("--stress-hi", type=float, default=None)
    ap.add_argument("--mult-lo", type=float, default=None)
    ap.add_argument("--mult-hi", type=float, default=1.12)
    ap.add_argument("--reg-lo", type=float, default=None)
    ap.add_argument("--reg-hi", type=float, default=None)
    ap.add_argument("--pf-lo", type=float, default=None)
    ap.add_argument("--pf-hi", type=float, default=None)
    ap.add_argument("--dvm", type=float, default=None)
    ap.add_argument("--qlim-lo", type=float, default=None)
    ap.add_argument("--qlim-hi", type=float, default=None)
    ap.add_argument("--p-gen-out", type=float, default=None)
    ap.add_argument("--no-gate", action="store_true", help="disable N-0 feasibility gate")
    args = ap.parse_args()

    cfg = dict(stress_lo=args.stress_lo, stress_hi=args.stress_hi,
               mult_lo=args.mult_lo, mult_hi=args.mult_hi,
               reg_lo=args.reg_lo, reg_hi=args.reg_hi,
               pf_lo=args.pf_lo, pf_hi=args.pf_hi, dvm=args.dvm,
               qlim_lo=args.qlim_lo, qlim_hi=args.qlim_hi,
               p_gen_out=args.p_gen_out,
               gate_n0=(False if args.no_gate else None),
               network=args.network)
    apply_config(cfg)

    t0 = time.time()
    mode_list = None
    if args.mode == "mixed":
        modes = np.array(["independent", "regional"])
        mode_list = list(modes[(np.arange(args.n) % 2)])

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    accepted_total = 0; reject_total = 0
    if args.nproc == 1:
        df = worker((args.seed, args.n, args.mode, mode_list, args.stress, None, cfg))
        accepted_total = int(df.attrs.get("accepted", df.scenario_id.nunique()))
        reject_total = int(df.attrs.get("n_reject", 0))
    else:
        import multiprocessing as mp
        import glob
        shard_dir = os.path.join(os.path.dirname(args.out) or ".", "_shards")
        os.makedirs(shard_dir, exist_ok=True)
        for old in glob.glob(os.path.join(shard_dir, "shard_*.parquet*")):
            os.remove(old)
        per = [args.n // args.nproc] * args.nproc
        for i in range(args.n % args.nproc):
            per[i] += 1
        tasks = []
        off = 0
        for w, cnt in enumerate(per):
            sub_ml = mode_list[off:off+cnt] if mode_list is not None else None
            shard = os.path.join(shard_dir, f"shard_{args.seed + w}.parquet")
            tasks.append((args.seed + w, cnt, args.mode, sub_ml, args.stress, shard, cfg))
            off += cnt
        with mp.Pool(args.nproc, maxtasksperchild=1) as pool:
            shard_paths = pool.map(worker, tasks)
        parts = []
        for p in shard_paths:
            parts.append(pd.read_parquet(p))
            rp = p + ".reject"
            if os.path.exists(rp):
                a, r = open(rp).read().split(","); accepted_total += int(a); reject_total += int(r)
                os.remove(rp)
            os.remove(p)
        df = pd.concat(parts, ignore_index=True)
        try:
            os.rmdir(shard_dir)
        except OSError:
            pass
    dt = time.time() - t0

    df.to_parquet(args.out, index=False)

    n_scen = df.scenario_id.nunique()
    conv = df[df.converged]
    n1 = conv[conv.outaged_type != "none"]
    gate_pass = accepted_total / (accepted_total + reject_total) * 100 if (accepted_total + reject_total) else float("nan")
    print(f"time_s={dt:.1f} scenarios_accepted={n_scen} rows={len(df)} cols={df.shape[1]}")
    print(f"N0_gate: accepted={accepted_total} rejected={reject_total} pass_rate={gate_pass:.2f}%")
    print(f"nonconverged={int((~df.converged).sum())} ({100*(~df.converged).mean():.2f}%)")
    print(f"N1 violations={int(n1.violation.sum())} ({100*n1.violation.mean():.1f}% of conv N-1) "
          f"straddle={int(n1.straddle.sum())} deep_collapse={int(n1.deep_collapse.sum())}")
    vc = n1[n1.violation].argmin_bus.value_counts()
    top2 = vc.iloc[:2].sum() / vc.sum() * 100 if vc.size >= 2 else float("nan")
    print(f"distinct argmin buses (N-1 viol): {vc.size} top2={top2:.1f}%; top: {list(vc.head(5).items())}")
    print(f"min_vm dtype={df.min_vm.dtype} range=[{conv.min_vm.min():.3f},{conv.min_vm.max():.3f}]")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
