# AutoSOC Backlog False Positive Pattern Analysis

- **Generated:** 2026-04-01
- **Total Cases Analyzed:** 328,515
- **Backlog Period:** 2026-01-09 through 2026-04-01
- **Data Source:** AutoSOC case directory names + sample alert JSON

## Agent Distribution

| Agent | Cases | % of Total | Platform |
|---|---|---|---|
| HOWE01 | 289,906 | 88.2% | Windows workstation |
| win-hawkinsops | 31,780 | 9.7% | Windows workstation (renamed) |
| ho-sr-01 | 2,582 | 0.8% | Linux server |
| ho-lm-01 | 1,752 | 0.5% | Linux (log manager) |
| ho-sr-wm-01 | 914 | 0.3% | Wazuh manager |
| ho-grafana-01 | 250 | 0.1% | Grafana server |
| ho-honeypot-01 | 225 | 0.1% | Honeypot |
| ho-runner-01 | 108 | <0.1% | CI runner |

**Finding:** 97.9% of all alerts originate from the Windows workstation (HOWE01 / win-hawkinsops). This is the primary developer machine running AI coding tools, browsers, and normal workstation activity.

---

## Top 20 Rules by Alert Volume

| Rank | Rule ID | Description | Alert Count | % of Total | Agent(s) | Current Disposition | FP Pattern | Proposed Action |
|---|---|---|---|---|---|---|---|---|
| 1 | 67027 | A process was created | 190,492 | 58.0% | HOWE01 | AUTO_CLOSE (rule list) | All process creation events at level 3 | Already auto-closed. No SPL change needed. |
| 2 | 60227 | New external device recognized | 84,746 | 25.8% | HOWE01, win-hawkinsops | AUTO_CLOSE_KNOWN_FP (override) | Printer, Bluetooth, audio device churn | Already suppressed via policy override. |
| 3 | 60104 | Windows audit failure event | 7,693 | 2.3% | HOWE01, win-hawkinsops | AUTO_CLOSE_KNOWN_FP (override) | Key Storage Provider open-key failure | Already suppressed via policy override. |
| 4 | 750 | Registry Value Integrity Checksum Changed | 6,256 | 1.9% | HOWE01 | AUTO_CLOSE (level <= 3) | FIM/syscheck registry churn from normal app activity | Add syscheck registry exclusions to SPL persistence rules. |
| 5 | 550 | Integrity checksum changed | 4,126 | 1.3% | HOWE01, ho-sr-wm-01 | ESCALATE (level 7) | FIM detecting normal file modifications | Review: escalation threshold too low for workstation FIM. |
| 6 | 553 | File deleted | 3,907 | 1.2% | HOWE01 | AUTO_CLOSE (level <= 3) | Normal file deletion from temp/cache cleanup | No SPL change; Wazuh-side noise. |
| 7 | 554 | File added to the system | 3,352 | 1.0% | HOWE01 | AUTO_CLOSE (level <= 3) | Normal file creation from app installs, updates | No SPL change; Wazuh-side noise. |
| 8 | 92151 | Binary loaded PowerShell automation library | 3,147 | 1.0% | win-hawkinsops | AUTO_CLOSE_KNOWN_FP (suppression) | pwsh.exe loading System.Management.Automation.dll | Already suppressed. Maps to encoded PS detection in SPL. |
| 9 | 594 | Registry Key Integrity Checksum Changed | 2,763 | 0.8% | HOWE01 | AUTO_CLOSE (level <= 3) | FIM registry churn | Same as rule 750. |
| 10 | 60642 | Software protection service scheduled | 2,416 | 0.7% | HOWE01 | AUTO_CLOSE (rule list) | Windows licensing service scheduled tasks | Already auto-closed. |
| 11 | 92153 | Suspicious process loaded VaultCli DLL | 2,188 | 0.7% | win-hawkinsops | AUTO_CLOSE_KNOWN_FP (suppression) | backgroundtaskhost, taskhostw, svchost loading VaultCli | Already suppressed via sysmon suppressions. |
| 12 | 67023 | Non-service account logged off | 2,038 | 0.6% | HOWE01 | AUTO_CLOSE (rule list) | Normal user logoff events | Already auto-closed. |
| 13 | 60118 | Windows workstation logon success | 2,007 | 0.6% | HOWE01 | AUTO_CLOSE (rule list) | Normal interactive logon events | Already auto-closed. |
| 14 | 752 | Registry value entry added | 1,452 | 0.4% | HOWE01 | AUTO_CLOSE (level <= 3) | FIM registry churn from app installs | Same as rule 750. |
| 15 | 100052 | Critical system file modified | 1,410 | 0.4% | HOWE01 | ESCALATE | hosts.ics file modification (ICS-managed) | Known FP in known_fps.yaml. Verify coverage. |
| 16 | 751 | Registry value entry deleted | 983 | 0.3% | HOWE01 | AUTO_CLOSE (level <= 3) | FIM registry churn | Same as rule 750. |
| 17 | 19007 | CIS benchmark check (failed) | 979 | 0.3% | ho-lm-01 | REVIEW | SCA scan results for hardening gaps | Not a FP -- informational. No change. |
| 18 | 61102 | Windows system error event (DCOM) | 927 | 0.3% | HOWE01 | AUTO_CLOSE_KNOWN_FP (override) | LinkedIn, HP printer DCOM noise | Already suppressed via policy override. |
| 19 | 19008 | CIS benchmark check (passed) | 670 | 0.2% | ho-lm-01 | REVIEW | SCA scan pass results | Not a FP -- informational. No change. |
| 20 | 40704 | Systemd service exited (failure) | 578 | 0.2% | ho-sr-01 | REVIEW | Transient service restart failures | Review: may warrant auto-close for known services. |

---

## Patterns Mapped to SPL Rule Improvements

### Pattern 1: AI Coding Tool PowerShell Noise (Rule 92151 -> SPL Encoded PS / LOLBin)

**Evidence:** 3,147 alerts from win-hawkinsops. All are pwsh.exe loading System.Management.Automation.dll -- standard PowerShell 7 operation triggered by AI tools (Codex CLI, Claude Code, Cursor) spawning pwsh for tool calls.

**SPL Rules Affected:**
- `execution_detections.spl` -- Encoded PowerShell (T1027)
- `windows_security_eventlog_detections.spl` -- Browser/Office spawning shell (T1059.003), LOLBin spike (T1140)

**Proposed Exclusion:**
```spl
# AI coding tool parent processes (legitimate encoded PowerShell)
where NOT match(ParentImage, "(?i)(codex|claude|copilot|cursor|aider|codeium)")
```

### Pattern 2: Workstation FIM/Syscheck Churn (Rules 550, 553, 554, 594, 750, 751, 752)

**Evidence:** 22,839 combined alerts. All from HOWE01 workstation. Registry and file integrity monitoring generating noise from normal application behavior (installs, updates, browser cache, temp files).

**SPL Rules Affected:**
- `persistence_detections.spl` -- Registry Run Key (T1547.001), detects registry changes
- `defense_evasion_detections.spl` -- Timestomping (T1070.006), detects file attribute changes

**Proposed Exclusion:** Add workstation temp/cache path exclusions and known updater processes.

### Pattern 3: Windows Process Creation Baseline (Rule 67027)

**Evidence:** 190,492 alerts -- 58% of all cases. Level 3 process creation logging. Already auto-closed by policy. Maps to broad process execution detection in SPL.

**SPL Rules Affected:**
- `discovery_detections.spl` -- Whoami (T1033), System Info (T1082)
- `execution_detections.spl` -- All execution detections

**Proposed Exclusion:** Not a SPL issue -- this is Wazuh telemetry volume. SPL rules already have process-specific filters.

### Pattern 4: Device/Hardware Enumeration (Rule 60227)

**Evidence:** 84,746 alerts. Printer, Bluetooth, audio device plug/unplug churn on workstation. Already suppressed in Wazuh policy. No SPL equivalent.

### Pattern 5: Sysmon DLL Load Noise (Rules 92151, 92153)

**Evidence:** 5,335 combined alerts. PowerShell automation DLL loads and VaultCli DLL loads from system processes. Already suppressed in Wazuh policy.

**SPL Rules Affected:**
- `defense_evasion_detections.spl` -- DLL Side-Loading (T1574.002)

**Proposed Exclusion:** Add PowerShell DLL and VaultCli to known-good DLL list.

---

## Summary

| Category | Alert Count | % of Total | Already Handled | SPL Action Needed |
|---|---|---|---|---|
| Process creation baseline | 190,492 | 58.0% | Yes (auto-close) | None |
| Device enumeration | 84,746 | 25.8% | Yes (policy override) | None |
| FIM/syscheck churn | 22,839 | 7.0% | Mostly (auto-close) | Minor persistence rule updates |
| Windows audit noise | 10,109 | 3.1% | Yes (policy override) | None |
| Sysmon DLL loads | 5,335 | 1.6% | Yes (suppressions) | AI tool + DLL exclusions in SPL |
| Service/logon events | 7,039 | 2.1% | Yes (auto-close) | None |
| SCA/CIS benchmarks | 1,649 | 0.5% | No (informational) | None -- not FP |
| Custom rules (100052) | 1,410 | 0.4% | Partial (known_fps) | Verify known FP coverage |
| Other | 4,896 | 1.5% | Mixed | Case-by-case review |

**Bottom line:** 94% of backlog volume is already handled by AutoSOC policy. The remaining SPL improvements target AI tool exclusions, developer workstation patterns, and EDR process refinement.
