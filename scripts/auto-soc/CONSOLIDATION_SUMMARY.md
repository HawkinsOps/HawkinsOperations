# AutoSOC Consolidation Summary

**Date:** 2026-03-30
**Canonical repo:** `Z:\GitHub\HawkinsOperations\scripts\auto-soc\`
**Proof artifacts:** `Z:\GitHub\HawkinsOperations\proof\autosoc\`
**Operational data:** `Z:\AutoSOC\` (cases, queue, output, logs)

---

## Legacy Sources Found on Z:

| Label | Original Path | Migrated Location on Z: | Last Modified | File Count |
|-------|--------------|------------------------|---------------|------------|
| Source A (C:\OPS\SYSTEM) | `C:\OPS\SYSTEM` | `Z:\Intake\from_OPS\system\` | 2026-03-25 | ~150 files across Automation/, Configs/, Logs/ |
| Source B (C:\RH\OPS) | `C:\RH\OPS` | `Z:\Intake\from_RH_OPS\` | 2026-03-25 | ~12,426 files in 30_Projects/ + 50_System/ |
| Proof copy | `C:\Operations` | `Z:\Intake\from_Operations\Operations\HawkinsOps-audit\proof\autosoc\` | 2026-03-21 | 8 files |

---

## What Was Consolidated

### Pipeline Scripts (45 files -> `scripts/auto-soc/`)

**From Source B** (35 files - complete pipeline):
- 19 Python modules: run-pipeline.py (orchestrator), common.py (path constants), poll-alerts.py (ingestion), triage.py (disposition engine), reconcile-state.py, coverage-check.py, policy-audit.py, escalation-quality.py, and 11 more
- 15 PowerShell scripts: daily-ops.ps1 (coordinator), run-autosoc-contract.ps1, install-autosoc-*-task.ps1 (scheduler installers), build_*.ps1, and more
- 1 CMD wrapper: run-autosoc-live-task.cmd
- 2 test files: test_triage.py, test_redact.py
- 1 template: portfolio.gitignore.snippet

**From Source A** (overwriting 2 Source B files with newer versions):
- `build_march_truth_index.ps1` (Source A: 5,523 bytes, 2026-03-23 vs Source B: 5,088 bytes, 2026-03-04)
- `build_runs_index.ps1` (Source A: 7,377 bytes, 2026-03-23 vs Source B: 6,938 bytes, 2026-03-04)

Source A versions were chosen because they contain additional logic (Assert-CanonicalPath function) added 19 days after Source B froze.

### Configuration (from Source A exclusively - `scripts/auto-soc/config/`)
- `policy.yaml` (5.8 KB) - Triage thresholds, escalation rules, auto-close policies
- `known_fps.yaml` (436 B) - Known false positive patterns
- `agent_inventory.json` (2.6 KB) - Required host coverage definitions
- `canonical_baseline.json` (309 B) - Locked metrics baseline
- `secrets/wazuh_indexer_pass.txt.TEMPLATE` - Credential template (not actual secret)

These configs existed ONLY in Source A. Source B's `Build/Config/` contained only a secrets folder.

### Operational Data (-> `Z:\AutoSOC\`)
- **Cases:** 2,508 case directories from Source B (full archive)
- **Queue:** Processed alert queue from Source B
- **Output:** Ledger (630 KB), heartbeat, metrics, reconciliation, escalation staging
- **Logs/Reports:** Runtime logs, indexes, reports from Source A (most complete set)

### Proof Artifacts (-> `proof/autosoc/latest/`)
- 8 files already existed in repo; updated with Source A versions where newer

---

## Biggest Merge Decisions

1. **Source B is the operational authority** for scripts. It contains the complete 35-file pipeline. Source A only had 4 of those scripts (assemble-pack.py, build_march_truth_index.ps1, build_runs_index.ps1, build_run_manifest.ps1).

2. **Source A is the config authority**. All three config files (policy.yaml, known_fps.yaml, agent_inventory.json) existed only in Source A.

3. **Two scripts overwritten with Source A versions** (build_march_truth_index.ps1, build_runs_index.ps1) because Source A had newer revisions with additional validation logic. The remaining 2 shared scripts were byte-identical (SHA256 match).

4. **Reports kept from Source A** where Source A had larger/more complete versions (e.g., triage-quality-history.csv: Source A 43,669 bytes vs Source B 16,289 bytes).

5. **Secrets templated, not copied.** The wazuh_indexer_pass.txt was copied as `.TEMPLATE` to prevent credential leakage.

---

## Remaining Risks / Review Items

1. **C:\ path defaults in `common.py`**: Lines 10-20 default to `C:\RH\OPS`. The env var `OPS_ROOT` / `AUTOSOC_ROOT` provides override, but defaults should be updated for Z: operation.

2. **PowerShell scripts with hardcoded C:\ paths**: `build_march_truth_index.ps1` and `build_runs_index.ps1` have `$RunsRoot = "C:\OPS\Control\Logs\AutoSOC\Runs"` style defaults. These need parameter overrides or editing.

3. **Scheduler tasks**: `install-autosoc-contract-task.ps1` and `install-autosoc-live-task.ps1` create Windows Scheduled Tasks with C:\ paths. Must be re-run with Z:\ paths before deployment.

4. **Coverage gap**: Last known coverage was 4/9 required hosts (44.4%). 5 hosts missing: core, ho-fs-01, HO-GPU-01, HO-GRAFANA-01, HO-HONEYPOT-01.

5. **Intake source trees not deleted**: Original migrated copies remain in `Z:\Intake\from_OPS\` and `Z:\Intake\from_RH_OPS\` for rollback if needed.
