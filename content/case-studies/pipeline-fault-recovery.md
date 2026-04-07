# Case Study: Pipeline Fault Recovery — Two Failure Domains, One Session
**Diagnosing a Sequential Poller Timeout and Reconciliation Serialization Defect Under Production Load**

---

## Problem / Hypothesis

On March 13, 2026, SignalFoundry — a 7-stage automated SOC triage pipeline processing live Wazuh alerts — began failing on every scheduled run. The pipeline heartbeat reported repeated failures at the `poll_alerts` stage at roughly 5-minute intervals. No unit test regression. No missing configuration. No credential rotation.

The hypothesis was straightforward: something between the runner and the Wazuh Indexer endpoint had broken. But the failure mode was not straightforward — it masked a second, independent defect that only surfaced after the first was resolved.

---

## Environment

| Component | Role |
|---|---|
| SignalFoundry pipeline | 7-stage Python + PowerShell SOC automation |
| Wazuh Manager + Indexer | SIEM engine; OpenSearch backend on `ho-sr-wm-01` |
| Windows Task Scheduler | Contract execution host (5-minute interval) |
| `poll-alerts.py` | Stage 2 — REST API poller against Wazuh Indexer |
| `reconcile-state.py` | Stage 7 — 4-way ledger/repo/content reconciliation |
| `heartbeat.json` | Pipeline health telemetry (stage, status, timestamps) |

Pre-failure validated state:
- 25,167 total cases processed
- 2,478 escalated cases
- 210 detection rules (CI-verified)
- 8/8 host coverage
- `MISMATCH_COUNT=0`

---

## Methodology

**Step 1 — Locate the failure.**
Read `heartbeat.json`. The `fail_stage` field pointed directly to `poll_alerts`. No ambiguity. The pipeline was dying before triage, before case processing, before reconciliation. Everything downstream was irrelevant to the first failure.

**Step 2 — Rule out configuration drift.**
Confirmed the poller had a configured endpoint, valid user value, and readable password-file source (`SECRET_SOURCE=PASS_FILE`). No credential rotation had occurred. No config file had been modified since the last successful run.

**Step 3 — Separate local runner health from remote endpoint reachability.**
The runner had general network connectivity. Direct connection to the Wazuh Indexer REST API was timing out. This isolated the failure to the network path between runner and indexer — not the poller logic itself.

**Step 4 — Trace the retry defect.**
While investigating, I found that `poll-alerts.py` had a retry implementation defect. The `fetch_with_retry` function handled `HTTPError` and `URLError` differently. On `URLError` (connection timeout), the retry counter was not incremented before the sleep call. Under delayed connection reset conditions — not clean refusal — the first attempt consumed an exception without entering the retry path. The function would exhaust retries prematurely.

**Step 5 — Restore polling and re-run.**
After upstream connectivity was corrected and the retry logic fixed, the poller completed successfully. I triggered a full pipeline run. It failed again — this time at `reconcile`.

**Step 6 — Diagnose the reconciliation defect.**
`reconcile-state.py` computes six mismatch categories by comparing ledger entries against repository incident directories. The script was resolving `repo_ids` (all directories in the portfolio repo) instead of `repo_ids_autosoc` (directories matching the AutoSOC case ID regex: `^\d{4}-\d{2}-\d{2}__.+__rule\d+__.+__.+$`). Non-AutoSOC directories were counted as phantom mismatches, inflating `mismatch_count` and triggering FAIL even though the actual ledger/content state was clean.

**Step 7 — Fix and validate.**
Scoped all six mismatch computations to `repo_ids_autosoc`. Re-ran strict reconciliation. `MISMATCH_COUNT=0`.

---

## Evidence

**Heartbeat telemetry (failure state):**
```
fail_stage: poll_alerts
status: FAIL
```

**Poller retry defect (before fix — pseudocode):**
```python
def fetch_with_retry(url, retries=3, backoff=2):
    for attempt in range(retries):
        try:
            return urlopen(Request(url, ...))
        except HTTPError as e:
            if e.code == 401:
                raise
        except URLError as e:
            pass  # BUG: counter not incremented, sleep skipped
        time.sleep(backoff ** attempt)
```

**Standalone poller validation after fix:**
```
SECRET_SOURCE=PASS_FILE
MODE=realtime
POLLED=0
SAVED=0
NO_NEW_ALERTS=TRUE
```

**Reconciliation validation after scoping fix:**
```
ledger_total_cases=25167
ledger_escalated_metric=2478
repo_incident_dirs_autosoc_scoped=2478
content_incidents=2478
MISMATCH_COUNT=0
```

**Recovery pipeline run:**
```
run_id: autosoc-20260313T183711Z-20032
status: SUCCESS
duration_seconds: 146.505
cases_scanned: 25167
reconciliation.status: PASS
reconciliation.mismatch_count: 0
```

**Full platform-health validation (same day, later run):**
```
run_id: autosoc-20260313T215029Z-31020
status: SUCCESS
duration_seconds: 31.843
cases_scanned: 26032
cases_processed: 173
reconciliation.status: PASS
reconciliation.mismatch_count: 0
coverage.status: PASS
coverage.present_hosts: 8
coverage.missing_hosts: 0
```

---

## Findings

Two independent defects surfaced simultaneously:

1. **Poller retry defect** — `URLError` on connection timeout did not enter the retry path on the first attempt. Under production scheduling (5-minute intervals), every run hit the same failure and exhausted retries without meaningful backoff.

2. **Reconciliation scoping error** — `reconcile-state.py` computed mismatches against unscoped `repo_ids` instead of `repo_ids_autosoc`. This bug had been latent since the repo was small — it only manifested at scale when non-AutoSOC directories accumulated enough to push `mismatch_count` above zero.

The second defect was invisible while the first was active. The poller failure prevented the pipeline from reaching the reconciliation stage. Only after polling was restored did the reconciliation defect surface — a sequential failure domain that would have been missed by restarting the pipeline without a full end-to-end validation pass.

---

## Operational Impact

- Pipeline restored from repeated FAIL to sustained SUCCESS in one session
- Strict reconciliation restored to zero hard mismatches
- Host telemetry coverage confirmed at 8/8 — no monitoring gaps during the outage window
- 173 new cases processed on the recovery run, confirming live alert ingestion was operational
- The poller retry fix ensures all 3 retry attempts are consumed before FAIL on future connectivity interruptions
- The reconciliation scoping fix eliminates a class of phantom mismatch that would have recurred as the repo grew

---

## Verification

A reviewer can confirm the claims in this case study through the following:

1. **Pipeline recovery documentation:** `docs/execution/AUTOSOC_PIPELINE_RECOVERY_CASE_STUDY_03-13-2026.md` — raw incident log with exact telemetry values
2. **Detailed incident debug log:** `docs/execution/AUTOSOC_PIPELINE_INCIDENT_DEBUG_03-13-2026.md` — step-by-step investigation trace
3. **Authority snapshot (locked 03-25):** `PROOF_PACK/VERIFIED_COUNTS.md` — 55,665 total cases post-recovery, confirming continued pipeline operation
4. **Reconciliation logic:** The scoping fix is visible in the `reconcile-state.py` commit history — search for `repo_ids_autosoc` replacing `repo_ids` in the six mismatch category computations
5. **Heartbeat telemetry:** The `heartbeat.json` schema includes `fail_stage`, `status`, and `run_id` fields referenced throughout this case study

---

*Date: 2026-03-13 | Environment: Windows 11, Python 3.14, PowerShell 7, Wazuh Indexer REST API | System: SignalFoundry (7-stage SOC triage pipeline)*
