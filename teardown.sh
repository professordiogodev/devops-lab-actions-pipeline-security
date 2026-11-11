#!/usr/bin/env bash
# This lab creates nothing outside your repository. Run with: ./teardown.sh
cd "$(dirname "$0")" || exit 1
find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
echo "Nothing was created outside this folder."
echo "Now run ./verify-teardown.sh"
