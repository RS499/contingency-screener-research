import sys
import numpy as np
import generate_dataset as gd

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5000


def main():
    gd.apply_config(dict(dvm=0.025))
    net = gd.build_net()
    base = net["_gen_vm0"]
    ngen = len(base)

    lo = np.maximum(base - gd.DVM, gd.GEN_VM_LO)
    hi = np.minimum(base + gd.DVM, gd.VMAX_LIMIT)
    p_accept = (hi - lo) / (2.0 * gd.DVM)
    exp_redraws = 1.0 / p_accept

    rng = np.random.default_rng(0)
    tot = np.zeros(ngen, dtype=np.int64)
    per_scen_max = np.zeros(N, dtype=np.int64)
    for s in range(N):
        _, rd = gd.draw_gen_vm(base, rng)
        tot += rd
        per_scen_max[s] = int(rd.max())
    emp_mean = tot / N

    n_redrawing = int((exp_redraws > 1.0001).sum())
    print(f"draw_gen_vm redraws over {N} scenarios (DVM={gd.DVM}, bounds [{gd.GEN_VM_LO}, {gd.VMAX_LIMIT}])")
    print(f"  generators that ever redraw (base within DVM of a bound): {n_redrawing}/{ngen}")
    print(f"  mean redraws per scenario (summed over gens): {tot.sum()/N:.2f}")
    print(f"  max redraws in any single scenario          : {int(per_scen_max.max())}")
    print(f"  worst single-gen expected redraws           : {exp_redraws.max():.3f}")
    if n_redrawing > 0:
        order = np.argsort(exp_redraws)[::-1][:8]
        print("  top gens by expected redraws (gen, base_vm, p_accept, exp_redraws, emp_mean):")
        for i in order:
            if exp_redraws[i] <= 1.0001:
                break
            print(f"    gen {i:2d}  base={base[i]:.4f}  p={p_accept[i]:.3f}  "
                  f"exp={exp_redraws[i]:.3f}  emp={emp_mean[i]:.3f}")


if __name__ == "__main__":
    main()
