#!/usr/bin/env bash
set -euo pipefail

SNAPSHOT="${1:-2026-03-25}"
REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
EXIT_CODE=0
PASS=0
FAIL=0

check() {
  local name="$1" result="$2" detail="${3:-}"
  if [ "$result" = "true" ]; then
    echo "[PASS] $name"; PASS=$((PASS + 1))
  else
    echo "[FAIL] $name"; EXIT_CODE=1; FAIL=$((FAIL + 1))
  fi
  [ -n "$detail" ] && echo "       $detail"
}

# JSON count
SIGMA_JSON=$(python3 -c "import json; print(json.load(open('$REPO_ROOT/PROOF_PACK/verified_counts.json'))['counts']['sigma'])")
check "Sigma=103 (JSON)" "$([ "$SIGMA_JSON" = "103" ] && echo true || echo false)" "Actual: $SIGMA_JSON"

# Physical count
SIGMA_PHYS=$(find "$REPO_ROOT/content/detection-rules/sigma" -name "*.yml" | wc -l | tr -d ' ')
check "Physical Sigma=103" "$([ "$SIGMA_PHYS" = "103" ] && echo true || echo false)" "Found: $SIGMA_PHYS"

# Tactic dirs
TACTIC_COUNT=$(find "$REPO_ROOT/content/detection-rules/sigma" -maxdepth 1 -type d | tail -n +2 | wc -l | tr -d ' ')
check "10 tactic directories" "$([ "$TACTIC_COUNT" = "10" ] && echo true || echo false)" "Found: $TACTIC_COUNT"

# HTML data-verified
if [ -f "$REPO_ROOT/site/case-study-sigma-library.html" ]; then
  check "HTML data-verified=103" \
    "$(grep -q 'data-verified="sigma">103<' "$REPO_ROOT/site/case-study-sigma-library.html" && echo true || echo false)"
fi

# Sitemap
if [ -f "$REPO_ROOT/site/sitemap.xml" ]; then
  check "Sitemap includes sigma library" \
    "$(grep -q 'case-study-sigma-library' "$REPO_ROOT/site/sitemap.xml" && echo true || echo false)"
fi

echo ""
echo "========================================"
echo "PASS: $PASS / $((PASS + FAIL))   FAIL: $FAIL"
echo "Snapshot: $SNAPSHOT"
echo "========================================"
exit $EXIT_CODE
