#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from common import OUTPUT_ROOT, utc_now


def day(ts: str) -> str:
    try:
        return datetime.fromisoformat(ts.replace('Z', '+00:00')).strftime('%Y-%m-%d')
    except Exception:
        return 'unknown'


def to_int(v):
    try:
        return int(v)
    except Exception:
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(description='Daily heartbeat trend rollup.')
    parser.add_argument('--history', type=Path, default=OUTPUT_ROOT / 'heartbeat_history.jsonl')
    parser.add_argument('--out-json', type=Path, default=OUTPUT_ROOT / 'heartbeat_trend_daily.json')
    parser.add_argument('--out-md', type=Path, default=OUTPUT_ROOT / 'heartbeat_trend_daily.md')
    args = parser.parse_args()

    rows = []
    if args.history.exists():
        for line in args.history.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue

    by_day = defaultdict(list)
    for r in rows:
        by_day[day(r.get('end_utc', ''))].append(r)

    out_rows = []
    for d in sorted(by_day):
        grp = by_day[d]
        n = len(grp)
        avg_run = round(sum(float(x.get('duration_seconds', 0) or 0) for x in grp) / max(1, n), 2)
        triaged = sum(to_int(x.get('counts', {}).get('triaged', 0)) for x in grp)
        escalated = sum(to_int(x.get('counts', {}).get('escalated', 0)) for x in grp)
        fails = sum(1 for x in grp if str(x.get('status', '')).upper() != 'SUCCESS')
        recon_fail = sum(1 for x in grp if str(x.get('reconciliation', {}).get('status', '')) == 'FAIL')
        coverage_fail = sum(1 for x in grp if str(x.get('coverage', {}).get('status', '')) == 'FAIL')
        freshness_fail = sum(1 for x in grp if str(x.get('freshness', {}).get('status', '')) == 'FAIL')
        out_rows.append({
            'date': d,
            'runs': n,
            'avg_run_seconds': avg_run,
            'triaged': triaged,
            'escalated': escalated,
            'failed_runs': fails,
            'recon_fail_runs': recon_fail,
            'coverage_fail_runs': coverage_fail,
            'freshness_fail_runs': freshness_fail,
        })

    out = {
        'generated_utc': utc_now(),
        'days': out_rows,
    }
    args.out_json.write_text(json.dumps(out, indent=2), encoding='utf-8')

    lines = ['# Heartbeat Daily Trend', '', f"- Generated UTC: {out['generated_utc']}", '']
    if not out_rows:
        lines.append('- no data')
    else:
        lines.append('| date | runs | avg_run_seconds | triaged | escalated | failed_runs | recon_fail_runs | coverage_fail_runs | freshness_fail_runs |')
        lines.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|')
        for r in out_rows:
            lines.append(
                f"| {r['date']} | {r['runs']} | {r['avg_run_seconds']} | {r['triaged']} | {r['escalated']} | {r['failed_runs']} | {r['recon_fail_runs']} | {r['coverage_fail_runs']} | {r['freshness_fail_runs']} |"
            )
    args.out_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"TREND_JSON={args.out_json}")
    print(f"TREND_MD={args.out_md}")


if __name__ == '__main__':
    main()
