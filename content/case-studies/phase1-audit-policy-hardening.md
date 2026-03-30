# Case Study: Phase 1 — Advanced Audit Policy Hardening
**Closing the Detection Gaps Found During the Splunk Threat Hunt**

---

## The Problem

A structured Splunk threat hunt across 283,976 Windows Security events identified four audit gaps on a domain-joined Windows 11 Enterprise endpoint:

1. **Command-line auditing disabled** — Event ID 4688 fired on every process creation, but the CommandLine field was empty. Every process chain observed during the hunt was visible by name only. Arguments were unknown.
2. **No failed logon events** — Zero EventID 4625 events across seven days on an internet-connected workstation. Brute force, password spray, and unauthorized access attempts were completely invisible.
3. **No credential validation telemetry** — EventID 4776 (NTLM credential validation) was not being captured.
4. **No Windows TA in Splunk** — All field extraction was manual regex against raw XML, limiting the speed and depth of analysis.

Gaps 1–3 were configuration issues. They could be fixed. This case study documents the fix.

---

## Approach

The goal was to harden the Windows Advanced Audit Policy to close the identified gaps and expand detection coverage across the full pipeline:

```
Windows Security Log → Wazuh Agent → Wazuh Manager (ho-sr-wm-01)
  → alerts.json → NFS mount → Splunk (ho-splunk-01) index:wazuh
  → OpenSearch (192.168.8.231:9200) → Grafana (192.168.8.134:3000)
```

Before any changes: snapshot the current state. After all changes: snapshot again and generate a before/after diff. The diff is the portfolio artifact. Every change is documented, not assumed.

Risk was low — audit policies only add logging, they don't block anything. Rollback was a single command restoring the before snapshot.

---

## Execution

**Step 0 — Before Snapshot**

Current audit policy exported to `C:\OPS\audit-hardening\<timestamp>\` in three formats: plain text, CSV for programmatic comparison, and a full Local Security Policy export. This established the documented baseline.

**Step 1 — 27 Audit Subcategories Enabled**

Each subcategory enabled for both Success and Failure events, annotated with the detection gap it closes and the MITRE ATT&CK technique it enables:

| Category | Subcategory | Detection Capability |
|---|---|---|
| Account Logon | Credential Validation | T1110 — Brute Force, credential stuffing |
| Account Logon | Kerberos Authentication Service | T1558 — Golden ticket, AS-REP roasting |
| Account Logon | Kerberos Service Ticket Operations | T1558.003 — Kerberoasting |
| Account Management | Security Group Management | T1098 — Account Manipulation |
| Account Management | User Account Management | T1136 — Create Account |
| Account Management | Computer Account Management | T1136.002 — Domain Account abuse |
| Detailed Tracking | Process Creation | All execution techniques |
| Detailed Tracking | Process Termination | Short-lived recon tool detection |
| Detailed Tracking | DPAPI Activity | T1555.004 — Windows Credential Manager |
| Detailed Tracking | Plug and Play Events | T1091 — Removable Media |
| Logon/Logoff | Logon | T1078 — Valid Accounts, lateral movement |
| Logon/Logoff | Logoff | Session duration analysis |
| Logon/Logoff | Special Logon | Unexpected privilege escalation |
| Logon/Logoff | Account Lockout | T1110 — Active brute force |
| Object Access | File System | T1005 — Data from Local System |
| Object Access | Registry | T1547.001 — Run Keys, T1003.002 — SAM |
| Object Access | SAM | T1003.002 — Credential Dumping |
| Object Access | Removable Storage | T1052.001 — Exfiltration over USB |
| Policy Change | Audit Policy Change | T1562.002 — Disable Windows Event Logging (meta-detection) |
| Policy Change | Authentication Policy Change | Kerberos policy tampering |
| Privilege Use | Sensitive Privilege Use | T1134 — Access Token Manipulation |
| System | Security System Extension | T1547.005 — SSP injection |
| System | System Integrity | Code integrity failures |
| System | Security State Change | Time stomping, unexpected reboots |

**Step 2 — Command-Line Logging Enabled**

Registry key set at `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit`:

```
ProcessCreationIncludeCmdLine_Enabled = 1
```

Event ID 4688 now includes the full CommandLine field. The gap that prevented triage of the bash→base64 and browser→shell findings from the original threat hunt is closed.

**Step 3 — Security Event Log Expanded to 1GB**

Default Security log size is 20MB. With 27 new subcategories firing, that fills in hours. Log expanded via `wevtutil sl Security /ms:1073741824`. Wazuh agent forwards events before rollover; the expanded buffer provides additional local retention during any forwarding delay.

**Step 4 — After Snapshot and Diff**

After snapshot captured in the same directory as the before snapshot. Diff report generated comparing before and after maps, producing a markdown table of every subcategory that changed from `No Auditing` to `Success and Failure`.

---

## Validation

**Self-detection:** Event ID 4719 (Audit Policy Change) fired immediately after Step 1. The hardening activity was captured and logged by the same pipeline being hardened. This proved the meta-detection capability — any future attempt to disable auditing would generate the same event class.

**CommandLine verification:** Post-Step 2, Event ID 4688 events queried directly. CommandLine field present. Sample output confirmed process name and full argument string visible.

**Failed logon verification:** Test credential failure generated a 4625 event. Failed logon attempts are now visible.

**Credential validation:** 4776 events confirmed firing on NTLM authentication.

**Splunk verification queries** documented for post-pipeline-fix confirmation:

```
# New: Process creation with command line — the gap, now closed
index=wazuh data.win.system.eventID=4688
| table _time, data.win.eventdata.newProcessName, data.win.eventdata.commandLine, data.win.eventdata.parentProcessName
| sort -_time | head 50

# New: Failed logon attempts — previously invisible
index=wazuh data.win.system.eventID=4625
| table _time, data.win.eventdata.targetUserName, data.win.eventdata.logonType, data.win.eventdata.failureReason
| sort -_time

# Meta-detection: Audit policy tampering
index=wazuh data.win.system.eventID=4719
| where match(data.win.eventdata.auditPolicyChanges, "removed|%%8448")
| eval severity="CRITICAL"
| table _time, host, data.win.eventdata.subjectUserName, severity
```

---

## Outcome

27 audit subcategories enabled. 11 MITRE ATT&CK techniques previously dark are now detectable. Command-line arguments now visible in every process creation event. The two highest-severity findings from the original threat hunt — bash→base64 and browser→shell spawning — can now be triaged to resolution if they recur. Failed logon visibility established for the first time on this endpoint.

The before/after diff, verification screenshots, and audit policy export artifacts are stored at `C:\OPS\audit-hardening\`.

---

## What This Demonstrates

The threat hunt found the gaps. This phase closed them. The sequence matters: detection engineering without configuration hardening is a report. Detection engineering followed by remediation is the job.

The before/after snapshot approach — capture state, change state, diff the delta, verify the diff — is the same discipline I applied in manufacturing when validating process changes. You don't call a changeover complete because you believe it worked. You call it complete because you can show the difference between before and after and verify the output changed.

The 4719 self-detection was not engineered. It was a result of the pipeline working correctly. When you build the logging right, it logs itself.

---

## What's Next (Phase 2)

Phase 1 applied the hardening via local policy on a single domain-joined endpoint. Phase 2 promotes this to a domain GPO deployed from dc01 — meaning the configuration applies to all domain-joined machines automatically and any new machine that joins inherits it. The GPO change events (5136) will be captured by the same pipeline, extending the audit trail to the domain management layer.

---

*Date: 2026-03-29 | Environment: Windows 11 Enterprise, domain-joined, PowerShell 7, auditpol, wevtutil | Pipeline: Wazuh → Splunk → OpenSearch → Grafana*
