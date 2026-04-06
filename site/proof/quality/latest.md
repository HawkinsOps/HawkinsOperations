# Alert Quality Scorecard

- Generated (UTC): 2026-04-06T19:27:37.307Z
- Window: lifetime_runtime_snapshot
- Overall status: WATCH
- Source: `data/metrics.json`

## Totals

- Total cases: 321351
- Auto-closed benign: 199672
- Known false positive: 85185
- Escalated: 6178
- Review backlog: 28544
- Staged pending: 8573

## Scorecard

| Metric | Value | Target | Status |
|---|---:|---|---|
| auto_close_benign_pct | 62.14 | >= 35 | PASS |
| known_fp_pct | 26.51 | <= 45 | PASS |
| escalation_pct | 1.92 | >= 3 | WATCH |
| review_backlog_pct | 8.88 | <= 20 | PASS |
| staged_pending_pct | 2.67 | <= 1 | WATCH |
| reconciliation_mismatch_count | 1 | 0 | FAIL |
