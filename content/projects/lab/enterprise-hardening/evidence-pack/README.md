# Enterprise Hardening Evidence Pack

**Project:** HawkinsOps Audit Policy Hardening
**Date:** 2026-03-29
**Operator:** HawkinsOps SOC (redacted in published artifacts)
**Environment:** 72-core Proxmox lab, Windows Server 2022, 8/8 hosts

## Result

- 22 audit subcategories hardened (Success + Failure)
- 96% coverage (26/27 targeted subcategories)
- 14 MITRE ATT&CK attack categories moved from zero telemetry to active detection
- 12 settings hardened beyond Microsoft Security Baseline; 0 regressions
- First detection: Event 4719 recorded the policy change itself

## Artifact Index

| File | Description |
|---|---|
| `gpo/GPO-export.xml` | Full GPO export (sanitized) |
| `gpo/GPO-readme.txt` | GPO contents and import instructions |
| `splunk/splunk-queries.txt` | Saved searches with explanation |
| `splunk/4719.json` | Raw JSON export for Event 4719 (sanitized) |
| `splunk/4688_before.json` | Pre-hardening 4688 events (sanitized) |
| `splunk/4688_after.json` | Post-hardening 4688 events (sanitized) |
| `evidence/kpi-before-after.csv` | Before/after KPI comparison |
| `evidence/change-log.md` | Timestamped changelog |
| `evidence/collection-metadata.txt` | Collection context and redaction notes |

## Reproduction Steps

### 1. Inventory current subcategories

```powershell
cmd.exe /c 'auditpol /list /subcategory:*' > C:\temp\audit_subcategories_raw.txt
```

### 2. Enable CommandLine capture

**Registry (local):**
```powershell
New-Item -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit' -ErrorAction SilentlyContinue
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit' -Name 'ProcessCreationIncludeCmdLine_Enabled' -Value 1 -Type DWord
# Verify:
Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit' | Select-Object ProcessCreationIncludeCmdLine_Enabled
```

**GPO (domain):**
Computer Configuration > Policies > Administrative Templates > System > Audit Process Creation > Include command line in process creation events > Enabled

### 3. Enable Advanced Audit subcategories

```powershell
$subs = @(
  "Process Creation",
  "Credential Validation",
  "Kerberos Authentication Service",
  "Kerberos Service Ticket Operations",
  "Computer Account Management",
  "Security Group Management",
  "DPAPI Activity",
  "Removable Storage",
  "Registry",
  "Audit Policy Change"
)

foreach ($s in $subs) {
  Write-Host "Setting $s"
  cmd.exe /c "auditpol /set /subcategory:`"$s`" /success:enable /failure:enable"
}
```

Verify: `auditpol /get /subcategory:"Process Creation"` should show Success and Failure enabled.

### 4. Verify with Splunk

- Run `ProcessCreation_CommandLine_Missing` before change — note counts
- After change + activity, run `ProcessCreation_CommandLine_Present` — confirm CommandLine populated
- Check `AuditPolicyChange_4719` across hardening window — confirm Event 4719 recorded the change

## Sanitization

All published artifacts have been redacted:
- IPv4 addresses replaced with `<IP>`
- Hostnames/FQDNs replaced with `<HOST>`
- User SIDs removed
- Exact timestamps rounded to date-level where noted

See `evidence/collection-metadata.txt` for full redaction documentation.
