# Verified Detection Counts

This file is generated from live repository file counts.

---

## Detection Rules

| Platform | Count | Location |
|----------|-------|----------|
| **Sigma** (YAML) | **103** rules | content/detection-rules/sigma/ |
| **Splunk** (SPL) | **9** files, **79** detection searches | content/detection-rules/splunk/ |
| **Wazuh** (XML) | **24** files, **28** rule blocks | content/detection-rules/wazuh/rules/ |

## Incident Response

| Type | Count | Location |
|------|-------|----------|
| **IR Playbooks** (IR-*.md) | **10** playbooks | content/incident-response/playbooks/ |

## MITRE ATT&CK Coverage

| Metric | Count | Source |
|--------|-------|--------|
| **MITRE ATT&CK coverage** | **123** techniques / **69** families | PROOF_PACK/VERIFIED_MITRE.csv |
---

## Verification Commands

    pwsh -NoProfile -File ".\scripts\verify\verify-counts.ps1"
    pwsh -NoProfile -File ".\scripts\verify\verify-mitre.ps1"
    pwsh -NoProfile -File ".\scripts\verify\generate-verified-counts.ps1" -OutFile ".\PROOF_PACK\VERIFIED_COUNTS.md"

## Build Artifact Command

    pwsh -NoProfile -File ".\scripts\build-wazuh-bundle.ps1"

---

_Regenerate this file after detection or playbook content changes._
