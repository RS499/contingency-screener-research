#!/usr/bin/env bash
# PreToolUse guard: the AI-authorship boundary, shell half.
#
# guard_report_prose.sh closes the Write/Edit/NotebookEdit path into report/.
# This closes the shell path, which is otherwise a complete bypass:
#   cat > report/x.tex    tee report/x.tex    sed -i ... report/x.tex
#   cp foo.tex report/    mv foo.tex report/x.tex
#
# The matching logic lives in report_bash_match.py. It is NOT inlined as a
# heredoc: a quoted heredoc nested in $( ... ) whose body contains unbalanced
# quote characters breaks the bash parser, and that is how this guard first
# failed -- it errored on every Bash call rather than on the ones it targets.
#
# FAIL-OPEN, DELIBERATELY: if the matcher cannot run, this exits 0 rather than
# blocking every shell command in the session. The Write/Edit hook is the
# primary boundary; this one is defence in depth. A guard that bricks the
# session is worse than a guard that occasionally misses, because the first
# thing anyone does with a bricked guard is remove it.
#
# exit 2 = BLOCK. exit 1 = warn only -- never use 1 to block.
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$here/../.." && pwd)"
py="$repo/.venv/bin/python"
matcher="$here/report_bash_match.py"

[ -x "$py" ] || exit 0
[ -f "$matcher" ] || exit 0

verdict="$("$py" "$matcher" 2>/dev/null)" || exit 0

case "$verdict" in
  BLOCK::*)
    op="${verdict#BLOCK::}"
    printf 'BLOCKED (authorship boundary): %s into report/\n' "$op" >&2
    printf 'Prose is author-only. STS report text may not be agent-written.\n' >&2
    printf 'Read-only inspection of report/ is allowed; writing to it is not.\n' >&2
    exit 2
    ;;
esac

exit 0
