# AutoSOC Recovered Runbook

**Recovered:** 2026-03-30
**Pipeline location:** `Z:\GitHub\HawkinsOperations\scripts\auto-soc\`
**Operational data:** `Z:\AutoSOC\`

---

## Execution Flow (End-to-End)

```
                        daily-ops.ps1 (coordinator)
                              |
              +-----------+---+---+-----------+
              |           |       |           |
         run-pipeline.py  |  triage-quality.py |
              |           |       |           |
    +---------+-------+   |       |    reconcile-state.py
    |         |       |   |       |
poll-alerts  triage  cases|  coverage-check.py
    |         |       |   |
  Queue/  Cases/   Output/|
              |       |   |
         ledger.json  heartbeat.json
```

### Primary Entrypoints

| Script | Role | Mode |
|--------|------|------|
| `daily-ops.ps1` | Top-level coordinator | Called by scheduled task or manually |
| `run-pipeline.py` | Pipeline orchestrator | `--mode live\|contract\|refresh` |
| `run-autosoc-contract.ps1` | Contract validation batch | Daily at 07:20 AM |
| `run-autosoc-live-task.ps1` | Live mode wrapper | Continuous polling |

### Step-by-Step Pipeline Execution

1. **`daily-ops.ps1`** starts (Parameters: `-Refresh`, `-SkipTests`, `-ExecutePromotion`)
2. Calls **`run-pipeline.py`** which executes these steps in sequence:
   - **`poll-alerts.py`** - Fetches alerts from Wazuh Indexer API (HTTPS)
     - Uses cursor-based pagination (`.cursor.json`)
     - Outputs raw alert JSON to `Queue/`
   - **`triage.py`** - Processes queued alerts
     - Loads `policy.yaml`, `known_fps.yaml`, `agent_inventory.json`
     - Dispositions: AUTO_CLOSE_BENIGN, AUTO_CLOSE_KNOWN_FP, ESCALATE, REVIEW
     - Creates case directories under `Cases/` with: alert.raw.json, triage.json, disposition_summary.json
     - Updates `ledger.json`
   - **`triage-quality.py`** - Generates quality metrics
   - **`reconcile-state.py`** - Validates ledger vs repo vs escalation staging
   - **`coverage-check.py`** - Validates required host coverage (7-day window)
3. Pipeline writes:
   - `heartbeat.json` (run status)
   - `run_metrics_latest.json` (step timing)
   - `heartbeat_history.jsonl` (append-only history)
4. **`daily-ops.ps1`** then runs freshness checks:
   - P95 max: 3,600 seconds
   - Oldest max: 7,200 seconds
   - Policy analysis: max 1,000 files, min recommend count 10

### Scheduled Tasks

| Task Name | Script | Schedule | Installer |
|-----------|--------|----------|-----------|
| `OPS_AutoSOC_Contract_Daily` | `run-autosoc-contract-task.ps1` | Daily 07:20 AM | `install-autosoc-contract-task.ps1` |
| AutoSOC Live | `run-autosoc-live-task.ps1` | Continuous | `install-autosoc-live-task.ps1` |

---

## Dependencies

### Runtime
- **Python 3.x** (no external packages - uses only stdlib: json, pathlib, datetime, urllib, ssl, argparse, subprocess)
- **PowerShell 7** (pwsh)
- **Wazuh Indexer API** (HTTPS endpoint for alert polling)

### Credentials
- `WAZUH_INDEXER_PASSWORD` env var, OR
- `config/secrets/wazuh_indexer_pass.txt` file, OR
- `config/.env` file with `WAZUH_INDEXER_PASSWORD=...`

### Config Files Required
| File | Purpose |
|------|---------|
| `config/policy.yaml` | Triage thresholds, auto-close rules, escalation groups, protected agents |
| `config/known_fps.yaml` | Pattern-based false positive definitions |
| `config/agent_inventory.json` | Required host list, VM IDs, coverage policy |

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OPS_ROOT` | `C:\RH\OPS` (NEEDS UPDATE) | Base path for all derived paths |
| `AUTOSOC_ROOT` | `{OPS_ROOT}\30_Projects\Active\AutoSOC` | AutoSOC project root |
| `WAZUH_INDEXER_PASSWORD` | (none) | Wazuh API credential |

### Path Migration for Z: Drive

To run on Z: without modifying `common.py`, set these environment variables:

```powershell
$env:OPS_ROOT = "Z:\AutoSOC"
$env:AUTOSOC_ROOT = "Z:\AutoSOC"
```

Or update `common.py` line 10:
```python
OPS_ROOT = Path(os.getenv("OPS_ROOT", r"Z:\AutoSOC"))
```

All derived paths (BUILD_ROOT, CONFIG_ROOT, CASES_ROOT, OUTPUT_ROOT, etc.) will cascade from this change.

---

## Triage Policy Summary

| Threshold | Value |
|-----------|-------|
| Auto-close benign max level | 3 |
| Auto-close known FP max level | 13 |
| Escalate min level | 12 |
| Protected agent min escalate level | 7 |

**Always escalate groups:** rootkit, malware, ransomware, data_exfiltration, sql_injection, credential_dumping, lateral_movement

**Protected agents:** HO-SR-01, HO-Wazuh-01, HO-GRAFANA-01, HO-HONEYPOT-01

---

## Operational Data Layout (Z:\AutoSOC)

```
Z:\AutoSOC\
├── data\
│   ├── Cases\         # 2,508 case directories (alert.raw.json + triage.json + disposition)
│   ├── Queue\         # Inbound alert queue + .cursor.json
│   └── Output\        # ledger.json, heartbeat.json, metrics, escalation_staging/
├── logs\
│   ├── Runtime\       # Daily execution logs (auto-soc-MM-DD-YYYY.log)
│   ├── Reports\       # Quality reports, agent summaries, system journal
│   ├── Indexes\       # Global + monthly run indexes (CSV, MD, JSONL)
│   └── Runs\          # Run manifests with SHA256 verification
├── config\            # (operational copy - source of truth is in repo)
├── tests\
└── archive\
    ├── _legacy_review\
    ├── _quarantine_diff\
    └── _generated_artifacts\
```

---

## Known Broken Assumptions Fixed

1. **Path drift:** Scripts referenced `C:\RH\OPS` and `C:\OPS\Control\` interchangeably. The env var `OPS_ROOT` in `common.py` unifies this - set it once for Z: and all Python scripts follow.

2. **Config split:** Config files were stored separately from scripts (in `C:\OPS\SYSTEM\Configs\AutoSOC\`). Now consolidated into `scripts/auto-soc/config/` alongside the pipeline code.

3. **Secrets exposure:** `wazuh_indexer_pass.txt` was a plain file. Now templated as `.TEMPLATE` in the repo.

---

## Smoke Test Commands

```powershell
# Verify Python imports work
python -c "import sys; sys.path.insert(0, 'Z:\\GitHub\\HawkinsOperations\\scripts\\auto-soc'); import common; print(common.OPS_ROOT)"

# Dry-run pipeline (requires OPS_ROOT set)
$env:OPS_ROOT = "Z:\AutoSOC"
python Z:\GitHub\HawkinsOperations\scripts\auto-soc\run-pipeline.py --mode refresh --dry-run

# Run tests
python -m pytest Z:\GitHub\HawkinsOperations\scripts\auto-soc\tests\ -v

# Verify config loads
python -c "import json, pathlib; p = pathlib.Path(r'Z:\GitHub\HawkinsOperations\scripts\auto-soc\config\policy.yaml'); print('OK' if p.exists() else 'MISSING')"
```

---

## What To Review Manually

1. **Scheduler re-installation**: Run `install-autosoc-contract-task.ps1` and `install-autosoc-live-task.ps1` with updated Z:\ paths
2. **Coverage gap**: 5 of 9 required hosts are missing from monitoring - investigate whether VMs are offline or agent enrollment is needed
3. **C:\ path references in PowerShell scripts**: `build_march_truth_index.ps1` and `build_runs_index.ps1` have hardcoded `$RunsRoot` defaults pointing to `C:\OPS\Control\...`
4. **Wazuh credential**: Populate `config/secrets/wazuh_indexer_pass.txt` from secure source before going live
