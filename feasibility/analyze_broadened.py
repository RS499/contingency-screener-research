import sys, json
import numpy as np
import pandas as pd

VMIN = 0.94
OLD_WINDOW = (0.940, 0.943)
OLD_DISTINCT_BUSES = 11
OLD_TOP2 = 98.5 

def pct(a, q): return float(np.percentile(a, q))

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/dataset.parquet"
    comp_s = float(sys.argv[2]) if len(sys.argv) > 2 else None
    df = pd.read_parquet(path)
    conv = df[df.converged].copy()
    viol = conv[conv.violation].copy()
    R = {}

    R["n_scen"] = int(df.scenario_id.nunique())
    R["n_rows"] = int(len(df))
    R["n_cols"] = int(df.shape[1])
    R["nonconv_rate"] = float((~df.converged).mean() * 100)
    R["nonconv_n"] = int((~df.converged).sum())
    R["n_conv"] = int(len(conv))
    R["n_viol"] = int(len(viol))
    R["viol_pct"] = float(len(viol) / len(conv) * 100)
    R["n_straddle"] = int(conv.straddle.sum())
    R["straddle_pct"] = float(conv.straddle.mean() * 100)
    R["n_safe"] = int((conv.min_vm > 0.95).sum())
    R["comp_s"] = comp_s

    mv = conv.min_vm.values
    R["minvm"] = {f"p{q}": pct(mv, q) for q in [0, 1, 5, 25, 50, 75, 95, 99, 100]}
    R["minvm_min"] = float(mv.min()); R["minvm_max"] = float(mv.max())
    R["minvm_width"] = float(mv.max() - mv.min())
    R["near_boundary_pct"] = float(((mv >= 0.935) & (mv <= 0.945)).mean() * 100)

    vc = viol.argmin_bus.value_counts()
    tot = int(vc.sum())
    R["distinct_buses"] = int(vc.size)
    R["top1_bus"] = int(vc.index[0]); R["top1_pct"] = float(vc.iloc[0] / tot * 100)
    R["top2_bus"] = int(vc.index[1]); R["top2_pct"] = float(vc.iloc[:2].sum() / tot * 100)
    R["top5_pct"] = float(vc.iloc[:5].sum() / tot * 100)
    R["top10_pct"] = float(vc.iloc[:10].sum() / tot * 100)
    R["top12"] = [(int(b), int(c), float(c / tot * 100)) for b, c in vc.head(12).items()]
    R["concentration_persists"] = bool(R["top2_pct"] > 80.0)

    R["by_mode"] = {}
    for m in df.sampling_mode.unique():
        s = conv[conv.sampling_mode == m]; sv = s[s.violation]
        vcm = sv.argmin_bus.value_counts()
        R["by_mode"][m] = dict(
            n=int(len(s)), viol_pct=float(s.violation.mean() * 100),
            straddle_pct=float(s.straddle.mean() * 100),
            distinct_buses=int(vcm.size),
            top2_pct=float(vcm.iloc[:2].sum() / vcm.sum() * 100) if vcm.size >= 2 else float("nan"),
            minvm_min=float(s.min_vm.min()), minvm_max=float(s.min_vm.max()),
        )

    with open("data/broadened_metrics.json", "w") as f:
        json.dump(R, f, indent=2)
    print(json.dumps(R, indent=2))
    return R

if __name__ == "__main__":
    main()
