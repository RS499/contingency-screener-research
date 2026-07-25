import json
import manifest as mf

IN = "data/tradeoff_curve.json"
OUT = "data/safety_operating_points.json"
LEVELS = [0.90, 0.94, 0.95, 0.96, 0.97, 0.98]
MODELS = ["ridge", "histgb"]


def pick(records, model, cov):
    for r in records:
        if r["model"] == model and abs(r["coverage_target"] - cov) < 1e-9:
            return r
    return None


def main():
    with open(IN) as f:
        d = json.load(f)
    recs = d["records"]

    rows = []
    print(f"safety-first operating points (from {IN})")
    print(f"{'model':8s} {'covT':>5s} {'covEmp%':>8s} {'esc%':>7s} {'missed%':>8s} {'speedup':>8s}")
    for model in MODELS:
        for cov in LEVELS:
            r = pick(recs, model, cov)
            if r is None:
                print(f"{model:8s} {cov:5.2f}   (coverage level not in tradeoff_curve.json)")
                continue
            rows.append(dict(model=model, coverage_target=cov,
                             coverage_emp=r["coverage_emp"], escalation=r["escalation"],
                             missed_viol=r["missed_viol"], net_speedup=r["net_speedup"]))
            print(f"{model:8s} {cov:5.2f} {r['coverage_emp']*100:8.1f} {r['escalation']*100:7.1f} "
                  f"{r['missed_viol']*100:8.2f} {r['net_speedup']:7.2f}x")

    out = dict(source=IN, coverage_levels=LEVELS, models=MODELS, rows=rows)
    mf.write_with_manifest(OUT, out)
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
