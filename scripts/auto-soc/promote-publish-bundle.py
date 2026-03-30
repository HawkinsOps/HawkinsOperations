#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path

from common import OUTPUT_ROOT, utc_now


def main() -> None:
    parser = argparse.ArgumentParser(description='Promote publish bundle into curated repo paths.')
    parser.add_argument('--bundle-manifest', type=Path, default=OUTPUT_ROOT / 'publish_bundle_manifest.json')
    parser.add_argument('--repo-root', type=Path, default=Path(r'C:\RH\OPS\10_Portfolio\HawkinsOperations'))
    parser.add_argument('--publish-subdir', type=Path, default=Path('proof/autosoc/latest'))
    parser.add_argument('--execute', action='store_true', help='Apply copies (default dry-run).')
    parser.add_argument('--out-json', type=Path, default=OUTPUT_ROOT / 'promotion_latest.json')
    args = parser.parse_args()

    man = json.loads(args.bundle_manifest.read_text(encoding='utf-8'))
    bundle_dir = Path(man['out_dir'])
    copied = []
    planned = []

    publish_root = args.repo_root / args.publish_subdir
    route = {
        'heartbeat.json': Path('heartbeat.json'),
        'reconciliation_latest.json': Path('reconciliation_latest.json'),
        'reconciliation_latest.md': Path('reconciliation_latest.md'),
        'coverage_latest.json': Path('coverage_latest.json'),
        'coverage_latest.md': Path('coverage_latest.md'),
        'run_metrics_latest.json': Path('run_metrics_latest.json'),
        'policy_audit_latest.json': Path('policy_audit_latest.json'),
        'policy_audit_latest.md': Path('policy_audit_latest.md'),
    }

    for rel in man.get('copied', []):
        src = bundle_dir / rel
        name = Path(rel).name
        if name not in route:
            continue
        dst = publish_root / route[name]
        planned.append({'src': str(src), 'dst': str(dst)})
        if args.execute:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied.append({'src': str(src), 'dst': str(dst)})

    out = {
        'generated_utc': utc_now(),
        'execute': args.execute,
        'manifest': str(args.bundle_manifest),
        'publish_subdir': str(args.publish_subdir),
        'planned': planned,
        'copied': copied,
        'planned_count': len(planned),
        'copied_count': len(copied),
    }
    args.out_json.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f"PROMOTION_JSON={args.out_json}")
    print(f"PLANNED={len(planned)}")
    print(f"COPIED={len(copied)}")


if __name__ == '__main__':
    main()
