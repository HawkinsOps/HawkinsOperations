# AutoSOC Operations Runbook (03-02-2026)

## Purpose
This runbook defines the daily operating model for the AutoSOC pipeline:
- ingest alerts from Wazuh Indexer
- apply policy-based triage
- enforce evidence quality gates
- generate transfer-ready incident packs
- stage repo-backed outputs for review

This is an operations document for repeatable execution, troubleshooting, and closure.

## Scope
- Pipeline host: primary Windows pipeline host
- Detection backend: Wazuh manager + indexer
- Transfer and publication target: `HawkinsOperations` repository
- Scheduler cadence: every 5 minutes

## Pipeline Components
Source path: `C:\RH\OPS\50_System\Scripts\Automation\auto-soc`

1. `poll-alerts.py`
- Pulls new indexer events with cursor-based checkpointing.
- Resilience: retry/backoff (`--retries`, `--backoff-seconds`).
- Queue control: overflow archive (`--max-queue-files`).

2. `triage.py`
- Applies `policy.yaml` and `known_fps.yaml`.
- Classifies alerts into `AUTO_CLOSE_BENIGN`, `AUTO_CLOSE_KNOWN_FP`, or `ESCALATE`.

3. `redact.py`
- Hard gate for public-safe output.
- Required before pack assembly.

4. `assemble-pack.py`
- Produces required evidence docs:
  - `00_one_pager.md`
  - `01_full_report.md`
  - `02_timeline.csv`
  - `03_queries.md`
  - `evidence_index.md`
  - `closure_report.md`

5. `create-pr.py`
- Copies escalated case pack into incident path.
- Updates repo-facing metadata.

6. `run-pipeline.py`
- Orchestrates tests, ingest, triage, redact, pack, publish-ready staging.
- Log maintenance: `--log-retention-days` (default 30).

## Runtime Paths
- Config: `C:\RH\OPS\30_Projects\Active\AutoSOC\Build\Config`
- Queue: `C:\RH\OPS\30_Projects\Active\AutoSOC\Build\Queue`
- Queue archive: `C:\RH\OPS\30_Projects\Active\AutoSOC\Build\Queue\Processed`
- Cases: `C:\RH\OPS\30_Projects\Active\AutoSOC\Build\Cases`
- Ledger: `C:\RH\OPS\30_Projects\Active\AutoSOC\Output\ledger.json`
- Logs: `C:\RH\OPS\50_System\Runs\Logs\auto-soc-MM-DD-YYYY.log`

## Scheduler Standard
Task name: `AutoSOC-Pipeline`

Command:
```powershell
"C:\Python314\python.exe" "C:\RH\OPS\50_System\Scripts\Automation\auto-soc\run-pipeline.py"
```

Validation:
```powershell
schtasks /Query /TN "AutoSOC-Pipeline" /V /FO LIST
```

Healthy signal:
- `Status: Ready`
- recent `Last Run Time`
- `Last Result: 0`

## Daily Operator Checklist
1. Confirm indexer connectivity:
```powershell
Test-NetConnection <wazuh-indexer-tailnet-name> -Port 9200
```
2. Confirm scheduler health:
```powershell
schtasks /Query /TN "AutoSOC-Pipeline" /V /FO LIST
```
3. Check last run log tail:
```powershell
Get-Content "C:\RH\OPS\50_System\Runs\Logs\auto-soc-03-02-2026.log" -Tail 80
```
4. Verify no persistent failures:
- no repeated `FAIL=`
- no repeated auth/network tracebacks

## Weekly Checklist
1. Run policy drift audit:
```powershell
python C:\RH\OPS\50_System\Scripts\Automation\auto-soc\policy-audit.py --max-files 1000 --min-recommend-count 10
```
2. Review false-positive patterns in `known_fps.yaml`.
3. Review escalation thresholds in `policy.yaml`.
4. Confirm log retention and queue growth behavior remain stable.
5. Rotate credentials when required by policy or after exposure events.

## Failure Playbook
### A) `HTTP Error 401: Unauthorized`
Cause: invalid indexer credentials.

Action:
1. Validate credentials locally on manager.
2. Update `Build\Config\.env` on the primary Windows pipeline host.
3. Re-run `poll-alerts.py`.

### B) `ConnectionRefusedError` or port unreachable
Cause: tunnel/endpoint path down.

Action:
1. Confirm `tailscale serve` on manager.
2. Validate `Test-NetConnection ... -Port 9200` from pipeline host.
3. Re-run poller with retries.

### C) `WinError 10013` socket access forbidden
Cause: local policy/EDR/firewall interference.

Action:
1. Verify outbound access policy on pipeline host.
2. Reconfirm tunnel reachability and DNS resolution.
3. Retest poller after policy update.

### D) Task returns non-zero (`Last Result != 0`)
Action:
1. Open latest auto-soc log.
2. Identify first `FAIL=` stage.
3. Execute failing script directly to isolate issue.
4. Validate fix by re-running task and confirming `Last Result: 0`.

## Current Hardened Controls
- Unit-test preflight before orchestration.
- Poll retry/backoff for transient failures.
- Explicit no-new-alert cycle telemetry:
  - `NO_NEW_ALERTS=TRUE|FALSE`
- Queue overflow archive guard:
  - `QUEUE_OVERFLOW_ARCHIVED=<n>`
- Log retention pruning and per-run metadata:
  - `RUN_UTC=...`
  - `LOG_PRUNE_REMOVED=<n>`
- Redaction hard gate before public-facing pack assembly.

## Verification Commands (End-to-End)
```powershell
python C:\RH\OPS\50_System\Scripts\Automation\auto-soc\poll-alerts.py --retries 3 --backoff-seconds 2 --max-queue-files 2000
python C:\RH\OPS\50_System\Scripts\Automation\auto-soc\triage.py
schtasks /Run /TN "AutoSOC-Pipeline"
Start-Sleep -Seconds 10
schtasks /Query /TN "AutoSOC-Pipeline" /V /FO LIST
Get-Content "C:\RH\OPS\50_System\Runs\Logs\auto-soc-03-02-2026.log" -Tail 120
```

## Notes
- Keep commands shell-correct: Linux commands on Linux hosts, PowerShell commands on Windows hosts.
- Do not publish internal identifiers, private host details, or credentials in public artifacts.
