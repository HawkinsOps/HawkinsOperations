# Continuous Detection Validation

- Generated (UTC): 2026-04-06T21:14:40.598Z
- Suite: continuous-detection-validation
- Overall status: PASS
- Checks passed: 6/6 (100%)

## Checks

| Check | Status | Value | Source |
|---|---|---|---|
| heartbeat | PASS | SUCCESS | `data/metrics.json` |
| reconciliation_mismatch | PASS | 0 | `proof/autosoc/latest/reconciliation_latest.json` |
| coverage_required_hosts | PASS | 8/8 | `data/metrics.json` |
| pipeline_last_status | PASS | SUCCESS | `proof/autosoc/latest/run_metrics_latest.json` |
| splunk_ingest_proof_present | PASS | content/lab/proxmox/vms/104/splunk/exports/WAZUH_SPLUNK_PIPELINE_PROOF_2026-03-20.md | `filesystem` |
| grafana_proof_present | PASS | proof/grafana/latest.md | `filesystem` |
