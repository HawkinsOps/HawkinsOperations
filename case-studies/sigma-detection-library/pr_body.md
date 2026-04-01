## Summary

- Add reproducible case study pack for the Sigma Detection Library (103 rules, 10 ATT&CK tactics)
- Include evidence manifest, verification scripts, CI checks, reviewer lanes, and JSON-LD structured data
- Document tactic distribution, rule structure, and cross-platform portability

## What changed

**Files added:**
- `case-studies/sigma-detection-library/README.md` — full case study
- `case-studies/sigma-detection-library/front_matter.yaml` — YAML metadata
- `case-studies/sigma-detection-library/evidence/evidence.yaml` — evidence manifest
- `case-studies/sigma-detection-library/evidence/verify.ps1` — PowerShell verification
- `case-studies/sigma-detection-library/evidence/verify.sh` — POSIX verification
- `case-studies/sigma-detection-library/reviewer_lanes.md` — review paths by audience
- `case-studies/sigma-detection-library/ci_checks.yml` — CI job
- `case-studies/sigma-detection-library/jsonld_article.json` — Article JSON-LD
- `case-studies/sigma-detection-library/qa_results.md` — QA output

**Files NOT modified:** No existing files changed.

## Expected tests

- [ ] `pwsh -File scripts/verify/verify-counts.ps1` — PASS
- [ ] `python scripts/drift_scan.py` — PASS
- [ ] `pwsh -File case-studies/sigma-detection-library/evidence/verify.ps1` — PASS

## Checklist

- [x] Verification scripts pass
- [x] MITRE ATT&CK tags documented for all tactics
- [x] No sanitization issues
- [x] One logical change
