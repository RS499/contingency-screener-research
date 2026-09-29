#!/bin/sh
# Commit plan, written 2026-09-21. Review, then run from the repo root: sh notes/commit-plan.sh
# Nothing here has been run. Four commits, grouped by intent.
set -e

# 1. Prose-free figure variants (default output of each script is byte-identical to the old PNGs)
git add feasibility/boundary_mass_hist.py feasibility/gate_schematic.py scripts/miss_depth_fig.py \
  data/boundary_mass_hist_v2.png data/boundary_mass_hist_v2.manifest.json \
  data/gate_schematic_v4.png data/gate_schematic_v4.manifest.json \
  data/miss_depth_v3.png data/miss_depth_v3.manifest.json
git commit -m "Add prose-free figure options; generate boundary_mass_hist_v2, gate_schematic_v4, miss_depth_v3"

# 2. STS report, plus the tracked source for the clip-artifact numbers it cites
git add report/paper_current_STS.tex scripts/clip_artifact.py \
  data/clip_artifact.json data/clip_artifact.manifest.json
git commit -m "STS report: title page and footer, prose-free figures with expanded captions, clip-artifact note backed by data/clip_artifact.json, reject-option and selective-prediction references, DOIs"

# 3. URTC camera-ready (confirm the dated snapshot was meant to be edited before running)
git add paper_current_URTC_20260808.tex
git commit -m "URTC camera-ready: IEEE copyright line, dataset description rewrite, tightened prose and scoping"

# 4. Unconditioned (no N-0 gate) confound analysis
git add scripts/uncond_analysis.py data/unconditioned_base.json \
  data/unconditioned_base.manifest.json data/unconditioned_base.parquet
git commit -m "Add unconditioned (no N-0 gate) build and boundary-mass confound analysis"

# Left out on purpose: SAHA.RAJAN.BIB.pdf (stale references printout) and
# "report/STS Activities Science Fair Projects.md" (personal application material).
# To keep them out permanently, uncomment:
# printf '%s\n' 'SAHA.RAJAN.BIB.pdf' 'report/STS Activities Science Fair Projects.md' >> .gitignore
# git add .gitignore && git commit -m "Ignore personal STS application files"
