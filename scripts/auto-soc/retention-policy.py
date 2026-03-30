#!/usr/bin/env python3
import argparse
import json
import shutil
import time
from pathlib import Path

from common import CASES_ROOT, OUTPUT_ROOT, utc_now


def main() -> None:
    parser = argparse.ArgumentParser(description="Retention policy for non-escalate case artifacts.")
    parser.add_argument("--days", type=int, default=14, help="Age threshold in days")
    parser.add_argument("--execute", action="store_true", help="Apply retention actions")
    parser.add_argument("--archive-dir", type=Path, default=OUTPUT_ROOT / "retention_archive")
    parser.add_argument("--report", type=Path, default=OUTPUT_ROOT / "retention_latest.json")
    args = parser.parse_args()

    cutoff = time.time() - (max(1, args.days) * 86400)
    scanned = 0
    candidates = []

    for case_dir in CASES_ROOT.iterdir():
        if not case_dir.is_dir():
            continue
        scanned += 1
        triage = case_dir / "triage.json"
        if not triage.exists():
            continue
        try:
            data = json.loads(triage.read_text(encoding="utf-8"))
        except Exception:
            continue
        disp = str(data.get("disposition", "")).upper()
        if disp == "ESCALATE":
            continue
        if case_dir.stat().st_mtime >= cutoff:
            continue
        candidates.append(case_dir)

    moved = 0
    if args.execute:
        args.archive_dir.mkdir(parents=True, exist_ok=True)
        for src in candidates:
            dst = args.archive_dir / src.name
            if dst.exists():
                continue
            shutil.move(str(src), str(dst))
            moved += 1

    report = {
        "generated_utc": utc_now(),
        "days": args.days,
        "execute": args.execute,
        "scanned_cases": scanned,
        "candidates": len(candidates),
        "moved": moved,
        "archive_dir": str(args.archive_dir),
    }
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"RETENTION_REPORT={args.report}")
    print(f"CANDIDATES={len(candidates)}")
    print(f"MOVED={moved}")


if __name__ == "__main__":
    main()
