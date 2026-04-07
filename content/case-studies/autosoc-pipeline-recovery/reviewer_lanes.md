---
title: "Reviewer Lanes — AutoSOC Pipeline Recovery"
case_study: autosoc-pipeline-recovery
---

# Reviewer Lanes

## Recruiter Lane (30 seconds)

**TL;DR:** Raylee Hawkins built a fully automated SOC triage pipeline (SignalFoundry) that processes Wazuh alerts end-to-end: classify, redact, package evidence, escalate. When the pipeline broke, she diagnosed two root causes and restored it in one session. The system has processed 321,351+ cases with a ~88% auto-close rate.

**Role fit:**
- **SOC Analyst T1/T2:** Demonstrated alert triage at scale (321,351+ cases), policy-based disposition, and false positive tuning from direct observation of a live environment.
- **Detection Engineering:** 140 verified detection rules across Sigma, Splunk SPL, and Wazuh XML, organized by MITRE ATT&CK tactics. CI-enforced counts.
- **SOC Automation:** Purpose-built Python+PowerShell pipeline with 8-stage processing, 4-way reconciliation, and evidence sanitization before any artifact leaves the internal store.

**Top metrics (locked 04-07-2026):**
| Metric | Value |
|---|---|
| Cases processed | 324,074 |
| Auto-close rate | ~88% |
| Escalated cases | 8,574 |
| Detection rules | 140 (CI-verified) |
| IR Playbooks | 10 |
| Host coverage | 8/8 |

**Contact:** raylee@hawkinsops.com | [hawkinsops.com](https://hawkinsops.com) | [Resume PDF](https://hawkinsops.com/assets/Raylee_Hawkins_Resume.pdf)

**Clearance:** Eligible to obtain clearance; willing to pursue sponsorship.

---

## Technical Reviewer Lane (5 minutes)

**Reproduce in 5 commands:**

```powershell
# 1. Clone and enter
git clone https://github.com/raylee-hawkins/HawkinsOperations.git && cd HawkinsOperations

# 2. Verify detection counts (CI gate)
pwsh -NoProfile -File ".\scripts\verify\verify-counts.ps1"

# 3. Run drift scan (markdown/JSON/HTML parity)
python scripts/drift_scan.py

# 4. Run site diagnosis
node scripts/diagnose-site.js

# 5. Run case study verification
pwsh -NoProfile -ExecutionPolicy Bypass -File ".\case-studies\autosoc-pipeline-recovery\evidence\verify.ps1"
```

**Prerequisites:** PowerShell 7, Python 3.x, Node.js 20.x

**Single-step failure mode to check:** Run `verify-counts.ps1` — if Sigma count != 103 or total != 140, the source of truth has drifted. This is the same gate CI uses on every push.

**Key artifacts to inspect:**
1. `PROOF_PACK/VERIFIED_COUNTS.md` — source of truth for all public numbers
2. `docs/SignalFoundry_Case_Study_March2026.md` — full engineering case study with pipeline architecture, work log, and metrics
3. `site/case-study-autosoc.html` — published case study page
4. `docs/execution/AUTOSOC_PIPELINE_RECOVERY_CASE_STUDY_03-13-2026.md` — detailed incident documentation
5. `PROOF_PACK/ARCHITECTURE.md` — detection platform architecture

**Runtime estimate:** < 2 minutes for all 5 commands on a modern machine.

---

## Detection Engineer Lane (deep dive)

### Sigma Rules
- **Location:** `content/detection-rules/sigma/` — 103 rules across 10 tactic folders
- **MITRE coverage:** 9 of 14 enterprise tactics, 36+ technique IDs
- **Browse:** [GitHub](https://github.com/raylee-hawkins/HawkinsOperations/tree/main/content/detection-rules/sigma)

**Tactic distribution:**
| Tactic | Rules | Key Techniques |
|---|---|---|
| Collection | 10 | Screen capture, keylogging, data staging |
| Credential Access | 10 | T1003 (LSASS), T1110, T1555, T1558 |
| Defense Evasion | 10 | T1027, T1070, T1112, T1562 |
| Discovery | 10 | T1046, T1057, T1083, T1135 |
| Execution | 9 | T1047, T1053, T1059, T1204 |
| Exfiltration | 10 | T1020, T1041, T1048, T1567 |
| Impact | 13 | T1485, T1486, T1490, T1491 |
| Lateral Movement | 10 | T1021, T1550, T1563 |
| Persistence | 11 | T1053, T1098, T1136, T1547 |
| Privilege Escalation | 10 | T1055, T1068, T1078, T1134 |

**Verification:**
```powershell
# Count per tactic
Get-ChildItem .\content\detection-rules\sigma -Directory |
  ForEach-Object { "$($_.Name): $((Get-ChildItem $_.FullName -Filter *.yml).Count)" }
```

### Splunk SPL
- **Location:** `content/detection-rules/splunk/` — 9 queries
- **Coverage:** Credential Access, Defense Evasion, Discovery, Execution, Lateral Movement, Persistence, Privilege Escalation, Collection/Exfiltration/Impact

### Wazuh XML
- **Location:** `content/detection-rules/wazuh/rules/` — 24 files, 28 rule blocks
- **Custom ID range:** 100000+
- **Deployable bundle:** `pwsh -NoProfile -File ".\scripts\build-wazuh-bundle.ps1"` → `dist/wazuh/local_rules.xml`

### IR Playbooks
- **Location:** `content/incident-response/playbooks/` — 10 playbooks (IR-001 through IR-022)
- **Structure:** 7-step framework (Detection → Triage → Investigation → Containment → Eradication → Recovery → Documentation)
- **Playbooks:** LSASS Access (T1003.001), Suspicious PowerShell (T1059.001), Ransomware (T1486), Brute Force (T1110), Malware (T1204), Privilege Escalation, AD Compromise (T1003.006), Lateral Movement, Exfiltration (T1041), Supply Chain (T1195)

### Tuning Notes
- Known-FP library built from direct observation, not vendor templates
- Sysmon Event 3 LOtL binary escalation: `rundll32.exe`, `regsvr32.exe`, `mshta.exe`, `powershell.exe`, `certutil.exe`, `bitsadmin` → ESCALATE
- Sysmon Event 10 (process access): unconditional ESCALATE for credential dumping coverage
- Windows workstation noise suppression: HP printer device enum, Bluetooth LE, DCOM app-launch failures
- Linux dpkg churn: rules 2902/2904 on honeypot and file server → AUTO_CLOSE_KNOWN_FP

### Test Data
- No dedicated Sigma test data directory in repo (gap noted in SignalFoundry doc Section 7.4)
- Triage logic tested via `test_triage.py`, `test_redact.py` (external to this portfolio repo)
- Recommended: add tactic-level replay tests as next hardening step
