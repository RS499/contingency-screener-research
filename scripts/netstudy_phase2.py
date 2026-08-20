"""Phase 2: cross-network aggregation of the sealed escalation-identity test.

Reads only the per-network artifacts. Recomputes nothing from models.
"""

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import netstudy as N

ROOT = "data/netstudy"
OUT = os.path.join(ROOT, "phase2_summary.json")
# case30-thermal's histgb escalation at its 0.96 crossing, the incumbent floor figure.
FLOOR_REF_FILE = "data/case30_thermal/case30_thermal_frozen.json"


def load_network(network):
    d = os.path.join(ROOT, network)
    out = dict(network=network)
    for key, fn in (("sweep", "range_sweep.json"), ("build", "build_stats.json"),
                    ("pred", "prediction_inputs.json"), ("frozen", "frozen.json"),
                    ("comp", "comparison.json"), ("seal", "seal_1c.json")):
        p = os.path.join(d, fn)
        out[key] = json.load(open(p)) if os.path.exists(p) else None
    return out


def find_seal_prefix(target_sha, max_lines=100000):
    """Recover which line-prefix of the shared prereg log hashes to a given seal."""
    import hashlib
    lines = open(N.PREREG, "rb").readlines()
    for k in range(len(lines), 0, -1):
        if hashlib.sha256(b"".join(lines[:k])).hexdigest() == target_sha:
            return k
    return None


def ms_solver_provenance(networks):
    """ms_solver is imported from case118 and NOT re-timed. Report the sensitivity."""
    tri = json.load(open("data/network_triage.json"))
    per_net = {r["network"]: r.get("ms_solve_min") for r in tri["networks"]}
    out = dict(
        used_value_source="data/solve_time.json (measured on case118, 400 timed solves)",
        defect=("every net_speedup in this study divides by a solve cost measured on a "
                "DIFFERENT network. A 24-bus or 39-bus AC solve is not a 118-bus solve."),
        why_impact_is_small=("net_speedup = n*ms_solver / (n*ms_surrogate + n_esc*ms_solver) "
                             "with ms_surrogate = 1e-6, so it collapses to approximately "
                             "1/escalation and is nearly independent of ms_solver."),
        per_network_measured_ms=per_net,
        measured_source="data/network_triage.json (minimum over 20 solves, warm-up discarded)",
        note="NOT substituted. Reported so the reader can see what was and was not measured.")
    for network in networks:
        d = os.path.join(ROOT, network, "frozen.json")
        if os.path.exists(d):
            fr = json.load(open(d))
            out.setdefault("used_in_artifacts", {})[network] = fr["ms_solver"]
    return out


def main():
    status = json.load(open(os.path.join(ROOT, "run_status.json")))
    ref = json.load(open(FLOOR_REF_FILE))
    ref_cross = ref["crossings_first_below_1pct_missed"]["histgb"]

    rows, all_comps = [], []
    for network in status["networks"]:
        n = load_network(network)
        st = status["results"].get(network, {}).get("status")
        if n["comp"] is None:
            rows.append(dict(network=network, status=st,
                             boundary_mass=(n["build"]["boundary_mass"] if n["build"] else None),
                             predicted_esc=None, measured_esc=None, error=None, hit_miss=None,
                             note="no comparison artifact: network did not reach 1e"))
            continue
        for c in n["comp"]["comparisons"]:
            all_comps.append(dict(network=network, n_bus_proxy=n["build"]["n_branches"],
                                  violation_rate=n["build"]["violation_rate"],
                                  boundary_mass=n["build"]["boundary_mass"], **c))
        at90 = [c for c in n["comp"]["comparisons"] if abs(c["coverage_target"] - 0.90) < 1e-9]
        for c in at90:
            rows.append(dict(
                network=network, status=st, family=c["family"],
                coverage_target=c["coverage_target"],
                boundary_mass=n["build"]["boundary_mass"],
                predicted_esc=c["predicted"], measured_esc=c["measured"],
                error=c["abs_error"], hit_miss=("HIT" if c["hit"] else "MISS"),
                seal_verdict=n["comp"]["seal"]["verdict"]))

    misses = [c for c in all_comps if not c["hit"]]
    errs = np.array([c["abs_error"] for c in all_comps]) if all_comps else np.array([])

    n_networks_completed = len({c["network"] for c in all_comps})
    corr = dict(
        verdict="NOT COMPUTABLE",
        reason=("every candidate predictor -- network size, violation rate, boundary mass -- "
                "is CONSTANT WITHIN a network, so with "
                f"{n_networks_completed} completed networks the effective n is "
                f"{n_networks_completed}, not {len(all_comps)}. A Pearson r over the "
                f"{len(all_comps)} rows is one two-group contrast reported 36 times, and its "
                "response variable is floating-point rounding dust at the 1e-17 scale. "
                "Reporting a correlation coefficient here would dress noise as signal."),
        effective_n=n_networks_completed,
        error_scale_note=("all absolute errors are at or below one ulp, so there is no error "
                          "variation for any predictor to explain"))

    floor = []
    for network in status["networks"]:
        n = load_network(network)
        if n["frozen"] is None:
            continue
        for fam in ("ridge", "histgb"):
            cr = n["frozen"]["crossings_first_below_1pct_missed"][fam]
            floor.append(dict(network=network, family=fam,
                              crossing=cr,
                              esc_at_crossing=(cr["escalation"] if cr else None),
                              esc_at_090=n["frozen"]["four_metrics_at_90pct_coverage"][fam]["escalation_mean"],
                              boundary_mass=n["build"]["boundary_mass"]))
    beats = [f for f in floor if f["esc_at_crossing"] is not None
             and f["esc_at_crossing"] < ref_cross["escalation"]]

    exactness = None
    seal_regions = []
    for network in status["networks"]:
        n = load_network(network)
        if n["comp"] is not None:
            exactness = n["comp"]["exactness_note"]
            seal_regions.append(dict(
                network=network,
                sha256_at_1c=n["seal"]["preregistration_sha256_at_1c"],
                sealed_prefix_lines=find_seal_prefix(
                    n["seal"]["preregistration_sha256_at_1c"])))

    doc = dict(
        phase="2 cross-network summary",
        WHAT_THIS_DOES_NOT_SHOW=(
            "The identity is ALGEBRAICALLY EXACT, so a 100% hit rate was guaranteed before "
            "any network was run. This is a PIPELINE CONFORMANCE TEST, not an out-of-sample "
            "physical prediction, and it must not be quoted as evidence that the escalation "
            "model generalises to new networks."),
        exactness_note=exactness,
        seal_reproduction=dict(
            problem=("notes/preregistration.md is a shared append-only log, so its whole-file "
                     "hash equals only the LAST network's seal. A reader holding the repo "
                     "cannot recover an earlier seal without knowing where its region ends."),
            recipe="head -n <sealed_prefix_lines> notes/preregistration.md | shasum -a 256",
            regions=seal_regions,
            residual_limitation=("notes/ is git-ignored, so there is no independent timestamp "
                                 "authority. Seal, prereg and artifacts were written by the "
                                 "same process; only file mtime corroborates the ordering.")),
        ms_solver_provenance=ms_solver_provenance(status["networks"]),
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        networks_attempted=status["networks"],
        per_network_status={k: v["status"] for k, v in status["results"].items()},
        table_at_090=rows,
        n_predictions=len(all_comps),
        n_hits=int(sum(c["hit"] for c in all_comps)),
        mean_abs_error=(float(errs.mean()) if len(errs) else None),
        max_abs_error=(float(errs.max()) if len(errs) else None),
        error_correlations=corr,
        misses=misses,
        floor_claim=dict(
            reference_source=FLOOR_REF_FILE,
            reference_crossing=ref_cross,
            reference_escalation_at_crossing=ref_cross["escalation"],
            per_network=floor,
            networks_beating_reference=beats,
            verdict=("BOUNDED: at least one network achieves lower escalation at its "
                     "sub-1%-missed crossing than the case30-thermal reference"
                     if beats else
                     "HOLDS across the attempted set: no network beats the reference")),
        all_comparisons=all_comps)
    N.write_json(OUT, doc, dict(seed=None, input_file=os.path.join(ROOT, "run_status.json"),
                                input_sha256=N.sha256_of(os.path.join(ROOT, "run_status.json")),
                                run_settings=dict(phase="2")))
    print(json.dumps(dict(n_predictions=doc["n_predictions"], n_hits=doc["n_hits"],
                          mean_abs_error=doc["mean_abs_error"],
                          max_abs_error=doc["max_abs_error"],
                          floor=doc["floor_claim"]["verdict"]), indent=1))


if __name__ == "__main__":
    main()
