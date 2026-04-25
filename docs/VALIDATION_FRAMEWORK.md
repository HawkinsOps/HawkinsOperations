# Detection Validation Framework — HawkinsOperations

**Date:** 2026-04-04
**Purpose:** Proposed test structure for continuous detection validation

---

## Proposed Directory Structure

```
validation/
├── README.md                          # Framework overview and usage
├── run-tests.ps1                      # Windows test runner (PowerShell)
├── run-tests.sh                       # Linux test runner (bash)
├── config/
│   └── test-config.yaml               # Environment-specific settings
├── tests/
│   ├── credential-access/
│   │   ├── TC-T1003.001-lsass-comsvcs.yaml
│   │   ├── TC-T1003.002-sam-registry.yaml
│   │   ├── TC-T1003.003-ntds-extraction.yaml
│   │   ├── TC-T1003.006-dcsync.yaml
│   │   └── TC-T1558.003-kerberoasting.yaml
│   ├── defense-evasion/
│   │   ├── TC-T1070.001-event-log-clear.yaml
│   │   ├── TC-T1562.001-amsi-bypass.yaml
│   │   ├── TC-T1562.001-defender-disable.yaml
│   │   └── TC-T1036-masquerading.yaml
│   ├── execution/
│   │   ├── TC-T1059.001-powershell-download.yaml
│   │   ├── TC-T1059.003-certutil-decode.yaml
│   │   ├── TC-T1218.005-mshta.yaml
│   │   └── TC-T1204.002-macro-execution.yaml
│   ├── lateral-movement/
│   │   ├── TC-T1021.002-psexec.yaml
│   │   ├── TC-T1047-wmi-remote.yaml
│   │   └── TC-T1550.002-pass-the-hash.yaml
│   ├── persistence/
│   │   ├── TC-T1547.001-registry-run-key.yaml
│   │   ├── TC-T1053.005-scheduled-task.yaml
│   │   └── TC-T1543.003-new-service.yaml
│   ├── privilege-escalation/
│   │   ├── TC-T1548.002-uac-bypass-fodhelper.yaml
│   │   └── TC-T1548.002-uac-bypass-eventvwr.yaml
│   └── impact/
│       ├── TC-T1490-vss-delete.yaml
│       ├── TC-T1486-ransomware-simulation.yaml
│       └── TC-T1489-service-stop.yaml
├── wazuh/
│   ├── logtest-inputs/                # Pre-built wazuh-logtest inputs
│   │   ├── test-100057-defender-disabled.txt
│   │   ├── test-100058-powershell-download.txt
│   │   ├── test-100071-wmi-process.txt
│   │   ├── test-100072-kerberoasting.txt
│   │   └── test-100075-comsvcs-dump.txt
│   └── run-logtest.sh                 # Batch logtest runner
├── sigma/
│   ├── compile-check.sh               # Sigma rule compilation validator
│   └── backends/                      # Backend-specific compiled outputs
│       ├── splunk/
│       ├── elasticsearch/
│       └── wazuh/
└── results/
    ├── .gitkeep
    └── YYYY-MM-DD-test-run.md         # Test run results template
```

---

## Test Case YAML Format

Each test case follows a standardized format:

```yaml
# Test Case: TC-T1003.006-dcsync
id: TC-T1003.006-dcsync
technique: T1003.006
technique_name: "OS Credential Dumping: DCSync"
tactic: credential-access
priority: critical
platforms_tested:
  - sigma: credential-access/dcsync_attack.yml
  - splunk: credential_access_detections.spl (DCSync query)
  - wazuh: null  # No Wazuh rule for this technique

prerequisites:
  - "Domain Controller in lab environment"
  - "Non-DC account with Replicating Directory Changes rights (for testing) or Mimikatz"
  - "EventID 4662 audit policy enabled (Advanced Audit: DS Access)"
  - "Sysmon NOT required for this detection"

test_input:
  command: 'Invoke-Mimikatz -Command "lsadump::dcsync /domain:lab.local /user:krbtgt"'
  alternative: 'python3 secretsdump.py lab.local/admin:Password123@dc01.lab.local -just-dc-user krbtgt'
  atomic_red_team: "T1003.006-1"
  
expected_log:
  source: "Windows Security"
  event_id: 4662
  key_fields:
    SubjectUserName: "!*$"  # NOT a machine account
    Properties: "*1131f6aa-9c07-11d1-f79f-00c04fc2dcd2*"  # DS-Replication-Get-Changes
    Properties: "*1131f6ad-9c07-11d1-f79f-00c04fc2dcd2*"  # DS-Replication-Get-Changes-All

expected_alert:
  sigma_rule: "DCSync Attack Detection"
  sigma_level: critical
  splunk_alert: "DCSync Attack Detection"
  
negative_test:
  description: "Normal DC-to-DC replication should NOT trigger"
  scenario: "DC01$ machine account performing scheduled replication"
  expected_result: "No alert — machine account ($) is excluded in detection logic"
  
cleanup:
  - "No persistent changes — DCSync is a read operation"
  - "Rotate krbtgt password if testing in production-like environment"
  
evidence_artifacts:
  - "Screenshot of EventID 4662 with replication GUIDs"
  - "Screenshot of alert in Splunk/Wazuh dashboard"
  - "Negative test confirmation (no alert for DC replication)"
```

---

## Quick Validation Script Concept

### PowerShell Test Runner (run-tests.ps1)

```powershell
# Detection Validation Runner — HawkinsOperations
# Usage: .\run-tests.ps1 -TestPath .\tests\credential-access\TC-T1003.006-dcsync.yaml
# Or:    .\run-tests.ps1 -All -Priority critical

param(
    [string]$TestPath,
    [switch]$All,
    [string]$Priority = "all",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Load test case YAML (requires powershell-yaml module or manual parsing)
# For each test:
#   1. Display test metadata
#   2. Check prerequisites
#   3. If not DryRun: execute test command
#   4. Wait for log propagation (5-10 seconds)
#   5. Query for expected alert (Splunk REST API or Wazuh API)
#   6. Record result: PASS (alert fired), FAIL (no alert), SKIP (prerequisites not met)
#   7. Execute cleanup commands

# Output: results/YYYY-MM-DD-test-run.md
```

### Wazuh Logtest Batch Runner (run-logtest.sh)

```bash
#!/bin/bash
# Batch wazuh-logtest runner
# Usage: ./run-logtest.sh wazuh/logtest-inputs/

INPUTS_DIR=${1:-"wazuh/logtest-inputs"}
RESULTS="results/$(date +%Y-%m-%d)-logtest-results.md"

echo "# Wazuh Logtest Results — $(date)" > "$RESULTS"

for input_file in "$INPUTS_DIR"/test-*.txt; do
    rule_id=$(basename "$input_file" | grep -oP '\d{6}')
    echo "Testing rule $rule_id..."
    
    # Feed input to wazuh-logtest and capture output
    result=$(echo "$(cat "$input_file")" | /var/ossec/bin/wazuh-logtest 2>&1)
    
    # Check if expected rule fired
    if echo "$result" | grep -q "Rule id: '$rule_id'"; then
        echo "## Rule $rule_id: PASS" >> "$RESULTS"
    else
        echo "## Rule $rule_id: FAIL" >> "$RESULTS"
        echo '```' >> "$RESULTS"
        echo "$result" >> "$RESULTS"
        echo '```' >> "$RESULTS"
    fi
done

echo "Results written to $RESULTS"
```

### Sigma Compilation Checker (compile-check.sh)

```bash
#!/bin/bash
# Validate all Sigma rules compile to target backends
# Requires: sigma-cli (pip install sigma-cli pySigma-backend-splunk pySigma-backend-elasticsearch)

SIGMA_DIR="content/detection-rules/sigma"
RESULTS="results/$(date +%Y-%m-%d)-sigma-compile.md"

echo "# Sigma Compilation Results — $(date)" > "$RESULTS"

backends=("splunk" "elasticsearch")
pass=0
fail=0

for rule in $(find "$SIGMA_DIR" -name "*.yml" -type f); do
    for backend in "${backends[@]}"; do
        if sigma convert -t "$backend" "$rule" > /dev/null 2>&1; then
            ((pass++))
        else
            ((fail++))
            echo "FAIL: $rule -> $backend" >> "$RESULTS"
            sigma convert -t "$backend" "$rule" 2>&1 | tail -3 >> "$RESULTS"
        fi
    done
done

echo "Pass: $pass, Fail: $fail" >> "$RESULTS"
```

---

## Execution Plan for Thursday Preparation

### Wednesday Quick Wins (2-3 hours)

1. **Create the validation/ directory structure** (30 min)
   - Even empty, the structure signals testing discipline
   - Add README.md explaining the framework

2. **Write 5 critical test case YAMLs** (1 hour)
   - TC-T1003.006-dcsync.yaml
   - TC-T1558.003-kerberoasting.yaml
   - TC-T1003.001-lsass-comsvcs.yaml
   - TC-T1548.002-uac-bypass-fodhelper.yaml
   - TC-T1547.001-registry-run-key.yaml

3. **Run 5 wazuh-logtest validations** (30 min)
   - Test rules 100057, 100058, 100071, 100072, 100075
   - Save screenshots of successful logtest output

4. **Execute 2-3 Atomic Red Team tests** (1 hour)
   - T1547.001 (Registry Run Key) — safe, reversible
   - T1070.001 (Event Log Clear) — generates clear evidence
   - T1003.002 (SAM Registry Dump) — if admin access available
   - Screenshot the detection alert in Wazuh/Splunk

### What to Say on the Call

**If asked "how do you validate detections?":**
"Every detection has a mapped test case — the technique ID links to a specific Atomic Red Team test or manual procedure. I validate in three ways: Sigma rules are compiled against the Splunk and Elasticsearch backends to confirm they parse correctly. Wazuh rules are tested through wazuh-logtest with crafted log inputs that should and shouldn't trigger the rule. And for the highest-priority detections, I run the actual attack simulation in my lab environment and confirm the alert fires end-to-end."

**If asked "what's your false positive rate?":**
"Each detection includes negative test cases — logs that should NOT trigger the rule. For example, my DCSync detection excludes domain controller machine accounts and Azure AD Connect sync accounts, because those generate the same EventID 4662 with replication GUIDs during legitimate operations. My Splunk implementations include extensive exclusion lists built from observing real lab telemetry over multi-day windows."

**If asked to walk through a specific rule:**
Lead with: technique definition → what log source → what specific conditions → what's excluded and why → how you'd test it.

---

## Maturity Roadmap (Post-Interview)

### Phase 1: Framework Foundation (Current)
- Test case YAML format defined
- 5 critical test cases written
- Manual execution and screenshot evidence

### Phase 2: Automated Validation (Next)
- PowerShell test runner that executes tests and queries for alerts
- CI integration: run compilation checks on every PR
- Wazuh logtest automation for all 29 rule blocks

### Phase 3: Continuous Validation (Future)
- Scheduled Atomic Red Team runs (weekly)
- Alert-to-test-case mapping in CI/CD pipeline
- Detection coverage drift monitoring (new techniques in ATT&CK vs current coverage)
- Purple team exercise documentation format

---

*This framework is designed to be incrementally built. The structure and methodology demonstrate detection engineering maturity even before full automation is in place.*
