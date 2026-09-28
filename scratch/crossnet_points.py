"""Read-only: escalation vs rho*q_hat across every network in data/netstudy2/cross_2a_points.json,
plus the per-network boundary mass / escalation / speedup at the 0.90 and first-<1%-missed points.
Writes nothing.

Usage: .venv/bin/python scratch/crossnet_points.py
"""

import json
import numpy as np

STRIP = 0.005

if __name__ == "__main__":
    with open("data/netstudy2/cross_2a_points.json") as fh:
        cp = json.load(fh)
    pts = cp["points"]
    print("networks:", cp["networks"], " n_points:", len(pts))
    print("point keys:", sorted(pts[0].keys()))

    print("\n=== per network x family: boundary mass, escalation at 0.90, ratio esc/(rho*q_hat) ===")
    for net in cp["networks"]:
        for fam in ["ridge", "histgb"]:
            sel = [p for p in pts if p["network"] == net and p["family"] == fam]
            if not sel:
                continue
            bm = sel[0]["boundary_mass"]
            x = np.array([p["boundary_mass"] / STRIP * p["q_hat"] for p in sel])
            y = np.array([p["escalation"] for p in sel])
            at90 = [p for p in sel if abs(p["coverage_target"] - 0.9) < 1e-9]
            e90 = at90[0]["escalation"] if at90 else float("nan")
            print(f"  {net:18s} {fam:6s} BM={100*bm:5.2f}%  n={len(sel):2d}  esc@0.90={100*e90:5.1f}%  "
                  f"median esc/(rho q)={np.median(y/x):.2f}  range [{(y/x).min():.2f}, {(y/x).max():.2f}]")

    x = np.array([p["boundary_mass"] / STRIP * p["q_hat"] for p in pts])
    y = np.array([p["escalation"] for p in pts])
    r = np.corrcoef(x, y)[0, 1]
    lr = np.corrcoef(np.log(x), np.log(y))[0, 1]
    print(f"\nall points: Pearson r(esc, rho*q_hat) = {r:.3f}; r(log, log) = {lr:.3f}")
    bms = {}
    for p in pts:
        bms[p["network"]] = p["boundary_mass"]
    print("boundary mass by network:", {k: round(100 * v, 2) for k, v in bms.items()})

    print("\n=== netstudy2 summary table_at_090 ===")
    with open("data/netstudy2/summary.json") as fh:
        s = json.load(fh)
    for row in s["table_at_090"]:
        print("  ", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})
