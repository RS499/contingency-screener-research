import sys, os, warnings
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_dataset as gd
import case57_gonogo as c57
import manifest as mf

warnings.filterwarnings("ignore")

NETWORKS = ["case30", "case89pegase", "case300"]
N_DRAW = 50
OUT = "data/probe_alt_networks.json"


def nominal_n0(name):
    try:
        net = gd.build_net(name)
    except Exception as e:
        return {"network": name, "built": False, "error": str(e)}
    conv, vm = gd.solve(net, init="dc")
    if not conv or vm is None:
        return {"network": name, "built": True, "pinned_oracle_converges": False,
                "base_min_vm": None, "clears_0p94": None, "n_bus": int(len(net.bus))}
    mn = float(np.nanmin(vm))
    return {"network": name, "built": True, "pinned_oracle_converges": True,
            "n_bus": int(len(net.bus)),
            "base_min_vm": round(mn, 4),
            "buses_below_0p94": int((vm < gd.VMIN_LIMIT).sum()),
            "clears_0p94": bool(mn >= gd.VMIN_LIMIT),
            "margin_above_0p94": round(mn - gd.VMIN_LIMIT, 4)}


def draw_bases(name, n_draw, seed):
    gd.apply_config(c57.COMMITTED_CFG)
    net = gd.build_net(name)
    load_region, n_regions = gd.region_of_load(net)
    rng = np.random.default_rng(seed)
    accepted_vm = []
    all_vm = []
    n0_nonconv = 0
    for i in range(n_draw):
        mode = "independent" if (i % 2 == 0) else "regional"
        params = gd.sample_scenario(rng, net, mode, load_region, n_regions, stress=c57.STRESS)
        n0_conv, _vm0, n0_min_vm = gd.solve_n0(net, params)
        if not n0_conv:
            n0_nonconv += 1
            continue
        all_vm.append(n0_min_vm)
        if n0_min_vm >= gd.VMIN_LIMIT:
            accepted_vm.append(n0_min_vm)
    accepted_vm = np.array(accepted_vm)
    all_vm = np.array(all_vm)
    return {
        "network": name, "n_draw": n_draw, "seed": int(seed),
        "n0_nonconverged": n0_nonconv,
        "accepted": int(accepted_vm.size),
        "accept_rate_pct": round(100.0 * accepted_vm.size / n_draw, 2),
        "accepted_base_min_vm_range": ([round(float(accepted_vm.min()), 4),
                                        round(float(accepted_vm.max()), 4)]
                                       if accepted_vm.size else None),
        "all_converged_n0_min_vm_range": ([round(float(all_vm.min()), 4),
                                           round(float(all_vm.max()), 4)]
                                          if all_vm.size else None),
    }


def main():
    gd.apply_config(c57.COMMITTED_CFG)
    scan = [nominal_n0(n) for n in NETWORKS]

    clearing = [r for r in scan if r.get("clears_0p94")]
    best = max(clearing, key=lambda r: r["margin_above_0p94"]) if clearing else None

    draws = [draw_bases(r["network"], N_DRAW, c57.SEED) for r in clearing]
    draw = next((d for d in draws if best and d["network"] == best["network"]), None)

    out = {
        "purpose": "cheap go/no-go probe: is a same-rule out-of-sample comparison available on "
                   "another network? NOT a training dataset; no frozen artifact.",
        "config_source": "IMPORTED from case57_gonogo.COMMITTED_CFG + generate_dataset.py module "
                         "globals + generate_dataset.solve; NOT retyped. Documented committed build: "
                         "feasibility/broadened-diversity.md line 62.",
        "committed_cfg_used": c57.COMMITTED_CFG,
        "stress": c57.STRESS, "seed": c57.SEED,
        "solver": {"enforce_q_lims": True, "init": "dc", "numba": True, "algorithm": "nr"},
        "n0_gate": "accept iff N-0 converges and n0_min_vm >= 0.94",
        "vmin_limit": gd.VMIN_LIMIT,
        "step2a_nominal_n0_scan": scan,
        "step2b_best_margin_network": (best["network"] if best else None),
        "step2b_draw": draw,
        "step2b_draws_all_clearing": draws,
        "case57_reference": "NO-GO: nominal 0.7199 pu, 0/3000 accepted (data/case57_feasibility.json)",
        "pegase_caveat": "case89pegase uses PEGASE per-unit conventions; its native voltage band may "
                         "differ from the IEEE 0.94 floor. 'clears 0.94' can be physically "
                         "inapplicable — verify the operating limit before any same-rule claim.",
    }
    mf.write_with_manifest(OUT, out)

    print("STEP 2a — nominal N-0 under the pinned oracle:")
    for r in scan:
        print(f"  {r['network']:12s} conv={r.get('pinned_oracle_converges')} "
              f"base_min_vm={r.get('base_min_vm')} clears0.94={r.get('clears_0p94')} "
              f"margin={r.get('margin_above_0p94')}")
    print(f"\nSTEP 2b — best-margin clearing network: {best['network'] if best else None}")
    for d in draws:
        print(f"  {d['network']:12s} accepted={d['accepted']}/{d['n_draw']} "
              f"({d['accept_rate_pct']}%) n0_nonconv={d['n0_nonconverged']} "
              f"accepted_min_vm_range={d['accepted_base_min_vm_range']}")
    print(f"\nwrote {OUT} (+ .manifest.json)")


if __name__ == "__main__":
    main()
