import numpy as np
import pandapower as pp
import pandapower.networks as nw
from scipy.sparse.linalg import splu

N_BUS = 118
LIMIT = 0.94
COMP_SIGN = 1.0
PI_EXPONENT_2N = 2



_TEMPLATE = None


def get_template():
    global _TEMPLATE
    if _TEMPLATE is None:
        net = nw.case118()
        net.load = net.load.iloc[0:0]
        for i in range(N_BUS):
            pp.create_load(net, bus=i, p_mw=0.0, q_mvar=0.0)
        _TEMPLATE = net
    return _TEMPLATE


def apply_row(net, row):
    net.load["p_mw"] = [float(row[f"pload_{i}"]) for i in range(N_BUS)]
    net.load["q_mvar"] = [float(row[f"qload_{i}"]) for i in range(N_BUS)]
    ng = len(net.gen)
    net.gen["vm_pu"] = [float(row[f"genvm_{g}"]) for g in range(ng)]
    net.gen["min_q_mvar"] = [float(row[f"genqmin_{g}"]) for g in range(ng)]
    net.gen["max_q_mvar"] = [float(row[f"genqmax_{g}"]) for g in range(ng)]
    net.gen["in_service"] = [bool(row[f"genon_{g}"]) for g in range(ng)]
    return net


def rebuild_net(row):
    return apply_row(get_template(), row)


def solve_base(net):
    try:
        pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)
        return True
    except Exception:
        return False



def sensitivity_setup(net):
    internal = net._ppc["internal"]
    J = internal["J"].tocsc()
    base_mva = float(internal["baseMVA"])
    pv = np.asarray(internal["pv"], dtype=int)
    pq = np.asarray(internal["pq"], dtype=int)
    npv, npq = len(pv), len(pq)
    pvpq = np.concatenate([pv, pq])

    p_row = {}
    for k, b in enumerate(pvpq):
        p_row[int(b)] = k
    q_row = {}
    for k, b in enumerate(pq):
        q_row[int(b)] = npv + npq + k

    buslu = net._pd2ppc_lookups["bus"]
    return dict(lu=splu(J), base_mva=base_mva, buslu=buslu,
                p_row=p_row, q_row=q_row, vm_slice=(npv + npq, npv + 2 * npq),
                pq=pq, n=npv + 2 * npq)


def inject_dv(setup, terminals):
    rhs = np.zeros(setup["n"], dtype=np.float64)
    base = setup["base_mva"]
    buslu = setup["buslu"]
    for pp_bus, dP_mw, dQ_mvar in terminals:
        ib = int(buslu[pp_bus])
        pr = setup["p_row"].get(ib, -1)
        if pr >= 0:
            rhs[pr] += COMP_SIGN * dP_mw / base
        qr = setup["q_row"].get(ib, -1)
        if qr >= 0:
            rhs[qr] += COMP_SIGN * dQ_mvar / base
    x = setup["lu"].solve(rhs)
    lo, hi = setup["vm_slice"]
    dvm_pq = x[lo:hi]
    dV = np.zeros(N_BUS, dtype=np.float64)
    dV[setup["pq"]] = dvm_pq
    return dV



def branch_terminals(net):
    out = []
    line, resl = net.line, net.res_line
    for idx in line.index:
        if not bool(line.at[idx, "in_service"]):
            continue
        f = int(line.at[idx, "from_bus"])
        t = int(line.at[idx, "to_bus"])
        out.append(dict(type="line", idx=int(idx), terminals=[
            (f, float(resl.at[idx, "p_from_mw"]), float(resl.at[idx, "q_from_mvar"])),
            (t, float(resl.at[idx, "p_to_mw"]), float(resl.at[idx, "q_to_mvar"]))]))
    trafo, rest = net.trafo, net.res_trafo
    for idx in trafo.index:
        if not bool(trafo.at[idx, "in_service"]):
            continue
        hv = int(trafo.at[idx, "hv_bus"])
        lv = int(trafo.at[idx, "lv_bus"])
        out.append(dict(type="trafo", idx=int(idx), terminals=[
            (hv, float(rest.at[idx, "p_hv_mw"]), float(rest.at[idx, "q_hv_mvar"])),
            (lv, float(rest.at[idx, "p_lv_mw"]), float(rest.at[idx, "q_lv_mvar"]))]))
    return out



def voltage_pi(pred_vm):
    deficit = np.maximum(0.0, (LIMIT - pred_vm) / LIMIT)
    return float(np.sum(deficit ** PI_EXPONENT_2N) / PI_EXPONENT_2N)



def screen_scenario(row_n0):
    net = rebuild_net(row_n0)
    if not solve_base(net):
        return None, None
    setup = sensitivity_setup(net)
    vm0 = net.res_bus.vm_pu.values.astype(np.float64)

    records = []
    for br in branch_terminals(net):
        dV = inject_dv(setup, br["terminals"])
        pred_vm = vm0 + dV
        records.append(dict(outaged_type=br["type"], outaged_idx=br["idx"],
                            pred_min_vm=float(pred_vm.min()), pi=voltage_pi(pred_vm)))
    base_info = base_diagnostics(net)
    return records, base_info


def base_bus_types(net):
    internal = net._ppc["internal"]
    pv = set(int(b) for b in internal["pv"])
    ref = set(int(b) for b in internal["ref"])
    buslu = net._pd2ppc_lookups["bus"]
    out = np.zeros(N_BUS, dtype=np.int8)
    for b in range(N_BUS):
        ib = int(buslu[b])
        if ib in ref:
            out[b] = 2
        elif ib in pv:
            out[b] = 1
    return out


def base_diagnostics(net):
    q = net.res_gen.q_mvar.values
    qmin = net.gen.min_q_mvar.values
    qmax = net.gen.max_q_mvar.values
    tol = 1e-3
    at_lim = (np.abs(q - qmin) < tol) | (np.abs(q - qmax) < tol)
    internal = net._ppc["internal"]
    pv = set(int(b) for b in internal["pv"])
    pq = set(int(b) for b in internal["pq"])
    ref = set(int(b) for b in internal["ref"])
    buslu = net._pd2ppc_lookups["bus"]

    def live_type(pp_bus):
        ib = int(buslu[pp_bus])
        if ib in pv:
            return "PV"
        if ib in pq:
            return "PQ"
        if ib in ref:
            return "ref"
        return "?"

    return dict(n_gen_at_qlim=int(at_lim.sum()), n_gen=int(len(q)),
                type_75=live_type(75), type_52=live_type(52), type_106=live_type(106))



def _pilot():
    import time
    import pandas as pd

    df = pd.read_parquet("data/dataset.parquet")
    sids = list(dict.fromkeys(df["scenario_id"].tolist()))[:12]
    print(f"pilot: {len(sids)} scenarios")

    vm0_err = []
    pred_all, true_all = [], []
    diags = []
    t_setup, t_apply, n_apply = 0.0, 0.0, 0
    for sid in sids:
        sdf = df[df.scenario_id == sid]
        n0 = sdf[sdf.outaged_type == "none"].iloc[0]
        net = rebuild_net(n0)
        if not solve_base(net):
            print(f"  scenario {int(sid)}: base did not converge (unexpected)")
            continue
        vm0 = net.res_bus.vm_pu.values.astype(np.float64)
        stored = np.array([float(n0[f"vm0_{i}"]) for i in range(N_BUS)])
        vm0_err.append(float(np.nanmax(np.abs(vm0 - stored))))

        t0 = time.perf_counter()
        setup = sensitivity_setup(net)
        t_setup += time.perf_counter() - t0
        terms = branch_terminals(net)
        conv = sdf[(sdf.outaged_type != "none") & (sdf.converged)]
        truth = {(r.outaged_type, int(r.outaged_idx)): float(r.min_vm) for r in conv.itertuples()}
        for br in terms:
            t0 = time.perf_counter()
            dV = inject_dv(setup, br["terminals"])
            pred_min = float((vm0 + dV).min())
            t_apply += time.perf_counter() - t0
            n_apply += 1
            key = (br["type"], br["idx"])
            if key in truth:
                pred_all.append(pred_min)
                true_all.append(truth[key])
        diags.append(base_diagnostics(net))

    vm0_err = np.array(vm0_err)
    pred_all = np.array(pred_all)
    true_all = np.array(true_all)
    err = pred_all - true_all
    corr = float(np.corrcoef(pred_all, true_all)[0, 1])
    print(f"  vm0 reproduction: max|err| over scenarios = {vm0_err.max():.2e}")
    print(f"  pred vs true min_vm (n={len(pred_all)}): corr={corr:+.3f} "
          f"MAE={np.mean(np.abs(err)):.4f} mean_signed_err={err.mean():+.4f} "
          f"(positive = over-prediction, hides violations)")
    frac_over = float((err > 0).mean())
    print(f"  over-prediction share = {frac_over*100:.1f}% of cases")
    print(f"  timing: setup {t_setup/len(sids)*1000:.2f} ms/scenario "
          f"(/186 = {t_setup/len(sids)/186*1000:.4f} ms/contingency); "
          f"apply {t_apply/n_apply*1000:.4f} ms/contingency")
    print(f"  base bus types (per scenario): 75={[d['type_75'] for d in diags]}")
    print(f"                                 52={[d['type_52'] for d in diags]}")
    print(f"                                 106={[d['type_106'] for d in diags]}")
    print(f"  gens at Q-limit at base: {[d['n_gen_at_qlim'] for d in diags]} of "
          f"{diags[0]['n_gen'] if diags else '?'}")


if __name__ == "__main__":
    _pilot()
