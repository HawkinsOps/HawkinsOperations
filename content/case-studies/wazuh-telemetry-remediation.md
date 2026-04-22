# Wazuh Windows Telemetry Remediation

**Platform:** Wazuh 4.14.4-rc2 (single-node: manager, indexer, dashboard)
**Date:** April 2026
**Scope:** Three-phase restoration of Windows process creation telemetry across a 10-agent deployment
**Status:** Complete (primary endpoint validated; one endpoint pending)

---

## Executive Summary

A 10-agent Wazuh deployment appeared healthy — daemons running, 5,000+ alerts per day, all agents connected. A configuration audit revealed it was blind to Windows process creation: zero Security Event 4688 alerts and zero Sysmon Event ID 1 alerts had ever been indexed. Three independent failures were responsible: an alert-level threshold that silently discarded low-level events, a severed manager-to-indexer pipeline caused by a prior security config reset, and a Sysmon installation running without a configuration file.

A three-phase remediation restored both telemetry paths and proved end-to-end detection on the primary Windows endpoint: 2,120+ Security 4688 alerts and 143 Sysmon EID 1 events indexed with full telemetry (process image, command line, parent process, user context).

---

## Environment

| Component | Detail |
|-----------|--------|
| Wazuh Manager | Ubuntu, Wazuh v4.14.4-rc2, single-node deployment |
| Wazuh Indexer | OpenSearch on same host, 294 shards |
| Total Agents | 10 (9 non-manager) |
| Windows Agents | 2 (Windows 11 Enterprise, Wazuh agents v4.14.0-4.14.3) |
| Linux Agents | 7 (Ubuntu, Debian, Linux Mint — servers, CI runner, honeypot) |
| Agent Groups | 5: default, windows_workstations, linux_servers, infrastructure, honeypot |
| Custom Rules | 29 detection rules + 5 local operational rules |
| Manager log_alert_level | 5 (only level 5+ alerts are indexed) |

---

## Initial Symptom

The dashboard showed zero process-creation alerts from any Windows agent. Ever. A query for rule 67027 (Security 4688) across all time returned zero results. Sysmon events existed only as Event ID 7 (ImageLoad) noise — 39,318+ events generating tens of thousands of high-level alerts — but zero Event ID 1 (ProcessCreate) events.

The deployment had full agent connectivity, healthy daemons, consistent alert flow, and active file integrity monitoring. It looked like it was working. It was not watching the thing that matters most for threat detection on Windows: what processes are executing.

---

## Why It Mattered

Process creation is the backbone of Windows threat detection. Without it:

- Credential dumping (Mimikatz, comsvcs.dll) is invisible
- PowerShell download cradles execute undetected
- Lateral movement tools (PsExec, WMI) leave no trace
- LOLBin abuse (certutil, mshta, rundll32) generates no alerts
- Parent-child process anomalies cannot be correlated

The 29 custom detection rules covering MITRE ATT&CK techniques were technically loaded but had no data to match against. The rules existed. The telemetry they needed did not.

---

## Phase 1 — Windows Telemetry Visibility

### Starting State

Rule 67027 (Security 4688 process creation) had been restored to its upstream level 3 during an earlier audit remediation. But zero process creation alerts appeared in the indexer.

### Root Causes Discovered

**Alert level threshold mismatch (Proven):** Rule 67027 fires at level 3. The manager `log_alert_level=5`. Only level 5+ alerts are written to the alerts file and forwarded to the indexer. Every 4688 event was decoded, matched by rule 67027, and silently discarded because 3 < 5.

**Host suppression rule (Proven):** A custom rule specifically suppressed all rule 67027 alerts for the primary Windows workstation. Even if the threshold were fixed, this machine's 4688 events would be silenced.

### Changes Made

1. Removed the host-scoped suppression rule from `local_rules.xml`
2. Added rule 100203 (level 5, child of rule 67027) to elevate Security 4688 alerts above the indexing threshold
3. Restarted wazuh-manager (8,490 rules loaded, no errors)

### Validation

- Rule 100203 confirmed loaded via API: level 5, parent 67027, enabled
- Manager receiving 20,343+ Windows events, writing 607+ alerts, 0 dropped
- Windows audit policy confirmed: Process Creation = "Success and Failure"
- Agent Security channel confirmed collecting 4688 events

### Remaining Gap

**End-to-end indexer proof was blocked.** The manager was writing alerts, but zero were reaching the indexer. The indexer connector was broken — a pre-existing issue discovered during validation.

---

## Phase 2 — Indexer Connector Restoration

### Starting State

The manager-to-indexer pipeline was completely down. 46,385 events decoded, 1,441 alerts written locally, but zero delivered to OpenSearch. The April 8 alerts index did not exist. Connector logs showed "No available server" for all agents.

### Root Causes Discovered

Two independent breaks in the OpenSearch security configuration, both caused by a prior `securityadmin.sh -cd` command that reloaded all 10 security config files from disk defaults:

**Client certificate auth disabled (Proven):** `config.yml` had `clientcert_auth_domain.http_enabled: false`. The manager authenticates to OpenSearch using a TLS client certificate. With HTTP client cert auth disabled, every connection attempt was rejected.

**No role mapping (Proven):** `roles_mapping.yml` had `all_access.users: []`. Even if auth succeeded, the manager's certificate identity had no role granting index write permissions.

### Why Both Broke Simultaneously

A prior fix ran `securityadmin.sh -cd` to apply a single change to `internal_users.yml`. The `-cd` flag reloads ALL 10 security config files from disk, not just the one that changed. The on-disk defaults had client cert auth disabled and no server mapping, overwriting whatever was previously in the live security index.

### Changes Made

1. Enabled `clientcert_auth_domain.http_enabled: true` in `config.yml`
2. Added manager server identity to `all_access.users` in `roles_mapping.yml`
3. Applied via `securityadmin.sh`, restarted wazuh-manager

### Validation

- IndexerConnector initialized successfully for ALL indices within 25 seconds
- New alerts index created: **2,197+ documents, growing in real-time**
- **2,120+ rule 100203 alerts** from the primary Windows agent — real Security 4688 process creation events
- End-to-end chain proven: Windows 4688 -> agent -> manager -> rule 100203 (level 5) -> indexer -> OpenSearch

---

## Phase 3 — Sysmon Telemetry Restoration

### Starting State

Security 4688 detection was working end-to-end. But Sysmon EID 1 — which provides richer telemetry than 4688 (command line hashes, parent process trees, detailed user context) — was still absent. Sysmon v15.15 was installed and running on the primary Windows endpoint, generating only default Event ID 7 (ImageLoad) events.

### Root Causes Discovered

**Sysmon had no configuration file (Proven):** Registry showed only `DriverName: SysmonDrv` with no ConfigFile parameter. Without a config, Sysmon generates only default events. Event ID 1 (ProcessCreate) requires explicit configuration.

**Rule 61603 at level 0, below indexing threshold (Proven):** The base Sysmon EID 1 rule in the default ruleset fires at level 0 — a classifier rule. Same threshold pattern as Phase 1: events decoded and discarded because 0 < 5. Higher-level Sysmon detection rules (92000-series) only fire for specific suspicious patterns — normal process creation stays at level 0.

**Second endpoint unreachable (Proven):** The second Windows agent did not respond to ping or remote management. All Phase 3 work on that agent was blocked.

### Changes Made

1. Created and deployed a minimal Sysmon config (schema 4.90): enables EID 1 (ProcessCreate) with noise exclusions, disables EID 7 (ImageLoad noise), adds targeted rules for network connections (LOLBins), registry persistence, LSASS access, file creation, and DNS queries
2. Added rule 100204 (level 5, child of rule 61603) to elevate Sysmon EID 1 above the indexing threshold
3. Restarted wazuh-manager (8,491 rules loaded, no errors)

### Validation

- **143 Sysmon EID 1 events indexed in 5 minutes** from the primary Windows agent
- Full telemetry confirmed: process image path, full command line, parent process, user context, timestamp
- Both user-level and SYSTEM-level process creation captured
- Sample validated event: `net.exe user` -> parent `pwsh.exe` -> user context confirmed

---

## Before / After Summary

| Metric | Before | After |
|--------|--------|-------|
| Security 4688 alerts indexed (all time) | 0 | 2,120+ (and growing) |
| Sysmon EID 1 alerts indexed (all time) | 0 | 143+ (first 5 minutes) |
| Sysmon EID 7 noise (primary endpoint) | 39,318 events | Disabled in new config |
| Alerts reaching indexer | 0 (pipeline broken) | 2,197+ and growing |
| Sysmon config on primary endpoint | Empty (no config file) | Minimal config: EID 1 enabled, EID 7 disabled |
| Primary endpoint process visibility | Blind | Full (4688 + Sysmon EID 1) |
| Secondary endpoint process visibility | Blind | Online — 9/9 agents connected |
| OpenSearch client cert auth | Disabled | Enabled |
| Manager total rules loaded | 8,490 | 8,491 |

---

## What Was Proven

1. Security 4688 events collected, decoded, matched by rule 100203, and indexed (2,120+ alerts)
2. Sysmon EID 1 events collected, decoded, matched by rule 100204, and indexed (143 alerts in 5 min)
3. Full telemetry present: process image, command line, parent process, user context
4. Both user-context and SYSTEM-context processes captured
5. IndexerConnector delivers alerts to OpenSearch in real-time
6. Client certificate auth path functional end-to-end

## What Was Not Fully Proven

1. ~~Secondary Windows endpoint — host unreachable~~ — resolved; back online, 9/9 agents connected
2. Long-term Sysmon EID 1 volume impact (just deployed)
3. Higher-level Sysmon detection rules (92000-series) firing for specific suspicious patterns
4. Recovery of alerts generated during the ~6-hour indexer outage

---

## Remaining Gaps

1. ~~**Secondary endpoint has zero process visibility**~~ — resolved; host back online, all 9 non-manager agents connected
2. **Event collection not centrally managed** — Windows agents rely on local config for channel collection; agent reinstall loses config
3. **FIM limit nearly exhausted** on primary endpoint (99,999/100,000 files monitored)
4. **Sysmon config is minimal** — may need tuning for noise patterns and additional detection scenarios

---

## Lessons Learned

### 1. The same threshold pattern broke two independent telemetry sources

Security 4688 (rule 67027, level 3) and Sysmon EID 1 (rule 61603, level 0) both fell below `log_alert_level=5`. The fix was identical both times: add a child rule at level 5. Any Wazuh deployment with `log_alert_level > 3` should audit all base event rules to ensure needed events cross the indexing threshold.

### 2. `securityadmin.sh -cd` is a shotgun, not a scalpel

Running `-cd` to apply a single file change reloaded all 10 security configs from disk defaults, breaking two unrelated settings. The correct approach is `securityadmin.sh -f <file> -t <type>` to scope the change to the specific config file.

### 3. Sysmon "installed and running" does not mean "configured and generating"

Sysmon was installed, auto-starting, running for weeks, and contributing ~39,000 ImageLoad events. This created the appearance of Sysmon telemetry without the substance. The most operationally valuable event type — ProcessCreate — was never generated because no configuration file existed.

### 4. A broken indexer pipeline is invisible until you look at the index

The manager continued processing events, writing alerts, and reporting healthy daemon status. The only sign of the broken pipeline was in connector logs and the absence of new documents in the index. The dashboard showed stale data without any visible error state.

### 5. Before-state evidence is the case study

Every config file, daemon status, and dashboard screenshot was captured before changes. This made it possible to precisely document what was broken, prove what changed, and demonstrate the delta.

---

## Evidence

- 14 before-state dashboard screenshots
- 7 before-state config exports (ossec.conf, local_rules.xml, disabled rules, agent.conf, auth config, daemon status)
- 20 after-state rule exports with unified diffs
- 3 phase fix documents with root cause analysis and validation
- 3 raw diagnostic output files
- 3 validation reports (all with PASS results)
- Sysmon configuration XML (deployed to primary endpoint)
- Complete session log with START/CHANGE/VALIDATION/END entries for all phases

---

*This case study documents a real remediation performed on a home lab Wazuh deployment. All IP addresses, hostnames, and identifying details have been sanitized.*
