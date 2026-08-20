"""Unattended driver: run 1a-1e per network, back to back, in the given order.

Appends a structured block to notes/RUN_REPORT.md as each network finishes, before the
next starts, so a crash costs one network rather than the run. Halts only on a broken
seal; every other failure abandons the network and continues.
"""

import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import netstudy as N

RUN_REPORT = "notes/RUN_REPORT.md"
DAY_SECONDS = 8 * 3600
NETWORKS = ["case39", "case24_ieee_rts", "case57"]


def log_block(network, phases, elapsed, status, extra):
    lines = ["", "---", "",
             f"## netstudy — {network} — {status}", "",
             f"| field | value |", "|---|---|",
             f"| phases completed | {', '.join(phases) if phases else 'none'} |",
             f"| elapsed_s | {round(elapsed, 1)} |",
             f"| elapsed vs 1-day cap | {elapsed / DAY_SECONDS:.4f} |",
             f"| abandon rule fired | {extra.get('abandon', False)} |",
             f"| abandon reason | {extra.get('abandon_reason')} |",
             f"| seal sha at 1c | {extra.get('seal_1c')} |",
             f"| seal sha at 1e | {extra.get('seal_1e')} |",
             f"| seal verdict | {extra.get('seal_verdict')} |",
             f"| hits | {extra.get('hits')} |",
             f"| mean abs error | {extra.get('mean_abs_error')} |",
             f"| max abs error | {extra.get('max_abs_error')} |",
             f"| artifacts | {extra.get('artifacts')} |",
             ""]
    with open(RUN_REPORT, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))


def run_one(network):
    t0 = time.time()
    phases, extra = [], {}
    try:
        r = N.phase_1a(network)
        phases.append("1a")
        if r["status"] == "ABANDON":
            extra.update(abandon=True, abandon_reason=r["reason"],
                         artifacts=r.get("sweep"))
            return "ABANDONED (no feasible range)", phases, time.time() - t0, extra
        if time.time() - t0 > DAY_SECONDS:
            extra.update(abandon=True, abandon_reason="1-day per-network cap exceeded after 1a")
            return "ABANDONED (cap)", phases, time.time() - t0, extra

        r = N.phase_1bc(network)
        phases += ["1b", "1c"]
        extra["seal_1c"] = r["seal_sha256"]
        if time.time() - t0 > DAY_SECONDS:
            extra.update(abandon=True, abandon_reason="1-day cap exceeded after 1c")
            return "ABANDONED (cap)", phases, time.time() - t0, extra

        N.phase_1d(network)
        phases.append("1d")
        doc = N.phase_1e(network)
        phases.append("1e")
        extra.update(seal_1e=doc["seal"]["sha256_at_1e"],
                     seal_verdict=doc["seal"]["verdict"],
                     hits=f"{doc['n_hits']}/{doc['n_predictions']}",
                     mean_abs_error=doc["mean_abs_error"],
                     max_abs_error=doc["max_abs_error"],
                     abandon=False, abandon_reason=None,
                     artifacts=f"data/netstudy/{network}/")
        if not doc["seal"]["unchanged"]:
            return "VOID (seal broken)", phases, time.time() - t0, extra
        return "COMPLETE", phases, time.time() - t0, extra
    except Exception as e:
        extra.update(abandon=True,
                     abandon_reason=f"{type(e).__name__}: {e}",
                     traceback=traceback.format_exc()[-800:])
        return "ABANDONED (error)", phases, time.time() - t0, extra


if __name__ == "__main__":
    total0 = time.time()
    results = {}
    for network in NETWORKS:
        print(f"\n{'='*70}\n=== {network}\n{'='*70}", flush=True)
        status, phases, elapsed, extra = run_one(network)
        log_block(network, phases, elapsed, status, extra)
        results[network] = dict(status=status, phases=phases, elapsed_s=elapsed, **extra)
        print(f"=== {network}: {status} [{elapsed:.0f}s]", flush=True)
        if status == "VOID (seal broken)":
            print("HALT: seal broken.", flush=True)
            break
        if time.time() - total0 > 5 * DAY_SECONDS:
            print("HALT: total cap exceeded.", flush=True)
            break
    with open("data/netstudy/run_status.json", "w") as f:
        json.dump(dict(networks=NETWORKS, total_elapsed_s=time.time() - total0,
                       results=results), f, indent=1, default=str)
    print("\nDRIVER DONE", flush=True)
