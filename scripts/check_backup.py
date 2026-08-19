import os
import sys
import time

# notes/ is gitignored (.gitignore "Private - never commit to the public fork") and
# holds ai-prompt-log.md, prior-art.md, erratum.md, contribution-log.md, RUN_REPORT.md
# and the retired/ quarantine. It is the STS Task 5 evidentiary basis and the only
# directory here that git cannot recover.
#
# This gate does NOT just check that a backup exists. Stage 0 found a backup that was
# a byte-identical copy of a DIFFERENT clone's notes/ - stale by 12 days, 601 log lines
# short, missing three files - and it would have passed any existence check. So the
# gate compares content, not presence.

NOTES = "notes"
MAX_AGE_DAYS = 7
SEARCH_ROOTS = ["~/Desktop", "~/Documents", "~"]
PATTERNS = ["notes-backup", "notes_backup"]


def find_candidates():
    out = []
    seen = set()
    for root in SEARCH_ROOTS:
        base = os.path.expanduser(root)
        if not os.path.isdir(base):
            continue
        try:
            entries = os.listdir(base)
        except OSError:
            continue
        for name in entries:
            low = name.lower()
            if not any(p in low for p in PATTERNS):
                continue
            path = os.path.join(base, name)
            real = os.path.realpath(path)
            if real in seen or not os.path.isdir(path):
                continue
            seen.add(real)
            out.append(path)
    return sorted(out)


def rel_files(root):
    found = {}
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if name == ".DS_Store":
                continue
            full = os.path.join(dirpath, name)
            found[os.path.relpath(full, root)] = full
    return found


def diff_against_live(candidate):
    live = rel_files(NOTES)
    back = rel_files(candidate)
    missing = sorted(set(live) - set(back))
    extra = sorted(set(back) - set(live))
    differing = []
    for rel in sorted(set(live) & set(back)):
        try:
            same = (os.path.getsize(live[rel]) == os.path.getsize(back[rel])
                    and open(live[rel], "rb").read() == open(back[rel], "rb").read())
        except OSError:
            same = False
        if not same:
            differing.append(rel)
    return missing, extra, differing


def age_days(path):
    return (time.time() - os.path.getmtime(path)) / 86400.0


def main():
    if not os.path.isdir(NOTES):
        print(f"FAIL: {NOTES}/ absent")
        return 1

    live = rel_files(NOTES)
    print(f"live {NOTES}/: {len(live)} files")

    candidates = find_candidates()
    if not candidates:
        print(f"FAIL: no backup directory found under {', '.join(SEARCH_ROOTS)}")
        print("      searched for directory names containing: " + ", ".join(PATTERNS))
        print("      NOT PROOF OF ABSENCE: external volumes and cloud sync targets")
        print("      were not searched.")
        return 1

    good = 0
    for c in candidates:
        missing, extra, differing = diff_against_live(c)
        age = age_days(c)
        ok = (not missing) and (not differing) and age <= MAX_AGE_DAYS
        verdict = "OK" if ok else "STALE/INCOMPLETE"
        print()
        print(f"  {verdict}  {c}")
        print(f"    age {age:.1f} d (limit {MAX_AGE_DAYS})   files {len(rel_files(c))}")
        if missing:
            print(f"    MISSING from backup ({len(missing)}): {', '.join(missing[:6])}")
        if differing:
            print(f"    CONTENT DIFFERS ({len(differing)}): {', '.join(differing[:6])}")
        if extra:
            print(f"    extra in backup ({len(extra)}): {', '.join(extra[:6])}")
        if missing or differing:
            print("    -> this backup does not protect the live notes/. A backup that")
            print("       copies a different clone passes an existence check and still")
            print("       loses the evidence.")
        if ok:
            good += 1

    print()
    if good:
        print(f"PASS: {good} backup(s) match the live notes/ and are within {MAX_AGE_DAYS} days")
        return 0
    print("FAIL: no backup both matches the live notes/ and is within the age limit")
    return 1


if __name__ == "__main__":
    sys.exit(main())
