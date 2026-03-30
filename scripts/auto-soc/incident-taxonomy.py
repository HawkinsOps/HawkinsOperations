#!/usr/bin/env python3
import argparse
import json
from collections import Counter
from pathlib import Path

from common import PROCESSED_ROOT, OUTPUT_ROOT, utc_now


def classify(alert: dict) -> str:
    rid = str(alert.get('rule', {}).get('id', ''))
    if rid != '67027':
        return 'not_process_created'
    txt = json.dumps(alert).lower()
    if any(x in txt for x in ['powershell.exe', 'pwsh.exe', 'rundll32.exe', 'regsvr32.exe', 'mshta.exe', 'certutil']):
        return 'lolbin_or_script_engine'
    if 'windows\\system32' in txt or 'program files' in txt:
        return 'likely_signed_system_binary'
    if any(x in txt for x in ['/bin/sh', '/bin/bash', 'cmd.exe /c', ' -enc ', 'base64']):
        return 'suspicious_commandline_pattern'
    return 'other_process_created'


def main() -> None:
    parser = argparse.ArgumentParser(description='Refine process-created taxonomy buckets.')
    parser.add_argument('--max-files', type=int, default=5000)
    parser.add_argument('--out-json', type=Path, default=OUTPUT_ROOT / 'taxonomy_latest.json')
    parser.add_argument('--out-md', type=Path, default=OUTPUT_ROOT / 'taxonomy_latest.md')
    args = parser.parse_args()

    files = sorted(PROCESSED_ROOT.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)[: args.max_files]
    c = Counter()
    for f in files:
        try:
            a = json.loads(f.read_text(encoding='utf-8'))
        except Exception:
            continue
        c[classify(a)] += 1

    out = {
        'generated_utc': utc_now(),
        'source_files': len(files),
        'buckets': dict(c),
    }
    args.out_json.write_text(json.dumps(out, indent=2), encoding='utf-8')
    lines = ['# Incident Taxonomy (Process Created Refinement)', '', f"- Generated UTC: {out['generated_utc']}", f"- Source files: {out['source_files']}", '', '## Buckets']
    for k, v in c.most_common():
        lines.append(f"- {k}: {v}")
    args.out_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"TAXONOMY_JSON={args.out_json}")
    print(f"TAXONOMY_MD={args.out_md}")


if __name__ == '__main__':
    main()
