# Case Study: Overnight Process-Creation Telemetry Tuning Sprint

**Environment:** HawkinsOps / Wazuh SIEM  
**Date:** 2026-04-08  
**Duration:** ~23-hour detection run + tuning session  
**Author:** Ray Lee Hawkins — Detection Engineering / SOC Operations  
**Classification:** Portfolio artifact, operational reference, tuning decision record

---

## 1. Executive Summary

Over a single overnight sprint, a Wazuh deployment running custom process-creation detection rules was taken from a state of partially restored telemetry with uncontrolled alert volume to a deliberately tuned, measurable detection pipeline. The work proceeded in strict sequence: restore missing telemetry from an offline agent, confirm rule stability across the fleet, identify that one host was producing 97% of all alerts, eliminate queue saturation that was silently distorting measurement, classify the noise by source category, deploy 28 narrowly scoped suppression rules targeting only confirmed low-value process classes, and preserve every binary with plausible detection relevance.

The result was not simply "fewer alerts." The result was a pipeline where the remaining alerts are interpretable, the suppression decisions are documented and reversible, and the next measurement window will produce data that can actually be trusted.

Total alerts observed over 24 hours: ~151,384. Of those, approximately 110,000 were classified as operationally low-value noise from known infrastructure processes. Suppression was deployed for the clearest categories. Higher-ambiguity categories (bash, Git coreutils) were deliberately deferred pending post-suppression re-measurement. No broad exclusions were applied. No rules were disabled. No detection coverage was removed.

This is a detection-engineering and SOC-throughput optimization exercise, documented as evidence that the environment is real, under load, and operated with discipline.

---

## 2. Operational Context

The HawkinsOps Wazuh deployment monitors a mixed fleet of Windows endpoints and servers. The environment is not a lab simulation — it runs production workloads including CI/CD runners, development tooling (Claude Code, Git, Node.js), Splunk Universal Forwarders, and standard Windows services.

Two custom detection rules had been deployed to capture process-creation telemetry:

| Rule ID | Source | Event Type |
|---------|--------|------------|
| 100203 | Windows Security Log | Event ID 4688 — Process Creation |
| 100204 | Sysmon | Event ID 1 — Process Create |

These rules were designed to provide broad visibility into what processes are running across the fleet — a prerequisite for any meaningful detection engineering. Without process-creation telemetry, you cannot build behavioral detections, identify anomalous execution chains, or validate that suppression decisions are well-founded.

The indexer connector (Wazuh-to-index pipeline) remained stable throughout the entire run. Alert ingestion, indexing, and retrieval were functioning normally. The problems encountered during this sprint were all upstream: agent-level telemetry gaps, queue capacity limits, and alert-volume composition.

---

## 3. Starting Conditions and Main Blocker

At the start of the sprint window, the fleet was mostly healthy but not fully operational.

**Prior blocker:** Agent 023 had been offline during the previous session (2026-04-07). This was significant because an offline agent means zero telemetry from that host — not reduced telemetry, not degraded telemetry, but a complete blind spot. Any tuning decisions made without agent 023's data would have been based on an incomplete picture of the fleet.

**Resolution:** Agent 023 came back online during the overnight window, restoring telemetry from that endpoint. By the time the tuning session began, all agents were reporting and both rules (100203 and 100204) had been executing continuously for approximately 23 hours.

This is worth noting because it illustrates a principle that matters in detection engineering: you cannot tune what you cannot measure. The first job was not "reduce alerts" — it was "make sure every host is actually sending data." Only after confirming full fleet coverage did the tuning work begin.

---

## 4. Detection Scope and Rules Under Test

Both custom rules targeted process-creation events, but from different log sources:

### Rule 100203 — Security Event 4688

Windows Security Event 4688 is the native Windows process-creation audit event. It records the new process name, the parent process, the account under which the process was created, and related metadata. It is enabled via audit policy and does not require additional software.

**Strengths:** Native to Windows, no agent dependency beyond Wazuh, covers all process creation visible to the Security log.  
**Limitations:** Less metadata than Sysmon (no command-line arguments in older configurations, no hashes by default).

### Rule 100204 — Sysmon Event ID 1

Sysmon Event ID 1 is the Sysmon process-creation event. It provides richer metadata: full command line, file hashes, parent process details, and more. It is the preferred telemetry source for behavioral detection engineering.

**Strengths:** Rich metadata, command-line visibility, hash capture, widely used in detection rule sets (Sigma, MITRE ATT&CK mappings).  
**Limitations:** Requires Sysmon deployment and configuration. Sysmon config tuning is itself a separate operational concern.

Running both rules simultaneously was intentional. The goal was to see the full picture of process-creation telemetry from both sources, understand the overlap, and make tuning decisions with maximum context. In production, you might choose to suppress one source in favor of the other for specific event classes, but during a baseline measurement window, you want both.

---

## 5. Fleet Health and Alert Distribution

After 24 hours of continuous rule execution, the fleet alert distribution looked like this:

| Agent | Host | Alerts (24h) | % of Total |
|-------|------|-------------|------------|
| 013 | win-hawkinsops | ~147,218 | ~97.2% |
| 023 | (restored agent) | ~2,528 | ~1.7% |
| ho-runner-01 | (CI runner) | ~1,387 | ~0.9% |
| ho-sr-01 | (server) | ~230 | ~0.2% |
| 6 others | (various) | ~21 combined | <0.01% |
| **Total** | | **~151,384** | **100%** |

This distribution is extreme but not surprising once you understand what agent 013 is. The host `win-hawkinsops` is the primary operator workstation — it runs Claude Code (which spawns heavy subprocess activity), Git operations, browser sessions, Splunk UF, and general development workloads. It is the noisiest host in the fleet by a wide margin because it has the most diverse and continuous process activity.

The six agents producing ~21 alerts combined are low-activity endpoints — servers or appliances with minimal process churn. Their low volume is expected and healthy. It means the rules are working (they do fire when processes are created) but the hosts simply do not have significant process-creation activity.

**Key interpretation:** A naive reading of this data would say "agent 013 is broken" or "agent 013 has a problem." The correct reading is: agent 013 is the host with the most operator activity, and it has not yet been tuned. The raw volume is a measurement, not a failure. The failure would be ignoring it.

---

## 6. Why Agent 013 Became the Tuning Focus

Given that agent 013 produced 97% of all alerts, every tuning decision for the immediate sprint had to focus there. The reasoning was straightforward:

1. **Volume concentration:** Tuning any other agent would affect at most 3% of total alert volume. The return on effort is negligible compared to addressing the 97% source.

2. **Queue saturation (see next section):** Agent 013 was the only agent experiencing queue-full warnings. Fixing this was prerequisite to trustworthy measurement.

3. **Noise diversity:** Agent 013 had the widest variety of process types, making it the richest dataset for noise classification. Lessons learned from tuning agent 013 would inform fleet-wide suppression strategy later.

4. **Operator workstation characteristics:** As the primary development machine, agent 013's noise profile includes categories (Claude Code subprocess churn, Git internals, Splunk UF polling) that are unique to this host or at least most concentrated here. Suppression rules for these categories should be scoped to this host, not applied fleet-wide.

This is an important design decision: the tuning was scoped to the host that needed it, not applied broadly. Fleet-wide suppression would risk silencing process-creation events on hosts where those same binaries might represent anomalous activity.

---

## 7. Queue Saturation, Measurement Distortion, and Why Step 1 Had to Come First

### The Problem

During the 24-hour measurement window, agent 013 triggered **42 queue-full warnings** (Wazuh rule 203). Each warning indicates that the agent's internal event buffer was full and incoming events were being dropped.

This is not a cosmetic issue. Dropped events mean:

- **Incomplete noise measurement:** If 5% of events are dropped, you are classifying noise based on 95% of reality. Your suppression rules might miss a category that only appears in the dropped fraction.
- **Incomplete detection coverage:** If the dropped events include the one process-creation event that matters (a lateral movement tool, a credential dumper, a reverse shell), you have a detection gap that does not appear in any dashboard or metric.
- **Distorted ratios:** If dropped events are disproportionately from one category (likely, since queue pressure is bursty and bursty processes tend to cluster), your noise taxonomy is skewed.

### The Fix

Before any noise analysis or suppression work, the agent 013 queue configuration was updated:

| Parameter | Before | After |
|-----------|--------|-------|
| Queue/buffer size | 5,000 | 16,384 |
| Drain rate | 500 eps | 1,000 eps |

The buffer increase (3.3x) provides more headroom for burst absorption. The drain rate increase (2x) ensures events are shipped to the manager faster, reducing the time events spend in the buffer.

After the change, agent 013 was confirmed active and reporting normally.

### Why This Had to Be Step 1

The temptation in a tuning sprint is to jump straight to suppression: "just turn off the noisy stuff." But suppression rules designed against distorted data are unreliable. If the queue was dropping events from a specific process category, that category would appear underrepresented in the noise analysis, and you might either:

- Over-suppress it (because you underestimated its volume and decided to suppress something else first), or
- Under-suppress it (because you did not realize it was a major contributor to queue pressure).

By fixing the queue first, the subsequent noise analysis was based on complete data. This is the difference between tuning from measurement and tuning from assumption.

---

## 8. Noise Taxonomy and What the Process Analysis Revealed

With the queue fix in place, the full 24-hour dataset from agent 013 was analyzed across both rules (100203 and 100204). The goal was to classify every major alert source into one of three categories:

- **Signal:** Process executions with genuine detection or forensic value.
- **Infrastructure noise:** Process executions from known monitoring, management, or platform tools that are predictable, repetitive, and low-value for detection.
- **Ambiguous:** Process executions that are currently noisy but might carry detection value under different conditions or with more context.

### Noise Classification Table

| Category | Representative Binaries | Approx. Volume (24h) | Classification | Rationale |
|----------|------------------------|----------------------|----------------|-----------|
| Git / bash internals | bash.exe, base64.exe, hostname.exe, which.exe, locale.exe, find.exe, wc.exe, grep.exe, head.exe, sed.exe | ~83,000 | Ambiguous / Deferred | Mostly Claude Code and shell subprocess churn. Low operational value in current form, but bash.exe itself and some coreutils have detection relevance in other contexts. |
| Splunk UF polling | splunk-powershell.exe, splunk-netmon.exe, splunk-MonitorNoHandle.exe, splunk-regmon.exe, splunk-admon.exe | ~13,500 | Infrastructure noise | Known agent infrastructure. Predictable polling cycle. Zero detection value — these are monitoring tools doing exactly what they are configured to do. |
| conhost.exe | conhost.exe | ~8,100 | Infrastructure noise | Console Host process. Spawned automatically by Windows whenever a console application runs. Pure platform machinery. |
| Edge / browser helpers | msedge.exe, identity_helper.exe | ~3,700 | Mixed | identity_helper.exe is noise. msedge.exe was preserved — browser process creation can be relevant for download-and-execute detection chains. |
| Windows platform housekeeping | backgroundTaskHost.exe, SearchProtocolHost.exe, dllhost.exe, taskhostw.exe, tzutil.exe, svchost.exe | ~2,100 | Infrastructure noise | Standard Windows scheduled and background processes. Predictable, high-frequency, low detection value on an operator workstation. |
| Google updater | updater.exe | ~350 | Infrastructure noise | Google Chrome/software updater. Periodic, predictable, no detection value. |

### Summary

| Classification | Approximate Volume | % of Agent 013 Total |
|---------------|--------------------|---------------------|
| Infrastructure noise (clear) | ~27,750 | ~18.9% |
| Ambiguous / Deferred (Git/bash) | ~83,000 | ~56.4% |
| Remaining (signal + unclassified) | ~36,468 | ~24.8% |

**Key finding:** Roughly 110,000 of 147,000 alerts were operationally low-value. But the largest single category — Git/bash subprocess churn at ~83,000 — was not immediately suppressed. This was a deliberate decision explained in Section 10.

---

## 9. Suppression Strategy Design

The suppression approach was designed around three principles:

### Principle 1: Host-scoped, not fleet-wide

Every suppression rule was scoped exclusively to agent 013 (`win-hawkinsops`). The same binary that is noise on the operator workstation might be signal on a server. For example:

- `svchost.exe` on the operator workstation: platform housekeeping, expected.
- `svchost.exe` on a server that normally runs only three services: potentially interesting if a new instance appears.

Fleet-wide suppression throws away this contextual distinction. Host-scoped suppression preserves it.

### Principle 2: Level-0 child rules, not rule modifications

All 28 suppression rules were deployed as **level 0 child rules** of the parent detection rules (100203 and 100204). This means:

- The parent rules were not modified. They continue to fire for every process-creation event.
- The child rules match specific process names and set the alert level to 0 (suppressed — not indexed, not alerted).
- If a suppression rule is later found to be too broad, it can be removed without touching the parent rule. The parent immediately resumes alerting for that process.

This is fundamentally different from editing the parent rule to exclude certain processes. Parent rule edits are harder to audit, harder to reverse, and create coupling between detection logic and tuning logic. Child suppression rules keep them separate.

### Principle 3: Staged deployment, not aggressive blanket exclusion

The suppression was deployed in a single batch but covers only the **clearest** noise categories. The largest category (Git/bash subprocess churn) was intentionally excluded from this round. The reasoning:

- Suppressing ~83,000 alerts in one shot based on one 24-hour window is aggressive.
- Some of those binaries (bash.exe, find.exe, grep.exe) are legitimate attack tools when used outside their expected context.
- The correct approach is: suppress the obvious noise first, re-measure, and then decide whether Layer B path-based tuning (suppressing only when the parent process is a known development tool) is needed for the ambiguous category.

### The Difference Between Broad Suppression, Scoped Suppression, and Deferred Path-Based Tuning

| Approach | What It Does | Risk | When to Use |
|----------|-------------|------|-------------|
| **Broad suppression** | Suppress a binary fleet-wide, regardless of context | High — removes detection on all hosts | Almost never in early tuning |
| **Scoped suppression** | Suppress a binary on a specific host | Low — preserves detection elsewhere | When a binary is confirmed noise on that host |
| **Deferred path-based tuning** | Suppress a binary only when spawned by a specific parent process or from a specific path | Very low — preserves detection for unexpected parent chains | When the binary has dual use (legitimate tool + potential attack tool) |

This sprint deployed scoped suppression. Path-based tuning is the planned next layer for the Git/bash category.

---

## 10. Why Certain Binaries Were Preserved

Not everything noisy was suppressed. The following binaries were intentionally kept in the alert stream:

| Binary | Reason for Preservation |
|--------|------------------------|
| cmd.exe | Primary Windows command interpreter. Process creation of cmd.exe is a core indicator in many attack chains (encoded commands, LOLBin execution, lateral movement). |
| powershell.exe | The most commonly abused Windows binary in post-exploitation. Suppressing it would be negligent. |
| pwsh.exe | PowerShell Core. Same reasoning as powershell.exe. |
| node.exe | Runs application logic. Unexpected node.exe execution could indicate supply-chain compromise or reverse shell activity. |
| python.exe | Same as node.exe. Scripting interpreter with offensive use cases. |
| claude.exe | Claude Code binary. Preserved for operational awareness — it drives significant subprocess activity and its execution pattern is worth tracking. |
| git.exe | Git itself was preserved even though Git internals were heavy noise contributors. git.exe process creation can indicate repository access, code exfiltration, or cloning activity. |
| ssh.exe | Remote access tool. Always preserved. |
| curl.exe | Download utility. Commonly used in attack chains for payload retrieval. |
| reg.exe | Registry editor CLI. Commonly used for persistence, defense evasion, and credential access. |
| msedge.exe | Browser process creation. Relevant for download-and-execute chains and browser exploitation. |
| bash.exe | Preserved pending Layer B path-based tuning. bash.exe itself can indicate WSL or Git Bash usage that might be operationally relevant. |
| Git coreutils | Preserved pending post-suppression re-measurement. Once the floor is lowered by suppressing clear noise, the relative volume and pattern of coreutils execution will be easier to assess. |

The decision framework was simple: **if a security analyst would want to know about this binary executing in an unexpected context, do not suppress it based on volume alone.**

---

## 11. Rule Deployment Details

### Suppression Rules Deployed

| Rule ID Range | Count | Parent Rule | Match Field | Scope |
|--------------|-------|-------------|-------------|-------|
| 100210–100221 | 12 | 100203 (Security 4688) | newProcessName | agent 013 / win-hawkinsops only |
| 100222–100237 | 16 | 100204 (Sysmon EID 1) | image | agent 013 / win-hawkinsops only |
| **Total** | **28** | | | |

### Suppressed Process Categories

| Category | Binaries Suppressed | Estimated Daily Volume Removed |
|----------|-------------------|-------------------------------|
| Splunk UF | splunk-powershell.exe, splunk-netmon.exe, splunk-MonitorNoHandle.exe, splunk-regmon.exe, splunk-admon.exe | ~13,500 |
| Windows housekeeping | backgroundTaskHost.exe, SearchProtocolHost.exe, dllhost.exe, taskhostw.exe, tzutil.exe, svchost.exe, conhost.exe | ~10,200 |
| Browser helpers | identity_helper.exe | ~500 |
| Google updater | updater.exe | ~350 |
| **Total estimated suppression** | | **~24,550/day** |

### Technical Implementation Notes

- **Security 4688 path (rules 100210–100221):** Match on the `win.eventdata.newProcessName` field. This is the field populated by Windows Security Event 4688 containing the full path of the newly created process.
- **Sysmon EID 1 path (rules 100222–100237):** Match on the `win.eventdata.image` field. This is the Sysmon-specific field containing the full image path of the created process.
- **Level 0:** All suppression rules set `level` to 0. This means the event is still processed by the Wazuh analysis engine (the rule fires, the match is evaluated) but the resulting alert is not indexed or forwarded. If the suppression rule is removed, the parent rule immediately resumes generating visible alerts for that process.
- **No syscheck or rootcheck impact:** These rules affect only alerting for process-creation events. They do not modify file integrity monitoring, rootkit detection, or any other Wazuh module.

---

## 12. Risk Tradeoffs and Why This Was Not Over-Suppression

### What was suppressed

Only processes that meet all of the following criteria:

1. Known infrastructure or platform binary (not a user-invoked tool)
2. Predictable execution pattern (polling cycle, scheduled task, console host spawn)
3. Zero or near-zero detection value on this specific host
4. High volume (contributes meaningfully to alert noise)

### What was not suppressed

- Any binary with dual-use potential (scripting interpreters, remote access tools, download utilities, registry editors)
- Any binary whose unexpected execution on a different host would be meaningful
- The entire Git/bash subprocess category, despite being the single largest noise source

### Risk assessment

| Risk | Mitigation |
|------|-----------|
| Suppressed binary is used in an attack on agent 013 | Unlikely for these specific binaries (Splunk UF components, conhost, background task hosts). If an attacker is naming their payload `splunk-regmon.exe`, that is a different detection problem (hash mismatch, unexpected path, anomalous parent). |
| Suppression rules are too broad | Rules match on full process name, scoped to one host. They cannot accidentally suppress events from other hosts or other process names. |
| Future process changes make suppression incorrect | Suppression rules are level-0 children, trivially removable. Periodic review (recommended quarterly) catches drift. |
| Suppressing conhost.exe hides console-spawn chains | conhost.exe is the console host, not the payload. The payload (cmd.exe, powershell.exe, etc.) is still visible. Suppressing conhost.exe removes the wrapper noise without losing the command interpreter alert. |

### Why Alert-Volume Reduction Is Not the Same as Restored Visibility

Reducing alert volume is easy. You can suppress everything and achieve zero alerts. That is not the goal.

The goal is to move from a state where the alert stream is dominated by known, predictable, low-value events to a state where the remaining alerts are worth examining. The metric that matters is not "alerts per day" — it is "percentage of alerts that an analyst would act on or at least acknowledge as potentially meaningful."

Before suppression: ~147,000 alerts/day on agent 013, of which ~110,000 were classifiable noise. An analyst opening the alert queue would see an unnavigable wall of Splunk UF polls and conhost spawns.

After suppression: ~122,000 alerts/day estimated (the Git/bash category remains), but the clear infrastructure noise is gone. The remaining volume is dominated by the deferred ambiguous category, which is the next tuning target, and actual operator/tooling activity that may have detection value.

The improvement is not in the number. The improvement is in the interpretability.

---

## 13. Immediate Outcomes

### Before vs. After Tuning State

| Dimension | Before Sprint | After Sprint |
|-----------|--------------|-------------|
| Fleet agent coverage | Agent 023 offline — blind spot | All agents reporting |
| Rule execution stability | Untested over extended period | 23h continuous run confirmed stable |
| Queue health (agent 013) | 42 queue-full warnings / day; event loss confirmed | Buffer 3.3x, drain 2x; no further queue warnings expected |
| Noise classification | Unclassified; raw volume only | Full taxonomy by source category |
| Suppression rules deployed | 0 | 28 (scoped, level-0, reversible) |
| Estimated daily noise removed | 0 | ~24,550 alerts/day |
| Detection coverage reduced | N/A | None — no detection rules disabled or weakened |
| Indexer connector | Stable | Stable (no change) |

### Decision Log

| Decision | Rationale |
|----------|-----------|
| Fix queue before analyzing noise | Dropped events distort noise classification; measurement must be trustworthy before tuning decisions are made |
| Scope all suppression to agent 013 only | 97% of volume originates there; same binaries may be signal on other hosts |
| Use level-0 child rules, not parent rule edits | Reversibility, auditability, separation of detection logic from tuning logic |
| Suppress Splunk UF, Windows housekeeping, browser helpers, updater | Confirmed infrastructure noise, predictable, zero detection value |
| Preserve cmd, powershell, pwsh, node, python, ssh, curl, reg | Dual-use binaries with genuine detection relevance |
| Defer bash/Git coreutils suppression | Largest noise category but ambiguous; needs post-suppression re-measurement and potential Layer B path-based tuning |
| Increase buffer to 16384 and drain to 1000 eps | Sized to handle current volume with headroom; will re-evaluate if queue warnings recur |

---

## 14. Remaining Open Question: bash / Git Coreutils / Layer B

The single largest unresolved noise source is the Git/bash subprocess category, responsible for approximately 83,000 alerts per day on agent 013. This category includes:

- `bash.exe` — the Git Bash shell
- `base64.exe`, `hostname.exe`, `which.exe`, `locale.exe` — coreutils invoked by shell scripts
- `find.exe`, `wc.exe`, `grep.exe`, `head.exe`, `sed.exe` — text processing utilities invoked by Claude Code and development workflows

### Why it was not suppressed in this round

1. **bash.exe has detection value.** An unexpected bash.exe execution on a Windows host — especially one not associated with Git or development tooling — can indicate WSL abuse, living-off-the-land activity, or unauthorized tool installation.

2. **Coreutils have detection value in unexpected contexts.** `find.exe` and `grep.exe` are used by attackers for discovery. Suppressing them by name alone would create a blind spot.

3. **The volume is context-dependent.** Most of the 83,000 alerts are generated by Claude Code subprocess churn. If Claude Code is not running, the volume drops dramatically. A static suppression rule does not account for this.

### Planned Layer B approach

The recommended next step is **path-based or parent-process-based suppression**:

- Suppress `bash.exe` and coreutils only when the parent process is a known development tool (e.g., `claude.exe`, `git.exe`, `node.exe`).
- Preserve alerting when the parent process is unexpected (e.g., `cmd.exe` spawning `bash.exe`, or `svchost.exe` spawning `find.exe`).

This requires Sysmon Event ID 1 data (which includes parent process information) and more granular rule logic. It is a natural second-layer tuning step that should be designed after the post-suppression re-measurement window.

---

## 15. Operational Lessons Learned

### Lesson 1: Fix the pipe before analyzing the water

Queue saturation was silently distorting the noise measurement. If the tuning session had started with noise analysis instead of queue repair, every subsequent decision would have been based on incomplete data. In detection engineering, the reliability of your measurement infrastructure is prerequisite to the reliability of your tuning decisions.

### Lesson 2: Volume concentration is normal; ignoring it is not

A 97/3 alert distribution looks alarming but is expected in environments where one host has dramatically more process activity than others. The correct response is not to treat the high-volume host as broken — it is to treat it as the priority tuning target. The danger is letting the volume persist unexamined because "that is just how it is."

### Lesson 3: Staged tuning is more defensible than aggressive first-pass exclusion

It would have been faster to suppress everything that was not cmd.exe, powershell.exe, or ssh.exe. It would also have been wrong. Aggressive first-pass suppression:

- Removes categories you have not fully analyzed
- Creates blind spots you have not quantified
- Makes it harder to identify what you lost, because the suppressed events stop appearing in your data
- Is difficult to justify to a reviewer or auditor who asks "why did you suppress this?"

Staged tuning — suppress the obvious, re-measure, then decide on the ambiguous — produces a defensible audit trail and reduces the risk of over-suppression.

### Lesson 4: The indexer is not the bottleneck you think it is

In this sprint, the indexer connector was stable throughout. The problems were all agent-side: offline agents, queue capacity, and process-creation volume. This is a useful reminder that "the SIEM is slow" or "the dashboard is not loading" often has nothing to do with the backend. Check the edges first.

### Lesson 5: Child suppression rules are operationally superior to parent rule edits

Modifying a parent detection rule to exclude certain processes mixes detection logic with tuning logic in a single rule definition. This makes it harder to:

- Audit what is being suppressed
- Reverse a specific suppression without touching the detection rule
- Track when a suppression was added and why
- Apply different suppression scopes to different hosts

Level-0 child rules keep the parent rule clean, the suppression logic separate, and the whole system more auditable.

---

## 16. Reviewer-Facing Interpretation: What This Sprint Proves

For a hiring manager, SOC lead, or detection engineer reviewing this work, the sprint demonstrates the following competencies:

**Measurement discipline.** The work did not begin with "reduce alerts." It began with "make sure we can trust the data." Queue repair preceded noise analysis. Full fleet coverage was confirmed before tuning. This is the difference between engineering and guessing.

**Noise taxonomy.** The alert volume was not treated as a single undifferentiated mass. It was broken down by source category, with each category assessed independently for detection value. The resulting taxonomy is documented, reviewable, and actionable.

**Scoped, reversible tuning.** Suppression was deployed as host-scoped level-0 child rules, not broad exclusions or parent rule modifications. Every suppression decision is individually reversible. No detection coverage was removed.

**Deliberate preservation of ambiguous categories.** The largest noise source was not suppressed because it had not been fully analyzed. This is not indecision — it is discipline. Suppressing 83,000 alerts without sufficient analysis would be reckless. Deferring that suppression pending re-measurement is the operationally correct choice.

**Pipeline thinking.** The sprint treated the detection pipeline as a system: agent health, queue capacity, rule execution, noise composition, suppression deployment, and re-measurement planning. Each step was prerequisite to the next. This is how production detection engineering works.

**Documentation as operational artifact.** This report is not retrospective narrative. It is the operational record. The decisions, rationale, and next steps are documented in a form that can be referenced in the next tuning session, handed to a colleague, or presented to a reviewer.

---

## 17. Recommended Next Steps for the Next 12 to 24 Hours

| Priority | Action | Rationale |
|----------|--------|-----------|
| 1 | Monitor agent 013 for queue-full warnings (rule 203) | Confirm that the buffer/drain increase resolved event loss |
| 2 | Measure post-suppression alert volume on agent 013 | Validate that ~24,550/day noise reduction is realized; compare actual vs. estimated |
| 3 | Re-examine Git/bash subprocess volume in post-suppression data | With clear noise removed, the relative contribution of bash/coreutils will be more visible |
| 4 | Design Layer B path-based suppression rules for bash/coreutils | Suppress only when parent process is a known development tool; preserve alerting for unexpected parent chains |
| 5 | Spot-check other agents for emerging noise patterns | Low volume now, but tuning should be proactive, not reactive |
| 6 | Validate indexer connector stability over 48h total | Confirm no degradation under changed alert composition |
| 7 | Document Layer B suppression rules before deployment | Maintain the same audit trail established in this sprint |

---

## 18. Final Assessment

This sprint took a Wazuh deployment from a state of partial visibility and uncontrolled volume to a state of full fleet coverage, measured noise composition, and targeted suppression. The work was operationally necessary: without it, the alert pipeline would have continued producing ~150,000 process-creation alerts per day, of which the majority were unactionable, and intermittent event loss would have continued silently degrading detection coverage.

The suppression deployed is conservative, scoped, reversible, and documented. It removes approximately 24,550 confirmed low-value alerts per day without touching any binary that has plausible detection relevance. The largest remaining noise source — Git/bash subprocess churn — is deferred pending re-measurement, not ignored.

The system is real, under load, and operated with the discipline expected of a production detection-engineering environment. The next tuning cycle will build on the foundation established here: trustworthy measurement, classified noise, and a suppression architecture designed for iterative refinement rather than one-time cleanup.

---

*End of report.*
