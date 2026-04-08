# Wazuh Operational Tuning — April 2026

## Scope

Manager-side noise suppression and FIM exclusion tuning applied to specific agents after baseline collection and alert analysis. This is operational tuning on the live Wazuh manager (`HO-SR-WM-01`, Wazuh v4.14.4-rc2), not changes to the repo's detection rule pack.

## Status

- **Tuning applied:** 2026-04-08
- **Immediate sanity checks:** Passed (both agents)
- **Full recollection:** Pending (earliest 2026-04-09, 24–48 hours post-tune)

Results below reflect immediate post-restart validation only. Final noise reduction percentages require a fixed-window recollection comparison against pre-tune baselines.

---

## Agent 013 — win-hawkinsops (Windows workstation)

### Changes applied

| Rule/Change | Type | Purpose |
|---|---|---|
| Rule 100205 | Suppression (if_sid 92213) | Suppress PSScriptPolicyTest false positives — PowerShell module policy test events firing on every AI tool invocation |
| Rule 100206 | Suppression (if_sid 60227) | Suppress benign external device (60227) churn from known USB/Bluetooth devices |
| FIM ignore: ossec-agent paths | Agent config | Exclude Wazuh agent's own file churn from syscheck |
| FIM ignore: Splunk UF var | Agent config | Exclude Splunk Universal Forwarder variable data |
| FIM ignore: BAM registry | Agent config | Exclude Background Activity Moderator registry key churn |

### Files modified on manager

- `/var/ossec/etc/rules/local_rules.xml` — added rules 100205, 100206
- `/var/ossec/etc/shared/windows_workstations/agent.conf` — created (FIM ignores)
- Backup: `/var/ossec/etc/rules/local_rules.xml.bak-pre-013-tune-20260408-0453`

### Immediate validation

- Rule 92213 alerts post-restart: **0** (was ~50 per 5 minutes before)
- Rule 60227 benign device alerts post-restart: **0** (suppressed)
- Preserved detections confirmed generating:
  - Rule 100203 (Windows 4688): 672 new alerts — generating
  - Rule 100204 (Sysmon EID 1): 633 new alerts — generating
  - Rule 92151 (PowerShell DLL): intact
  - Rule 92153 (VaultCli.dll): intact

### Pending

- FIM exclusions: periodic scan-based, pending next syscheck cycle
- Full recollection per `Z:\Data\wazuh\04-08\02_post_tune\013_win-hawkinsops\summary\machine\013_recollection_plan.md`

---

## Agent 006 — ho-sr-01 (Proxmox server)

### Changes applied

| Rule/Change | Type | Purpose |
|---|---|---|
| Rule 100301 | Suppression (if_sid 40704) | Suppress systemd service failure alerts for `hawkinsops-pull.service` — timer fires every 15 min, service has been failing since 2026-03-20 (infrastructure issue, not security) |
| Rule 100304 | Suppression (if_sid 100053) | Suppress rootcheck false positives for 6 Debian 13 PAM binaries that have legitimate hash mismatches against the CIS rootkit database |
| FIM ignores: /etc/pve/ paths | Agent config (default group) | Exclude 7 Proxmox cluster config paths that change on every VM/container state transition |

### Files modified on manager

- `/var/ossec/etc/rules/local_rules.xml` — added rule 100301
- `/var/ossec/etc/rules/raylee/wazuh-053-rootkit-detection.xml` — added rule 100304
- `/var/ossec/etc/shared/default/agent.conf` — added 7 FIM ignore entries for /etc/pve/

### Immediate validation

- Rule 40704 suppression: **confirmed working** — `hawkinsops-pull.service` failed at 05:00 UTC, no alert generated
- Rule 100304: loaded without warnings, pending first rootcheck scan (12h interval)
- FIM /etc/pve/ ignores: merged, pending agent sync and next syscheck scan
- API sanity checks:
  - Agent 006: active, keepalive current
  - FIM: 4,922 entries (baseline 4,928)
  - SCA: 41%, 207 checks (identical to baseline)

### Pending

- Rootcheck suppression untested (next scan in ~12 hours)
- FIM ignores pending agent sync
- Full recollection per `Z:\Data\wazuh\04-08\02_post_tune\006_ho-sr-01\summary\machine\006_recollection_plan.md`

---

## Unresolved items for future tuning

- Rule 100052 false positive pattern on agent 013 (not yet scoped)
- Wazuh queue buffer tuning (agent 013 high-volume periods)
- FIM file limit on agent 013 (99,999/100,000 — near capacity)
- `hawkinsops-pull.service` infrastructure fix (out of scope for Wazuh tuning, but the root cause of rule 40704 noise)

---

## Relationship to other docs

- **Splunk detection tuning:** See `docs/detection-tuning-sprint-apr2026.md` (SPL-side refinements, separate scope)
- **Wazuh rule pack deploy process:** See `docs/wazuh_change_control.md` (repo pack deployment, not manager-side operational tuning)
- **Telemetry remediation case study:** See `content/case-studies/wazuh-telemetry-remediation.md` (the prerequisite work that restored process creation visibility before this tuning could begin)
