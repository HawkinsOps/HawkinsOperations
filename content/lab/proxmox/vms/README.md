# Proxmox VM Inventory

VM mapping for the lab:

| VMID | Hostname    | Purpose            | Path |
| ---- | ----------- | ------------------ | ---- |
| 100  | [REDACTED_HOST] | Detection VM       | `content/lab/proxmox/vms/100/detection-vm/` |
| 101  | [REDACTED_HOST] | Wazuh Manager VM   | `content/lab/proxmox/vms/101/wazuh-manager/` |
| 102  | [REDACTED_HOST] | OpenClo VM         | `content/lab/proxmox/vms/102/openclaw/` |
| 104  | HO-SPLUNK-01 | Splunk VM         | `content/lab/proxmox/vms/104/splunk/` |
| 900  | win11-template | Windows 11 Enterprise Template (Sysmon + Wazuh) | Template — clone with `qm clone 900` |
| 901  | ubuntu-template | Ubuntu Server 24.04 Template (Wazuh)           | Template — clone with `qm clone 901` |
| —    | HO-RUNNER-01 | GitHub Actions self-hosted runner               | Ubuntu — runs all CI/CD workflows |

Guardrails:
- No internal IPs.
- No secrets, tokens, keys, or credentials.
- Use `[REDACTED_INTERNAL]` for sensitive internal details.

