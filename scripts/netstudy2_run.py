"""Unattended v2 driver: 1a -> 1b/1c -> 2b seal -> 1d -> 1e -> 2b compare, per network.

The 2b seal happens AFTER 1b (q_hat known) and BEFORE 1d (gate not yet run), and uses only
networks whose gate already ran. Each network's block is appended to notes/RUN_REPORT.md
before the next starts.
"""

import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import netstudy as V1
import netstudy2 as V2
import netstudy2_cross as X

RUN_REPORT = "notes/RUN_REPORT.md"
DAY_SECONDS = V2.DAY_SECONDS
NETWORKS = ["case39", "case24_ieee_rts", "case89pegase", "case_illinois200"]


def log_block(network, phases, elapsed, status, extra):
    lines = ["", "---", "", f"## netstudy v2 — {network} — {status}", "",
             "| field | value |", "|---|---|",
             f"| phases completed | {', '.join(phases) if phases else 'none'} |",
             f"| elapsed_s | {round(elapsed, 1)} |",
             f"| elapsed vs 1-day cap ({DAY_SECONDS}s) | {elapsed / DAY_SECONDS:.4f} |",
             f"| abandon fired | {extra.get('abandon', False)} |",
             f"| abandon reason | {extra.get('abandon_reason')} |",
             f"| cal/test disjoint all seeds | {extra.get('disjoint')} |",
             f"| seal sha at 1c | {extra.get('seal_1c')} |",
             f"| seal verdict at 1e | {extra.get('seal_verdict')} |",
             f"| within-network hits (1e) | {extra.get('hits')} |",
             f"| within-network mean abs err | {extra.get('mean_abs_error')} |",
             f"| within-network max abs err | {extra.get('max_abs_error')} |",
             f"| epsilon alarm | {extra.get('epsilon_alarm')} |",
             f"| cross-network prior set (2b) | {extra.get('prior_networks')} |",
             f"| 2b A mean abs err | {extra.get('A_mean_abs_err')} |",
             f"| 2b B mean abs err | {extra.get('B_mean_abs_err')} |",
             f"| 2b B hits | {extra.get('B_hits')} |",
             ""]
    with open(RUN_REPORT, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))


def run_one(network, prior_done):
    t0 = time.time()
    phases, extra = [], {}
    try:
        ds, _st = V2.ensure_dataset(network)
        if ds is None:
            extra.update(abandon=True, abandon_reason="NO FEASIBLE RANGE in 1a")
            return "ABANDONED (no feasible range)", phases, time.time() - t0, extra
        phases.append("1a")
        if time.time() - t0 > DAY_SECONDS:
            extra.update(abandon=True, abandon_reason="1-day cap exceeded after 1a")
            return "ABANDONED (cap)", phases, time.time() - t0, extra

        r = V2.phase_1bc(network)
        phases += ["1b", "1c"]
        extra["seal_1c"] = r["seal_sha256"]
        pi = json.load(open(os.path.join(V2.ROOT, network, "prediction_inputs.json")))
        extra["disjoint"] = pi["disjoint_all_seeds"]

        s2 = X.phase_2b_seal(network, prior_done)
        phases.append("2b-seal")
        extra["prior_networks"] = ",".join(s2["prior_networks"])
        if time.time() - t0 > DAY_SECONDS:
            extra.update(abandon=True, abandon_reason="1-day cap exceeded after 2b seal")
            return "ABANDONED (cap)", phases, time.time() - t0, extra

        V2.phase_1d(network)
        phases.append("1d")
        doc = V2.phase_1e(network)
        phases.append("1e")
        extra.update(seal_verdict=doc["seal"]["verdict"],
                     hits=f"{doc['n_hits']}/{doc['n_predictions']}",
                     mean_abs_error=doc["mean_abs_error"],
                     max_abs_error=doc["max_abs_error"],
                     epsilon_alarm=doc["epsilon_alarm"])
        c = X.phase_2b_compare(network)
        phases.append("2b-compare")
        extra.update(A_mean_abs_err=c["A_mean_abs_err"], B_mean_abs_err=c["B_mean_abs_err"],
                     B_hits=f"{c['B_hits']}/{c['n_predictions']}",
                     abandon=False, abandon_reason=None)
        if not doc["seal"]["unchanged"]:
            return "VOID (seal broken)", phases, time.time() - t0, extra
        return "COMPLETE", phases, time.time() - t0, extra
    except Exception as e:
        extra.update(abandon=True, abandon_reason=f"{type(e).__name__}: {e}",
                     traceback=traceback.format_exc()[-900:])
        return "ABANDONED (error)", phases, time.time() - t0, extra


if __name__ == "__main__":
    os.makedirs(V2.ROOT, exist_ok=True)
    total0 = time.time()
    results, done = {}, []
    for network in NETWORKS:
        print(f"\n{'='*70}\n=== v2 {network}   prior={done}\n{'='*70}", flush=True)
        status, phases, elapsed, extra = run_one(network, list(done))
        log_block(network, phases, elapsed, status, extra)
        results[network] = dict(status=status, phases=phases, elapsed_s=elapsed, **extra)
        print(f"=== {network}: {status} [{elapsed:.0f}s]", flush=True)
        with open(os.path.join(V2.ROOT, "run_status.json"), "w") as f:
            json.dump(dict(networks=NETWORKS, results=results,
                           total_elapsed_s=time.time() - total0), f, indent=1, default=str)
        if status == "COMPLETE":
            done.append(network)
        if status == "VOID (seal broken)":
            print("HALT: seal broken.", flush=True)
            break
        if time.time() - total0 > 5 * DAY_SECONDS:
            print("HALT: total cap exceeded.", flush=True)
            break
    X.phase_2a(done)
    print("\nV2 DRIVER DONE", flush=True)
