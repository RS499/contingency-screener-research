import re
import json
import numpy as np

# Read-only numeric comparison of the N10 Part C artifacts (data/sts_n10_fig_*, data/sts_n10_tables.*) with the
# owner's data/sts_paper_* versions (scripts/sts_paper_corrected.py). Nothing under data/ is written.
# Output: scratch/n10_vs_paper_check.md

OUT = "scratch/n10_vs_paper_check.md"


def load(p):
    return json.load(open(p))


def fig2(lines):
    mine = load("data/sts_n10_fig_tradeoff.json")["models"]
    theirs = load("data/sts_paper_fig2_tradeoff.json")["models"]
    lines.append("## Fig. 2 — escalation / missed vs target (values JSON)\n")
    lines.append("| model | points (mine / theirs) | targets identical | max abs diff: escalation, escalation_std, missed, missed_std |")
    lines.append("|---|---|---|---|")
    for m in ["ridge", "histgb"]:
        a = mine[m]["points"]
        b = theirs[m]
        same_t = [round(x["coverage_target"], 2) for x in a] == [round(x["target"], 2) for x in b]
        d = [max(abs(x["escalation"] - y["escalation"]) for x, y in zip(a, b)),
             max(abs(x["escalation_std"] - y["escalation_std"]) for x, y in zip(a, b)),
             max(abs(x["missed_viol"] - y["missed"]) for x, y in zip(a, b)),
             max(abs(x["missed_viol_std"] - y["missed_std"]) for x, y in zip(a, b))]
        lines.append(f"| {m} | {len(a)} / {len(b)} | {same_t} | {d[0]:.3g}, {d[1]:.3g}, {d[2]:.3g}, {d[3]:.3g} |")
    lines.append("")
    lines.append("- Image-level difference, not a number: mine draws the first-sub-1% dash-dot markers with value labels "
                 f"(ridge {mine['ridge']['first_sub_1pct_missed_coverage']}, histgb {mine['histgb']['first_sub_1pct_missed_coverage']}); "
                 "yours omits them by design (its note: \"" + load("data/sts_paper_fig2_tradeoff.json")["note"] + "\").\n")


def fig3(lines):
    mine = load("data/sts_n10_fig_missdepth.json")["per_model"]
    theirs = load("data/sts_paper_fig3_missdepth.json")["models"]
    lines.append("## Fig. 3 — miss depth at 0.90 (values JSON)\n")
    lines.append("| model | n misses (mine / theirs) | q̂@0.90 mean abs diff | max depth abs diff |")
    lines.append("|---|---|---|---|")
    for m in ["ridge", "histgb"]:
        a, b = mine[m], theirs[m]
        lines.append(f"| {m} | {a['n_misses']} / {b['n_misses_pooled']} | {abs(a['qhat90_mean'] - b['qhat90_mean']):.3g} | "
                     f"{abs(a['max_depth_pu'] - b['max_depth']):.3g} |")
    lines.append("")
    lines.append("- Fields only in yours (share_within_qhat, share_deeper_than_0p005, p99_depth) and only in mine (per-bin counts) "
                 "are not compared.\n")


def fig4(lines):
    a = load("data/sts_n10_fig_boundary.json")
    b = load("data/sts_paper_fig4_boundary.json")
    lines.append("## Fig. 4 — corrected min_vm histogram (values JSON)\n")
    lines.append("| quantity | mine | theirs | abs diff |")
    lines.append("|---|---|---|---|")
    pairs = [("n rows", a["n_rows"], b["n_rows"]),
             ("boundary mass (%)", 100 * a["boundary_mass_0p94_0p945"], b["boundary_mass_pct"]),
             ("violation rate (%)", 100 * a["violation_rate"], b["violation_rate_pct"]),
             ("tallest bin share (%)", a["tallest_bin_pct"], b["tallest_bin_share_pct"]),
             ("tallest bin left edge (pu)", a["tallest_bin_left"], b["tallest_bin_left"]),
             ("share below 0.87 view (%)", 100 * a["share_below_view_0p87"], b["share_below_view_lo_pct"])]
    for name, x, y in pairs:
        lines.append(f"| {name} | {x!r} | {y!r} | {abs(x - y):.3g} |")
    lines.append("")


def budget(lines):
    a = load("data/sts_n10_fig_budget.json")
    b = load("data/sts_paper_fig_budget.json")
    lines.append("## Budget-curve figure\n")
    lines.append(f"- Both are drawn from the same source: mine `{a['source']}`, yours `{b['source']}`.")
    lines.append(f"- Your values JSON carries no curve values (panels hold only n_splits = {b['panels']['D94']['n_splits']} and "
                 f"k_max = {b['panels']['D94']['k_max']}), so curve values cannot be compared file to file.")
    lines.append(f"- k_max: mine {len(a['k'])}, yours {b['panels']['D94']['k_max']}; x view: mine {a['x_view']}, yours \"{b['x_view']}\".")
    lines.append("- Content differences, not numbers: mine draws ridge and histgb rankings and bands the oracle; yours draws "
                 f"histgb only (family = {b['family']}) and draws the oracle without a band.\n")


def tex_rows(path):
    rows = {}
    section = None
    for line in open(path):
        if line.startswith("%%%%"):
            section = line.strip("% \n")
            rows[section] = []
            continue
        if section and "&" in line and not line.startswith("%"):
            rows[section].append([c.strip() for c in line.split("%")[0].replace("\\\\", "").split("&")])
    return rows


def cell_num(c):
    c = c.replace("$", "").replace("\\pm", " ").replace("{\\times}", "e")
    return [float(x) for x in re.findall(r"-?\d+\.\d+|-?\d+", c)]


def tables(lines):
    mine = tex_rows("data/sts_n10_tables.tex")
    theirs = tex_rows("data/sts_paper_tables.tex")
    mk = [k for k in mine if "tab:ops" in k][0]
    tk = [k for k in theirs if k.startswith("tab:ops body")][0]
    lines.append("## Table bodies (printed cells, `data/sts_n10_tables.tex` vs `data/sts_paper_tables.tex`)\n")
    lines.append("Comparison is of the printed (rounded) cells; the largest difference is in the printed units.\n")
    lines.append("### tab:ops (the 12 grid-target rows)\n")
    lines.append("| row | identical text | largest numeric diff |")
    lines.append("|---|---|---|")
    tmap = {(r[0], r[1]): r for r in theirs[tk]}
    for r in mine[mk]:
        t = tmap.get((r[0], r[1]))
        if t is None:
            lines.append(f"| {r[0]} {r[1]} | missing in yours | — |")
            continue
        diff = max(abs(x - y) for x, y in zip(sum([cell_num(c) for c in r[2:]], []), sum([cell_num(c) for c in t[2:]], [])))
        lines.append(f"| {r[0]} {r[1]} | {r == t} | {diff:.3g} |")
    extra = [r for r in theirs[tk] if (r[0], r[1]) not in {(x[0], x[1]) for x in mine[mk]}]
    lines.append("")
    lines.append(f"- Rows only in yours: {len(extra)} ({', '.join(r[0] + ' ' + r[1] for r in extra)}); not in the N10 spec.\n")
    mk2 = [k for k in mine if "tab:models" in k][0]
    tk2 = [k for k in theirs if "tab:models" in k][0]
    lines.append("### tab:models (4 rows)\n")
    lines.append("| row | identical text | largest numeric diff | note |")
    lines.append("|---|---|---|---|")
    tmap = {r[0]: r for r in theirs[tk2]}
    for r in mine[mk2]:
        t = tmap[r[0]]
        diff = max(abs(x - y) for x, y in zip(sum([cell_num(c) for c in r[1:]], []), sum([cell_num(c) for c in t[1:]], [])))
        note = ""
        if r != t:
            note = "; ".join(f"col {i}: mine `{x}` vs yours `{y}`" for i, (x, y) in enumerate(zip(r, t)) if x != y)
        lines.append(f"| {r[0]} | {r == t} | {diff:.3g} | {note} |")
    lines.append("")
    # full-precision check where your JSON carries it: persistence and train-mean per seed
    tj = load("data/sts_paper_tables.json")["tab_models_baselines_per_seed"]
    mj = load("data/sts_n10_tables.json")["rows"]
    lines.append("### Full-precision check: persistence and train mean (your JSON per-seed rows vs my JSON means)\n")
    lines.append("| model | quantity | mine (mean) | yours (mean of per-seed) | abs diff |")
    lines.append("|---|---|---|---|---|")
    for m in ["persistence", "train_mean"]:
        rows = [r for r in tj if r["model"] == m]
        for q, key, scale in [("MAE (mV)", "mae", 1000.0), ("R2", "r2", 1.0), ("escalation (%)", "escalation", 100.0),
                              ("missed (%)", "missed", 100.0), ("speedup A", "speedup_A", 1.0)]:
            y = float(np.mean([r[key] for r in rows])) * scale
            src = {"mae": "mae", "r2": "r2", "escalation": "esc", "missed": "mis", "speedup_A": "spd"}[key]
            x = mj[m][src][0] if key in ("mae", "r2") else mj[m]["0.9"][src][0]
            lines.append(f"| {m} | {q} | {x!r} | {y!r} | {abs(x - y):.3g} |")
    lines.append("")
    lines.append("- Sections only in yours (not in the N10 spec, so not compared): tab:ops held-out rows, the speedup-B "
                 "variant, the floor table, and gate vs static.\n")


def main():
    lines = ["# N10 Part C vs `data/sts_paper_*` — numeric check\n",
             "Read-only comparison (scratch/n10_vs_paper_check.py). No `data/sts_paper_*` file was modified. "
             "\"abs diff\" is the largest absolute difference over the compared values; 0 means equal to the last bit.\n"]
    fig2(lines)
    fig3(lines)
    fig4(lines)
    budget(lines)
    tables(lines)
    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
