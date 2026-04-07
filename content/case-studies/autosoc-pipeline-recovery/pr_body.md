## Summary

- Add reproducible case study pack for the AutoSOC Pipeline Recovery incident (March 13, 2026)
- Include evidence manifest (YAML), verification scripts (PowerShell + Bash), CI checks, reviewer lanes, and JSON-LD structured data
- Document metric reconciliation between VERIFIED_COUNTS.md, SignalFoundry doc, and published HTML
- QA checklist: 17/22 PASS, 5 FAIL (3 missing operational files not in repo, 1 missing checksums, 1 missing privacy page)

## What changed

**Files added:**
- `case-studies/autosoc-pipeline-recovery/README.md` — full case study with repro steps, technical analysis, metrics reconciliation
- `case-studies/autosoc-pipeline-recovery/front_matter.yaml` — parsed YAML metadata
- `case-studies/autosoc-pipeline-recovery/evidence/evidence.yaml` — machine-readable evidence manifest
- `case-studies/autosoc-pipeline-recovery/evidence/verify.ps1` — PowerShell verification script (exits non-zero on count mismatch)
- `case-studies/autosoc-pipeline-recovery/evidence/verify.sh` — POSIX verification script (same checks)
- `case-studies/autosoc-pipeline-recovery/reviewer_lanes.md` — recruiter (30s), technical (5min), detection engineer (deep) review paths
- `case-studies/autosoc-pipeline-recovery/ci_checks.yml` — GitHub Actions workflow for case study CI
- `case-studies/autosoc-pipeline-recovery/jsonld_article.json` — Article + Person + WebSite JSON-LD
- `case-studies/autosoc-pipeline-recovery/pr_body.md` — this file
- `case-studies/autosoc-pipeline-recovery/qa_results.md` — programmatic QA results

**Files NOT modified:**
- No changes to `PROOF_PACK/VERIFIED_COUNTS.md` or any existing site files
- No changes to CI workflows
- No changes to detection rules or playbooks

## Expected tests

- [ ] `pwsh -File scripts/verify/verify-counts.ps1` — PASS (counts unchanged)
- [ ] `python scripts/drift_scan.py` — PASS (no site content changed)
- [ ] `node scripts/diagnose-site.js` — PASS (no site files changed)
- [ ] `pwsh -File case-studies/autosoc-pipeline-recovery/evidence/verify.ps1` — PASS (all artifact checks)

## Failing conditions

- Any detection count in `PROOF_PACK/verified_counts.json` differs from expected values (Sigma=103, Splunk=79, Wazuh=24/28, IR=10, Total=210)
- Physical file counts don't match JSON counts
- Required artifacts missing (VERIFIED_COUNTS.md, case-study-autosoc.html, resume PDF, etc.)
- sitemap.xml missing case-study-autosoc URL
- robots.txt missing sitemap reference

## Checklist

- [x] Verification scripts pass
- [x] No sanitization issues
- [x] MITRE ATT&CK tags documented
- [x] Commit messages follow conventions
- [x] One logical change per PR
- [ ] `CONTROL_PANEL.md` present (NOT FOUND — tracked as known gap)
- [ ] Privacy page exists (NOT FOUND — tracked as known gap)
