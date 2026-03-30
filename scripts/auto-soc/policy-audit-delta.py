#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from common import OUTPUT_ROOT, read_json, utc_now


def to_map(rows, key='rule_id'):
    m = {}
    for r in rows:
        k = str(r.get(key, ''))
        if k:
            m[k] = r
    return m


def main() -> None:
    parser = argparse.ArgumentParser(description='Create weekly policy delta for PR review.')
    parser.add_argument('--current', type=Path, default=OUTPUT_ROOT / 'policy_audit_latest.json')
    parser.add_argument('--previous', type=Path, default=OUTPUT_ROOT / 'policy_audit_previous.json')
    parser.add_argument('--out-md', type=Path, default=OUTPUT_ROOT / 'policy_audit_delta_latest.md')
    parser.add_argument('--out-json', type=Path, default=OUTPUT_ROOT / 'policy_audit_delta_latest.json')
    args = parser.parse_args()

    cur = read_json(args.current, {})
    prev = read_json(args.previous, {})

    cur_rules = to_map(cur.get('top_rules', []))
    prev_rules = to_map(prev.get('top_rules', []))

    deltas = []
    keys = set(cur_rules) | set(prev_rules)
    for k in sorted(keys):
        c = int(cur_rules.get(k, {}).get('count', 0))
        p = int(prev_rules.get(k, {}).get('count', 0))
        if c != p:
            deltas.append({'rule_id': k, 'current': c, 'previous': p, 'delta': c - p})

    out = {
        'generated_utc': utc_now(),
        'current_source': str(args.current),
        'previous_source': str(args.previous),
        'rule_count_deltas': sorted(deltas, key=lambda x: abs(x['delta']), reverse=True)[:50],
        'candidate_suppressions': cur.get('candidate_suppressions', []),
        'candidate_always_escalate': cur.get('candidate_always_escalate', []),
    }
    args.out_json.write_text(json.dumps(out, indent=2), encoding='utf-8')

    lines = [
        '# Weekly Policy Audit Delta',
        '',
        f"- Generated UTC: {out['generated_utc']}",
        f"- Current: `{args.current}`",
        f"- Previous: `{args.previous}`",
        '',
        '## Top Rule Count Deltas',
    ]
    if not out['rule_count_deltas']:
        lines.append('- none')
    else:
        for r in out['rule_count_deltas'][:20]:
            lines.append(f"- Rule {r['rule_id']}: prev={r['previous']} curr={r['current']} delta={r['delta']:+}")

    lines.append('')
    lines.append('## Candidate Suppressions')
    if not out['candidate_suppressions']:
        lines.append('- none')
    else:
        for r in out['candidate_suppressions'][:10]:
            lines.append(f"- Rule {r.get('rule_id')} (count={r.get('count')}, max_level={r.get('max_level')})")

    lines.append('')
    lines.append('## Candidate Always-Escalate Adds')
    if not out['candidate_always_escalate']:
        lines.append('- none')
    else:
        for r in out['candidate_always_escalate'][:10]:
            lines.append(f"- Rule {r.get('rule_id')} (count={r.get('count')}, max_level={r.get('max_level')})")

    args.out_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    # roll forward previous snapshot for next run
    args.previous.write_text(json.dumps(cur, indent=2), encoding='utf-8')

    print(f"DELTA_MD={args.out_md}")
    print(f"DELTA_JSON={args.out_json}")
    print(f"DELTA_RULES={len(out['rule_count_deltas'])}")


if __name__ == '__main__':
    main()
