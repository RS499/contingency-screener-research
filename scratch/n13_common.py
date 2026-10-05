import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import generate_dataset as gd
import case30_thermal as H
import sts_n2_label_audit as n2
import n10_relabel_illinois as n10r

# N13 shared helpers (scratch/n13_decision_rule.md §1). No existing file is edited: the original build and replay
# functions are imported unchanged, and only generate_dataset.solve / generate_dataset.solve_n0 are replaced at run
# time, inside the N13 process, by the wrappers below. Every original loop (sampler, RNG, row construction,
# acceptance) then runs as written.
#   mode "pinned":    the original pinned solve (check 1 replays); every N-0 call is logged.
#   mode "corrected": pinned solve, then, if any generator's Q-limit state contradicts its voltage, the N2
#                     switch-back loop. case118: scripts/sts_n2_label_audit.py corrected_solve (add_pq_sgens /
#                     apply_fixed); other networks: the N10/N11 helper-only version (scratch/n10_relabel_illinois.py).
#                     A failed switch-back returns (False, None): an N-0 draw is then rejected ("N-0 correction
#                     failed"), an outage row is kept with converged = False.
# Logs (per process): one entry per N-0 call (draw number, parameter hash, status, minima, loading) and one audit
# entry per outage solve (draw number, outaged branch, pinned and corrected minima, status, outer iterations).

ORIG_SOLVE = gd.solve
ORIG_SOLVE_N0 = gd.solve_n0
STATE = dict(mode="pinned", kind="case118", phase="n1", draw=-1, n0_log=[], audit=[], n0_info=None, params={})


def params_hash(params):
    h = hashlib.sha256()
    for k in sorted(params.keys()):
        v = np.ascontiguousarray(np.asarray(params[k]))
        h.update(k.encode())
        h.update(str(v.dtype).encode())
        h.update(v.tobytes())
    return h.hexdigest()


def params_jsonable(params):
    out = {}
    for k in params:
        v = np.asarray(params[k])
        if v.ndim == 0:
            out[k] = v.item()
        else:
            out[k] = v.tolist()
    return out


def params_from_json(d):
    out = {}
    for k in d:
        if isinstance(d[k], list):
            out[k] = np.asarray(d[k])
        else:
            out[k] = d[k]
    return out


def outaged_branch(net):
    ln = net.line.index[~net.line.in_service.to_numpy(bool)]
    tr = net.trafo.index[~net.trafo.in_service.to_numpy(bool)]
    out = [("line", int(i)) for i in ln] + [("trafo", int(i)) for i in tr]
    return out


def corrected_pf(net):
    # pinned solve + switch-back; returns (ok, vm, info)
    if STATE["kind"] == "case118":
        if "_sgen_of" not in net:
            n2.add_pq_sgens(net)
    else:
        if "_helper_sgen" not in net:
            n10r.add_helper_sgens(net)
    gen_on = net.gen.in_service.values.copy()
    ok = n2.pinned_solve(net)
    if not ok:
        return False, None, dict(status="pinned_nonconverged", pinned_min=np.nan, corrected_min=np.nan, n_outer=0)
    vm = net.res_bus.vm_pu.values.copy()
    pmin = float(np.nanmin(vm))
    chk = n2.gen_check(net, {}, gen_on)
    if int((chk["bad_abs"] | chk["bad_inj"]).sum()) == 0:
        return True, vm, dict(status="not_needed", pinned_min=pmin, corrected_min=pmin, n_outer=0)
    if STATE["kind"] == "case118":
        cs = n2.corrected_solve(net, chk, gen_on)
        vm_c = net.res_bus.vm_pu.values.copy()
        n2.apply_fixed(net, {}, gen_on)
    else:
        cs = n10r.corrected_solve(net, chk, gen_on)
        vm_c = net.res_bus.vm_pu.values.copy()
        n10r.apply_fixed(net, {}, gen_on)
    if cs["status"] != "converged":
        return False, None, dict(status=cs["status"], pinned_min=pmin, corrected_min=np.nan, n_outer=int(cs["n_outer"]))
    return True, vm_c, dict(status="converged", pinned_min=pmin, corrected_min=float(np.nanmin(vm_c)),
                            n_outer=int(cs["n_outer"]))


def solve_wrapper(net, init="dc"):
    if STATE["mode"] == "pinned":
        ok, vm = ORIG_SOLVE(net, init=init)
        if STATE["phase"] == "n0":
            STATE["n0_info"] = dict(status="pinned_converged" if ok else "pinned_nonconverged",
                                    pinned_min=float(np.nanmin(vm)) if ok else np.nan, n_outer=0)
        return ok, vm
    ok, vm, info = corrected_pf(net)
    if STATE["phase"] == "n0":
        STATE["n0_info"] = info
    else:
        br = outaged_branch(net)
        rec = dict(draw=STATE["draw"], scen=STATE.get("scen", -1), outaged_type=br[0][0] if len(br) == 1 else "multi",
                   outaged_idx=br[0][1] if len(br) == 1 else -1)
        rec.update(info)
        STATE["audit"].append(rec)
    return ok, vm


def solve_n0_wrapper(net, params):
    STATE["draw"] += 1
    STATE["phase"] = "n0"
    STATE["n0_info"] = None
    n0_conv, vm0, n0_min_vm = ORIG_SOLVE_N0(net, params)
    load_pct = H.max_loading_pct(net) if n0_conv else np.nan
    h = params_hash(params)
    info = STATE["n0_info"] or {}
    STATE["n0_log"].append(dict(draw=STATE["draw"], params_hash=h, n0_conv=bool(n0_conv),
                                n0_min_vm=float(n0_min_vm) if n0_conv else np.nan,
                                n0_status=info.get("status"), n0_pinned_min=info.get("pinned_min", np.nan),
                                n0_outer=info.get("n_outer", 0), load_pct=float(load_pct)))
    STATE["params"][h] = params
    STATE["phase"] = "n1"
    return n0_conv, vm0, n0_min_vm


def install(mode, kind):
    STATE.update(mode=mode, kind=kind, phase="n1", draw=-1, n0_log=[], audit=[], n0_info=None, params={})
    gd.solve = solve_wrapper
    gd.solve_n0 = solve_n0_wrapper


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        chunk = f.read(1 << 20)
        while chunk:
            h.update(chunk)
            chunk = f.read(1 << 20)
    return h.hexdigest()


def stored_n0(path):
    df = pd.read_parquet(path, columns=["scenario_id", "outaged_type", "n0_min_vm"])
    return df[df.outaged_type == "none"].set_index("scenario_id")["n0_min_vm"]


# Rule §1 dataset table. case118 builds: feasibility/generate_dataset.py worker per RNG shard (the N3/N5/N9/N11
# drivers call the same worker), committed invocation, GEN_VM_LO = floor. Other networks: netstudy.py phase 1a
# (ILL, C24) and scripts/case30_thermal_build.py (C30), one RNG stream, seed 100, thermal N-0 check.
DATASETS = {
    "D94": dict(kind="case118", file="data/dataset.parquet", floor=0.94, seeds=[100, 101, 102, 103],
                labels="data/sts_n2_label_audit.parquet", tier="A"),
    "ILL": dict(kind="netstudy", network="case_illinois200", file="data/netstudy/case_illinois200/dataset.parquet",
                stats="data/netstudy/case_illinois200/build_stats.json",
                labels="data/sts_n10_relabel_illinois200.parquet", tier="A"),
    "C30": dict(kind="case30", network="case30", file="data/case30_thermal/dataset.parquet",
                stats="data/case30_thermal/h3_build_stats.json",
                labels="data/sts_n11_relabel_case30_thermal.parquet", tier="A"),
    "C24": dict(kind="netstudy", network="case24_ieee_rts", file="data/netstudy/case24_ieee_rts/dataset.parquet",
                stats="data/netstudy/case24_ieee_rts/build_stats.json",
                labels="data/sts_n11_relabel_case24_ieee_rts.parquet", tier="A"),
    "D93": dict(kind="case118", file="data/sts_n11_floor093.parquet", floor=0.93, seeds=[100, 101, 102, 103],
                labels="data/sts_n11_floor093_relabel.parquet", tier="A"),
    "D95a": dict(kind="case118", file="data/sts_n3_floor095.parquet", floor=0.95, seeds=[100, 101, 102, 103],
                 labels="data/sts_n5_relabel095.parquet", tier="A"),
    "D96": dict(kind="case118", file="data/sts_n11_floor096.parquet", floor=0.96, seeds=[100, 101, 102, 103],
                labels="data/sts_n11_floor096_relabel.parquet", tier="A"),
    "D95b": dict(kind="case118", file="data/sts_n5_floor095_seed200.parquet", floor=0.95, seeds=[200, 201, 202, 203],
                 labels="data/sts_n9_relabel095_seed200.parquet", tier="B"),
    "D95c": dict(kind="case118", file="data/sts_n9_floor095_seed300.parquet", floor=0.95, seeds=[300, 301, 302, 303],
                 labels="data/sts_n9_relabel095_seed300.parquet", tier="B"),
}
