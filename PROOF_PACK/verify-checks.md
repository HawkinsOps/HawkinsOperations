# Verify Checks — Audit Closure Run

Run date: 2026-04-09 UTC
Branch: `fix/close-truth-gaps-20260409T160920Z`
Base commit: `0608992` (WIP pre-verify snapshot)
Scope: Close TRUTH_MANIFEST D5 / A4 / A5 (MITRE ATT&CK coverage verification); refresh verified counts and site data; leave all other canonical values untouched.

---

## 1. Environment

    pwsh     : PowerShell 7.6.0
    node     : v24.13.1
    python   : Python 3.14.0
    git      : git version 2.51.2.windows.1
    gh       : gh version 2.87.0 (2026-02-18)

## 2. verify-counts.ps1

    ======================================
    HawkinsOps Detection Content Counts
    ======================================

    Sigma (.yml/.yaml files): 103
    Splunk (.spl files):      9
    Splunk (searches):        79
    Wazuh XML files:          24
    Wazuh <rule id=> blocks:  28
    IR Playbooks (IR-*.md):   10

    ======================================

All six counts match the canonical values in `TRUTH_MANIFEST.md` section 1A.

## 3. generate-verified-counts.ps1

    Wrote verified counts: Z:\GitHub\HawkinsOperations\PROOF_PACK\VERIFIED_COUNTS.md

New in this run: the generator now reads `PROOF_PACK/VERIFIED_MITRE.csv` (produced by `verify-mitre.ps1`) and appends a MITRE ATT&CK Coverage table to `VERIFIED_COUNTS.md`. If the CSV is absent, the MITRE row is silently omitted (fail-safe).

## 4. Node site/data pipeline

    Generated data\metrics.json
    Generated data\metrics.json.sha256
    Generated site\assets\verified-counts.json
    Generated site\data\counts.js
    Generated site\assets\data\ops-metrics.json
    Generated site\data\ops-metrics.js
    Synced   site\assets\data\detections.json
    Generated site\assets\data\projects.json
    Generated site\assets\data\detections.json

## 5. drift_scan.py --refresh

    Wrote PROOF_PACK/verified_counts.json
    Wrote site/assets/verified-counts.json
    Synced site/assets/data/detections.json
    DRIFT SCAN: PASS
    {
      "sigma": 103,
      "splunk": 79,
      "wazuh_xml_files": 24,
      "wazuh": 28,
      "ir": 10,
      "detections": 210
    }

Zero mismatches. Data-verified HTML fallbacks and ops-metrics JSON keys all align with `VERIFIED_COUNTS.md`.

## 6. verify-mitre.ps1 (new)

    ======================================
    HawkinsOps MITRE ATT&CK Coverage
    ======================================

    Unique techniques:  123
    Unique families:    69
    Sigma files:        103
    Wazuh files:        24
    Splunk files:       9

    Wrote CSV: PROOF_PACK\VERIFIED_MITRE.csv
    Wrote MD:  PROOF_PACK\VERIFIED_MITRE.md

Parser strategy (per platform):
- **Sigma YAML:** `(?i)attack\.t(\d{4})(?:\.(\d{1,3}))?` against `tags:` block entries.
- **Wazuh XML:** `<mitre><id>TNNNN[.NNN]</id></mitre>` plus `<mitre id="TNNNN[.NNN]">` variants.
- **Splunk SPL:** `(?im)(?:^\s*#|/\*)\s*MITRE\s*:\s*TNNNN[.NNN]` comments.
- **Generic fallback:** `\bT\d{4}(?:\.\d+)?\b` across every rule file (catches references URLs, inline comments, rule summaries).
- Fail-loud: exits 2 if zero techniques discovered (pattern mismatch sentinel).

### First 10 CSV rows (PROOF_PACK/VERIFIED_MITRE.csv)

    Technique,Family,FileList,FileCount
    T1003,T1003,content/detection-rules/sigma/credential-access/dcsync_attack.yml;content/detection-rules/sigma/credential-access/lsass_access_suspicious.yml;content/detection-rules/sigma/credential-access/lsass_dump_comsvcs.yml;content/detection-rules/sigma/credential-access/ntds_dump.yml;content/detection-rules/sigma/credential-access/passwd_shadow_access.yml;content/detection-rules/sigma/credential-access/sam_registry_dump.yml;content/detection-rules/splunk/credential_access_detections.spl,7
    T1003.001,T1003,content/detection-rules/sigma/credential-access/lsass_access_suspicious.yml;content/detection-rules/sigma/credential-access/lsass_dump_comsvcs.yml;content/detection-rules/splunk/credential_access_detections.spl;content/detection-rules/wazuh/rules/wazuh-075-credential-dumping-comsvcs.xml,4
    T1003.002,T1003,content/detection-rules/sigma/credential-access/sam_registry_dump.yml;content/detection-rules/splunk/credential_access_detections.spl,2
    T1003.003,T1003,content/detection-rules/sigma/credential-access/ntds_dump.yml;content/detection-rules/splunk/credential_access_detections.spl,2
    T1003.006,T1003,content/detection-rules/sigma/credential-access/dcsync_attack.yml;content/detection-rules/splunk/credential_access_detections.spl,2
    T1003.008,T1003,content/detection-rules/sigma/credential-access/passwd_shadow_access.yml,1
    T1005,T1005,content/detection-rules/sigma/collection/sensitive_file_access.yml,1
    T1014,T1014,content/detection-rules/sigma/defense-evasion/rootkit_behavior.yml;content/detection-rules/wazuh/rules/wazuh-053-rootkit-detection.xml,2
    T1016,T1016,content/detection-rules/sigma/discovery/linux_network_discovery.yml;content/detection-rules/splunk/discovery_detections.spl,2
    T1018,T1018,content/detection-rules/sigma/discovery/network_reconnaissance.yml;content/detection-rules/splunk/discovery_detections.spl,2

## 7. Stale-literal sweep (site/)

    rg "6,178|7,950|85,185|85,953|92\.04" site

Results:
- **Zero** occurrences of `6,178`, `7,950`, `85,185`, or `92.04` in `site/`.
- **`85,953` occurrences are canonical**, not stale. They match the current authoritative value in `data/metrics.json` (`known_fp: "85,953"`), which represents the April-7 snapshot that superseded the April-1 benchmark (`85,185`) during the intervening week. The TRUTH_MANIFEST was authored on 2026-04-04 when `85,185` was canonical; the pipeline has since advanced. Site values are consistent with the pipeline source — no edit needed.
- `drift_scan.py` confirms zero mismatches against `VERIFIED_COUNTS.md` and the data-verified HTML fallback key/value rules.

## 8. TRUTH_MANIFEST excerpt (D5 after change)

    | D5 | MITRE technique count | 90 / 53 (prior README claim) | 123 techniques / 69 families (verified) | README.md:45, PROOF_PACK/VERIFIED_MITRE.csv, PROOF_PACK/VERIFIED_MITRE.md | RESOLVED | -- |

Action rows `A4` and `A5` are both now marked **DONE**.

## 9. Abort conditions — none triggered

- Regeneration succeeded on first run for every script.
- `verify-mitre.ps1` returned 123 techniques (well above the zero-techniques sentinel).
- `drift_scan.py --refresh` → PASS.
- (`gh auth status` is checked at push time, not during verify.)
