# Case Study: Splunk Detection Rule Audit
**Four Ways My Own Rules Would Flood a Real Analyst With Noise**

---

## Problem / Hypothesis

I had written detection rules in Splunk targeting a constrained Windows telemetry environment — single sourcetype (`XmlWinEventLog:Security`), no Sysmon, no Windows TA, manual `rex`-based field extraction. The rules worked. They fired. They matched MITRE ATT&CK techniques.

The hypothesis: working rules are not the same as deployable rules. Before publishing any of this as portfolio evidence, I needed to answer one question — if a real analyst inherited these rules in a production SOC, what would their first week look like?

I audited every one of my Splunk detection rules against that standard. The answer was not flattering.

---

## Environment

| Component | Detail |
|---|---|
| Splunk Enterprise | 10.0.2, REST API on port 8089 |
| Host monitored | Single Windows 11 workstation (HO-WE-01) |
| Log source | Wazuh agent → Security Event Log → Splunk `index=wazuh` |
| Sourcetype | `XmlWinEventLog:Security` |
| Analysis window | 7 days, ~283,976 security events (~119,633/day) |
| Field extraction | Manual `rex` against raw XML (`<Data Name='field'>value</Data>`) |
| Splunk Add-on for Windows | Not installed — no CIM-normalized fields |

This Splunk instance operates as a detection content development and investigation lane, separate from the live SOC pipeline runtime.

---

## Methodology

**Step 1 — Inventory the rules.**
Cataloged every SPL detection query I had written. Each rule was mapped to a MITRE ATT&CK technique, had a defined threshold or pattern, and targeted specific EventIDs.

**Step 2 — Run each rule against 7 days of production data.**
Every rule was executed against the full 283,976-event dataset via the Splunk REST API. I recorded the hit count, the volume distribution over time, and sampled the matching events to characterize what was actually firing.

**Step 3 — Apply the analyst-workload test.**
For each rule, I asked: if this alert fired in a SOC queue, could an analyst triage it to a conclusion with the information available? Or would they need to pivot to data that doesn't exist in this environment?

**Step 4 — Classify the noise sources.**
Every rule that failed the analyst-workload test was categorized by the specific reason it would generate untriageable alerts.

---

## Evidence

### Noise Source 1: Empty CommandLine Fields

The single most impactful gap. Event ID 4688 (Process Creation) fired on every process start, but the `CommandLine` field was empty in 100% of events. Command-line auditing was not enabled on the host.

Rules affected:
- **bash.exe → base64.exe detection** (T1140) — 30,855 hits in 7 days, peak of 10,023 spawns in a single hour. Every alert would land in a queue with the process name visible but zero argument context. An analyst cannot distinguish `base64 --decode payload.bin` from `base64 --help` without the arguments.
- **Browser → shell spawning** (T1059.003) — 59 hits from chrome.exe and msedge.exe spawning cmd.exe. Could be Chrome's crash handler, a browser extension, or post-exploitation. Without the command line, an analyst must escalate every single one — 59 tickets with no path to closure.

### Noise Source 2: No Failed Logon Baseline

Zero EventID 4625 events in 7 days. Failed logon auditing was not enabled. Any rule targeting brute force (T1110) or password spray would either never fire (silent failure) or fire on the first event after auditing is enabled with no baseline to distinguish normal from abnormal.

### Noise Source 3: Missing Sourcetype Coverage

Rules written against `XmlWinEventLog:Security` only. No Sysmon telemetry meant no network connections (Event 3), no DNS queries (Event 22), no file creation (Event 11), no registry modification (Event 13). Detection rules targeting lateral movement or C2 beaconing had no data to match against. They would sit in the rule set as dead weight — zero fires, zero value, creating a false sense of coverage.

### Noise Source 4: Manual Field Extraction Fragility

All field extraction used `rex` patterns targeting XML structure. No CIM normalization. No Windows TA. If the XML structure changed between Wazuh versions, or if a field was nested differently than expected, the extraction would silently return null. The analyst would see alerts with blank fields and no indication that the extraction failed rather than the field being genuinely empty.

Sample extraction pattern:
```spl
| rex field=_raw "<Data Name='NewProcessName'>(?<NewProcessName>[^<]+)</Data>"
| rex field=_raw "<Data Name='CommandLine'>(?<CommandLine>[^<]+)</Data>"
| rex field=_raw "<Data Name='ParentProcessName'>(?<ParentProcessName>[^<]+)</Data>"
```

---

## Findings

Four categories of noise that would degrade analyst effectiveness:

| # | Noise Source | Rules Affected | Analyst Impact |
|---|---|---|---|
| 1 | Empty CommandLine fields | 3 rules (T1140, T1059.003, encoded command detection) | Alerts fire but cannot be triaged — no argument visibility |
| 2 | No failed logon baseline | 1 rule (T1110) | Rule either silent-fails or fires without context on first enable |
| 3 | Missing sourcetype coverage | 2 rules (network/lateral movement) | Rules never fire — false coverage |
| 4 | Rex extraction fragility | All rules | Silent field extraction failure indistinguishable from empty fields |

Of the 8 detection rules I had built, 3 were immediately actionable in the current environment, 3 required command-line auditing to be enabled before they could produce triageable alerts, 1 required failed logon auditing, and 1 required Sysmon or equivalent network telemetry.

I flagged every rule with an explicit dependency annotation:
```
# DEPENDENCY: Requires ProcessCreationIncludeCmdLine_Enabled = 1
# Without this registry key, CommandLine field is empty in all 4688 events.
# This rule will fire on process-chain pattern alone, flooding the queue
# with untriageable alerts.
```

---

## Operational Impact

This audit directly triggered two follow-on actions:

1. **Phase 1 Audit Policy Hardening** — I enabled command-line logging (`ProcessCreationIncludeCmdLine_Enabled = 1`), failed logon auditing, and 25 additional audit subcategories. Documented in `content/case-studies/phase1-audit-policy-hardening.md`.

2. **Detection rule dependency flags** — Every rule now carries an explicit annotation identifying what telemetry it requires and what happens if that telemetry is absent. Rules are not marked "stable" until their dependencies are confirmed present.

The audit also changed how I write rules going forward. Every new detection includes a "deployment prerequisites" section before the SPL, not after.

---

## Verification

1. **Detection rules with dependency flags:** `content/detection-rules/splunk/` — each `.spl` file includes dependency annotations
2. **Raw analysis data:** The 283,976-event dataset was queried via Splunk REST API; sample queries and output are documented in `content/case-studies/signalfoundry-splunk-detection-engineering.md`
3. **Phase 1 hardening (remediation):** `content/case-studies/phase1-audit-policy-hardening.md` — the direct result of this audit
4. **Audit gap confirmation:** Run the following against the Splunk index to verify the empty CommandLine claim:
   ```spl
   index=wazuh data.win.system.eventID=4688
   | eval has_cmdline=if(len(CommandLine)>0,"yes","no")
   | stats count by has_cmdline
   ```
5. **Published analysis:** `hawkinsops.com/case-study-detection-harness` — the portfolio page referencing this work

---

## What This Demonstrates

Writing detection rules is the easy part. Knowing whether your rules are deployable — whether they'll help an analyst or bury them — requires running them against real data and asking uncomfortable questions about what happens when the alert fires.

I found four ways my own rules would make a real analyst's life worse. I documented them, flagged the dependencies, and fixed the underlying gaps. That sequence — build, audit, document the gaps honestly, fix them — is what separates a detection library from a noise generator.

---

*Date: 2026-03-24 | Environment: Splunk Enterprise 10.0.2, Windows 11, Wazuh agent, PowerShell 7 | System: Detection content development lane (separate from live SOC pipeline)*
