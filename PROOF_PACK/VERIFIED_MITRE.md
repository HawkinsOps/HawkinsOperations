# Verified MITRE ATT&CK Coverage

This file is generated from live detection rule content by `scripts/verify/verify-mitre.ps1`.

---

## Summary

| Metric | Value |
|---|---|
| Unique techniques (T####[.###]) | **123** |
| Unique technique families (T####) | **69** |
| Sigma YAML files scanned | 103 |
| Wazuh XML files scanned | 24 |
| Splunk SPL files scanned | 9 |

## Top 10 techniques by rule coverage

| Technique | Family | # Rule files |
|---|---|---|
| T1003 | T1003 | 7 |
| T1021 | T1021 | 7 |
| T1021.002 | T1021 | 5 |
| T1048 | T1048 | 5 |
| T1059 | T1059 | 5 |
| T1548 | T1548 | 5 |
| T1003.001 | T1003 | 4 |
| T1048.003 | T1048 | 4 |
| T1053 | T1053 | 4 |
| T1053.005 | T1053 | 4 |

## Verification commands

    pwsh -NoProfile -File .\scripts\verify\verify-mitre.ps1

Full per-technique provenance is in `PROOF_PACK/VERIFIED_MITRE.csv` (columns: Technique, Family, FileList, FileCount).

---

_Regenerate after adding or removing detection rules._
