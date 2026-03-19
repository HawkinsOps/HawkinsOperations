# Metrics Provenance

## Status

Active.

`data/metrics.json` is generated from committed proof artifacts by `scripts/generate-metrics.js`.

## Current authority

Use the authority order defined in `docs/PRECEDENCE_CONTRACT.md`.

For the current `data/metrics.json` fields, the intended source mapping is:

- `running_totals.total_cases`
  - source: `proof/autosoc/latest/reconciliation_latest.json`
  - field: `counts.ledger_total_cases`

- `running_totals.escalated`
  - source: `proof/autosoc/latest/reconciliation_latest.json`
  - field: `counts.ledger_escalated_metric`

- `running_totals.auto_closed_benign`
  - source: `proof/autosoc/latest/heartbeat.json`
  - field: `counts.auto_closed_benign`

- `running_totals.known_fp`
  - source: `proof/autosoc/latest/heartbeat.json`
  - field: `counts.auto_closed_known_fp`

- `host_coverage`
  - source: `proof/autosoc/latest/coverage_latest.json`
  - derived from: `present_hosts` and `required_hosts`

- `reconciliation_mismatch`
  - source: `proof/autosoc/latest/reconciliation_latest.json`
  - field: `mismatch_count`

- `heartbeat`
  - source: `proof/autosoc/latest/heartbeat.json`
  - field: `status`

- `last_updated`
  - source: `proof/autosoc/latest/coverage_latest.json`
  - field: `generated_utc`

- `detection_inventory.*`
  - source: `PROOF_PACK/verified_counts.json`

## Known limitations

- `running_totals.review` does not yet have a durable upstream committed source and remains a placeholder required by the current schema.
- `running_totals.staged_pending` is currently sourced from `ledger_pending_escalate_ids`, which may remain zero even when other non-ledger staging concepts exist elsewhere.
- `scripts/generate-site-data.js` distributes this file, but it does not define the metrics contract itself.

## Next hardening step

Tighten the generator and validation so that:
- stale or contradictory proof timestamps fail closed
- unsupported placeholder fields are either removed from schema or sourced from committed artifacts
- downstream pages distinguish latest live state from historical validated recovery snapshots
