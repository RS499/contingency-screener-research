import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import classical_manifest as cm

CONFIG = dict(
    limit_pu=0.94,
    seeds=5,
    std_convention="population std ddof=0 across the 5 seeds; a gap smaller than the larger of the "
                   "two stds is NOT a finding (std rule)",

    metric=dict(
        thresholds_pu=[0.01, 0.02, 0.05],
        primary_threshold_pu=0.02,
        primary=["n_misses_deeper_than_0.02_pu", "expected_shortfall_depth_given_miss"],
        expected_shortfall_def="E[depth | certified miss] = mean(0.94 - Y) over certified true "
                               "violations (depth in pu)",
        secondary="full miss-depth distribution with bootstrap CIs, pooled over the 5 splits",
        bootstrap=dict(n_boot=10000, ci=0.95, resample="pooled miss depths over 5 splits"),
        max_depth_role="FOOTNOTE only (one order statistic over a handful of events); never a headline"),

    coverage=dict(
        baseline_target=0.90,
        primary_basis="matched_empirical",
        also_report="matched_target",
        matched_empirical_def="for each arm/model, pick the coverage TARGET on the sweep grid whose "
                              "measured empirical coverage on test equals arm A's empirical coverage "
                              "at target 0.90 (nearest grid point; report the achieved empirical "
                              "coverage so the match is auditable)",
        sweep_grid=[round(0.70 + 0.01 * i, 2) for i in range(30)]),

    features=dict(
        headroom_def=dict(
            source="each base's N-0 solve (res_gen.q_mvar); requires re-solving the 1500 N-0 bases",
            q_headroom_up="max_q_mvar - q_mvar   (VAR the gen can still SUPPLY; binds under-voltage)",
            q_headroom_down="q_mvar - min_q_mvar (VAR the gen can still ABSORB)",
            per_gen="computed for every in-service generator"),
        arm_A="baseline features only (current design matrix)",
        arm_B="baseline + SCALARS: min q_headroom_up among gens within 1/2/3 graph-hops of EITHER "
              "terminal bus of the outaged element; total system q_headroom_up; (same three-hop + "
              "total for q_headroom_down). Scalars because ridge cannot represent a min over a set.",
        arm_C="arm_B + the raw per-generator q_headroom_up and q_headroom_down vectors (53*2 cols)",
        hop_distances=[1, 2, 3],
        report="per model (ridge, histgb), per arm (A, B, C)"),

    diagnostic=dict(
        qbind_label="a contingency is Q-BIND if, post-outage, any in-service gen has "
                    "q_mvar >= max_q_mvar - tol OR q_mvar <= min_q_mvar + tol",
        qbind_tolerance_mvar=1e-3,
        qbind_scope="labeled ONCE over the full N-1 dataset (seed-independent) by re-solving each "
                    "contingency with res_gen; reused across arms/seeds. This is the heavy compute: "
                    "~278,955 AC solves.",
        separation="AUC of the arm-B min-headroom scalar vs the Q-bind label",
        importance="permutation importance of the headroom features RESTRICTED to Q-bind rows",
        purpose="distinguish 'genuinely unpredictable' (feature has signal but tail unmoved) from "
                "'feature carries no signal'"),

    focus_case=dict(scenario_id=101000025, outaged_type="line", outaged_idx=78, truth_min_vm=0.84854,
                    report="each arm's prediction for this row"),

    do_not_assume="the tail may NOT collapse; an unchanged tail WITH confirmed feature signal is a "
                  "publishable result and must be reported as such",
)


def main():
    settings = dict(task="pin tail-metric / feature / diagnostic / comparison config (STEP 1)",
                    source="design spec; STEP 0 counts (data/miss_tail_counts.json)")
    cm.write_with_manifest("data/tail_metric_config.json", CONFIG, settings)
    print("wrote data/tail_metric_config.json")


if __name__ == "__main__":
    main()
