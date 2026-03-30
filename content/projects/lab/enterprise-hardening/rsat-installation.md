# RSAT Installation — HO-WE-01
**Phase:** Enterprise Security Phase 2 | **Date:** 2026-03-29 | **Host:** HO-WE-01 (Windows 11 Enterprise)

---

## Executive Summary

Remote Server Administration Tools (RSAT) were assessed for installation on HO-WE-01 to enable domain administration from the workstation — eliminating the need to log directly into dc01 for AD, Group Policy, and DNS management.

**Status:** Install script prepared and tested. Elevation required for capability installation. Script available at `C:\OPS\enterprise-security\rsat-install.ps1`.

---

## Pre-Installation State

```
Tool                           Status
----                           ------
gpmc.msc (Group Policy Mgmt)   NOT FOUND
dsa.msc (AD Users & Computers) NOT FOUND
dnsmgmt.msc (DNS Manager)      NOT FOUND
dsac.exe (AD Admin Center)     NOT FOUND
AD PowerShell Module           NOT FOUND
GroupPolicy PowerShell Module  NOT FOUND
gpresult.exe                   PRESENT (built-in)
dsregcmd.exe                   PRESENT (built-in)
```

---

## Installation Method

RSAT is delivered as Windows Optional Features (on-demand capabilities), not as a standalone installer. Installation requires:
- Windows Update connectivity OR WSUS/SCCM
- Administrator elevation
- `Add-WindowsCapability -Online`

### Install Script

Location: `C:\OPS\enterprise-security\rsat-install.ps1`

Run as Administrator:
```powershell
pwsh -ExecutionPolicy Bypass -File "C:\OPS\enterprise-security\rsat-install.ps1"
```

The script performs:
1. Scans all `RSAT.*` capabilities via `Get-WindowsCapability -Name RSAT* -Online`
2. Installs each capability not yet in `Installed` state
3. Verifies post-install state
4. Checks presence of key MMC snap-ins and PowerShell modules

### Key Capabilities Installed

| Capability | What It Provides |
|---|---|
| `Rsat.ActiveDirectory.DS-LDS.Tools` | AD Users & Computers (dsa.msc), AD Admin Center (dsac.exe), AD PowerShell module |
| `Rsat.GroupPolicy.Management.Tools` | Group Policy Management Console (gpmc.msc), GroupPolicy PS module |
| `Rsat.Dns.Tools` | DNS Manager (dnsmgmt.msc) |
| `Rsat.DHCP.Tools` | DHCP console |
| `Rsat.ServerManager.Tools` | Server Manager, remote server roles management |
| `Rsat.CertificateServices.Tools` | PKI / Certificate Authority management |
| `Rsat.BitLocker.Recovery.Tools` | BitLocker recovery key management |
| `Rsat.FileServices.Tools` | DFS management, File Server Resource Manager |

---

## What RSAT Enables

### Active Directory Management
- Browse, create, modify, and disable user/computer/group objects without RDP to dc01
- Reset passwords, unlock accounts, manage OUs from the workstation
- Run AD PowerShell cmdlets (`Get-ADUser`, `Get-ADComputer`, `Get-ADGroupMember`, etc.)

### Group Policy
- Create, edit, and link GPOs directly from HO-WE-01
- Use GPMC to verify GPO inheritance, delegation, and link order
- Use `Get-GPO`, `New-GPO`, `New-GPLink`, `Invoke-GPUpdate` from PowerShell

### DNS
- Manage forward/reverse lookup zones on dc01's DNS server
- Add/remove A, CNAME, PTR records
- Check replication and zone health

### Operational Value
Without RSAT, every administrative action on the domain required:
1. RDP session to dc01 (attack surface, session token exposure)
2. Manual console access or scripted remoting

With RSAT, domain administration is consolidated to the hardened, monitored workstation. All admin actions produce 4688 (Process Creation) events locally — feeding directly into the Wazuh → Splunk → Grafana pipeline.

---

## Verification Commands (Post-Install)

```powershell
# Confirm tools are present
Get-WindowsCapability -Name RSAT* -Online | Where-Object State -eq Installed | Select-Object Name

# Test AD module
Import-Module ActiveDirectory
Get-ADDomain

# Test GP module
Import-Module GroupPolicy
Get-GPO -All

# Open GPMC
gpmc.msc

# Open ADUC
dsa.msc
```

---

## Security Notes

- RSAT tools are read/write against production AD — use only from accounts with appropriate delegation
- All tool usage produces 4688 events (CommandLine logging enabled) feeding the SIEM pipeline
- RSAT is a management plane tool — not a security risk on a hardened, domain-joined workstation with full audit policy enabled

---

## Artifact Location

- Install script: `C:\OPS\enterprise-security\rsat-install.ps1`
- Post-install output: `C:\OPS\enterprise-security\rsat-output.txt` (generated after elevated run)

*Part of the HawkinsOps Enterprise Security Hardening Sprint — Phase 2*