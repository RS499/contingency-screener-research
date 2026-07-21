
EDITS = [
    ("notes/science-review.md", "| Top-1 (bus 75) |", "| Top-1 (bus 76) |", 1),
    ("notes/science-review.md", "| Top-2 (buses 75, 52) |", "| Top-2 (buses 76, 53) |", 1),
    ("notes/science-review.md", "sweeping the bus-75 generator's", "sweeping the bus-76 generator's", 1),
    ("notes/science-review.md", "(min_vm 0.943 at bus 75)", "(min_vm 0.943 at bus 76)", 1),
    ("notes/science-review.md", "and bus 75 losing voltage support", "and bus 76 losing voltage support", 1),
    ("notes/science-review.md", "buses 52 at 72.7% / 75 at 25.8%", "buses 53 at 72.7% / 76 at 25.8%", 1),
    ("notes/science-review.md", "memorization of buses 52 and 75", "memorization of buses 53 and 76", 1),

    ("notes/artifact-clip-0.94.md", "bus 75 (16,511 cases) and bus 106 (9,800)",
     "bus 76 (16,511 cases) and bus 107 (9,800)", 1),
    ("notes/artifact-clip-0.94.md", "Bus 75 is a generator with base setpoint 0.943",
     "Bus 76 is a generator with base setpoint 0.943", 1),
    ("notes/artifact-clip-0.94.md", "bus at bus 75 or 106**", "bus at bus 76 or 107**", 1),
    ("notes/artifact-clip-0.94.md", "(bus 75 at 0.943, bus 106)", "(bus 76 at 0.943, bus 107)", 1),
    ("notes/artifact-clip-0.94.md", "Buses 75 and 106 are over-represented",
     "Buses 76 and 107 are over-represented", 1),
    ("notes/artifact-clip-0.94.md", "On the clip data buses 75 and 106",
     "On the clip data buses 76 and 107", 1),
    ("notes/artifact-clip-0.94.md", "the top critical bus is 75 at 27.1% (frozen), followed by 52 and 106",
     "the top critical bus is 76 at 27.1% (frozen), followed by 53 and 107", 1),
    ("notes/artifact-clip-0.94.md", "the 75/106 pairing no longer dominates",
     "the 76/107 pairing no longer dominates", 1),
    ("notes/artifact-clip-0.94.md", "| argmin at bus 75 or 106 |", "| argmin at bus 76 or 107 |", 1),

    ("notes/state-of-project.md", '"bus 75 loses reactive support at its Q-limit"',
     '"bus 76 loses reactive support at its Q-limit"', 1),
    ("notes/state-of-project.md", "(buses 9, 24, 65)", "(buses 10, 25, 66)", 1),
    ("notes/state-of-project.md", "dominated by bus 52 (72.7%) and bus 75 (25.8%)",
     "dominated by bus 53 (72.7%) and bus 76 (25.8%)", 1),
    ("notes/state-of-project.md",
     "bus 52 is a pure load bus with no local generator, and bus 75 is a generator held",
     "bus 53 is a pure load bus with no local generator, and bus 76 is a generator held", 1),
    ("notes/state-of-project.md", "memorization of buses 52 and 75", "memorization of buses 53 and 76", 1),
    ("notes/state-of-project.md", "buses beyond 52 and 75 appear", "buses beyond 53 and 76 appear", 1),

    ("CLAUDE.local.md",
     "  N-1 branch outages.\n- Voltage binds, not thermal:",
     "  N-1 branch outages.\n"
     "- Bus numbering: PROSE and the PAPER use IEEE 1-based bus names; CODE and ARTIFACTS use pandapower\n"
     "  0-based indices (`argmin_bus`, positional `net.bus`/`line`/`gen`). IEEE name = index + 1 on case118.\n"
     "  Never mix the two conventions in one document.\n"
     "- Voltage binds, not thermal:", 1),

    ("feasibility/generate_dataset.py",
     "- Loading capped at <=160% aggregate (gonogo ceiling: non-convergence 17.6% at 180%).\n\n"
     "*** ORACLE DEVIATION",
     "- Loading capped at <=160% aggregate (gonogo ceiling: non-convergence 17.6% at 180%).\n"
     "- Bus/line/gen numbers in this file are pandapower 0-based INDICES (positional), NOT IEEE names;\n"
     "  IEEE name = index + 1 on case118. (Code/artifacts use indices; prose and the paper use IEEE.)\n\n"
     "*** ORACLE DEVIATION", 1),
]


def main():
    cache = {}
    for path, old, new, want in EDITS:
        if path not in cache:
            with open(path) as f:
                cache[path] = f.read()
        got = cache[path].count(old)
        if got != want:
            raise SystemExit(f"ABORT: {path}: expected {want} of {old!r}, found {got}. No file written.")
    for path, old, new, want in EDITS:
        cache[path] = cache[path].replace(old, new)
    for path in sorted(set(p for p, _o, _n, _c in EDITS)):
        with open(path, "w") as f:
            f.write(cache[path])
        print(f"wrote {path}")
    print(f"\napplied {len(EDITS)} replacements across {len(set(p for p,_o,_n,_c in EDITS))} files")


if __name__ == "__main__":
    main()
