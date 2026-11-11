#!/usr/bin/env bash
rc=0
python3 -c "import yaml,glob;[yaml.safe_load(open(f)) for f in glob.glob(\".github/workflows/*.yml\")]" 2>/dev/null && echo "- ✅ the workflows are valid YAML" || { echo "- ❌ a workflow is not valid YAML (or PyYAML is missing)"; rc=1; }
grep -qE "write-all" .github/workflows/*.yml && { echo "- ❌ a workflow still has permissions: write-all"; rc=1; } || echo "- ✅ no write-all"
grep -q "TODO" SECURITY-NOTES.md && { echo "- ❌ SECURITY-NOTES.md still has TODO"; rc=1; } || echo "- ✅ SECURITY-NOTES.md is filled in"
grep -qE "^ALL CHECKS PASSED \(" SUBMISSION.md && echo "- ✅ SUBMISSION.md shows ALL CHECKS PASSED" || { echo "- ❌ paste the verify.sh output (ALL CHECKS PASSED) into SUBMISSION.md"; rc=1; }
exit $rc
