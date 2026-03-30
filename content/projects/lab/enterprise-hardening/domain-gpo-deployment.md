# Domain GPO Deployment — HawkinsOps Security Baseline
**Phase:** Enterprise Security Phase 2 | **Date:** 2026-03-29 | **Host:** HO-WE-01

---

## Executive Summary

This document captures the plan and PowerShell commands to promote HO-WE-01's hardened local audit policy into a domain-wide GPO, enforcing the same 27-subcategory baseline across all domain-joined machines.

**Current Status:** HO-WE-01 is currently in WORKGROUP mode (not domain-joined). The GPO deployment plan is fully documented and ready to execute once domain join is completed and RSAT is installed.

---

## Blocker: Domain Join Required

```
Get-CimInstance Win32_ComputerSystem | Select-Object Name, Domain, PartOfDomain, Workgroup

Name     Domain     PartOfDomain Workgroup
----     ------     ------------ ---------
HO-WE-01 WORKGROUP  False        WORKGROUP
```

**Next step:** Join HO-WE-01 to the domain (dc01) before executing GPO deployment.

```powershell
# Domain join (requires domain admin credentials)
Add-Computer -DomainName "hawkinsops.local" -Credential (Get-Credential) -Restart
```

---

## Audit Policy Backup

The hardened local policy is exported and ready for GPO application:

**File:** `C:\OPS\enterprise-security\hardened-audit-policy.csv`

```powershell
# Export current hardened policy (run as Administrator)
auditpol /backup /file:"C:\OPS\enterprise-security\hardened-audit-policy.csv"
```

This CSV contains all 60 audit subcategory settings and is the authoritative source for the GPO configuration.

---

## GPO Creation — Commands

Once RSAT is installed and the machine is domain-joined, run the following as a Domain Admin or user with GPO creation rights:

```powershell
Import-Module GroupPolicy
Import-Module ActiveDirectory

# Step 1: Create the GPO
$gpo = New-GPO -Name "HawkinsOps Security Baseline" `
    -Comment "Enterprise audit policy hardening - 27 subcategories, CommandLine logging, 1GB Security log. Deployed $(Get-Date -Format yyyy-MM-dd)."

Write-Host "GPO created: $($gpo.DisplayName) | ID: $($gpo.Id)"

# Step 2: Link to domain root
$domainDN = (Get-ADDomain).DistinguishedName
$link = Get-GPO -Name "HawkinsOps Security Baseline" | New-GPLink -Target $domainDN
Write-Host "GPO linked to: $domainDN"

# Step 3: Verify
Get-GPO -Name "HawkinsOps Security Baseline" | Format-List DisplayName, Id, GpoStatus, CreationTime
Get-GPInheritance -Target $domainDN | Select-Object -ExpandProperty GpoLinks | Format-Table DisplayName, Enabled, Enforced
```

---

## Audit Subcategory Settings via GPO

The GPO configures **Computer Configuration > Policies > Windows Settings > Security Settings > Advanced Audit Policy Configuration**.

These settings map directly to the 27 subcategories hardened on HO-WE-01:

### Account Logon
| Subcategory | Setting |
|---|---|
| Credential Validation | Success and Failure |
| Kerberos Authentication Service | Success and Failure |
| Kerberos Service Ticket Operations | Success and Failure |
| Other Account Logon Events | Success and Failure |

### Account Management
| Subcategory | Setting |
|---|---|
| Computer Account Management | Success and Failure |
| Security Group Management | Success and Failure |
| User Account Management | Success and Failure |
| Other Account Management Events | Success and Failure |

### Detailed Tracking
| Subcategory | Setting |
|---|---|
| Process Creation | Success and Failure |
| Process Termination | Success and Failure |
| DPAPI Activity | Success and Failure |
| Plug and Play Events | Success and Failure |

### Logon/Logoff
| Subcategory | Setting |
|---|---|
| Logon | Success and Failure |
| Logoff | Success and Failure |
| Special Logon | Success and Failure |
| Account Lockout | Success and Failure |
| Other Logon/Logoff Events | Success and Failure |

### Object Access
| Subcategory | Setting |
|---|---|
| File System | Success and Failure |
| Registry | Success and Failure |
| SAM | Success and Failure |
| Removable Storage | Success and Failure |

### Policy Change
| Subcategory | Setting |
|---|---|
| Audit Policy Change | Success and Failure |
| Authentication Policy Change | Success and Failure |

### Privilege Use
| Subcategory | Setting |
|---|---|
| Sensitive Privilege Use | Success and Failure |

### System
| Subcategory | Setting |
|---|---|
| Security System Extension | Success and Failure |
| System Integrity | Success and Failure |
| Security State Change | Success and Failure |

---

## Additional GPO Settings

Beyond audit subcategories, the GPO should also configure:

### CommandLine Process Logging (via Registry Policy)
```
Computer Configuration > Preferences > Windows Settings > Registry
Hive: HKLM
Key: SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit
Value: ProcessCreationIncludeCmdLine_Enabled = 1 (DWORD)
```

### Security Event Log Size
```
Computer Configuration > Policies > Windows Settings > Security Settings > Event Log
Maximum security log size: 1048576 KB (1 GB)
Retention method for security log: Overwrite events as needed
```

---

## Verification After Deployment

```powershell
# Check GPO exists and is linked
Get-GPO -Name "HawkinsOps Security Baseline"

# Check GPO link on domain
Get-GPInheritance -Target (Get-ADDomain).DistinguishedName | Select-Object -ExpandProperty GpoLinks

# Force policy application on a test machine
Invoke-GPUpdate -Computer "HO-WE-01" -Force

# Verify resultant set of policy
gpresult /r /scope computer
```

---

## auditpol Backup/Restore Approach (Alternative)

If direct GPO configuration is unavailable, the hardened policy can be pushed via logon script using auditpol restore:

```powershell
# Restore policy from backup (on target machine, elevated)
auditpol /restore /file:"\\dc01\NETLOGON\hardened-audit-policy.csv"
```

Deploy via GPO startup script:
```
Computer Configuration > Policies > Windows Settings > Scripts > Startup
Script: auditpol /restore /file:"\\dc01\NETLOGON\hardened-audit-policy.csv"
```

---

## Next Steps

1. Join HO-WE-01 to domain: `Add-Computer -DomainName hawkinsops.local`
2. Install RSAT (see `rsat-installation.md`)
3. Run GPO creation commands above as Domain Admin
4. Verify with `Get-GPInheritance` and `gpresult /r`
5. Test on a second machine to confirm domain-wide enforcement

---

*Part of the HawkinsOps Enterprise Security Hardening Sprint — Phase 2*