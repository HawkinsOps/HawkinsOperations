# Alert Quality Scorecard

- Generated (UTC): 2026-04-01T22:46:12.484Z
- Window: lifetime_runtime_snapshot
- Overall status: WATCH
- Source: `data/metrics.json`

## Totals

- Total cases: 55665
- Auto-closed benign: 199672
- Known false positive: 85266
- Escalated: 0
- Review backlog: 28969
- Staged pending: 6178

## Scorecard

| Metric | Value | Target | Status |
|---|---:|---|---|
| auto_close_benign_pct | 358.7 | >= 35 | PASS |
| known_fp_pct | 153.18 | <= 45 | WATCH |
| escalation_pct | 0 | >= 3 | WATCH |
| review_backlog_pct | 52.04 | <= 20 | WATCH |
| staged_pending_pct | 11.1 | <= 1 | WATCH |
| reconciliation_mismatch_count | 0 | 0 | PASS |
