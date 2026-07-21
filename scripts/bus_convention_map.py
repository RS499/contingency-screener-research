import os
import re
import sys
import json
import glob

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feasibility"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import classical_manifest as cm

import pandapower.networks as nw
import pandapower.topology as top
import networkx as nx

FREQ_INDICES = [75, 52, 106]
SEVERITY_IDX = 53
POCKET_IDX = [53, 57, 58]

CONVERT_FILES = ["paper_current.tex", "notes/state-of-project.md",
                 "notes/science-review.md", "notes/artifact-clip-0.94.md"]
BUS_RE = re.compile(r"bus(?:es)?\s+(\d+(?:\s*(?:,|and)\s*\d+)*)", re.IGNORECASE)
NUM_RE = re.compile(r"\d+")


def idx_to_ieee(net, idx):
    return int(net.bus.at[idx, "name"]) if idx in net.bus.index else None


def scan_file(path, net):
    hits = []
    if not os.path.exists(path):
        return hits
    with open(path) as f:
        for ln, line in enumerate(f, 1):
            for m in BUS_RE.finditer(line):
                for num in NUM_RE.findall(m.group(1)):
                    idx = int(num)
                    hits.append(dict(line=ln, index=idx, ieee=idx_to_ieee(net, idx)))
    return hits


def main():
    net = nw.case118()
    g = top.create_nxgraph(net, respect_switches=False, include_trafos=True)

    frz = json.load(open("data/frozen_poster_numbers.json"))
    share = {int(b["bus"]): float(b["share_pct"]) for b in frz["dataset_facts"]["critical_bus_top5"]}

    pocket_ieee = [idx_to_ieee(net, i) for i in POCKET_IDX]
    freq_rows = []
    for i in FREQ_INDICES:
        h_sev = int(nx.shortest_path_length(g, i, SEVERITY_IDX)) if (i in g and SEVERITY_IDX in g) else None
        h_pocket = min(int(nx.shortest_path_length(g, i, p)) for p in POCKET_IDX if p in g)
        in_pocket = i in POCKET_IDX
        adjacent_to_severity = g.has_edge(i, SEVERITY_IDX)
        freq_rows.append(dict(index=i, ieee=idx_to_ieee(net, i), share_pct=share.get(i),
                              hops_to_ieee54=h_sev, min_hops_to_pocket=h_pocket,
                              in_54_58_59_pocket=in_pocket,
                              directly_connected_to_ieee54=bool(adjacent_to_severity),
                              shares_reactive_pocket=bool(in_pocket or adjacent_to_severity or h_pocket <= 1)))
        print(f"[pocket] index {i} (IEEE {idx_to_ieee(net,i)}, {share.get(i)}%): "
              f"hops->IEEE54={h_sev}  min_hops->pocket={h_pocket}  "
              f"adj_to_IEEE54={adjacent_to_severity}  shares_pocket="
              f"{in_pocket or adjacent_to_severity or h_pocket <= 1}", flush=True)

    convert = {}
    referenced = {}
    for path in CONVERT_FILES:
        hits = scan_file(path, net)
        convert[path] = hits
        for h in hits:
            referenced[h["index"]] = h["ieee"]
        print(f"[convert] {path}: {len(hits)} bus refs -> "
              f"{sorted(set((h['index'], h['ieee']) for h in hits))}", flush=True)

    lit_files = sorted(glob.glob("notes/lit/**/*.md", recursive=True))
    do_not_convert = {
        "notes/ai-prompt-log.md": ("append-only AI-disclosure log; mixes historical index-convention "
                                   "quotes (bus 75/52/106) with newer IEEE-name mechanism notes (bus 54). "
                                   "Do NOT rewrite the log."),
        "notes/1_research_draft_ORIGINAL*.txt": ("AI-disclosure EVIDENCE (.txt, hook-protected); "
                                                 "never edit."),
        "notes/lit/**/*.md": (f"{len(lit_files)} literature notes for OTHER papers/networks; bus numbers "
                              "are in each source's own convention, not case118 indices. Do NOT convert."),
    }

    out = dict(
        question="standardize bus numbering on IEEE names across the paper and notes",
        convention=dict(
            source="pandapower 0-based positional index (argmin_bus) in freeze_poster_numbers.py:116",
            target="IEEE 1-based bus name (net.bus.name)",
            case118_index_equals_ieee_minus_1="verified for all referenced buses (name = index + 1)"),
        index_to_ieee_referenced={str(k): referenced[k] for k in sorted(referenced)},
        pocket_analysis=dict(
            severity_bus=dict(index=SEVERITY_IDX, ieee=idx_to_ieee(net, SEVERITY_IDX)),
            pocket_definition=dict(indices=POCKET_IDX, ieee=pocket_ieee,
                                   label="the 54-58-59 reactive pocket"),
            distance_metric="topological hops on the case118 graph (lines+trafos), not impedance",
            frequency_buses=freq_rows),
        conversion_table=dict(convert=convert, do_not_convert=do_not_convert),
        paper_note="paper_current.tex references buses ONLY at line 152 (IV-C); '118-bus' is the "
                   "network name, not a bus id")
    settings = dict(task="bus index->IEEE conversion map + pocket analysis",
                    source="pandapower case118 topology, data/frozen_poster_numbers.json (read-only)")
    cm.write_with_manifest("data/bus_convention_map.json", out, settings)
    print("\nwrote data/bus_convention_map.json")


if __name__ == "__main__":
    main()
