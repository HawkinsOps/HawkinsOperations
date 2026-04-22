# Site Link Inventory

Date: 02-27-2026
Scope: links reviewed in Stage 4/5 edited pages

## Fixed / replaced / removed

| Type | File | Link or reference | Action | Reason |
|---|---|---|---|---|
| Internal reference | `site/index.html` | `IR alert brief` card copy | Replaced copy only | Removed endpoint machine-name disclosure while preserving route |
| Internal reference | `site/projects.html` | featured SOC card copy | Replaced copy only | Redaction and credibility tightening |
| Internal reference | `site/detections.html` | IR case-study card copy | Replaced copy only | Redaction of endpoint machine-name token |
| Internal reference | `site/case-study-ir-howe01.html` | dashboard filter text and hostname example | Replaced copy only | Removed internal manager and hostname markers |
| Internal reference | `site/case-study.html` | rule simulation sentence | Replaced copy only | Removed endpoint machine-name token |
| Internal links (`/path`) | Edited pages in scope | All route links | Verified unchanged and valid pattern | Preserve pretty-routing and avoid `.html` hardcoding |
| External links | Case-study and proof pages | GitHub repo artifact links | Verified retained | Evidence-backed and recruiter-reviewable |

Removed links: none

## Authoritative external links in active use
- GitHub repository and artifact paths under `https://github.com/raylee-hawkins/HawkinsOperations/...`
- National Vulnerability Database (NVD): `https://nvd.nist.gov/vuln/detail/CVE-2025-55130`
- Node.js security advisories: `https://nodejs.org/en/blog/vulnerability`
- LinkedIn profile: `https://linkedin.com/in/raylee-hawkins`

## Internal route checks (edited scope)
- Primary nav routes present and unchanged: `/`, `/soc-lab`, `/detections`, `/proof`, `/projects`, `/resume`, `/wildcard`
- Case-study routes present and unchanged:
  - `/case-study-cve-patch`
  - `/case-study-detection-harness`
  - `/case-study-honeypot`
  - `/case-study-ir-howe01`
  - `/case-study-ir-playbooks`
  - `/case-study-sigma-library`
  - `/case-study-soc-integration`

## Notes
- No `.html` internal hrefs were introduced.
- Link changes in this cycle were primarily copy/redaction adjustments, not routing changes.