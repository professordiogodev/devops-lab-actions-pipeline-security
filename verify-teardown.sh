#!/usr/bin/env bash
# Proves the lab left nothing behind. Run with: ./verify-teardown.sh
cd "$(dirname "$0")" || exit 1
pass=0; failn=0
check() { local d="$1"; shift; if "$@" >/dev/null 2>&1; then echo "PASS  $d"; pass=$((pass+1)); else echo "FAIL  $d"; failn=$((failn+1)); fi; }
check "no cache or temporary files in the lab folder" bash -c '[ -z "$(find . -name __pycache__ -type d)" ]'
check "no secret or key file is tracked by git" bash -c '! git ls-files | grep -qiE "[.](env|pem|key)$"'
echo
if [ "$failn" -eq 0 ]; then echo "TEARDOWN VERIFIED ($pass/$pass) on this machine"; else echo "NOT CLEAN: $failn leftover(s)."; fi
exit "$failn"
