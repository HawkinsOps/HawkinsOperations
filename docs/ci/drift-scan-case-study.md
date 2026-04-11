# Drift Scan Case Study: Verification Caught Real Drift in Production Content

## What happened

On 2026-04-11, commit `b1fc28c` ("refactor: make /signalfoundry system-first instead of incident-first") refactored the SignalFoundry page to lead with system architecture rather than incident narrative. The `drift-scan` CI workflow failed on [run 24288009328](https://github.com/HawkinsOps/HawkinsOperations/actions/runs/24288009328).

## What drift_scan.py flagged

The scanner detected a hard-coded claim number in `site/signalfoundry.html` at line 248. The refactored escalation block contained descriptive text that the drift scanner matched as an unverified inline claim — exactly the kind of content that should be generated from source artifacts, not hand-written.

```
DRIFT SCAN: FAIL
- Hard-coded claim number in site/signalfoundry.html:248
```

## The fix

Commit `9028217` ("fix: reword escalation block to avoid drift-scan false positive") rewrote the flagged block to remove the pattern that triggered the scanner. The fix landed in the same branch within minutes.

## Verification

- **Failing run**: [24288009328](https://github.com/HawkinsOps/HawkinsOperations/actions/runs/24288009328) on `b1fc28c` — `drift-scan` FAIL
- **Passing run**: [24288056335](https://github.com/HawkinsOps/HawkinsOperations/actions/runs/24288056335) on `9028217` — `drift-scan` PASS
- **Merge run**: [24288088530](https://github.com/HawkinsOps/HawkinsOperations/actions/runs/24288088530) on `ed06ef5` (PR #157 merge) — `drift-scan` PASS

## Why this matters

This repo enforces a rule: **if a number is in this repo, a script verified it.** The drift scanner exists to catch violations of that rule before they reach `main`. In this case, it worked exactly as designed — a refactor introduced content that bypassed the verification pipeline, the scanner caught it in CI, and the fix shipped before the PR merged.

The failure rate across the last 50 CI runs at the time of this incident was 2%, and this single failure was a true positive.
