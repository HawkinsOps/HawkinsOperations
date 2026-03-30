# Alert Quality Scorecard

- Generated (UTC): 2026-03-30T11:58:10.327Z
- Window: lifetime_runtime_snapshot
- Overall status: WATCH
- Source: `data/metrics.json`

## Totals

- Total cases: 54700
- Auto-closed benign: 0
- Known false positive: 1925
- Escalated: 0
- Review backlog: 417
- Staged pending: 53

## Scorecard

| Metric | Value | Target | Status |
|---|---:|---|---|
| auto_close_benign_pct | 0 | >= 35 | WATCH |
| known_fp_pct | 3.52 | <= 45 | PASS |
| escalation_pct | 0 | >= 3 | WATCH |
| review_backlog_pct | 0.76 | <= 20 | PASS |
| staged_pending_pct | 0.1 | <= 1 | PASS |
| reconciliation_mismatch_count | 0 | 0 | PASS |
