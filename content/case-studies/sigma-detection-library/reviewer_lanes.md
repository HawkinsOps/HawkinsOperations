---
title: "Reviewer Lanes — Sigma Detection Library"
case_study: sigma-detection-library
---

# Reviewer Lanes

## Recruiter Lane (30 seconds)

**TL;DR:** Raylee Hawkins authored 103 Sigma detection rules across 10 MITRE ATT&CK tactics. Every rule has explicit logsource schemas, false positive filters, and technique tags. The rules compile to Splunk, Elastic, Wazuh, QRadar, and Sentinel. Count is CI-enforced on every commit.

**Role fit:**
- **Detection Engineering:** 103 platform-agnostic rules demonstrating Sigma spec mastery, logsource schema design, and false positive handling
- **SOC Analyst T1/T2:** Detection content covers the full kill chain — credential access, lateral movement, privilege escalation, impact (ransomware), exfiltration
- **SIEM Engineering:** Rules compile to any backend, demonstrating platform-agnostic thinking

**Top metrics:**
| Metric | Value |
|---|---|
| Sigma rules | 103 |
| ATT&CK tactics covered | 10 of 14 |
| Technique IDs | 36+ |
| CI-verified | Yes (every push) |

**Contact:** raylee@hawkinsops.com | [hawkinsops.com](https://hawkinsops.com) | [Resume PDF](https://hawkinsops.com/assets/Raylee_Hawkins_Resume.pdf)

---

## Technical Reviewer Lane (5 minutes)

```powershell
# 1. Clone
git clone https://github.com/raylee-hawkins/HawkinsOperations.git && cd HawkinsOperations

# 2. Count Sigma rules
(Get-ChildItem -Recurse .\content\detection-rules\sigma -Filter *.yml).Count
# Expected: 103

# 3. Verify CI gate
pwsh -NoProfile -File ".\scripts\verify\verify-counts.ps1"

# 4. Inspect a sample rule
Get-Content .\content\detection-rules\sigma\credential-access\lsass_process_access.yml

# 5. Run case study verification
pwsh -NoProfile -ExecutionPolicy Bypass -File ".\case-studies\sigma-detection-library\evidence\verify.ps1"
```

**Single-step failure mode:** `(Get-ChildItem -Recurse .\content\detection-rules\sigma -Filter *.yml).Count` — if this is not 103, the source of truth has drifted.

**Runtime estimate:** < 1 minute for all 5 commands.

---

## Detection Engineer Lane (deep dive)

### Browse the rules
- [GitHub: content/detection-rules/sigma/](https://github.com/raylee-hawkins/HawkinsOperations/tree/main/content/detection-rules/sigma)

### Per-tactic inspection
```powershell
Get-ChildItem .\content\detection-rules\sigma -Directory |
  ForEach-Object {
    $rules = Get-ChildItem $_.FullName -Filter *.yml
    "$($_.Name): $($rules.Count) rules"
    $rules | ForEach-Object { "  - $($_.Name)" }
  }
```

### MITRE technique extraction
```powershell
Get-ChildItem -Recurse .\content\detection-rules\sigma -Filter *.yml |
  Get-Content |
  Select-String -Pattern "attack\.t\d{4}" -AllMatches |
  ForEach-Object { $_.Matches.Value } |
  Sort-Object -Unique
```

### Cross-reference with Splunk
The `content/detection-rules/splunk/` directory contains 79 detection searches across 9 SPL files covering overlapping tactics. Compare detection logic between Sigma YAML and direct SPL implementation for the same technique.

### Tuning notes
- No untagged rules (every rule has `tags: attack.*`)
- No empty `falsepositives` fields
- Logsource primarily targets Windows Sysmon + Windows Security
- Impact tactic has the most rules (13) — covers ransomware indicators, shadow copy deletion, service disruption
- Execution tactic has the fewest (9)
- Gap: `initial-access` has no dedicated tactic folder

### Test data
- No dedicated Sigma test data in this repo
- Recommended: add a `tests/sigma/` directory with sample event JSON per tactic for replay testing
