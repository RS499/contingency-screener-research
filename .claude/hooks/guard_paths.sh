#!/usr/bin/env bash
# PreToolUse guard: read-only freeze + AI-disclosure-evidence protection.
#
# WHY A HOOK, NOT A PROMPT RULE: hooks fire inside subagents too, and subagents do
# NOT inherit the main agent's permissions or memory. A convention in CLAUDE.md is
# context a model can drift from; this hook is the real enforcement gate.
#
# exit 2 = BLOCK the tool call (the model sees stderr and the edit does not happen).
# exit 1 = warn only (the action would still proceed) — never use 1 to block.
#
# Blocks Write/Edit to:
#   data/frozen_poster_numbers.json, data/screener_metrics.json   (the read-only freeze)
#   notes/1_research_draft*.txt                                    (AI-disclosure evidence)
set -euo pipefail
input=$(cat)
fp=$(printf '%s' "$input" | python3 -c 'import sys,json
try:
    d=json.load(sys.stdin)
    print(d.get("tool_input",{}).get("file_path",""))
except Exception:
    print("")' 2>/dev/null || printf '')

case "$fp" in
  *frozen_poster_numbers.json)
    echo "BLOCKED (read-only freeze): data/frozen_poster_numbers.json is READ-ONLY. Write a NEW file (e.g. *_v2.json) instead." >&2
    exit 2 ;;
  *screener_metrics.json)
    echo "BLOCKED (read-only freeze): data/screener_metrics.json is READ-ONLY. Write a NEW file instead." >&2
    exit 2 ;;
esac

case "$fp" in
  *notes/1_research_draft*.txt)
    echo "BLOCKED (AI-disclosure evidence): notes/1_research_draft*.txt is the recovered agent-drafted reference and must never be written to. The live draft is paper_current.tex." >&2
    exit 2 ;;
esac

exit 0
