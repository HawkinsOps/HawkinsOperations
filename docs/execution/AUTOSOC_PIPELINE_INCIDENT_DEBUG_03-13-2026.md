# AutoSOC Pipeline Incident Debug - 03-13-2026

- Status: Resolved
- Scope: AutoSOC live pipeline ingestion failure, reconciliation follow-up, and recovery validation
- Started: 03-13-2026
- Resolved: 03-13-2026
- Owner: Raylee Hawkins

## 1. Summary

This document tracks the investigation, remediation, and validation work for an AutoSOC live pipeline failure observed on 03-13-2026.

Resolved outcome:
- the live pipeline returned to `SUCCESS`
- strict reconciliation returned to `PASS`
- required host coverage returned to `8/8`
- the strongest pre-failure corpus and published portfolio metrics remained intact throughout the incident

High-level root cause:
- primary outage cause: infrastructure-side network disruption prevented the poller from reaching the configured indexer endpoint
- secondary recovery blocker: the reconciliation script was resolving the wrong repo incident path and failed strict validation until corrected

## 2. Pre-Failure Baseline

These are the strongest known pre-failure metrics used as the baseline for recovery validation.

Published portfolio counts:
- Total detections: `140`
- Sigma: `103`
- Wazuh rule blocks: `28`
- Wazuh XML files: `24`
- Splunk detections: `9`
- IR playbooks: `10`

AutoSOC corpus snapshot:
- Total cases: `25167`
- Auto-closed benign: `20942`
- Auto-closed known FP: `1747`
- Escalated: `2478`
- Coverage: `6/8` required hosts
- Processed telemetry files scanned: `35962`

Primary source files:
- `PROOF_PACK/VERIFIED_COUNTS.md`
- `content/incidents.json`
- external AutoSOC output artifacts mirrored from the working environment during validation

## 3. Detection

The outage pattern was visible in the latest AutoSOC heartbeat artifacts and the 03-13-2026 run log.

Observed run pattern:
- repeated failures every approximately 5 minutes on 03-13-2026
- fail stage: `poll-alerts`
- latest confirmed failed run before recovery:
  - `run_id`: `autosoc-20260313T164401Z-2384`
  - `start_utc`: `2026-03-13T16:44:01Z`
  - `end_utc`: `2026-03-13T16:45:39Z`
  - `status`: `FAILED`
  - `run_seconds`: `98.575`

Interpretation:
- the failure occurred before ingestion and case-processing work, which initially pointed to connectivity or service reachability rather than triage logic

## 4. Evidence Collected

### 4.1 Configuration validation

Confirmed from the configured AutoSOC build environment:
- the poller still had a configured indexer endpoint
- the poller still had an available username value
- the poller still had a readable password-file source
- the alert index configuration was still present

Interpretation:
- this did not look like a missing-config or missing-secret failure

### 4.2 Poller error

Observed in the 03-13-2026 run log:
- `RuntimeError: Indexer connection error after 4 attempts`
- underlying error: `WinError 10060`
- failure description: connection attempt timed out because the remote host did not respond

Interpretation:
- this pointed to connectivity or service availability, not unit-test failure or triage-policy failure

### 4.3 Connectivity checks from the runner

Observed during debugging:
- endpoint name resolution succeeded
- direct TCP connectivity to the configured indexer endpoint timed out
- the runner still retained general internet connectivity
- the runner still retained mesh-VPN control-plane connectivity

Interpretation:
- this did not look like a total loss of network on the runner
- the failure was more consistent with a remote-node reachability problem, a remote service outage, or a broken path between the runner and the indexer endpoint

### 4.4 Infrastructure-side validation

Follow-up validation after network recovery showed:
- the previously unreachable remote endpoint became reachable again
- a standalone poller run completed successfully
- the poller continued to use the expected password-file source
- the poller returned `POLLED=0` and `NO_NEW_ALERTS=TRUE`, which indicated a healthy path with no new events rather than a failed path

Interpretation:
- the original blocker was infrastructure-side network reachability, not the Python polling logic itself

## 5. Working Theory and Confirmation

Confirmed fault chain:
1. infrastructure-side network disruption broke the poller-to-indexer path
2. once connectivity was restored, the poller recovered
3. the next blocker surfaced in `reconcile`, where strict validation failed because the script was checking the wrong repo incident path

This sequence matters because it separates the incident into two different classes of failure:
- an infrastructure outage that blocked ingestion
- a code-path bug in reconciliation that was only visible after ingestion recovered

## 6. Steps Taken

Completed investigation steps:
- verified latest heartbeat failure state
- verified repeated failure pattern in heartbeat history
- verified fail stage was `poll-alerts`
- verified configured secret file was present and readable
- verified the indexer endpoint remained configured
- verified runner-side network was not fully down
- verified direct TCP timeout to the configured indexer endpoint
- restored the upstream network path
- re-ran `poll-alerts.py` by itself after connectivity recovery
- re-ran the full pipeline after poller recovery
- inspected reconciliation logic after the pipeline progressed beyond polling
- corrected the reconciliation repo path logic
- re-ran strict reconciliation after the patch
- re-ran the full pipeline after the reconciliation fix

## 7. Reconciliation Fix

Follow-up debugging confirmed that the reconciliation failure was not caused by missing published incidents or ledger corruption.

Actual issue:
- the reconciliation script was checking the wrong repo incident path
- published incident content still existed and was aligned with the ledger and content index

Action taken:
- updated `reconcile-state.py` to resolve incidents from the actual repo content path first
- preserved fallback behavior for the legacy non-content path shape

Post-fix reconciliation evidence:
- `MISMATCH_COUNT=0`
- `ledger_total_cases=25167`
- `ledger_escalated_metric=2478`
- `repo_incident_dirs=2480`
- `repo_incident_dirs_autosoc_scoped=2478`
- `content_incidents=2478`

Interpretation:
- strict reconciliation now passes
- the published incident inventory and the internal escalation inventory are aligned again

## 8. Recovery Validation

Standalone poller validation after network recovery:
- poller completed successfully
- `SECRET_SOURCE=PASS_FILE`
- `MODE=realtime`
- `POLLED=0`
- `SAVED=0`
- `NO_NEW_ALERTS=TRUE`

Final post-fix pipeline validation:
- `run_id`: `autosoc-20260313T183711Z-20032`
- `start_utc`: `2026-03-13T18:37:11Z`
- `end_utc`: `2026-03-13T18:39:38Z`
- `duration_seconds`: `146.505`
- `status`: `SUCCESS`
- `fail_stage`: blank
- `cases_scanned`: `25167`
- `cases_processed`: `0`
- `reconciliation.status`: `PASS`
- `reconciliation.mismatch_count`: `0`

Recovered run timings:
- `tests`: `0.189s`
- `poll_alerts`: `0.264s`
- `triage`: `0.174s`
- `triage_quality`: `15.780s`
- `triage_quality_chart`: `0.852s`
- `cases_processing`: `3.808s`
- `reconcile`: `0.427s`
- `coverage_check`: `123.624s`

Current state after recovery:
- the original `poll-alerts` outage is resolved
- the pipeline completes end-to-end successfully
- strict reconciliation is repaired and passing
- required host coverage has returned to full parity

Final validation run after host coverage recovery:
- `run_id`: `autosoc-20260313T215029Z-31020`
- `start_utc`: `2026-03-13T21:50:29Z`
- `end_utc`: `2026-03-13T21:51:01Z`
- `duration_seconds`: `31.843`
- `status`: `SUCCESS`
- `cases_scanned`: `26032`
- `cases_processed`: `173`
- `reconciliation.status`: `PASS`
- `reconciliation.mismatch_count`: `0`
- `freshness.status`: `PASS`
- `coverage.status`: `PASS`
- `coverage.present_hosts`: `8`
- `coverage.missing_hosts`: `0`
- `required_coverage_percent`: `100.0`

Recovered host coverage:
- `ho-fs-01`
- `HO-GPU-01`
- `HO-GRAFANA-01`
- `HO-HONEYPOT-01`
- `HO-LM-01`
- `HO-RUNNER-01`
- `HO-WAZUH-01`
- `HO-WE-01`

Final interpretation:
- the platform recovered from ingestion failure to full end-to-end health
- reconciliation, freshness, and host coverage all returned to `PASS`
- the last blocker was not a Proxmox or Windows-side pipeline issue; it was delayed arrival of fresh Honeypot alerts into the processed coverage window

## 9. Interview-Safe Explanation

The strongest concise explanation is:

"The high-volume stable corpus was generated during the successful March 2 to March 4 operating window. On March 13, 2026, a network-path issue prevented the poller from reaching the indexer endpoint, which caused repeated scheduled ingestion failures. After restoring connectivity, I found and fixed a separate reconciliation path bug, revalidated strict reconciliation at zero mismatches, and returned the full pipeline to a successful end-to-end state."

## 10. Lessons Learned

- split infrastructure availability metrics from case-processing quality metrics so one outage does not distort the entire story
- keep a standalone poller validation step available for fast fault-domain isolation
- treat reconciliation as a separate control-plane check, because it can fail independently after ingestion recovers
- keep public incident write-ups sanitized while preserving exact operational evidence in the private working environment

## 11. Update Log

### 03-13-2026 Initial Entry

Added initial incident record with:
- pre-failure baseline metrics
- failure detection timestamps
- poller configuration validation
- timeout evidence
- runner-side connectivity findings
- recovery plan and validation criteria

### 03-13-2026 Network Recovery

Added recovery evidence showing:
- the remote endpoint became reachable again
- standalone polling completed successfully
- the pipeline advanced past `poll-alerts`

### 03-13-2026 Reconciliation Fix and Final Recovery

Added final recovery evidence showing:
- reconciliation path logic was corrected
- strict reconciliation returned `MISMATCH_COUNT=0`
- the full pipeline returned to `SUCCESS`

### 03-13-2026 Coverage Closure

Added final validation showing:
- fresh Honeypot manager alerts were confirmed
- Windows-side poll and pipeline reruns pulled the remaining host into processed coverage
- required host coverage returned to `8/8`
- final heartbeat reported `SUCCESS`, `reconciliation=PASS`, `freshness=PASS`, and `coverage=PASS`
