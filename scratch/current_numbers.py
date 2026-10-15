import os
import sys
import json
import time
import hashlib
import platform
import numpy as np
import pandas as pd
import pandapower.networks as pn

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "feasibility"))
import manifest as mf

# Current numbers after N14: one row per number the paper can use, with its source file and key.
# Read-only: reads the N13/N14 result files and the rebuilt datasets; fits no model and runs no solve.
# Output: data/sts_current_numbers.json (+ manifest) and the markdown table printed to stdout.

OUT = "data/sts_current_numbers.json"
LIMIT = 0.94
ROWS = []


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    with open(path) as f:
        return json.load(f)


def pm(mean, std, scale, nd):
    return f"{scale * mean:.{nd}f} ± {scale * std:.{nd}f}"


def add(group, quantity, value, source, key):
    ROWS.append(dict(group=group, quantity=quantity, value=value, source=source, key=key))


def ms_of(vals):
    v = np.array(vals, dtype=float)
    return float(v.mean()), float(v.std())


def held_out(gate_path, fam):
    g = load(gate_path)
    return sorted([p for p in g["points"] if p["family"] == fam and p["point"] == "held_out"], key=lambda p: p["seed"])


def gate_rows(group, gate_path, fam):
    p = held_out(gate_path, fam)
    key = f"points[family={fam}, point=held_out], 5 splits"
    per = " / ".join([f"{100 * x['missed']:.2f}" for x in p])
    n_le = sum([x["missed"] <= 0.01 for x in p])
    m, s = ms_of([x["target"] for x in p])
    add(group, f"{fam} held-out target", pm(m, s, 1, 3), gate_path, key + " → target")
    for name, scale, nd, unit in [("escalation", 100, 1, "%"), ("flag_share", 100, 1, "%"), ("missed", 100, 2, "%"),
                                  ("speedup_A", 1, 2, ""), ("speedup_B", 1, 2, ""), ("q_hat", 1000, 2, " mV"),
                                  ("gate_catch", 100, 2, "%"), ("static_catch_B", 100, 2, "%")]:
        m, s = ms_of([x[name] for x in p])
        add(group, f"{fam} held-out {name}", pm(m, s, scale, nd) + unit, gate_path, key + f" → {name}")
    add(group, f"{fam} held-out missed per split", per + f" % ({n_le}/5 ≤ 1%)", gate_path, key + " → missed")


def compare_rows(table, group):
    d = load("data/sts_n13_compare.json")
    for r in d["rows"]:
        if r["table"] != table:
            continue
        k = r["key"]
        if r.get("rebuilt_mean") is None:
            continue
        scale, nd, unit = 1, 3, ""
        if ("escalation" in k) or ("missed" in k) or (k.endswith("r2") is False and "share" in k):
            scale, nd, unit = 100, 2, "%"
        if "mae" in k:
            nd = 2
        if "r2" in k:
            nd = 3
        if "speedup" in k:
            nd = 2
        add(group, k, pm(r["rebuilt_mean"], r["rebuilt_std"] or 0.0, scale, nd) + unit,
            "data/sts_n13_compare.json", f"rows[table={table}, key='{k}'] → rebuilt_mean/std")


def dataset_rows(group, path, drop):
    df = pd.read_parquet(path, columns=["outaged_type", "outaged_idx", "converged", "min_vm", "max_vm", "argmin_bus"])
    n1 = df[(df["outaged_type"] != "none") & (df["converged"])]
    for t, i in drop:
        n1 = n1[~((n1["outaged_type"] == t) & (n1["outaged_idx"] == i))]
    y = n1["min_vm"].to_numpy()
    src = path + (" (trafo 63 removed)" if drop else "")
    add(group, "converged outage rows", f"{len(n1):,}", src, "outaged_type != none & converged")
    add(group, "violation rate", f"{100 * (y < LIMIT).mean():.2f}%", src, "mean(min_vm < 0.94)")
    add(group, "boundary mass [0.94, 0.945)", f"{100 * ((y >= LIMIT) & (y < 0.945)).mean():.2f}%", src, "share of rows")
    add(group, "min_vm range", f"{y.min():.4f} to {y.max():.4f} pu", src, "min, max of min_vm")
    add(group, "rows in [0.940, 0.941)", f"{100 * ((y >= LIMIT) & (y < 0.941)).mean():.2f}%", src, "share of rows")
    add(group, "rows within 1e-3 pu of the limit", f"{100 * (np.abs(y - LIMIT) <= 1e-3).mean():.2f}%", src,
        "share with abs(min_vm - 0.94) <= 1e-3 (label set within switch-back tolerance)")
    add(group, "over-voltage share (max_vm > 1.05)", f"{100 * (n1['max_vm'].to_numpy() > 1.05).mean():.2f}%", src,
        "share of rows")
    ub, cb = np.unique(n1["argmin_bus"].to_numpy(), return_counts=True)
    order = np.argsort(cb)[::-1][:5]
    tops = ", ".join([f"index {int(ub[i])} (IEEE {int(ub[i]) + 1}) {100 * cb[i] / len(n1):.2f}%" for i in order])
    add(group, "critical-bus top 5 (argmin_bus share of rows)", tops, src,
        "feasibility/freeze_poster_numbers.py definition; 0-based index, IEEE name = index + 1 on case118")


def condhist_rows(group, path, net):
    s = load(path)["networks"][net]["summary"]
    key = f"networks.{net}.summary"
    for name in ["gate_catch", "static_fixed_catch", "condhist_catch", "global_static_catch"]:
        add(group, name, pm(s[name + "_mean"], s[name + "_std"], 100, 2) + "%", path, key + f" → {name}_mean/std")
    gap = s["global_static_catch_mean"] - s["static_fixed_catch_mean"]
    add(group, "GLOBAL-STATIC minus fixed static", f"{100 * gap:+.2f} pp", path, key + " (difference of means)")
    add(group, "rule-B solve share s_B", pm(s["s_B_mean"], s["s_B_std"], 100, 1) + "%", path, key + " → s_B")


def verdict_row(group, name, v, path, key):
    add(group, name, v, path, key)


def network_size(name):
    net = getattr(pn, name)()
    return len(net.bus), len(net.line) + len(net.trafo)


def main():
    t0 = time.time()
    v13 = load("data/sts_n13_verdicts.json")["verdicts"]
    v14 = load("data/sts_n14_verdicts.json")["verdicts"]
    vb = load("data/sts_n13_verdicts_tierB.json")["verdicts"]

    # case118 (D94): N13 rebuilt, restated by N14
    g = "D94 (case118, 0.94 floor)"
    compare_rows("tab:models", g + " — Table 1")
    compare_rows("tab:ops", g + " — Table 2")
    for fam in ["histgb", "ridge"]:
        gate_rows(g + " — held-out", "data/sts_n13_gate_D94.json", fam)
    dataset_rows(g + " — dataset", "data/sts_n13_D94.parquet", [])
    condhist_rows(g + " — baselines", "data/sts_n13_condhist.json", "D94")
    gu = load("data/sts_n13_guarantee.json")["networks"]["D94"]["histgb"]["per_split"]
    for cal in ["global_gate", "row_level", "base_level"]:
        for name, scale, nd in [("any_miss_share", 100, 1), ("escalation", 100, 1), ("missed", 100, 2), ("speedup_B", 1, 2)]:
            m, s = ms_of([x[cal][name] for x in gu])
            add(g + " — guarantee (histgb)", f"{cal} {name}", pm(m, s, scale, nd) + ("%" if scale == 100 else ""),
                "data/sts_n13_guarantee.json", f"networks.D94.histgb.per_split[].{cal}.{name}")
    for r in load("data/sts_n13_budget.json")["table"]:
        if r["family"] != "histgb":
            continue
        add(g + " — budget curve (histgb)", f"k = {r['k']}",
            f"ML {pm(r['surr_mean'], r['surr_std'], 100, 2)} vs static {pm(r['static_mean'], r['static_std'], 100, 2)}: {r['verdict']}",
            "data/sts_n13_budget.json", f"table[family=histgb, k={r['k']}]")
    n2 = [x for x in load("data/sts_n13_n2.json")["summary"] if x["family"] == "histgb"]
    for x in n2:
        add(g + " — N-2 (RQ2)", f"histgb {x['point']}: N-2 coverage / N-1 coverage",
            f"{pm(x['n2_coverage_mean'], x['n2_coverage_std'], 1, 4)} / {pm(x['n1_coverage_mean'], x['n1_coverage_std'], 1, 4)}",
            "data/sts_n13_n2.json", f"summary[family=histgb, point={x['point']}]")
        add(g + " — N-2 (RQ2)", f"histgb {x['point']}: N-2 missed", pm(x["n2_missed_mean"], x["n2_missed_std"], 100, 2) + "%"
            + f" ({x['n2_splits_missed_le_1pct']}/5 ≤ 1%)", "data/sts_n13_n2.json", f"summary[family=histgb, point={x['point']}]")
    for x in load("data/sts_n13_mondrian.json")["summary"]:
        add(g + " — Mondrian", f"{x['family']} gate vs static catch",
            f"{pm(x['gate_catch_mean'], x['gate_catch_std'], 100, 2)} vs {pm(x['static_catch_B_mean'], x['static_catch_B_std'], 100, 2)}",
            "data/sts_n13_mondrian.json", f"summary[family={x['family']}]")
    for x in load("data/sts_n13_floor.json")["per_floor"]:
        add("Floor dose-response (rebuilt)", f"floor {x['floor']} ({x['dataset']})",
            f"BM {x['BM']:.2f}%, CBM {x['CBM']:.2f}%, VR {x['VR']:.2f}%, rows {x['n_rows']:,}", "data/sts_n13_floor.json",
            f"per_floor[floor={x['floor']}]")
    fr = load("data/sts_n13_floorrep.json")["across"]
    add("Floor dose-response (rebuilt)", "0.95 builds D95a/b/c, mean ± std (ddof=0)",
        f"BM {fr['BM']['mean']:.2f} ± {fr['BM']['std_ddof0']:.2f}, CBM {fr['CBM']['mean']:.2f} ± {fr['CBM']['std_ddof0']:.2f}, "
        f"VR {fr['VR']['mean']:.2f} ± {fr['VR']['std_ddof0']:.2f}", "data/sts_n13_floorrep.json", "across")

    # Illinois (N14 primary: trafo 63 excluded)
    g = "ILL (case_illinois200, trafo 63 excluded)"
    gate_rows(g + " — held-out", "data/sts_n14_gate_ILL.json", "histgb")
    dataset_rows(g + " — dataset", "data/sts_n13_ILL.parquet", [("trafo", 63)])
    condhist_rows(g + " — baselines", "data/sts_n14_condhist.json", "ILL")
    gi = load("data/sts_n14_guarantee.json")["networks"]["ILL"]["histgb"]["per_split"]
    for cal in ["global_gate", "base_level"]:
        for name, scale, nd in [("any_miss_share", 100, 1), ("speedup_B", 1, 2)]:
            m, s = ms_of([x[cal][name] for x in gi])
            add(g + " — guarantee (histgb)", f"{cal} {name}", pm(m, s, scale, nd) + ("%" if scale == 100 else ""),
                "data/sts_n14_guarantee.json", f"networks.ILL.histgb.per_split[].{cal}.{name}")

    # case30_thermal (N13, restated by N14) and case24_ieee_rts (N14, under the amendment)
    for g, gate, ds, ch, net in [("C30 (case30_thermal)", "data/sts_n13_gate_C30.json", "data/sts_n13_C30.parquet",
                                  "data/sts_n13_condhist.json", "C30"),
                                 ("C24 (case24_ieee_rts, N14 amendment)", "data/sts_n14_gate_C24.json",
                                  "data/sts_n13_C24.parquet", "data/sts_n14_condhist.json", "C24")]:
        gate_rows(g + " — held-out", gate, "histgb")
        dataset_rows(g + " — dataset", ds, [])
        condhist_rows(g + " — baselines", ch, net)

    for g, name in [("case118", "case118"), ("ILL", "case_illinois200"), ("C30", "case30"), ("C24", "case24_ieee_rts")]:
        nb, nbr = network_size(name)
        add("Network size", g, f"{nb} buses, {nbr} branches", f"pandapower.networks.{name}()", "len(bus), len(line) + len(trafo)")

    # verdicts
    vg = "Verdicts (current)"
    verdict_row(vg, "V1 SAFER-94 (D94)", f"{'YES' if v13['V1_SAFER_94']['holds'] else 'NO'} ({v13['V1_SAFER_94']['splits_missed_le_1pct']}/5)",
                "data/sts_n13_verdicts.json", "verdicts.V1_SAFER_94")
    x = v13["V2_SAFETY_CHANGED"]
    verdict_row(vg, "V2 SAFETY-CHANGED (D94 rebuilt vs old)",
                f"{'YES' if x['holds'] else 'NO'}: {100 * x['rebuilt_mean']:.2f} ± {100 * x['rebuilt_std']:.2f}% vs {100 * x['old_mean']:.2f} ± {100 * x['old_std']:.2f}%",
                "data/sts_n13_verdicts.json", "verdicts.V2_SAFETY_CHANGED")
    # N14 primary holds all four networks (D94 and C30 restated from N13)
    prim = v14["primary"]
    for net in ["D94", "ILL", "C30", "C24"]:
        for vname, e in [("BEATS_STATIC", prim["BEATS_STATIC"][net]), ("GATE_BEATS_CONDHIST", prim["GATE_BEATS_CONDHIST"]["per_network"][net])]:
            gap = 100 * e["gap"]
            std = 100 * e["STD"]
            if e["holds"]:
                word = "YES"
            elif abs(gap) <= std:
                word = "NO: tie (within the larger std)"
            else:
                word = "NO: baseline higher beyond the larger std"
            key = f"verdicts.primary.{vname}" + (".per_network" if vname == "GATE_BEATS_CONDHIST" else "") + f".{net}"
            verdict_row(vg, f"{vname} {net}", f"{word}; gap {gap:+.2f} pp vs larger std {std:.2f}",
                        "data/sts_n14_verdicts.json", key)
    x = prim["SAFER_IL"]
    verdict_row(vg, "SAFER-IL", f"{'YES' if x['holds'] else 'NO'} ({x['splits_missed_le_1pct']}/5)", "data/sts_n14_verdicts.json", "verdicts.primary.SAFER_IL")
    verdict_row(vg, "ILL outcome wording (fixed in advance)", v14["ILL_outcome"]["wording"], "data/sts_n14_verdicts.json", "verdicts.ILL_outcome")
    x = v13["COVERAGE_HOLDS_N2"]
    verdict_row(vg, "COVERAGE-HOLDS-N2 (RQ2)",
                f"{'YES' if x['holds'] else 'NO'}: N-2 coverage {x['coverage_n2_mean']:.4f} ± {x['coverage_n2_std']:.4f} vs threshold {x['threshold']:.4f}",
                "data/sts_n13_verdicts.json", "verdicts.COVERAGE_HOLDS_N2")
    x = v13["MONDRIAN_BEATS_STATIC"]
    verdict_row(vg, "MONDRIAN-BEATS-STATIC", f"{'YES' if x['holds'] else 'NO'}: gap {100 * x['gap']:.2f} pp vs std {100 * x['STD']:.2f}",
                "data/sts_n13_verdicts.json", "verdicts.MONDRIAN_BEATS_STATIC")
    x = v13["FLOOR_DOSE_RESPONSE"]
    verdict_row(vg, "FLOOR_DOSE_RESPONSE (replication)",
                f"{'YES' if x['holds'] else 'NO'}: clause 1 {x['clause1']}, clause 2 {x['clause2']}; BM {x['bm']['0.93']:.2f} / {x['bm']['0.94']:.2f} / {x['bm']['0.95']:.2f} / {x['bm']['0.96']:.2f}",
                "data/sts_n13_verdicts.json", "verdicts.FLOOR_DOSE_RESPONSE")
    a = load("data/sts_n13_armF.json")["V3"]
    verdict_row(vg, "V3 MISMATCH-DRIVES-DRIFT-GAP (arm F, diagnostic)",
                f"{'YES' if a['MISMATCH_DRIVES_DRIFT_GAP'] else 'NO'}: >1e-3 drift bin missed {100 * a['pinned_mean']:.2f} ± {100 * a['pinned_std']:.2f}% (pinned inputs) vs {100 * a['corrected_mean']:.2f} ± {100 * a['corrected_std']:.2f}% (corrected); split 4 {100 * a['pinned_per_split'][4]:.2f} → {100 * a['corrected_per_split'][4]:.2f}%",
                "data/sts_n13_armF.json", "V3")
    tb = vg + " — tier B (rebuilt D95a; all ran except the D95c gate)"
    e = vb["SAFER_N5"]
    verdict_row(tb, "SAFER (N5 form, D95a)", f"{'YES' if e['holds'] else 'NO'} ({e['splits_missed_le_1pct']}/5)",
                "data/sts_n13_verdicts_tierB.json", "verdicts.SAFER_N5")
    e = vb["FASTER_N5"]
    c1 = e["clause1"]
    c2 = e["clause2"]
    verdict_row(tb, "FASTER (N5 form)",
                f"{'YES' if e['holds'] else 'NO'}: clause 1 {c1['holds']} (speedup B 0.95 {c1['speedup_B_095']:.2f} ± {c1['std_095']:.2f} vs 0.94 {c1['speedup_B_094']:.2f} ± {c1['std_094']:.2f}); "
                f"clause 2 {c2['holds']} (gate {100 * c2['gate_catch']:.2f} vs static {100 * c2['static_catch']:.2f}, diff {100 * c2['diff']:.2f} < {100 * c2['STD']:.2f})",
                "data/sts_n13_verdicts_tierB.json", "verdicts.FASTER_N5")
    e = vb["SHIFT_ADVANTAGE"]
    verdict_row(tb, "SHIFT-ADVANTAGE (D94 → D95a)",
                f"{'YES' if e['holds'] else 'NO'}: gate {pm(e['gate_catch_mean'], e['gate_catch_std'], 100, 2)} vs static {pm(e['static_catch_mean'], e['static_catch_std'], 100, 2)}",
                "data/sts_n13_verdicts_tierB.json", "verdicts.SHIFT_ADVANTAGE")
    bc = load("data/sts_n13_gate095bc.json")["builds"]
    for b in ["D95a", "D95b"]:
        h = bc[b]["histgb_held_out"]
        verdict_row(tb, f"{b} gate, histgb held-out",
                    f"escalation {pm(h['escalation']['mean'], h['escalation']['std'], 100, 1)}%, missed {pm(h['missed']['mean'], h['missed']['std'], 100, 2)}%",
                    "data/sts_n13_gate095bc.json", f"builds.{b}.histgb_held_out")
    verdict_row(tb, "D95c gate", "not run on rebuilt data (crash); report from the old build, labeled 'old build, uncorrected solver'",
                "data/sts_n11_gate_095bc.json", "N14 rule §C")
    sv = v14["sensitivity"]
    for net in ["D94", "ILL", "C30", "C24"]:
        for vname in ["BEATS_STATIC", "GATE_BEATS_CONDHIST"]:
            e = sv[vname][net]
            verdict_row(vg + " — islanding sensitivity (beside primary, never replaces it)", f"{vname} {net}",
                        f"{'YES' if e['holds'] else 'NO'}; gap {100 * e['gap']:+.2f} pp vs larger std {100 * e['STD']:.2f}",
                        "data/sts_n14_verdicts.json", f"verdicts.sensitivity.{vname}.{net}")

    out = dict(question="every number the paper can use after N14, with source file and key", rows=ROWS, n_rows=len(ROWS),
               wall_s=time.time() - t0)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    inputs = sorted(set([r["source"].split(" ")[0] for r in ROWS if r["source"].startswith("data/")]))
    man = dict(artifacts=[OUT], generating_script="scratch/current_numbers.py",
               regeneration_argv=[".venv/bin/python", "scratch/current_numbers.py"],
               script_sha256=sha256_of("scratch/current_numbers.py"), inputs={p: sha256_of(p) for p in inputs},
               model_hyperparameters="none (no model fit; reads stored results)",
               packages={p: mf.pkg_version(p) for p in mf.PACKAGES}, python=platform.python_version(),
               output_sha256=sha256_of(OUT), generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(OUT.replace(".json", ".manifest.json"), "w") as f:
        json.dump(man, f, indent=2)
    last = ""
    for r in ROWS:
        if r["group"] != last:
            print(f"\n**{r['group']}**\n")
            print("| Quantity | Value | Source → key |")
            print("|---|---|---|")
            last = r["group"]
        print(f"| {r['quantity']} | {r['value']} | `{r['source']}` → {r['key']} |")


if __name__ == "__main__":
    main()
