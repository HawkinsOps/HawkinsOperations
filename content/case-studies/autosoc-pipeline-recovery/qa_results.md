# QA Results — AutoSOC Pipeline Recovery Case Study

**Run date:** 2026-03-30
**Snapshot:** 2026-03-25
**Runner:** Windows 11, PowerShell 7, programmatic checks

## Results

| Check | Status | Detail |
|---|---|---|
| VERIFIED_COUNTS.md exists | PASS | PROOF_PACK/VERIFIED_COUNTS.md |
| verified_counts.json exists | PASS | PROOF_PACK/verified_counts.json |
| CONTROL_PANEL.md exists | FAIL | NOT FOUND in repository |
| CURRENT_DECISIONS.md exists | FAIL | NOT FOUND in repository |
| SESSION_LOG_LATEST.md exists | FAIL | NOT FOUND in repository |
| Sigma=103 (JSON) | PASS | Actual: 103 |
| Total=210 (JSON) | PASS | Actual: 210 |
| IR=10 (JSON) | PASS | Actual: 10 |
| Physical Sigma=103 | PASS | Found: 103 |
| Physical Splunk=9 | PASS | Found: 9 |
| Physical Wazuh=24 | PASS | Found: 24 |
| Physical IR=10 | PASS | Found: 10 |
| case-study-autosoc.html | PASS | |
| proof.html | PASS | |
| resume PDF | PASS | |
| sitemap.xml | PASS | |
| robots.txt | PASS | |
| security.html | PASS | |
| privacy.html | FAIL | NOT FOUND — no privacy page exists |
| robots.txt -> sitemap | PASS | Sitemap URL present |
| sitemap -> case-study-autosoc | PASS | URL in sitemap |

## Summary: 17 PASS / 4 FAIL

### FAIL Remediation

| Item | Root Cause | Fix | Effort |
|---|---|---|---|
| CONTROL_PANEL.md | Not part of HawkinsOperations repo architecture | Create or document as external-only | 1 hour |
| CURRENT_DECISIONS.md | Not part of HawkinsOperations repo architecture | Create or document as external-only | 1 hour |
| SESSION_LOG_LATEST.md | Not part of HawkinsOperations repo architecture | Create or document as external-only | 30 min |
| privacy.html | Never created | Create minimal privacy page, add to sitemap + _redirects | 30 min |

### Notes

- Evidence checksums are marked `MISSING_CHECKSUM` in evidence.yaml — compute by running the `compute_checksum` commands listed per artifact
- LinkedIn profile (https://www.linkedin.com/in/raylee-hawkins) is MANUAL_VERIFICATION_REQUIRED — confirm profile exists and matches portfolio claims
- Cloudflare Pages deployment status is MANUAL_VERIFICATION_REQUIRED — confirm site is live at hawkinsops.com
- The 3 missing canonical files (CONTROL_PANEL.md, CURRENT_DECISIONS.md, SESSION_LOG_LATEST.md) are referenced by the case study template but are not part of the established HawkinsOperations repository architecture. They may exist in a private operational context.
