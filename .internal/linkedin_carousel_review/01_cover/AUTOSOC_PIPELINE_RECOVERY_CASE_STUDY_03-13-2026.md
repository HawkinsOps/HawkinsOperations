# AutoSOC Pipeline Recovery Case Study

Date: 2026-03-13
Status: CLOSED
Scope: live pipeline outage investigation, recovery, and validation

## Executive Outcome

- Restored a failed AutoSOC live pipeline to full end-to-end `SUCCESS`.
- Isolated the original outage to infrastructure-side connectivity, not triage logic or secret handling.
- Identified and fixed a second reconciliation-path bug that only surfaced after ingestion recovered.
- Revalidated strict reconciliation at `MISMATCH_COUNT=0`.
- Restored required host telemetry coverage to `8/8`.

## Why This Matters

This project is not a static portfolio mock-up. It is an operating SOC workflow with real pipeline health, control-plane checks, and recovery work. The value of this incident is that it demonstrates fault isolation, debugging discipline, and recovery validation under production-like conditions.

## Starting State

Pre-failure validated system metrics:
- Total detections: `139`
- Sigma rules: `103`
- Wazuh rule blocks: `28`
- Splunk detections: `8`
- IR playbooks: `10`
- Total AutoSOC cases: `25167`
- Auto-closed benign: `20942`
- Auto-closed known FP: `1747`
- Escalated: `2478`

## Problem

On 2026-03-13, scheduled AutoSOC runs were repeatedly failing in `poll-alerts`.

Initial signals:
- repeated run failures at roughly 5-minute intervals
- timeout behavior before ingestion and case processing
- no evidence of a unit-test regression
- no evidence of missing configuration or missing secret material

## Investigation Approach

The investigation was handled in stages:

1. Validate the failure location.
- Confirmed the pipeline was failing in `poll-alerts`, before triage and case processing.

2. Rule out obvious configuration drift.
- Confirmed the poller still had a configured endpoint, user value, and readable password-file source.

3. Separate local runner health from remote endpoint reachability.
- Confirmed the runner still had general network connectivity.
- Confirmed direct endpoint connectivity was timing out.

4. Restore the network path first.
- After upstream connectivity was corrected, the poller completed successfully.

5. Re-run the full pipeline and continue debugging.
- Once polling recovered, a second failure surfaced in `reconcile`.

6. Fix the reconciliation bug.
- Found that the reconciliation script was resolving the wrong repo incident path.
- Patched the script to resolve the actual content path first, with fallback for the legacy layout.

## Root Cause

Primary cause:
- infrastructure-side network disruption prevented the poller from reaching the configured indexer endpoint

Secondary cause:
- reconciliation script path resolution did not match the current repo layout, which caused strict validation to fail even after polling recovered

## Fix

Actions taken:
- restored the network path required for the poller-to-indexer connection
- revalidated standalone polling
- patched `reconcile-state.py` to use the correct repo incident path
- re-ran strict reconciliation
- re-ran the full pipeline end to end

## Validation

Standalone poller validation after network recovery:
- `SECRET_SOURCE=PASS_FILE`
- `MODE=realtime`
- `POLLED=0`
- `SAVED=0`
- `NO_NEW_ALERTS=TRUE`

Strict reconciliation validation after code fix:
- `ledger_total_cases=25167`
- `ledger_escalated_metric=2478`
- `repo_incident_dirs_autosoc_scoped=2478`
- `content_incidents=2478`
- `MISMATCH_COUNT=0`

Final pipeline recovery run:
- `run_id`: `autosoc-20260313T183711Z-20032`
- `status`: `SUCCESS`
- `duration_seconds`: `146.505`
- `cases_scanned`: `25167`
- `cases_processed`: `0`
- `reconciliation.status`: `PASS`
- `reconciliation.mismatch_count`: `0`

Final platform-health validation after coverage closure:
- `run_id`: `autosoc-20260313T215029Z-31020`
- `status`: `SUCCESS`
- `duration_seconds`: `31.843`
- `cases_scanned`: `26032`
- `cases_processed`: `173`
- `reconciliation.status`: `PASS`
- `reconciliation.mismatch_count`: `0`
- `freshness.status`: `PASS`
- `coverage.status`: `PASS`
- `coverage.present_hosts`: `8`
- `coverage.missing_hosts`: `0`
- `required_coverage_percent`: `100.0`

## What This Demonstrates

- Evidence-driven debugging instead of guesswork
- Ability to separate infrastructure failures from application logic failures
- Control-plane validation through reconciliation, not just “it runs on my machine”
- Recovery verification with exact metrics and post-fix reruns
- Ability to drive an unstable system all the way back to full host coverage, not just partial service restoration

## Interview-Safe Summary

"I diagnosed an AutoSOC live-ingestion outage by isolating the failure to network reachability rather than triage logic, restored polling, then fixed a separate reconciliation path bug that surfaced during retest. The final validation runs returned the pipeline to `SUCCESS`, strict reconciliation to zero mismatches, and required host coverage to `8/8`."

## Related Document

- Detailed incident report: `docs/execution/AUTOSOC_PIPELINE_INCIDENT_DEBUG_03-13-2026.md`
