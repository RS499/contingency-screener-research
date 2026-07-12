import json, numpy as np
from collections import Counter

d = json.load(open("results.json"))
s = d["summary"]
near = d["near_cases"]

min_vm = np.array([c["min_vm"] for c in near])
max_vm = np.array([c["max_vm"] for c in near])
near_lo = np.array([c["near_lo"] for c in near])
near_hi = np.array([c["near_hi"] for c in near])

print("=== summary ===")
for k, v in s.items():
    print(f"  {k}: {v}")

print("\n=== near-limit composition ===")
lo_only = int(np.sum(near_lo & ~near_hi))
hi_only = int(np.sum(~near_lo & near_hi))
both = int(np.sum(near_lo & near_hi))
print(f"  near_lo only: {lo_only}")
print(f"  near_hi only: {hi_only}")
print(f"  both bands:   {both}")

print("\n=== min_vm distribution (near cases) ===")
for q in (0, 5, 25, 50, 75, 95, 100):
    print(f"  p{q:>3}: {np.percentile(min_vm, q):.4f}")
print("\n=== max_vm distribution (near cases) ===")
for q in (0, 5, 25, 50, 75, 95, 100):
    print(f"  p{q:>3}: {np.percentile(max_vm, q):.4f}")

for band in (0.001, 0.002, 0.005):
    n = int(np.sum(np.abs(min_vm - 0.94) <= band))
    print(f"  min_vm within +/-{band} of 0.94 lower limit: {n}")
for band in (0.001, 0.002, 0.005):
    n = int(np.sum(np.abs(max_vm - 1.06) <= band))
    print(f"  max_vm within +/-{band} of 1.06 upper limit: {n}")

print("\n=== diversity: contingency elements driving near cases ===")
elems = Counter((c["etype"], c["idx"]) for c in near)
print(f"  distinct elements: {len(elems)} / 186")
print("  top 10 elements by near-case count:")
for (et, idx), n in elems.most_common(10):
    print(f"    {et} {idx}: {n}")

print("\n=== diversity: critical buses ===")
minbuses = Counter(c["min_bus"] for c in near)
maxbuses = Counter(c["max_bus"] for c in near)
print(f"  distinct min-voltage (weak) buses: {len(minbuses)}  top: {minbuses.most_common(8)}")
print(f"  distinct max-voltage buses:        {len(maxbuses)}  top: {maxbuses.most_common(8)}")

print("\n=== distinctness (dedup) ===")
pairs = set((c["scen"], c["etype"], c["idx"]) for c in near)
print(f"  distinct (scenario, contingency) pairs: {len(pairs)}")
sig = set((c["etype"], c["idx"], c["min_bus"], round(c["min_vm"], 3)) for c in near)
print(f"  distinct (element, weak-bus, min_vm~1e-3) signatures: {len(sig)}")
sig2 = set((c["etype"], c["idx"], c["min_bus"], c["max_bus"],
            round(c["min_vm"], 4), round(c["max_vm"], 4)) for c in near)
print(f"  distinct fine signatures (~1e-4 voltages): {len(sig2)}")

print("\n=== train/calibrate split feasibility ===")
n = len(near)
print(f"  total straddle: {n}")
print(f"  70/30 -> train {int(n*0.7)}  calibrate {int(n*0.3)}")
print(f"  violation (positive class) available: {s['violation_cases']}")
