"""Phase 0 feasibility triage for the escalation-identity study.

Per candidate network, at NOMINAL load (no scenario sampling, no gate):
  - does the base case converge under the pinned solver?
  - are line max_i_ka and trafo sn_mva populated, and PLACEHOLDER-uniform?
    The placeholder test is the committed one from scripts/case30_thermal.py
    (assert_ratings_usable), imported rather than restated.
  - base-case min_vm and max line/trafo loading_percent
  - a go/no-go with the reason

Writes data/network_triage.json plus a Schema-B manifest. Runs no gate and
builds no dataset.
"""

import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandapower as pp
import pandapower.networks as nw

sys.path.insert(0, "scripts")
sys.path.insert(0, "feasibility")
import case30_thermal as T

OUT = "data/network_triage.json"
APA = ("Thurner, L., Scheidler, A., Schafer, F., Menke, J., Dollichon, J., Meier, F., "
       "Meinecke, S., & Braun, M. (2018). pandapower - an open-source Python tool for "
       "convenient modeling, analysis, and optimization of electric power systems. "
       "IEEE Transactions on Power Systems, 33(6), 6510-6521. "
       "https://doi.org/10.1109/TPWRS.2018.2829021")

# Judgment call, stated: the prompt names only case57. This is the pandapower
# standard-case family up to a size where a 1,500-base build is even arguable,
# plus the two networks that already carry result sets.
CANDIDATES = ["case14", "case24_ieee_rts", "case30", "case_ieee30", "case39",
              "case57", "case89pegase", "case118", "case145", "case_illinois200",
              "case300", "GBreducednetwork", "iceland", "case1354pegase"]

VMIN = 0.94
THERMAL_MAX_PCT = 100.0
N_TIMED = 20
BASES_PER_BUILD = 1500
DAY_SECONDS = 8 * 3600


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_out(args):
    try:
        return subprocess.check_output(["git"] + args, text=True).strip()
    except Exception:
        return None


def rating_audit(net, name):
    """Same placeholder rule as scripts/case30_thermal.assert_ratings_usable."""
    out = {}
    line_r = net.line["max_i_ka"]
    out["n_lines"] = int(len(net.line))
    out["n_trafos"] = int(len(net.trafo))
    out["line_max_i_ka_populated"] = bool(len(net.line) > 0 and not line_r.isna().all())
    out["line_max_i_ka_n_nan"] = int(line_r.isna().sum()) if len(net.line) else 0
    out["line_max_i_ka_n_distinct"] = int(line_r.nunique()) if len(net.line) else 0
    if len(net.trafo):
        trafo_r = net.trafo["sn_mva"]
        out["trafo_sn_mva_populated"] = bool(not trafo_r.isna().all())
        out["trafo_sn_mva_n_distinct"] = int(trafo_r.nunique())
        out["trafo_sn_mva_max"] = float(trafo_r.max())
    else:
        out["trafo_sn_mva_populated"] = None
        out["trafo_sn_mva_n_distinct"] = 0
        out["trafo_sn_mva_max"] = None
    try:
        T.assert_ratings_usable(net, name)
        out["placeholder_verdict"] = "USABLE"
        out["placeholder_reason"] = None
    except ValueError as e:
        out["placeholder_verdict"] = "PLACEHOLDER (thermal predicate UNDEFINED)"
        out["placeholder_reason"] = str(e)
    return out


def max_loading_pct(net):
    vals = []
    lp = net.res_line["loading_percent"]
    if len(lp) and lp.notna().any():
        vals.append(float(lp.max()))
    if len(net.trafo):
        tp = net.res_trafo["loading_percent"]
        if len(tp) and tp.notna().any():
            vals.append(float(tp.max()))
    return max(vals) if vals else np.nan


def time_solve(net):
    """Minimum over N_TIMED solves, warm-up discarded. Same basis as ms_solver."""
    pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)
    best = np.inf
    for _ in range(N_TIMED):
        t0 = time.perf_counter()
        pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)
        best = min(best, (time.perf_counter() - t0) * 1000.0)
    return best


def diagnose_nonconvergence(name):
    """Which pinned setting blocks convergence. DIAGNOSTIC ONLY - nothing is unpinned."""
    out = {}
    for label, kw in [("pinned", dict(enforce_q_lims=True, init="dc", numba=True)),
                      ("init_flat_q_lims_on", dict(enforce_q_lims=True, init="flat", numba=True)),
                      ("init_dc_q_lims_off", dict(enforce_q_lims=False, init="dc", numba=True))]:
        net = getattr(nw, name)()
        try:
            pp.runpp(net, **kw)
            out[label] = dict(converged=True, min_vm_pu=float(net.res_bus.vm_pu.min()))
        except Exception as e:
            out[label] = dict(converged=False, error=type(e).__name__)
    out["converges_without_q_lims"] = bool(out["init_dc_q_lims_off"]["converged"])
    out["note"] = ("recorded to make the abandon reason precise. enforce_q_lims stays pinned "
                   "ON; no result is produced from any alternate configuration.")
    return out


def triage_one(name):
    row = dict(network=name)
    try:
        net = getattr(nw, name)()
    except Exception as e:
        row["status"] = "NO-GO"
        row["reason"] = f"network constructor failed: {type(e).__name__}: {e}"
        return row

    row["n_bus"] = int(len(net.bus))
    row["n_line"] = int(len(net.line))
    row["n_trafo"] = int(len(net.trafo))
    row["n_branch_n1"] = int(len(net.line) + len(net.trafo))
    row["n_load"] = int(len(net.load))
    row["n_gen"] = int(len(net.gen))
    row["n_sgen"] = int(len(net.sgen))
    row["n_ext_grid"] = int(len(net.ext_grid))
    row["n_gen_nonslack"] = int((~net.gen["slack"]).sum()) if len(net.gen) and "slack" in net.gen else 0

    try:
        pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)
        row["base_converged"] = True
    except Exception as e:
        row["base_converged"] = False
        row["base_error"] = f"{type(e).__name__}: {e}"
        row["nonconvergence_diagnostic"] = diagnose_nonconvergence(name)
        row["status"] = "NO-GO"
        if row["nonconvergence_diagnostic"]["converges_without_q_lims"]:
            row["reason"] = ("base case does not converge under the PINNED solver config at "
                             "nominal load; it converges only with enforce_q_lims=False, which "
                             "is pinned ON (CLAUDE.md section 5) and must not be changed. "
                             "ABANDON: the pinned config is not negotiable for a result.")
        else:
            row["reason"] = ("base case does not converge at nominal load under any probed "
                             "solver configuration")
        return row

    row["base_min_vm_pu"] = float(net.res_bus.vm_pu.min())
    row["base_max_vm_pu"] = float(net.res_bus.vm_pu.max())
    row["base_max_loading_pct"] = float(max_loading_pct(net))
    row["base_max_line_loading_pct"] = (float(net.res_line["loading_percent"].max())
                                        if len(net.line) else None)
    row["base_meets_voltage_criterion"] = bool(row["base_min_vm_pu"] >= VMIN)
    row["ratings"] = rating_audit(getattr(nw, name)(), name)
    if row["ratings"]["placeholder_verdict"] == "USABLE":
        row["base_meets_thermal_criterion"] = bool(row["base_max_loading_pct"] <= THERMAL_MAX_PCT)
        row["n0_criterion_available"] = "voltage AND thermal"
    else:
        row["base_meets_thermal_criterion"] = None
        row["n0_criterion_available"] = "voltage ONLY (thermal UNDEFINED)"

    row["ms_solve_min"] = float(time_solve(net))
    solves = BASES_PER_BUILD * (1 + row["n_branch_n1"])
    row["projected_solves_at_100pct_acceptance"] = int(solves)
    row["projected_build_s_at_100pct_acceptance"] = float(solves * row["ms_solve_min"] / 1000.0)
    row["projected_build_days_at_20pct_acceptance"] = float(
        solves * row["ms_solve_min"] / 1000.0 / 0.20 / DAY_SECONDS)

    if row["n_load"] == 0:
        row["status"] = "NO-GO"
        row["reason"] = "no load table: the load-multiplier sampler has nothing to scale"
    elif row["n_gen_nonslack"] == 0:
        row["status"] = "GO (degraded)"
        row["reason"] = ("converges, but no non-slack generator: the generator-outage draw "
                         "and the gen_vm / gen_q jitter of the committed sampler are inert here")
    elif row["projected_build_days_at_20pct_acceptance"] > 1.0:
        row["status"] = "NO-GO (cost)"
        row["reason"] = (f"projected build exceeds the 1-day per-network cap: "
                         f"{row['projected_build_days_at_20pct_acceptance']:.2f} d at 20% "
                         f"acceptance, from a measured {row['ms_solve_min']:.3f} ms solve")
    else:
        row["status"] = "GO"
        row["reason"] = (f"converges at nominal; N-0 criterion available: "
                         f"{row['n0_criterion_available']}")
    return row


if __name__ == "__main__":
    rows = []
    for name in CANDIDATES:
        print(f"triaging {name} ...", flush=True)
        rows.append(triage_one(name))

    doc = dict(
        phase="0 (feasibility triage)",
        purpose=("per-network go/no-go for the escalation-identity study; no scenario "
                 "sampling, no gate, no dataset built"),
        solver=dict(enforce_q_lims=True, numba=True, init="dc", algorithm="nr"),
        criteria=dict(
            vmin_pu=VMIN,
            thermal_max_pct=THERMAL_MAX_PCT,
            n0_criterion=("CORRECTED criterion: converges AND min_vm >= 0.94 AND max "
                          "loading_percent <= 100. Where ratings are PLACEHOLDER the "
                          "thermal clause is UNDEFINED and the network is voltage-only-feasible."),
            placeholder_rule=("imported unchanged from scripts/case30_thermal.py "
                              "assert_ratings_usable: line ratings are PLACEHOLDER if "
                              f"n_distinct <= {T.PLACEHOLDER_MAX_DISTINCT} AND base-case max "
                              f"loading < {T.PLACEHOLDER_BASE_LOADING_PCT}%; trafo ratings are "
                              f"PLACEHOLDER if a single value >= {T.PLACEHOLDER_TRAFO_MVA} MVA"),
            cost_rule=(f"NO-GO (cost) if the projected build exceeds 1 day, taken as "
                       f"{BASES_PER_BUILD} bases x (1 + n_branch) solves at the measured "
                       f"per-network minimum solve time, divided by a 20% acceptance rate, "
                       f"against a {DAY_SECONDS}-second working day"),
        ),
        timing_basis=f"minimum over {N_TIMED} solves, warm-up discarded",
        candidate_set_note=("judgment call: the prompt names only case57. This is the "
                            "pandapower standard-case family plus the two networks that "
                            "already carry result sets (case118, case30)."),
        networks=rows,
    )
    with open(OUT, "w") as f:
        json.dump(doc, f, indent=1)

    man = dict(
        artifact=os.path.basename(OUT),
        generating_script="scripts/triage_networks.py",
        argv=sys.argv,
        seed=None,
        seed_note="no random draw is made in Phase 0",
        nproc=os.cpu_count(),
        script_git_blob_sha=git_out(["hash-object", "scripts/triage_networks.py"]),
        script_tracked_in_git=bool(git_out(["ls-files", "scripts/triage_networks.py"])),
        repo_head_commit=git_out(["rev-parse", "HEAD"]),
        input_file="pandapower.networks (library constructors; no repo input file)",
        input_sha256=None,
        input_sha256_note=("NO SOURCE: inputs are library constructors, not a repo file. "
                           "pandapower version is pinned below instead."),
        interpreter=sys.version,
        interpreter_short=".".join(str(x) for x in sys.version_info[:3]),
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        pandapower=pp.__version__,
        numpy=np.__version__,
        apa_citation=APA,
        content_sha256=sha256_of(OUT),
    )
    with open(os.path.splitext(OUT)[0] + ".manifest.json", "w") as f:
        json.dump(man, f, indent=1)
    print("wrote", OUT)
