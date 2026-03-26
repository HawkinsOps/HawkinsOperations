# Verified Detection Counts

This file is generated from live repository file counts.

---

## Detection Rules

| Platform | Count | Location |
|----------|-------|----------|
| **Sigma** (YAML) | **103** rules | content/detection-rules/sigma/ |
| **Splunk** (SPL) | **8** queries | content/detection-rules/splunk/ |
| **Wazuh** (XML) | **24** files, **28** rule blocks | content/detection-rules/wazuh/rules/ |

## Incident Response

| Type | Count | Location |
|------|-------|----------|
| **IR Playbooks** (IR-*.md) | **10** playbooks | content/incident-response/playbooks/ |

---

## Verification Commands

    pwsh -NoProfile -File ".\scripts\verify\verify-counts.ps1"
    pwsh -NoProfile -File ".\scripts\verify\generate-verified-counts.ps1" -OutFile ".\PROOF_PACK\VERIFIED_COUNTS.md"

## Build Artifact Command

    pwsh -NoProfile -File ".\scripts\build-wazuh-bundle.ps1"

---

_Regenerate this file after detection or playbook content changes._
