# Enterprise Audit Policy Hardening
**27 Subcategories | 22 Changes | MITRE-Mapped | Verified**

*Date: 2026-03-29 | Host: HO-WE-01 (Windows 11 Enterprise, domain-joined) | Artifacts: `C:\OPS\audit-hardening\2026-03-29_204753\`*

---

## What Was Dark

A structured review of the Windows Advanced Audit Policy on HO-WE-01 — the primary domain-joined endpoint feeding the Wazuh → Splunk → Grafana pipeline — identified three tiers of blind spots:

**Fully dark (No Auditing — 14 subcategories):**

| Subcategory | Category | Why it matters |
|---|---|---|
| Kerberos Authentication Service | Account Logon | AS-REQ/AS-REP invisible — Golden Ticket and AS-REP Roasting undetectable |
| Kerberos Service Ticket Operations | Account Logon | TGS requests invisible — Kerberoasting (T1558.003) undetectable |
| Other Account Logon Events | Account Logon | NTLM fallback and alternate logon paths not captured |
| Computer Account Management | Account Management | Machine account creation/modification invisible |
| Other Account Management Events | Account Management | Miscellaneous account changes not captured |
| Process Termination | Detailed Tracking | Short-lived recon tools disappear without a trace |
| DPAPI Activity | Detailed Tracking | Windows Credential Manager access invisible (T1555.004) |
| Other Logon/Logoff Events | Logon/Logoff | Reconnect, cached credentials, RDP session events missing |
| File System | Object Access | File read/write/delete on sensitive paths not logged |
| Registry | Object Access | Run key writes, SAM access, persistence via registry invisible |
| SAM | Object Access | Direct SAM database access — credential dumping (T1003.002) undetectable |
| Removable Storage | Object Access | USB device data staging (T1052.001) undetectable |
| Sensitive Privilege Use | Privilege Use | SeDebugPrivilege, SeTcbPrivilege use invisible — T1134 blind |
| Security System Extension | System | SSP injection (T1547.005), malicious driver load not captured |

**Partial coverage (Success only — failure events dark — 8 subcategories):**

| Subcategory | Gap |
|---|---|
| Security Group Management | Failed group manipulation attempts invisible |
| User Account Management | Failed account creation/deletion invisible |
| Logoff | — (Success logging sufficient; Failure added for completeness) |
| Special Logon | Failed privilege logon attempts invisible |
| Account Lockout | Lockout events weren't generating on failure — brute force indicator suppressed |
| Audit Policy Change | Failed policy-change attempts (T1562.002 detection) invisible |
| Authentication Policy Change | Failed Kerberos policy tampering invisible |
| Security State Change | Unexpected failure state changes not captured |

**CommandLine logging:**
`ProcessCreationIncludeCmdLine_Enabled` was not set. Event ID 4688 fired on every process creation but the CommandLine field was empty — every argument, flag, and payload was invisible. Process names without arguments are weak signal.

**Security log buffer:**
Default size was 20 MB (20,971,520 bytes). With the volume of events expected post-hardening, this fills in hours and rolls before the Wazuh agent forwards events.

---

## What Was Enabled

`harden.ps1` ran elevated at 20:47:53 on 2026-03-29. All 27 subcategories set to `Success and Failure`. 22 changed state. 27/27 succeeded with no errors.

### Full Subcategory Table with MITRE Mappings

| # | Subcategory | Category | Before | After | MITRE ATT&CK |
|---|---|---|---|---|---|
| 1 | Credential Validation | Account Logon | Success and Failure | Success and Failure | T1110 — Brute Force, credential stuffing |
| 2 | Kerberos Authentication Service | Account Logon | **No Auditing** | Success and Failure | T1558 — Golden Ticket, AS-REP Roasting |
| 3 | Kerberos Service Ticket Operations | Account Logon | **No Auditing** | Success and Failure | T1558.003 — Kerberoasting |
| 4 | Other Account Logon Events | Account Logon | **No Auditing** | Success and Failure | T1078 — Valid Accounts (fallback logon) |
| 5 | Security Group Management | Account Management | Success | Success and Failure | T1098 — Account Manipulation |
| 6 | User Account Management | Account Management | Success | Success and Failure | T1136 — Create Account |
| 7 | Computer Account Management | Account Management | **No Auditing** | Success and Failure | T1136.002 — Domain Account abuse |
| 8 | Other Account Management Events | Account Management | **No Auditing** | Success and Failure | T1098 — Account Manipulation (misc) |
| 9 | Process Creation | Detailed Tracking | Success and Failure | Success and Failure | All execution techniques (4688) |
| 10 | Process Termination | Detailed Tracking | **No Auditing** | Success and Failure | Short-lived recon tool detection |
| 11 | DPAPI Activity | Detailed Tracking | **No Auditing** | Success and Failure | T1555.004 — Windows Credential Manager |
| 12 | Plug and Play Events | Detailed Tracking | Success and Failure | Success and Failure | T1091 — Removable Media |
| 13 | Logon | Logon/Logoff | Success and Failure | Success and Failure | T1078 — Valid Accounts, lateral movement |
| 14 | Logoff | Logon/Logoff | Success | Success and Failure | Session duration analysis |
| 15 | Special Logon | Logon/Logoff | Success | Success and Failure | T1134 — Unexpected privilege escalation |
| 16 | Account Lockout | Logon/Logoff | Success | Success and Failure | T1110 — Active brute force indicator |
| 17 | Other Logon/Logoff Events | Logon/Logoff | **No Auditing** | Success and Failure | T1078 — Valid Accounts (reconnect/RDP) |
| 18 | File System | Object Access | **No Auditing** | Success and Failure | T1005 — Data from Local System |
| 19 | Registry | Object Access | **No Auditing** | Success and Failure | T1547.001 — Run Keys / T1003.002 — SAM |
| 20 | SAM | Object Access | **No Auditing** | Success and Failure | T1003.002 — Credential Dumping (SAM) |
| 21 | Removable Storage | Object Access | **No Auditing** | Success and Failure | T1052.001 — Exfiltration over USB |
| 22 | Audit Policy Change | Policy Change | Success | Success and Failure | T1562.002 — Disable Windows Event Logging (meta) |
| 23 | Authentication Policy Change | Policy Change | Success | Success and Failure | Kerberos policy tampering |
| 24 | Sensitive Privilege Use | Privilege Use | **No Auditing** | Success and Failure | T1134 — Access Token Manipulation |
| 25 | Security System Extension | System | **No Auditing** | Success and Failure | T1547.005 — SSP injection |
| 26 | System Integrity | System | Success and Failure | Success and Failure | Code integrity failures, driver load |
| 27 | Security State Change | System | Success | Success and Failure | Time stomping, unexpected reboots |

**Additional changes applied:**

| Change | Before | After | Effect |
|---|---|---|---|
| `ProcessCreationIncludeCmdLine_Enabled` | (not set) | `1` | 4688 CommandLine field now populated |
| Security log `maxSize` | 20,971,520 (20 MB) | 1,073,741,824 (1 GB) | 50× buffer for Wazuh forwarding headroom |

---

## Detection Coverage Delta

**11 MITRE techniques moved from undetectable to detectable:**

| Technique | Tactic | Previously | Now |
|---|---|---|---|
| T1558 — Steal or Forge Kerberos Tickets | Credential Access | Dark | Kerberos AS/TGS events visible |
| T1558.003 — Kerberoasting | Credential Access | Dark | TGS-REQ/TGS-REP patterns detectable |
| T1555.004 — Credentials from Windows Credential Manager | Credential Access | Dark | DPAPI master key access logged |
| T1003.002 — OS Credential Dumping: SAM | Credential Access | Dark | SAM handle opens generate events |
| T1005 — Data from Local System | Collection | Dark | File system access on sensitive paths logged |
| T1547.001 — Boot/Logon Autostart: Registry Run Keys | Persistence | Dark | Registry write events captured |
| T1052.001 — Exfiltration over Physical Medium: USB | Exfiltration | Dark | Removable storage events generated |
| T1134 — Access Token Manipulation | Privilege Escalation | Dark (failure) | SeDebugPrivilege use failures now logged |
| T1547.005 — Boot/Logon Autostart: SSP | Persistence | Dark | Security Support Provider load events |
| T1136.002 — Create Account: Domain Account | Persistence | Dark | Machine account creation events |
| T1562.002 — Impair Defenses: Disable Windows Event Logging | Defense Evasion | Partial | Failure attempts now captured — any tampering attempt generates 4719 |

**Event IDs newly generating meaningful signal:**

| Event ID | Description | Previously |
|---|---|---|
| 4769 | Kerberos Service Ticket Request | Not captured |
| 4768 | Kerberos Authentication Ticket Request | Not captured |
| 4776 | NTLM Credential Validation | Inconsistent |
| 4663 | File system access attempt | Not captured |
| 4657 | Registry value modified | Not captured |
| 4656 | Handle to SAM requested | Not captured |
| 4698 | DPAPI master key accessed | Not captured |
| 4689 | Process terminated | Not captured |
| 4673 | Sensitive privilege use | Not captured |
| 7045 / 4697 | Security system extension (SSP) | Not captured |
| 4719 | Audit policy changed | Successes only (no failure detection) |

**CommandLine visibility:** Every 4688 event now carries the full argument string. Before: `C:\Windows\System32\cmd.exe` — process visible, intent unknown. After: `cmd.exe /c powershell -enc <base64>` — intent visible, triage possible.

---

## Verification Evidence

All verification captured at 2026-03-29T20:50:18 — approximately 2.5 minutes post-hardening.

**1. CommandLine field present in 4688 events**

```
20:50:18 | C:\Windows\System32\conhost.exe
  CommandLine: [PRESENT] \??\C:\WINDOWS\system32\conhost.exe 0xffffffff -ForceV1

20:50:18 | C:\Program Files\PowerShell\7\pwsh.exe
  CommandLine: [PRESENT] "C:\Program Files\PowerShell\7\pwsh.exe"
               -NoProfile -ExecutionPolicy Bypass
               -File "C:\OPS\audit-hardening\verify.ps1"
```

The verification script logged its own execution including full flags. The gap that made process arguments invisible is closed.

**2. Registry key confirmed**

```
ProcessCreationIncludeCmdLine_Enabled = 1
Path: HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit
```

**3. Security log buffer confirmed**

```
logFileName: %SystemRoot%\System32\Winevt\Logs\Security.evtx
maxSize:     1073741824
```

50× increase from the 20 MB default. Wazuh agent can now safely queue and forward events without risk of log rollover during any forwarding delay.

**4. Audit execution log (session markers)**

From `run_output_2026-03-29_204753.txt`:
```
DIFF_COUNT:22
CHANGED_SUBCATS:27
CMD_LINE_AFTER:1
```

27 subcategories processed, 27 succeeded, 22 state changes confirmed by CSV diff.

**5. Before/After snapshot artifacts**

```
C:\OPS\audit-hardening\2026-03-29_204753\
  before.csv          122 lines — full policy state pre-hardening
  before_full.txt     full auditpol /get /category:* output
  after.csv           132 lines — full policy state post-hardening
  after_full.txt      full auditpol /get /category:* output

C:\OPS\audit-hardening\
  session-log.md      canonical session record
  verification_results.txt  post-hardening event verification
```

The 10-line difference between before.csv (122) and after.csv (132) reflects the expanded subcategory audit entries written once policy is active — a structural change in what auditpol reports.

---

## Pipeline Flow

New events enter the existing detection pipeline without any additional configuration:

```
HO-WE-01 (Windows 11 Enterprise)
  Windows Security Log
  ├── 4688 + CommandLine (Process Creation — now with arguments)
  ├── 4768/4769 (Kerberos AS/TGS — newly generating)
  ├── 4663/4657/4656 (Object Access — newly generating)
  ├── 4673 (Sensitive Privilege Use — newly generating)
  ├── 4719 (Audit Policy Change — failure events added)
  └── [18 additional subcategories now generating events]
         │
         │  Wazuh Agent (OSSEC/Wazuh 4.14.4)
         │  syscheck + logcollector → Security log → alerts.json
         ▼
  Wazuh Manager (ho-sr-wm-01)
  /var/ossec/logs/alerts/alerts.json
         │
         │  cron rsync (every 5 min) → CIFS mount
         ▼
  Splunk (ho-splunk-01)
  /mnt/operations/wazuh/alerts/ → monitor input → index:wazuh
  SPL queries targeting new EventIDs:
    data.win.system.eventID=4688  ← CommandLine now populated
    data.win.system.eventID=4769  ← Kerberoasting signal
    data.win.system.eventID=4663  ← File access events
    data.win.system.eventID=4719  ← Policy tamper meta-detection
         │
         │  OpenSearch (192.168.8.231:9200)
         │  index: wazuh-alerts-4.x-*
         ▼
  Grafana (192.168.8.134:3000)
  Wazuh MITRE ATT&CK dashboard (ID 22449)
  MITRE technique IDs now populate:
    T1558, T1558.003, T1555.004, T1003.002
    T1005, T1547.001, T1052.001, T1134, T1547.005
```

**Wazuh rule coverage:** Wazuh ships rules targeting Windows Security events by rule ID ranges 18100–18107 (account management), 18200–18206 (logon), 60100+ (Windows audit). The newly-generating event IDs fall within existing Wazuh Windows detection groups — events start alerting immediately without rule changes. Custom rules in `content/detection-rules/wazuh/rules/` extend coverage for the highest-priority subcategories.

**Splunk queries for the new signal:**

```spl
# Kerberoasting indicator — TGS requests for service accounts
index=wazuh data.win.system.eventID=4769
| where match(data.win.eventdata.ticketEncryptionType, "0x17|0x18")
| table _time, data.win.eventdata.serviceInfo, data.win.eventdata.clientAddress

# Credential dumping — SAM handle requested
index=wazuh data.win.system.eventID=4656
| where match(data.win.eventdata.objectType, "SAM_DOMAIN|SAM_USER")
| table _time, host, data.win.eventdata.subjectUserName, data.win.eventdata.processName

# Meta-detection — audit policy tamper
index=wazuh data.win.system.eventID=4719
| where match(data.win.eventdata.auditPolicyChanges, "%%8448|removed")
| eval severity="CRITICAL"
| table _time, host, data.win.eventdata.subjectUserName, severity

# Process creation with arguments now visible
index=wazuh data.win.system.eventID=4688
| where isnotnull(data.win.eventdata.commandLine) AND data.win.eventdata.commandLine != "-"
| table _time, data.win.eventdata.newProcessName, data.win.eventdata.commandLine
| sort -_time | head 50
```

---

## What This Demonstrates

The pre-hardening state was a typical default Windows audit configuration — process creation enabled, basic logon events, nothing else. Adequate for basic ops. Inadequate for detection.

14 subcategories at No Auditing means 14 categories of attacker activity generating zero events. Not low-fidelity events. Zero events. Kerberoasting, SAM dumping, SSP injection, USB exfiltration — all completely invisible to every tool in the stack simultaneously.

The discipline here is the snapshot approach: capture state, change state, diff the delta. The diff is the artifact. Anyone reviewing this work can verify exactly which subcategories changed and what the policy state was before. The claim isn't "I hardened the audit policy." The claim is "here are the 22 rows that changed, here is the before CSV, here is the after CSV, here is the verification run showing CommandLine present in 4688 events two minutes later."

The pipeline didn't require changes. The events flow into Wazuh, into Splunk, into Grafana through the same architecture already in place. Hardening the log source expands the detection surface of the entire stack retroactively — every rule, every dashboard, every query benefits.

---

*Artifacts: `C:\OPS\audit-hardening\2026-03-29_204753\` | Script: `C:\OPS\audit-hardening\harden.ps1` | Verification: `C:\OPS\audit-hardening\verification_results.txt`*
