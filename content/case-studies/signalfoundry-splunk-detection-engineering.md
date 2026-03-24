# Case Study: Detection Engineering on Constrained Windows Telemetry
**Building and evaluating detection logic against a single-sourcetype endpoint environment**

---

## Overview

This case study documents a structured detection engineering pass conducted against a
Windows endpoint in the HawkinsOps lab. The Splunk environment used here operates as a
parallel investigation and detection content development lane — separate from the
live SOC runtime. The objective was to determine what detection logic could be built,
validated, or ruled out from the available telemetry, and to document with precision
what the evidence actually supports versus what it cannot answer.

The work surfaces two triage-worthy process-chain patterns, confirms four audit and
telemetry gaps, and produces a set of detection rules with explicit dependency flags
that identify which rules are immediately actionable and which require logging
improvements before they can be trusted to fire correctly.

---

## Environment and Scope

- **Host monitored**: Single Windows 11 developer workstation (HO-WE-01)
- **Log collection**: Wazuh agent forwarding Security Event Log to Splunk as `XmlWinEventLog:Security`
- **Analysis window**: 7 days (~283,976 security events total, ~119,633/day)
- **Sourcetype coverage**: Security Event Log only — no Sysmon, no Application or System logs, no network telemetry
- **Splunk Add-on for Windows**: Not installed — standard CIM fields absent, all extraction performed via manual regex against raw XML
- **This Splunk lane is not part of the live SOC runtime.** Detection content developed here is evaluated separately before consideration for the live pipeline.

---

## Objective

Determine what detection signal is available in a constrained single-sourcetype
environment, characterize findings at the appropriate level of certainty, identify
gaps that prevent triage from reaching a conclusion, and produce detection rules
that accurately reflect those constraints. The secondary objective was to document
what logging changes would unlock the highest-value detections.

---

## Method

All queries executed against Splunk Enterprise 10.0.2 via the REST API (port 8089),
using PowerShell for job submission and result retrieval. Because the Splunk Add-on
for Windows was not installed, field values were extracted from raw XML using `rex`
patterns targeting the `<Data Name='FieldName'>value</Data>` structure. Process names
were normalized to basenames using `mvindex(split(path,"\\"),-1)`.

Parent-child process chain analysis used EventID 4688 (Process Creation). Authentication
analysis used EventIDs 4624 (Successful Logon), 4625 (Failed Logon), and 4672
(Special Logon). Credential access analysis used EventID 5379 (Credential Manager Read).
Discovery event analysis used EventIDs 4798 and 4799.

---

## Key Findings

**bash.exe spawning base64.exe at high volume** is the most statistically prominent
pattern in the data. Over 7 days, this parent-child pair appeared 30,855 times, with a
peak of 10,023 spawns in a single hour. The process chain maps to T1140 (Deobfuscate /
Decode Files or Information), a documented technique for payload staging. However:
command-line auditing is not enabled on this host. The arguments passed to base64 are
unknown. The pattern is triage-worthy and volume-significant, but cannot be characterized
as malicious or benign from the available evidence. Both conclusions require the
CommandLine field, which is empty in every 4688 event in this dataset.

**chrome.exe and msedge.exe spawning cmd.exe** appeared 59 times across the window.
Browser-to-shell spawning is one of the higher-fidelity parent-child anomaly signals in
Windows endpoint telemetry. It is equally consistent with Chrome's internal crash handler,
a browser extension with shell permissions, or post-exploitation activity following
browser compromise. All 59 events have empty CommandLine fields. This finding cannot be
closed — in either direction — without command-line content.

**Zero EventID 4625 events** across 7 days on an active endpoint is not a clean result.
It is a confirmed audit gap: failed logon auditing is not enabled. The 547 successful
4624 logon events in the same window confirm the host is actively authenticating.
Brute force, password spraying, and credential stuffing attempts would be invisible
in this configuration.

**Credential Manager reads** (2,098 events, EventID 5379) are documented as a behavioral
baseline rather than a finding. The reads are attributable to Microsoft account token
refresh cycles by known processes. The value is baseline establishment: deviation from
this pattern — particularly reads by a shell process — would warrant immediate triage.

---

## Detection Gaps Identified

Four gaps materially limit what detection logic can do in this environment:

1. **Process command-line auditing is disabled.** The CommandLine field is empty in all
   4688 events. This makes LOLbin argument patterns, encoded command detection, and
   browser-shell triage all unavailable. It is the single highest-priority logging change
   for this environment.

2. **Failed logon auditing is not enabled.** Zero 4625 events renders brute force and
   password spray detection impossible regardless of what detection rules are deployed.

3. **No Sysmon telemetry.** Network connections, DNS queries, file creation, registry
   modification, and process injection events are entirely absent. The Security Event Log
   alone does not support the full scope of behavioral detection expected on a modern
   endpoint.

4. **Single-sourcetype ingestion without the Windows Add-on.** All field extraction
   is manual and regex-dependent, increasing the risk of silent extraction failures.
   Detection rules written to CIM-normalized field names will not match this data.

---

## Recommended Detections

Eight detection rules were developed from the telemetry. Three are flagged as requiring
logging improvements before they are reliably actionable:

- **Browser or Office application spawning a shell process** (T1059.003) — any single
  occurrence; requires command-line auditing to triage
- **bash→base64 volume spike** (T1140) — threshold >500/hour on this host; requires
  command-line auditing to confirm
- **Shell process reading from Credential Manager** (T1555.004) — any single occurrence;
  actionable now
- **After-hours process execution by non-baseline account** (T1078) — any occurrence;
  actionable now
- **Failed logon spike** (T1110) — requires failed logon auditing to be enabled

Detection rules are written in SPL targeting the `XmlWinEventLog:Security` sourcetype
with `rex`-based field extraction. Each rule includes its gap dependency and MITRE
ATT&CK mapping in the full evidence documentation.

---

## What This Demonstrates

Detection engineering is not only about writing rules that fire. It is about knowing
when the evidence is strong enough to support a conclusion and being direct when it
is not.

The bash→base64 pattern in this dataset is volume-significant and technique-mapped.
It is also genuinely ambiguous without the arguments. Both of those things are true,
and the analysis says so instead of forcing a verdict the telemetry cannot support.
Labeling that finding as confirmed malicious because the process chain looks like a
known technique would be wrong. Dismissing it because there is a legitimate explanation
would also be wrong. The disciplined answer is: triage-worthy, currently unresolvable,
blocked by a specific logging gap with a known remediation.

The same discipline applies to the audit gaps themselves. Zero failed logon events is
not a good result — it is a configuration gap. Treating absence of evidence as evidence
of absence is one of the more consequential errors an analyst can make. Documenting the
gap precisely, including its operational impact and the specific policy setting required
to close it, is the correct response.

The detection rules produced here are honest about their own limits. Three of the eight
are flagged as dependent on logging changes before they will produce actionable results.
A detection that passes internal testing in a constrained environment and then silently
fails to fire in production because the required telemetry was never collected is worse
than no detection at all — it creates false confidence. The dependency flags exist to
prevent that outcome.

---

## Conclusion

This pass produced a documented baseline, two triage-worthy process-chain patterns
requiring follow-up investigation, a set of eight detection rules with explicit gap
dependencies, and a prioritized remediation list for the four logging gaps that most
limit detection capability in this environment. No activity in the 7-day window was
confirmed as malicious. The work is reproducible: all SPL is included in the supporting
evidence documentation, all counts are derived from live queries against the indexed data,
and all findings are characterized at the level of certainty the evidence supports.

---

*HawkinsOps | Detection Engineering Lab | 2026-03-24*
*Splunk Enterprise 10.0.2 — Detection content development and investigation lane*
