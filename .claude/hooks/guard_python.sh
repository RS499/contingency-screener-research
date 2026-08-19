#!/usr/bin/env bash
# PreToolUse guard: enforce .venv/bin/python for all reproduction.
#
# WHY A HOOK, NOT A PROMPT RULE: hooks fire inside subagents too, and subagents do
# NOT inherit the main agent's permissions or memory. A convention in CLAUDE.md is
# context a model can drift from; this hook is the real enforcement gate.
#
# exit 2 = BLOCK the Bash call (the model sees stderr and the command does not run).
# exit 1 = warn only (the command would still run) — never use 1 to block.
#
# Bare `python` / `python3` on PATH is the wrong interpreter (3.12 / scikit-learn 1.8)
# and silently changes numerical results (notes/repro-fixes.md section 3). All runs must
# use .venv/bin/python. This blocks a python/python3 command word that is NOT part of a
# path (so .venv/bin/python — where python is preceded by "/" — is allowed).
set -euo pipefail
input=$(cat)
cmd=$(printf '%s' "$input" | python3 -c 'import sys,json
try:
    d=json.load(sys.stdin)
    print(d.get("tool_input",{}).get("command",""))
except Exception:
    print("")' 2>/dev/null || printf '')

# python/python3 as a command word: at start or after ; & | or whitespace, and NOT
# preceded by "/" (which would make it .venv/bin/python or another explicit path).
if printf '%s' "$cmd" | grep -Eq '(^|[;&|]|[[:space:]])python3?([[:space:]]|$)'; then
  echo "BLOCKED (interpreter): use .venv/bin/python, never bare python/python3. Bare python is 3.12 / scikit-learn 1.8 and changes numerical results (notes/repro-fixes.md section 3)." >&2
  exit 2
fi

exit 0
