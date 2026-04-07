# Alert Quality Scorecard

- Generated (UTC): 2026-04-07T16:24:03.478Z
- Window: lifetime_runtime_snapshot
- Overall status: WATCH
- Source: `data/metrics.json`

## Totals

- Total cases: 324074
- Auto-closed benign: 199672
- Known false positive: 85953
- Escalated: 8574
- Review backlog: 29875
- Staged pending: 67

## Scorecard

| Metric | Value | Target | Status |
|---|---:|---|---|
| auto_close_benign_pct | 61.61 | >= 35 | PASS |
| known_fp_pct | 26.52 | <= 45 | PASS |
| escalation_pct | 2.65 | >= 3 | WATCH |
| review_backlog_pct | 9.22 | <= 20 | PASS |
| staged_pending_pct | 0.02 | <= 1 | PASS |
| reconciliation_mismatch_count | 0 | 0 | PASS |
