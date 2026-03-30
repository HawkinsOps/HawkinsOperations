# Change Log — Audit Policy Hardening

## Entry 1
- **Timestamp:** 2026-03-29
- **Operator:** [REDACTED] (administrator account)
- **Action:** Enabled CommandLine capture (GPO and registry)
- **Files changed:** GPO-export.xml, registry `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit\ProcessCreationIncludeCmdLine_Enabled`
- **Rollback:** Restore GPO from backup; Set registry DWord to 0
- **Reason:** 4688 events emitted without command line; required for detection of encoded PowerShell and certutil download cradles

## Entry 2
- **Timestamp:** 2026-03-29
- **Operator:** [REDACTED] (administrator account)
- **Action:** auditpol /set for 22 subcategories to Success+Failure
- **Files changed:** N/A (auditpol state change)
- **Rollback:** Run `auditpol /set /subcategory:"<name>" /success:disable /failure:disable` for each affected entry
- **Reason:** 14 MITRE ATT&CK technique categories produced zero telemetry prior to this change

## Entry 3
- **Timestamp:** 2026-03-29
- **Operator:** [REDACTED] (administrator account)
- **Action:** Security log max size increased from 20 MB to 1 GB
- **Rollback:** Set Security log MaxSize back to 20480 KB via registry or GPO
- **Reason:** 20 MB log was rolling over before Wazuh could forward events; 1 GB provides 50x headroom
