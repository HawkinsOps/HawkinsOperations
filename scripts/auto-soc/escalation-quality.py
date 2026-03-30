#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from common import CASES_ROOT, OUTPUT_ROOT, utc_now


def score_case(case_dir: Path) -> dict:
    triage = case_dir / 'triage.json'
    pack = case_dir / 'pack'
    redaction = case_dir / 'redaction_report.json'
    if not triage.exists():
        return {}
    try:
        t = json.loads(triage.read_text(encoding='utf-8'))
    except Exception:
        return {}
    if str(t.get('disposition', '')).upper() != 'ESCALATE':
        return {}

    score = 0
    checks = {}
    checks['triage_present'] = True
    score += 10

    redaction_pass = False
    if redaction.exists():
        try:
            red = json.loads(redaction.read_text(encoding='utf-8'))
            redaction_pass = bool(red.get('pass', False))
        except Exception:
            redaction_pass = False
    checks['redaction_pass'] = redaction_pass
    score += 30 if redaction_pass else 0

    required = [
        '00_one_pager.md',
        '01_full_report.md',
        '02_timeline.csv',
        '03_queries.md',
        'evidence_index.md',
        'closure_report.md',
    ]
    present = 0
    for r in required:
        if (pack / r).exists():
            present += 1
    checks['pack_files_present'] = present
    checks['pack_files_required'] = len(required)
    score += int((present / len(required)) * 40)

    status = str(t.get('status', '')).upper()
    checks['status_processed'] = (status == 'PROCESSED' or status == 'ESCALATED')
    score += 20 if checks['status_processed'] else 0

    return {
        'case_id': t.get('case_id', case_dir.name),
        'score': score,
        'checks': checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Score escalation closure quality.')
    parser.add_argument('--out-json', type=Path, default=OUTPUT_ROOT / 'escalation_quality_latest.json')
    parser.add_argument('--out-md', type=Path, default=OUTPUT_ROOT / 'escalation_quality_latest.md')
    args = parser.parse_args()

    rows = []
    for case_dir in CASES_ROOT.iterdir():
        if not case_dir.is_dir():
            continue
        rec = score_case(case_dir)
        if rec:
            rows.append(rec)

    rows.sort(key=lambda x: x['score'])
    avg = round(sum(r['score'] for r in rows) / len(rows), 2) if rows else 0
    out = {
        'generated_utc': utc_now(),
        'total_escalations_scored': len(rows),
        'average_score': avg,
        'lowest_20': rows[:20],
        'highest_20': rows[-20:] if len(rows) > 20 else rows,
    }
    args.out_json.write_text(json.dumps(out, indent=2), encoding='utf-8')

    lines = [
        '# Escalation Quality Score',
        '',
        f"- Generated UTC: {out['generated_utc']}",
        f"- Escalations scored: {out['total_escalations_scored']}",
        f"- Average score: {out['average_score']}",
        '',
        '## Lowest 20 (Priority Fixes)',
    ]
    if not out['lowest_20']:
        lines.append('- none')
    else:
        for r in out['lowest_20']:
            lines.append(f"- {r['case_id']}: score={r['score']}")
    args.out_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"QUALITY_JSON={args.out_json}")
    print(f"QUALITY_MD={args.out_md}")
    print(f"AVERAGE_SCORE={avg}")


if __name__ == '__main__':
    main()
