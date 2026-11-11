#!/usr/bin/env bash
# Reads your three workflows and checks every hole is closed. Run with: ./verify.sh
cd "$(dirname "$0")" || exit 1
exec python3 .lab/wfcheck.py
