import os
import sys
import json
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import run_classical as rc
import eval_classical as ec
import sts_manifest as sm

# N13 Step 4, arm S, classical screen (scratch/n13_decision_rule.md §3): scripts/run_classical.py and
# scripts/eval_classical.py on the rebuilt D94, with only the input/output paths changed (module constants set here;
# neither file is edited). N11 Part 4 scored the committed predictions against corrected labels; on the rebuilt D94
# the dataset's own labels are the corrected ones, so eval_classical's conformal scoring IS that scoring.
# run_classical rebuilds each base from its stored features, re-solves the base with the PINNED solver
# (classical_screen.solve_base) and stops if that state differs from the stored vm0_* by > 1e-5 (its own guard).
# The rebuilt vm0_* are the corrected N-0 states, so the guard may stop the run; if it does, the analysis is stopped
# and reported under N13 rule 2 (no setting is changed to make it pass).
# Output: data/sts_n13_classical.json + manifest (and, only if run_classical completes, the prediction and metric files).

DATASET = "data/sts_n13_D94.parquet"
PREDS = "data/sts_n13_classical_predictions.parquet"
METRICS = "data/sts_n13_classical_screen_metrics.json"
OUT = "data/sts_n13_classical.json"


def main():
    t0 = time.time()
    rc.DATASET = DATASET
    sys.argv = ["run_classical.py", "--out", PREDS]
    status = dict(run_classical="not started")
    try:
        rc.main()
        status["run_classical"] = "completed"
    except RuntimeError as e:
        status["run_classical"] = "stopped by its own guard"
        status["guard_message"] = str(e)
    except Exception as e:
        status["run_classical"] = "crashed"
        status["error"] = traceback.format_exc()[-2000:]
    if status["run_classical"] == "completed":
        ec.PREDS = PREDS
        ec.DATASET = DATASET
        ec.OUT = METRICS
        ec.main()
        m = json.load(open(METRICS))
        r90 = [r for r in m["conformalized"] if abs(r["coverage_target"] - 0.90) < 1e-9][0]
        status["summary_at_0p90"] = dict(mae=m["fit_quality"]["mae"], mae_std=m["fit_quality"]["mae_std"], r2=m["fit_quality"]["r2"],
                                         escalation=r90["escalation"], escalation_std=r90["escalation_std"], missed=r90["missed_viol"],
                                         missed_std=r90["missed_viol_std"], speedup=r90["net_speedup"], speedup_std=r90["net_speedup_std"])
    status["analysis"] = "classical screen (run_classical + eval_classical) on rebuilt D94"
    status["wall_s"] = time.time() - t0
    with open(OUT, "w") as f:
        json.dump(status, f, indent=2)
    man = sm.build_manifest([OUT], "scratch/n13_classical.py", [".venv/bin/python", "scratch/n13_classical.py"],
                            [DATASET, "scripts/run_classical.py", "scripts/eval_classical.py", "scripts/classical_screen.py",
                             "scratch/n13_decision_rule.md"],
                            dict(model_hyperparameters="none: linearized screen, no fit", vm0_guard_tol=rc.VM0_TOL,
                                 solver="classical_screen.solve_base: pandapower runpp enforce_q_lims=True init=dc numba=True"), "")
    man["no_new_solves"] = "FALSE: classical base solves per scenario (if run_classical ran)"
    sm.write_manifest(man, OUT)
    print(json.dumps({k: status[k] for k in status if k != "error"}, indent=1)[:3000])


if __name__ == "__main__":
    main()
