#!/usr/bin/env python3
import glob, os, re, shutil, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)
passed = failed = 0

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is missing:  python3 -m pip install pyyaml")


def check(desc, ok, hint=""):
    global passed, failed
    if ok:
        passed += 1; print("PASS  " + desc)
    else:
        failed += 1; print("FAIL  " + desc + (("   -> " + hint) if hint else ""))


UNTRUSTED = re.compile(r"\$\{\{\s*(github\.event\.(pull_request|issue|comment|review|head_commit|pages|commits|discussion)[^}]*|github\.head_ref|github\.event\.workflow_run\.head_branch)\s*\}\}")
SHA = re.compile(r"^[0-9a-f]{40}$")


def load(p):
    d = yaml.safe_load(open(p)) or {}
    if True in d and "on" not in d:   # YAML 1.1 reads the key `on` as the boolean True
        d["on"] = d.pop(True)
    return d


def triggers(d):
    on = d.get("on")
    return set(on) if isinstance(on, (dict, list)) else {on}


def steps(d):
    for jn, j in (d.get("jobs") or {}).items():
        for s in j.get("steps", []):
            yield jn, j, s


files = {os.path.basename(p): p for p in glob.glob(".github/workflows/*.yml") if os.path.basename(p) in ("ci.yml", "preview.yml", "release.yml")}
check("the three workflows (ci.yml, preview.yml, release.yml) are there and valid YAML", len(files) == 3)
if len(files) != 3:
    sys.exit(1)
docs = {n: load(p) for n, p in files.items()}

print("== Script injection ==")
for n, d in docs.items():
    bad = [s.get("name", "?") for _, _, s in steps(d) if s.get("run") and UNTRUSTED.search(s["run"])]
    check("%s: no attacker-controlled expression (title, body, branch ...) inside a `run:` script" % n, not bad, "pass it through `env:` and use \"$VAR\": steps %s" % bad)
    bad2 = [s.get("name", "?") for _, _, s in steps(d) if s.get("run") and re.search(r"\$\{\{\s*secrets\.", s["run"])]
    check("%s: no secret written into a `run:` script (use `env:` on that step)" % n, not bad2, str(bad2))

print("== Triggers and checkouts ==")
pre = docs["preview.yml"]
check("preview.yml does not use pull_request_target, or never checks out / runs the pull request's code", "pull_request_target" not in triggers(pre) or not any(
    "uses" in s and s["uses"].startswith("actions/checkout") and "head" in str((s.get("with") or {}).get("ref", "")) for _, _, s in steps(pre)), "a stranger's code must never run with your secrets")
check("preview.yml no longer hands a secret to code from the pull request", not any("secrets." in str(s.get("env", "")) for _, _, s in steps(pre)) or "pull_request_target" not in triggers(pre))

print("== Permissions ==")
for n, d in docs.items():
    top = d.get("permissions")
    jobs = [j.get("permissions") for j in (d.get("jobs") or {}).values()]
    allp = ([top] if top is not None else []) + [p for p in jobs if p is not None]
    wild = any(p == "write-all" for p in allp)
    ok = bool(allp) and not wild and (top is None or isinstance(top, dict))
    check("%s: `permissions:` is set and is not write-all" % n, ok, "start with `permissions: contents: read`")
def perm(d):
    p = d.get("permissions")
    return p if isinstance(p, dict) else None


check("ci.yml and preview.yml can only READ the repository contents (preview may also write pull-request comments)",
      all(perm(docs[n]) is not None and perm(docs[n]).get("contents") == "read" and all(v in ("read", "none") or k == "pull-requests" for k, v in perm(docs[n]).items()) for n in ("ci.yml", "preview.yml")))
rel = docs["release.yml"]
rj = (rel.get("jobs") or {}).get("release", {})
check("release.yml: contents: write only on the job that publishes (the workflow default is read)",
      perm(rel) is not None and perm(rel).get("contents") in ("read", None) and isinstance(rj.get("permissions"), dict) and rj["permissions"].get("contents") == "write")

print("== Supply chain ==")
for n, d in docs.items():
    unpinned = []
    for _, _, s in steps(d):
        u = s.get("uses")
        if not u or u.startswith("./"):
            continue
        name, _, ref = u.partition("@")
        if not SHA.match(ref):
            unpinned.append(u)
    check("%s: every action is pinned to a full 40-character commit SHA" % n, not unpinned, ", ".join(unpinned))
check("no `curl | bash` (or sh) anywhere", not any(re.search(r"(curl|wget)[^\n|]*\|\s*(sudo\s+)?(ba)?sh", s.get("run", "")) for d in docs.values() for _, _, s in steps(d)))
check("no action from an unknown owner on a moving branch (the notify action is gone or pinned)", not any(s.get("uses", "").startswith("some-random-org/") and not SHA.match(s["uses"].partition("@")[2]) for d in docs.values() for _, _, s in steps(d)))

print("== Hygiene ==")
for n, d in docs.items():
    check("%s: every job has timeout-minutes (a hijacked job must not run for six hours)" % n, all("timeout-minutes" in j for j in (d.get("jobs") or {}).values()))
check("release.yml has a concurrency group (two releases must not run at once)", "concurrency" in rel)
notes = open("SECURITY-NOTES.md").read() if os.path.exists("SECURITY-NOTES.md") else ""
check("SECURITY-NOTES.md explains the three workflows (no TODO left)", "TODO" not in notes and len(notes.split()) > 60)
if shutil.which("actionlint"):
    r = subprocess.run(["actionlint"] + list(files.values()), capture_output=True, text=True)
    check("actionlint finds no problem", r.returncode == 0, r.stdout[:300])
else:
    print("      (actionlint is not installed: skipped. Install it to catch typos in expressions.)")
check("the tests still pass (the pipeline must still work)", subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], capture_output=True).returncode == 0)
print()
print(("ALL CHECKS PASSED (%d/%d)" % (passed, passed)) if failed == 0 else ("%d check(s) failed, %d passed" % (failed, passed)))
sys.exit(1 if failed else 0)
