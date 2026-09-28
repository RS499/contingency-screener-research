import os
import sys
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, HERE)
import manifest as mf
import classical_manifest as cm

# Missed-violation rate of ridge and histgb compared at MATCHED escalation instead of matched
# coverage target (review item C8). Each seed's 30-point M2 sweep (coverage 0.70-0.99) is
# linearly interpolated onto a common escalation grid; no extrapolation outside a seed's range.
#
# usage: .venv/bin/python scripts/sts_matched_escalation.py OUT_DIR [REF_DIR]

TUNED = "data/tuned_metrics.json"
SCRIPT = "scripts/sts_matched_escalation.py"
OUT_NAME = "sts_matched_escalation.json"
MODELS = ["ridge", "histgb"]
GRID_LO_PCT, GRID_HI_PCT = 25, 75


def seed_curves(tm, family):
    # per seed: escalation (strictly increasing after merging ties), missed rate, coverage target
    out = []
    for r in tm["records"]:
        if r["metric"] != "m2" or r["family"] != family:
            continue
        esc = np.array([s["escalation"] for s in r["sweep"]])
        mis = np.array([s["missed_viol"] for s in r["sweep"]])
        cov = np.array([s["coverage_target"] for s in r["sweep"]])
        keep = np.concatenate([[True], np.diff(esc) > 0])
        dup = ~keep
        # a tie in escalation means the same escalated set, so the certified set and the
        # missed rate must be the same too; record the largest gap to prove it
        tie_gap = 0.0
        for i in np.where(dup)[0]:
            tie_gap = max(tie_gap, abs(float(mis[i] - mis[i - 1])))
        out.append({"seed": r["seed"], "esc": esc[keep], "mis": mis[keep], "cov": cov[keep],
                    "n_ties_merged": int(dup.sum()), "max_missed_gap_at_ties": tie_gap,
                    "esc_min": float(esc.min()), "esc_max": float(esc.max())})
    return out


def interp_at(curve, g):
    if g < curve["esc"][0] or g > curve["esc"][-1]:
        return None, None
    return float(np.interp(g, curve["esc"], curve["mis"])), float(np.interp(g, curve["esc"], curve["cov"]))


def stats(values):
    v = np.array([x for x in values if x is not None])
    if len(v) == 0:
        return {"n_seeds": 0, "mean": None, "std": None}
    return {"n_seeds": int(len(v)), "mean": float(v.mean()), "std": float(v.std(ddof=0))}


def verdict(r, h):
    # project std rule: a gap counts only if it exceeds the larger of the two stds
    if r["n_seeds"] < 5 or h["n_seeds"] < 5:
        return f"incomplete (ridge {r['n_seeds']} / histgb {h['n_seeds']} seeds reach this escalation)"
    gap = r["mean"] - h["mean"]
    larger = max(r["std"], h["std"])
    if gap > larger:
        return "histgb safer"
    if -gap > larger:
        return "ridge safer"
    return "tie"


def runs(rows):
    # consecutive grid points with the same verdict
    out = []
    for row in rows:
        if len(out) > 0 and out[-1]["verdict"] == row["verdict"]:
            out[-1]["to_escalation_pct"] = row["escalation_pct"]
        else:
            out.append({"verdict": row["verdict"], "from_escalation_pct": row["escalation_pct"],
                        "to_escalation_pct": row["escalation_pct"]})
    return out


def repro(path, ref_dir):
    if ref_dir == "":
        return "not checked in this run"
    ref = os.path.join(ref_dir, os.path.basename(path))
    return {"compared_with": ref, "same_sha256": cm.content_hash(ref) == cm.content_hash(path)}


def main():
    out_dir = sys.argv[1]
    ref_dir = ""
    if len(sys.argv) > 2:
        ref_dir = sys.argv[2]
    out_path = os.path.join(out_dir, OUT_NAME)

    with open(TUNED) as f:
        tm = json.load(f)
    curves = {}
    for m in MODELS:
        curves[m] = seed_curves(tm, m)

    rows = []
    for pct in range(GRID_LO_PCT, GRID_HI_PCT + 1):
        g = pct / 100.0
        row = {"escalation_pct": pct}
        per = {}
        for m in MODELS:
            mis = []
            cov = []
            for c in curves[m]:
                a, b = interp_at(c, g)
                mis.append(a)
                cov.append(b)
            per[m] = stats(mis)
            row[m] = {"missed_viol": per[m], "coverage_target_at_this_escalation": stats(cov),
                      "missed_viol_per_seed": mis}
        row["gap_ridge_minus_histgb"] = None
        if per["ridge"]["mean"] is not None and per["histgb"]["mean"] is not None:
            row["gap_ridge_minus_histgb"] = per["ridge"]["mean"] - per["histgb"]["mean"]
        row["verdict"] = verdict(per["ridge"], per["histgb"])
        rows.append(row)

    seed_ranges = {}
    for m in MODELS:
        seed_ranges[m] = [{"seed": c["seed"], "esc_min": c["esc_min"], "esc_max": c["esc_max"],
                           "n_ties_merged": c["n_ties_merged"],
                           "max_missed_gap_at_ties": c["max_missed_gap_at_ties"]} for c in curves[m]]
    out = {
        "source": TUNED,
        "selection": "records with metric == 'm2' (promoted gate-aware surrogates), 5 seeds",
        "method": "per seed, linear interpolation of missed_viol (and coverage_target) against "
                  "escalation over the 30-point sweep; a grid point outside a seed's escalation "
                  "range is left out for that seed (no extrapolation)",
        "grid": f"escalation {GRID_LO_PCT}% to {GRID_HI_PCT}% in 1-point steps",
        "std_convention": "population std (ddof=0) over the seeds that reach the grid point",
        "verdict_rule": "histgb safer if ridge_mean - histgb_mean > max(std_ridge, std_histgb); "
                        "ridge safer if the reverse gap exceeds it; otherwise tie; incomplete "
                        "if either model has fewer than 5 seeds at that point",
        "units": "missed_viol is a fraction of true violations (0-1)",
        "verdict_runs": runs(rows),
        "seed_ranges": seed_ranges,
        "grid_points": rows,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {out_path}")
    for r in out["verdict_runs"]:
        print(f"  {r['from_escalation_pct']}-{r['to_escalation_pct']}%: {r['verdict']}")

    configs = {}
    for r in tm["records"]:
        if r["metric"] == "m2":
            configs[f"{r['family']}_seed{r['seed']}"] = r["config"]
    settings = {
        "task": "matched-escalation missed-rate comparison (review C8)",
        "generating_script": SCRIPT,
        "regeneration_argv": [SCRIPT, "data"],
        "inputs": [{"path": TUNED, "sha256": cm.content_hash(TUNED)}],
        "outputs": [{"path": out_path, "sha256": cm.content_hash(out_path),
                     "repro": repro(out_path, ref_dir)}],
        "grid_lo_pct": GRID_LO_PCT, "grid_hi_pct": GRID_HI_PCT, "grid_step_pct": 1,
        "interpolation": "numpy.interp (linear), within each seed's range only",
        "no_new_solves": "computed from data/tuned_metrics.json sweeps; no fit or AC solve",
    }
    man = cm.build_manifest(out_path, out, settings, configs)
    with open(mf.manifest_path(out_path), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {mf.manifest_path(out_path)}")


if __name__ == "__main__":
    main()
