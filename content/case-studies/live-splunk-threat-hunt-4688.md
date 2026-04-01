# Case Study: Live Splunk Threat Hunt — EventID 4688 Process Creation Analysis
**Rex-Based Field Extraction, Parent-Process Exclusion Logic, and Codex AI Tool Classification**

---

## Problem / Hypothesis

Event ID 4688 (Process Creation) is one of the highest-volume Windows Security events and one of the most valuable for behavioral detection. In a constrained Splunk environment — single sourcetype, no Windows TA, no CIM fields — the question was whether meaningful threat hunting could be conducted using only manual field extraction against raw XML.

The hypothesis: with `rex`-based extraction and parent-process chain analysis built from scratch, I could surface anomalous process behavior in live endpoint telemetry — and distinguish genuine threats from tool behavior without relying on pre-built field mappings.

---

## Environment

| Component | Detail |
|---|---|
| Splunk Enterprise | 10.0.2, REST API on port 8089 |
| Host monitored | Single Windows 11 developer workstation (HO-WE-01) |
| Log source | Wazuh agent → Security Event Log → Splunk `index=wazuh` |
| Sourcetype | `XmlWinEventLog:Security` |
| Analysis window | 7 days, ~283,976 security events |
| Field extraction | Manual `rex` against raw XML — no Windows TA, no CIM normalization |
| Process telemetry | EventID 4688 (Process Creation) — CommandLine field empty (auditing not yet enabled) |

---

## Methodology

**Step 1 — Build the field extraction layer.**

With no Windows TA installed, every field had to be extracted from raw XML using `rex`. I built extraction patterns for the three critical 4688 fields:

```spl
| rex field=_raw "<Data Name='NewProcessName'>(?<NewProcessName>[^<]+)</Data>"
| rex field=_raw "<Data Name='ParentProcessName'>(?<ParentProcessName>[^<]+)</Data>"
| rex field=_raw "<Data Name='CommandLine'>(?<CommandLine>[^<]+)</Data>"
```

Process names were normalized to basenames for aggregation:
```spl
| eval process=mvindex(split(NewProcessName,"\\"),-1)
| eval parent=mvindex(split(ParentProcessName,"\\"),-1)
```

**Step 2 — Baseline parent-child process relationships.**

Ran a full parent→child frequency analysis across the 7-day window to establish what normal looks like:

```spl
index=wazuh sourcetype="XmlWinEventLog:Security" EventCode=4688
| rex field=_raw "<Data Name='NewProcessName'>(?<NewProcessName>[^<]+)</Data>"
| rex field=_raw "<Data Name='ParentProcessName'>(?<ParentProcessName>[^<]+)</Data>"
| eval process=mvindex(split(NewProcessName,"\\"),-1)
| eval parent=mvindex(split(ParentProcessName,"\\"),-1)
| stats count by parent, process
| sort -count
```

This produced the baseline frequency table. The top entries were expected system noise — `svchost.exe` spawning services, `explorer.exe` spawning applications, `RuntimeBroker.exe` lifecycle events.

**Step 3 — Build parent-process exclusion logic.**

To surface anomalies, I needed to suppress the known-normal parent-child pairs. I built an exclusion layer:

```spl
| where NOT (
    parent="svchost.exe" OR
    parent="services.exe" OR
    parent="RuntimeBroker.exe" OR
    parent="WmiPrvSE.exe" OR
    (parent="explorer.exe" AND match(process, "^(chrome|msedge|firefox|notepad)"))
)
```

The exclusions were additive — each was added only after verifying the parent-child pair was legitimate baseline behavior, not assumed. Every exclusion was documented with the volume it suppressed.

**Step 4 — Hunt for anomalous parent-child chains.**

With baseline noise suppressed, the remaining events surfaced two categories:
- High-volume automated process chains (developer tooling)
- Low-volume unusual parent-child pairs (investigation targets)

**Step 5 — Deep-dive the top anomaly.**

The single highest-volume non-baseline finding: `pwsh.exe` being spawned 375 times by a process chain originating from Codex, an AI coding tool.

---

## Evidence

### Finding 1: Codex AI Tool Spawning pwsh.exe — 375 Occurrences

The parent-process exclusion logic surfaced `pwsh.exe` being spawned at high frequency. Tracing the parent chain:

```
Codex (AI tool) → node.exe → pwsh.exe (375x over 7 days)
```

**Volume profile:**
- 375 total spawns across the analysis window
- Clustered during active development hours (09:00–18:00 local)
- Zero spawns outside development hours
- Consistent spawn intervals suggesting automated tool behavior, not interactive use

**Classification question:** Is this LOLBin abuse (T1059.001 — PowerShell execution) or legitimate developer tooling?

**Analysis:**
- `pwsh.exe` is a known LOLBin — PowerShell execution is one of the most common adversary techniques
- The parent chain (Codex → node.exe → pwsh.exe) is consistent with an AI coding assistant executing shell commands as part of its workflow
- The temporal clustering during business hours with zero off-hours activity is inconsistent with persistent threat behavior
- The volume (375 over 7 days, ~54/day) is consistent with a developer tool running commands, not a C2 beacon or automated exfiltration loop

**Verdict:** Correctly classified as developer tool behavior. Not LOLBin abuse. The pattern is documented as a known-benign baseline entry for this endpoint.

### Finding 2: bash.exe → base64.exe — 30,855 Occurrences

Previously documented in the detection engineering case study. The parent-process exclusion logic confirmed this as the highest-volume non-system process chain. Without CommandLine content, the finding remains triage-worthy but unresolvable. Flagged as the primary driver for enabling command-line auditing.

### Finding 3: Browser → cmd.exe — 59 Occurrences

chrome.exe and msedge.exe spawning cmd.exe. The exclusion logic correctly did not suppress this pair — browser→shell is never baseline. 59 occurrences over 7 days. Without CommandLine content, each event requires manual triage. This finding was the secondary driver for the audit policy hardening.

### Rex Extraction Validation

To verify the `rex` patterns were extracting correctly and not silently dropping fields:

```spl
index=wazuh sourcetype="XmlWinEventLog:Security" EventCode=4688
| rex field=_raw "<Data Name='NewProcessName'>(?<NewProcessName>[^<]+)</Data>"
| eval has_process=if(isnotnull(NewProcessName),"yes","no")
| stats count by has_process
```

Result: extraction success rate >99.9% for `NewProcessName` and `ParentProcessName`. `CommandLine` extraction returned null in 100% of events — confirmed as an audit configuration gap, not an extraction failure.

---

## Findings

| Finding | Volume | Classification | Action Required |
|---|---|---|---|
| Codex → node.exe → pwsh.exe | 375 spawns | Developer tool behavior (not LOLBin) | Baselined; no action |
| bash.exe → base64.exe | 30,855 spawns | Triage-worthy, unresolvable | Enable CommandLine auditing |
| Browser → cmd.exe | 59 spawns | Triage-worthy, unresolvable | Enable CommandLine auditing |
| Rex extraction null rate (CommandLine) | 100% null | Audit gap, not extraction failure | Enable CommandLine auditing |

The Codex/pwsh.exe classification is the methodologically interesting finding. An automated detection rule matching on `pwsh.exe` spawned by a non-standard parent would have flagged all 375 events as suspicious. The parent-chain analysis, temporal profiling, and volume characterization were required to correctly classify the behavior. This is the difference between detection and triage — the rule fires, but the analyst must characterize.

---

## Operational Impact

1. **Codex/pwsh.exe baselined** — added to the known-benign parent-chain library for this endpoint. Future detections from this chain will be auto-suppressed, reducing analyst queue noise by 375 events per week.

2. **Parent-process exclusion methodology documented** — the additive exclusion approach (suppress only after verification, document each suppression with volume) is reusable for any new endpoint onboarded to the pipeline.

3. **CommandLine auditing gap confirmed as blocking** — three of the four findings required CommandLine content to resolve. This directly triggered the Phase 1 audit policy hardening.

4. **Rex extraction layer validated** — the manual extraction patterns demonstrated >99.9% success rate on structured fields, confirming that meaningful threat hunting is possible without the Windows TA, albeit with the fragility risk documented in the detection rule audit.

---

## Verification

1. **Splunk query reproducibility:** All SPL queries in this case study can be executed against `index=wazuh` with `sourcetype="XmlWinEventLog:Security"` and `EventCode=4688`. The `rex` patterns are included verbatim.

2. **Parent-child frequency baseline:**
   ```spl
   index=wazuh sourcetype="XmlWinEventLog:Security" EventCode=4688
   | rex field=_raw "<Data Name='NewProcessName'>(?<NewProcessName>[^<]+)</Data>"
   | rex field=_raw "<Data Name='ParentProcessName'>(?<ParentProcessName>[^<]+)</Data>"
   | eval process=mvindex(split(NewProcessName,"\\"),-1)
   | eval parent=mvindex(split(ParentProcessName,"\\"),-1)
   | stats count by parent, process
   | sort -count
   | head 50
   ```

3. **Codex/pwsh temporal profile:**
   ```spl
   index=wazuh sourcetype="XmlWinEventLog:Security" EventCode=4688
   | rex field=_raw "<Data Name='NewProcessName'>(?<NewProcessName>[^<]+)</Data>"
   | where match(NewProcessName, "pwsh\.exe$")
   | timechart span=1h count
   ```

4. **Cross-reference:** Detection rule audit (`content/case-studies/splunk-detection-rule-audit.md`) and Phase 1 hardening (`content/case-studies/phase1-audit-policy-hardening.md`) document the downstream actions taken based on these findings.

5. **Published analysis:** `hawkinsops.com/case-study-detection-harness` references this work.

---

## What This Demonstrates

Threat hunting on constrained telemetry is not an excuse for shallow analysis. The rex extraction layer, built from scratch against raw XML, achieved >99.9% field extraction accuracy. The parent-process exclusion logic was additive and documented — no suppression without verification. And the Codex classification required actual analytical work: temporal profiling, volume characterization, and parent-chain tracing to arrive at the correct conclusion that 375 PowerShell spawns were tool behavior, not adversary behavior.

The easy answer was to flag pwsh.exe spawned by a non-standard parent as suspicious and move on. The correct answer required understanding what was actually happening. That distinction scales — in a SOC processing thousands of alerts, the analysts who can correctly classify ambiguous findings are the ones who keep the queue from drowning in false positives.

---

*Date: 2026-03-24 | Environment: Splunk Enterprise 10.0.2, Windows 11, Wazuh agent, PowerShell 7 | System: Detection content development and threat hunting lane*
