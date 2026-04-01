#!/usr/bin/env bash
# Verification script for AutoSOC Pipeline Recovery case study
# Usage: ./verify.sh [--snapshot=2026-03-25]
set -euo pipefail

SNAPSHOT="${1:-2026-03-25}"
REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
EXIT_CODE=0
PASS=0
FAIL=0

check() {
  local name="$1" result="$2" detail="${3:-}"
  if [ "$result" = "true" ]; then
    echo "[PASS] $name"
    PASS=$((PASS + 1))
  else
    echo "[FAIL] $name"
    EXIT_CODE=1
    FAIL=$((FAIL + 1))
  fi
  [ -n "$detail" ] && echo "       $detail"
}

# ── Check 1: VERIFIED_COUNTS.md exists ──
check "VERIFIED_COUNTS.md exists" \
  "$([ -f "$REPO_ROOT/PROOF_PACK/VERIFIED_COUNTS.md" ] && echo true || echo false)"

# ── Check 2: verified_counts.json exists ──
check "verified_counts.json exists" \
  "$([ -f "$REPO_ROOT/PROOF_PACK/verified_counts.json" ] && echo true || echo false)"

# ── Check 3-8: JSON count parity ──
if [ -f "$REPO_ROOT/PROOF_PACK/verified_counts.json" ]; then
  SIGMA=$(python3 -c "import json; print(json.load(open('$REPO_ROOT/PROOF_PACK/verified_counts.json'))['counts']['sigma'])")
  SPLUNK=$(python3 -c "import json; print(json.load(open('$REPO_ROOT/PROOF_PACK/verified_counts.json'))['counts']['splunk'])")
  WAZUH_FILES=$(python3 -c "import json; print(json.load(open('$REPO_ROOT/PROOF_PACK/verified_counts.json'))['counts']['wazuh_xml_files'])")
  WAZUH_BLOCKS=$(python3 -c "import json; print(json.load(open('$REPO_ROOT/PROOF_PACK/verified_counts.json'))['counts']['wazuh'])")
  IR=$(python3 -c "import json; print(json.load(open('$REPO_ROOT/PROOF_PACK/verified_counts.json'))['counts']['ir'])")
  TOTAL=$(python3 -c "import json; print(json.load(open('$REPO_ROOT/PROOF_PACK/verified_counts.json'))['counts']['detections'])")

  check "Sigma count = 103" "$([ "$SIGMA" = "103" ] && echo true || echo false)" "Actual: $SIGMA"
  check "Splunk count = 9" "$([ "$SPLUNK" = "9" ] && echo true || echo false)" "Actual: $SPLUNK"
  check "Wazuh XML files = 24" "$([ "$WAZUH_FILES" = "24" ] && echo true || echo false)" "Actual: $WAZUH_FILES"
  check "Wazuh rule blocks = 28" "$([ "$WAZUH_BLOCKS" = "28" ] && echo true || echo false)" "Actual: $WAZUH_BLOCKS"
  check "IR playbooks = 10" "$([ "$IR" = "10" ] && echo true || echo false)" "Actual: $IR"
  check "Total detections = 140" "$([ "$TOTAL" = "140" ] && echo true || echo false)" "Actual: $TOTAL"
fi

# ── Check 9-12: Physical file counts ──
SIGMA_PHYS=$(find "$REPO_ROOT/content/detection-rules/sigma" -name "*.yml" 2>/dev/null | wc -l | tr -d ' ')
check "Physical Sigma YAML files = 103" "$([ "$SIGMA_PHYS" = "103" ] && echo true || echo false)" "Found: $SIGMA_PHYS"

SPLUNK_PHYS=$(find "$REPO_ROOT/content/detection-rules/splunk" -name "*.spl" 2>/dev/null | wc -l | tr -d ' ')
check "Physical Splunk SPL files = 9" "$([ "$SPLUNK_PHYS" = "9" ] && echo true || echo false)" "Found: $SPLUNK_PHYS"

WAZUH_PHYS=$(find "$REPO_ROOT/content/detection-rules/wazuh/rules" -name "*.xml" 2>/dev/null | wc -l | tr -d ' ')
check "Physical Wazuh XML files = 24" "$([ "$WAZUH_PHYS" = "24" ] && echo true || echo false)" "Found: $WAZUH_PHYS"

IR_PHYS=$(find "$REPO_ROOT/content/incident-response/playbooks" -name "IR-*.md" 2>/dev/null | wc -l | tr -d ' ')
check "Physical IR playbooks = 10" "$([ "$IR_PHYS" = "10" ] && echo true || echo false)" "Found: $IR_PHYS"

# ── Check 13: Key artifacts exist ──
for f in \
  "PROOF_PACK/ARCHITECTURE.md" \
  "docs/SignalFoundry_Case_Study_March2026.md" \
  "site/case-study-autosoc.html" \
  "site/proof.html" \
  "site/sitemap.xml" \
  "site/robots.txt" \
  "site/assets/Raylee_Hawkins_Resume.pdf" \
  "START_HERE.md"; do
  check "Artifact: $f" "$([ -f "$REPO_ROOT/$f" ] && echo true || echo false)"
done

# ── Check 14: robots.txt → sitemap ──
if [ -f "$REPO_ROOT/site/robots.txt" ]; then
  check "robots.txt references sitemap" \
    "$(grep -q 'Sitemap.*hawkinsops.com/sitemap.xml' "$REPO_ROOT/site/robots.txt" && echo true || echo false)"
fi

# ── Check 15: sitemap → case-study-autosoc ──
if [ -f "$REPO_ROOT/site/sitemap.xml" ]; then
  check "sitemap includes case-study-autosoc" \
    "$(grep -q 'case-study-autosoc' "$REPO_ROOT/site/sitemap.xml" && echo true || echo false)"
fi

echo ""
echo "═══════════════════════════════════"
TOTAL_CHECKS=$((PASS + FAIL))
echo "PASS: $PASS / $TOTAL_CHECKS   FAIL: $FAIL"
echo "Snapshot: $SNAPSHOT"
echo "═══════════════════════════════════"

exit $EXIT_CODE
