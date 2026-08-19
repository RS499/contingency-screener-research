import json
import re
import sys

# Decide whether a Bash command writes to a report/ prose file.
#
# Kept in its own file rather than a heredoc inside the shell hook: a quoted
# heredoc nested in $( ... ) whose body contains unbalanced quote characters
# breaks the bash parser, which is exactly how this guard first failed.
#
# PRECISION: require BOTH a write-capable operator AND a report/ path with a
# prose extension. guard_python.sh in this repo fires on the literal word
# "python" inside a quoted echo string; that false positive is the thing this
# design avoids. Read-only commands that merely mention report/ pass.

PATH_RE = r'[^\s;|&<>\'"]*\breport/[^\s;|&<>\'"]*\.(?:tex|md)\b'

PATTERNS = [
    (r'>>?\s*' + PATH_RE, "shell redirection"),
    (r'\btee\b(?:\s+-\S+)*\s+' + PATH_RE, "tee"),
    (r'\bsed\b[^;|&]*?-i[^;|&]*?' + PATH_RE, "sed -i"),
    (r'\bperl\b[^;|&]*?-i[^;|&]*?' + PATH_RE, "perl -i"),
    (r'\b(?:cp|mv|install|rsync)\b[^;|&]*?' + PATH_RE, "copy/move"),
    (r'\bdd\b[^;|&]*?of=' + PATH_RE, "dd"),
    (r'\btruncate\b[^;|&]*?' + PATH_RE, "truncate"),
]


def read_command(stream):
    try:
        payload = json.load(stream)
    except Exception:
        return ""
    tool_input = payload.get("tool_input", {})
    return tool_input.get("command", "") or ""


def classify(cmd):
    for pattern, label in PATTERNS:
        if re.search(pattern, cmd):
            return label
    return ""


if __name__ == "__main__":
    command = read_command(sys.stdin)
    verdict = classify(command)
    if verdict:
        print(f"BLOCK::{verdict}")
    else:
        print("ALLOW")
