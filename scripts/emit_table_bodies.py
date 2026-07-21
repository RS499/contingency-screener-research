import json
import statistics

SCREENER = "data/screener_metrics.json"
TRADEOFF = "data/tradeoff_curve.json"
OPS_TARGETS = [0.90, 0.94, 0.95, 0.96, 0.97, 0.98]


def mean(values):
    return sum(values) / len(values)


def pstd(values):
    return statistics.pstdev(values)


def collect_raw(records):
    raw = {}
    for r in records:
        model = raw.setdefault(r["model"], {})
        for m in ("escalation", "coverage", "missed_viol", "net_speedup", "mae", "r2"):
            model.setdefault(m, []).append(r[m])
    return raw


def tradeoff_lookup(records):
    table = {}
    for r in records:
        table[(r["model"], round(r["coverage_target"], 2))] = r
    return table


def cell(m, s, dec):
    return f"{m:.{dec}f}$\\pm${s:.{dec}f}"


def r2_cell(m, s):
    if m < 0:
        return f"$-{abs(m):.2f}\\pm{s:.2f}$"
    return f"{m:.2f}$\\pm${s:.2f}"


def ops_row(label, cov, esc, cvg, mis, spd):
    return (f"{label:6s} & {cov:.2f} & {cell(esc[0], esc[1], 1)} & {cell(cvg[0], cvg[1], 1)} & "
            f"{cell(mis[0], mis[1], 2)} & {cell(spd[0], spd[1], 2)} \\\\")


def emit_ops_body(raw, tlook):
    lines = []
    for model in ("ridge", "histgb"):
        for cov in OPS_TARGETS:
            if cov == 0.90:
                e = raw[model]
                esc = (mean(e["escalation"]) * 100, pstd(e["escalation"]) * 100)
                cvg = (mean(e["coverage"]) * 100, pstd(e["coverage"]) * 100)
                mis = (mean(e["missed_viol"]) * 100, pstd(e["missed_viol"]) * 100)
                spd = (mean(e["net_speedup"]), pstd(e["net_speedup"]))
            else:
                r = tlook[(model, cov)]
                esc = (r["escalation"] * 100, r["escalation_std"] * 100)
                cvg = (r["coverage_emp"] * 100, r["coverage_emp_std"] * 100)
                mis = (r["missed_viol"] * 100, r["missed_viol_std"] * 100)
                spd = (r["net_speedup"], r["net_speedup_std"])
            lines.append(ops_row(model, cov, esc, cvg, mis, spd))
    return lines


def emit_models_body(raw):
    labels = {"persistence": "persistence", "train_mean": "train mean",
              "ridge": "ridge", "histgb": "gradient-boosted"}
    lines = []
    for model in ("persistence", "train_mean", "ridge", "histgb"):
        e = raw[model]
        mae = cell(mean(e["mae"]), pstd(e["mae"]), 4)
        r2 = r2_cell(mean(e["r2"]), pstd(e["r2"]))
        esc = cell(mean(e["escalation"]) * 100, pstd(e["escalation"]) * 100, 1)
        mis = cell(mean(e["missed_viol"]) * 100, pstd(e["missed_viol"]) * 100, 2)
        if model == "train_mean":
            spd = "$2.1{\\times}10^{7\\dagger}$"
        else:
            spd = cell(mean(e["net_speedup"]), pstd(e["net_speedup"]), 2)
        lines.append(f"{labels[model]:16s} & {mae} & {r2} & {esc} & {mis} & {spd} \\\\")
    return lines


def main():
    with open(SCREENER) as f:
        raw = collect_raw(json.load(f)["records"])
    with open(TRADEOFF) as f:
        tlook = tradeoff_lookup(json.load(f)["records"])

    print("% tab:ops body")
    for line in emit_ops_body(raw, tlook):
        print(line)
    print()
    print("% tab:models body")
    for line in emit_models_body(raw):
        print(line)


if __name__ == "__main__":
    main()
