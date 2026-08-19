#!/usr/bin/env bash
# PreToolUse guard: the AI-authorship boundary.
#
# STS 2027 requires the report be written by the student WITHOUT generative AI.
# Research use of AI is permitted and disclosable; authorship of the prose is not.
# This hook makes that boundary mechanical rather than remembered.
#
# Blocks Write / Edit / NotebookEdit to:
#   report/**/*.tex
#   report/**/*.md
#
# Agents own experiments, gates, figures, tables, and specifications. Every one of
# those lives outside report/. Nothing an agent legitimately produces needs to be
# written into report/, so this hook has no legitimate exception.
#
# exit 2 = BLOCK (the model sees stderr and the edit does not happen).
# exit 1 = warn only (the action would still proceed) -- never use 1 to block.
#
# KNOWN GAP: PreToolUse matchers are per-tool. This guards the file-editing tools.
# Shell writes (`> report/x.tex`, `tee`, `sed -i`, `cp`) are guarded separately by
# guard_report_bash.sh on the Bash matcher. Both must be registered in settings.json
# for the boundary to be closed.
set -euo pipefail
input=$(cat)

fp=$(printf '%s' "$input" | .venv/bin/python -c 'import sys,json
try:
    d = json.load(sys.stdin)
    ti = d.get("tool_input", {})
    print(ti.get("file_path") or ti.get("notebook_path") or "")
except Exception:
    print("")' 2>/dev/null || printf '')

# Normalise: strip any leading path up to and including a "report/" component, then
# test whether the remainder still looks like a report file. Matches both absolute
# and repo-relative forms.
case "$fp" in
  */report/*.tex|report/*.tex|*/report/*.md|report/*.md)
    echo "BLOCKED (authorship boundary): $fp" >&2
    echo "Prose is author-only. STS report text may not be agent-written." >&2
    echo "Agents own experiments, gates, figures, tables and specifications --" >&2
    echo "write those outside report/ (notes/, data/, scripts/)." >&2
    exit 2
    ;;
esac

exit 0
