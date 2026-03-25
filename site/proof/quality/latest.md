# Alert Quality Scorecard

- Generated (UTC): 2026-03-25T13:50:43.391Z
- Window: lifetime_runtime_snapshot
- Overall status: WATCH
- Source: `data/metrics.json`

## Totals

- Total cases: 49774
- Auto-closed benign: 0
- Known false positive: 1622
- Escalated: 2478
- Review backlog: 312
- Staged pending: 28

## Scorecard

| Metric | Value | Target | Status |
|---|---:|---|---|
| auto_close_benign_pct | 0 | >= 35 | WATCH |
| known_fp_pct | 3.26 | <= 45 | PASS |
| escalation_pct | 4.98 | >= 3 | PASS |
| review_backlog_pct | 0.63 | <= 20 | PASS |
| staged_pending_pct | 0.06 | <= 1 | PASS |
| reconciliation_mismatch_count | 0 | 0 | PASS |
