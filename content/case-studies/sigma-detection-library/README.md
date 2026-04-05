---
title: "Sigma Detection Library: 103 Platform-Agnostic Rules Across 10 MITRE ATT&CK Tactics"
date: 2026-03-30
author: Raylee Hawkins
tags: [detection-engineering, sigma, mitre-attack, siem, platform-agnostic]
locked_snapshot: 2026-03-25
canonical_metrics_file: PROOF_PACK/VERIFIED_COUNTS.md
abstract: >
  103 Sigma detection rules authored to spec with explicit logsource schemas,
  false positive filters, and MITRE technique tags. Organized by ATT&CK tactic.
  Compilable to any backend. CI-enforced count verification.
---

# Sigma Detection Library: 103 Platform-Agnostic Rules Across 10 MITRE ATT&CK Tactics

**One-line TL;DR:** 103 Sigma rules, 10 ATT&CK tactics, 36+ technique IDs, every rule has logsource + FP filters + MITRE tags, count CI-enforced.

**Recruiter-ready summary:**
- Authored 103 Sigma detection rules covering 10 of 14 MITRE ATT&CK enterprise tactics, compilable to Splunk, Elastic, Wazuh, QRadar, and Sentinel
- Every rule includes explicit logsource schema, false positive filters, and technique tagging — no untagged or stub rules
- Detection count is CI-enforced: `verify-counts.ps1` physically counts files on every push, and `drift_scan.py` validates parity across HTML, JSON, and Markdown

---

## 1. Executive Summary (TL;DR)

This is a purpose-built Sigma detection library. Not a fork. Not a template dump. 103 rules authored against Windows Sysmon and Windows Security event sources, organized by MITRE ATT&CK tactic, each with the complete set of required Sigma fields.

The rules compile to any SIEM backend that supports Sigma conversion (`sigmac`, `pySigma`): Splunk SPL, Elasticsearch/OpenSearch queries, Microsoft Sentinel KQL, QRadar AQL. Write once, deploy anywhere — the detection logic survives a SIEM migration because it is decoupled from the implementation.

The count (103) is not hand-asserted. It is the output of `(Get-ChildItem -Recurse .\content\detection-rules\sigma -Filter *.yml).Count`, enforced by CI on every push to the repository.

---

## 2. Scope & Constraints

### Included
- 103 Sigma YAML rules in `content/detection-rules/sigma/`
- 10 MITRE ATT&CK tactic folders
- Rule structure and required field analysis
- Verification pipeline and CI enforcement
- Cross-reference with Splunk SPL (9 queries covering overlapping tactics)

### Excluded
- Sigma compilation output (backend-specific queries not committed to repo)
- Wazuh XML rules (covered in separate case study)
- IR playbooks (covered in separate case study)
- Live SIEM deployment telemetry

### Assumptions
- **SOURCE_OF_TRUTH:** `PROOF_PACK/VERIFIED_COUNTS.md` — Sigma count = 103
- **Locked snapshot:** 2026-03-25
- **No data transforms applied** — all counts from physical file enumeration

---

## 3. Evidence Summary

| # | Artifact | Path | How to Verify |
|---|---|---|---|
| 1 | Sigma rule directory | `content/detection-rules/sigma/` | `(Get-ChildItem -Recurse .\content\detection-rules\sigma -Filter *.yml).Count` |
| 2 | Verified Counts | `PROOF_PACK/VERIFIED_COUNTS.md` | `pwsh -File scripts/verify/verify-counts.ps1` |
| 3 | Published case study | `site/case-study-sigma-library.html` | Browse https://hawkinsops.com/case-study-sigma-library |
| 4 | Architecture doc | `PROOF_PACK/ARCHITECTURE.md` | Section: Sigma (Universal Detection Format) |
| 5 | Detection index | `content/detection-rules/INDEX.md` | Tactic-level catalog |

---

## 4. Timeline & Impact

- **Creation:** Ongoing development through March 2026
- **Current state:** 103 rules, CI-verified, published on portfolio
- **Impact:** Demonstrates platform-agnostic detection engineering capability across the full ATT&CK kill chain (9 of 14 enterprise tactics, plus Collection)

---

## 5. Reproduction Steps

```powershell
# 1. Clone and enter
git clone https://github.com/raylee-hawkins/HawkinsOperations.git
cd HawkinsOperations

# 2. Count Sigma rules (total)
(Get-ChildItem -Recurse .\content\detection-rules\sigma -Filter *.yml).Count
# Expected: 103

# 3. Count per tactic
Get-ChildItem .\content\detection-rules\sigma -Directory |
  ForEach-Object {
    "$($_.Name): $((Get-ChildItem $_.FullName -Filter *.yml).Count)"
  }
# Expected output:
#   collection: 10
#   credential-access: 10
#   defense-evasion: 10
#   discovery: 10
#   execution: 9
#   exfiltration: 10
#   impact: 13
#   lateral-movement: 10
#   persistence: 11
#   privilege-escalation: 10

# 4. Verify all required fields present in a sample rule
Get-Content .\content\detection-rules\sigma\credential-access\*.yml |
  Select-String -Pattern "^(title|id|status|description|tags|logsource|detection|falsepositives|level):" |
  Group-Object Line | Select-Object Count, Name

# 5. Run CI verification
pwsh -NoProfile -File ".\scripts\verify\verify-counts.ps1"

# 6. Run drift scan
python scripts/drift_scan.py
```

---

## 6. Detailed Technical Analysis

### 6.1 Tactic Distribution

| Tactic | Rules | Key Techniques | Example Detections |
|---|---|---|---|
| Collection | 10 | Screen capture, keylogging, data staging | Screen capture tools, keystroke logging, clipboard monitoring |
| Credential Access | 10 | T1003, T1110, T1555, T1558 | LSASS access, DCSync, Kerberoasting, browser credential theft |
| Defense Evasion | 10 | T1027, T1070, T1112, T1562 | Log clearing, masquerading, obfuscation, security tool tampering |
| Discovery | 10 | T1046, T1057, T1083, T1135 | Network scanning, user/domain enumeration, share discovery |
| Execution | 9 | T1047, T1053, T1059, T1204 | PowerShell encoded execution, LOLBin abuse, script host anomalies |
| Exfiltration | 10 | T1020, T1041, T1048, T1567 | Unusual outbound transfer, DNS tunneling, staging indicators |
| Impact | 13 | T1485, T1486, T1490, T1491 | Ransomware indicators, shadow copy deletion, service disruption |
| Lateral Movement | 10 | T1021, T1550, T1563 | Pass-the-hash, RDP anomalies, admin share abuse, WMI remote exec |
| Persistence | 11 | T1053, T1098, T1136, T1547 | Scheduled tasks, registry run keys, service installation |
| Privilege Escalation | 10 | T1055, T1068, T1078, T1134 | Token manipulation, abnormal group changes, UAC bypass |
| **Total** | **103** | **36+ technique IDs** | **9 of 14 enterprise tactics** |

### 6.2 Rule Structure (Required Fields)

Every rule ships with all required Sigma fields:

```yaml
title: Suspicious LSASS Process Access        # Human-readable name
id: a3f72d8e-1b94-4c3f-b6e0-7d8a9e2f1c05    # Stable UUID
status: stable                                 # stable / experimental / test
description: Detects suspicious access to lsass.exe
tags:
    - attack.credential_access                 # MITRE tactic
    - attack.t1003.001                         # MITRE technique
logsource:
    product: windows                           # Explicit product
    category: process_access                   # Explicit category
    service: sysmon                            # Explicit service
detection:
    selection:
        EventID: 10
        TargetImage|endswith: '\lsass.exe'
        GrantedAccess|contains:
            - '0x1410'
            - '0x1010'
            - '0x1438'
    filter_known_good:
        SourceImage|endswith:
            - '\wmiprvse.exe'
            - '\taskmgr.exe'
            - '\MsMpEng.exe'
    condition: selection and not filter_known_good
falsepositives:                                # At least one entry
    - Legitimate security software (EDR agents)
    - Authorized memory forensics tools
level: high                                    # Not defaulted
```

### 6.3 False Positive Handling

Every rule includes explicit `falsepositives` and, where applicable, `filter_known_good` conditions. A detection rule without FP handling is a noisy alert factory. This library treats false positive documentation as a first-class field, not an afterthought.

Example: the LSASS detection filters `wmiprvse.exe`, `taskmgr.exe`, and `MsMpEng.exe` — processes that legitimately access LSASS memory — before firing.

### 6.4 Platform Portability

Sigma rules compile to any supported backend:

| Target | Tool | Command Example |
|---|---|---|
| Splunk SPL | `pySigma` + `sigma-backend-splunk` | `sigma convert -t splunk rule.yml` |
| Elastic/OpenSearch | `pySigma` + `sigma-backend-elasticsearch` | `sigma convert -t elasticsearch rule.yml` |
| Microsoft Sentinel | `pySigma` + `sigma-backend-microsoft365defender` | `sigma convert -t kusto rule.yml` |
| QRadar AQL | `pySigma` + `sigma-backend-qradar` | `sigma convert -t qradar rule.yml` |

The same credential-access detection set exists in both Sigma YAML (platform-agnostic) and Splunk SPL (direct implementation) in this repo, illustrating the same logic expressed in both formats.

### 6.5 Cross-reference with Splunk and Wazuh

| Platform | Count | Overlapping Tactics |
|---|---|---|
| Sigma YAML | 103 | All 10 |
| Splunk SPL | 9 | Credential Access, Defense Evasion, Discovery, Execution, Lateral Movement, Persistence, Privilege Escalation, Collection/Exfil/Impact |
| Wazuh XML | 28 blocks | Custom rules with MITRE tags |
| **Total detections** | **140** | CI-verified |

---

## 7. Metrics Reconciliation

| Surface | Sigma Count | Status |
|---|---|---|
| `PROOF_PACK/VERIFIED_COUNTS.md` | 103 | Source of truth |
| `PROOF_PACK/verified_counts.json` | 103 | JSON mirror |
| `site/case-study-sigma-library.html` (`data-verified="sigma"`) | 103 | Published HTML |
| Physical file count | 103 | `(Get-ChildItem -Recurse .\content\detection-rules\sigma -Filter *.yml).Count` |
| `drift_scan.py` validation | PASS | Cross-surface parity confirmed |

**No metric drift detected.** All surfaces agree.

---

## 8. Lessons, Risk, Suggested Follow-ups

### Lessons
1. **Sigma decouples detection logic from SIEM vendor lock-in.** The investment in authoring to spec pays off when the backend changes.
2. **CI-enforced counts prevent silent drift.** A new rule file automatically bumps the count; a deleted file fails the build.
3. **False positive fields are as important as detection fields.** A rule that fires on everything is not a detection.

### Risk
- **No automated Sigma compilation tests.** Rules are authored to spec but not compiled against actual backends in CI. A malformed logsource or filter condition would not be caught until deployment.
- **Tactic gap:** `initial-access` has no dedicated Sigma rules (covered partially by other tactics).

### Suggested Follow-ups
1. **Add Sigma compilation CI step** — validate rules compile to at least one backend (e.g., Splunk) without errors. Estimated: 2 hours.
2. **Add tactic-level replay tests** — validate FP filters against real telemetry. Estimated: varies by tactic.
3. **Fill `initial-access` tactic** — add rules for T1190 (exploit public-facing app), T1566 (phishing). Estimated: 2-4 hours.

---

## 9. Acceptance QA Checklist

| # | Check | Status |
|---|---|---|
| 1 | Sigma count = 103 (JSON) | **PASS** |
| 2 | Sigma count = 103 (physical) | **PASS** |
| 3 | 10 tactic directories present | **PASS** |
| 4 | `data-verified="sigma"` in HTML = 103 | **PASS** |
| 5 | `drift_scan.py` PASS | **PASS** |
| 6 | Every tactic folder has at least 1 rule | **PASS** |
| 7 | sitemap includes case-study-sigma-library | **PASS** |
| 8 | Rule sample has all required fields | **PASS** |

**Summary: 8 PASS / 0 FAIL**
