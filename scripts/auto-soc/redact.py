#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict

from common import CASES_ROOT, utc_now


TEXT_EXTS = {".md", ".txt", ".json", ".csv", ".log", ".yaml", ".yml", ".xml", ".ps1", ".sh"}

# Redacted output lives outside the case directory so repeat runs never see
# prior output as new input. Per-case path: REDACTED_ROOT/<case_name>/redacted.
# Override with AUTOSOC_REDACTED (consistent with other AUTOSOC_* env vars in
# common.py). Default parallels CASES_ROOT as a sibling tree.
REDACTED_ROOT = Path(os.getenv("AUTOSOC_REDACTED", str(CASES_ROOT.parent / "Cases_Redacted")))


def default_out_dir(case_dir: Path) -> Path:
    return REDACTED_ROOT / case_dir.name / "redacted"

REPLACEMENTS = {
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"): "[REDACTED_IP]",
    re.compile(r"\b[A-Za-z]:(?:\\|/)+[^\s,\"']+"): "[REDACTED_PATH]",
    re.compile(r"\b(?:HO-[A-Za-z0-9-]+)\b", re.IGNORECASE): "[REDACTED_HOST]",
    re.compile(r"\b(?:raylee|rayleeadmin)\b", re.IGNORECASE): "[REDACTED_USER]",
    re.compile(r"\b(?:[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b"): "[REDACTED_EMAIL]",
}


def redact_text(text: str) -> str:
    out = text
    for pattern, repl in REPLACEMENTS.items():
        out = pattern.sub(repl, out)
    return out


def _redact_json_value(obj):
    """Walk a parsed JSON structure and redact all string values."""
    if isinstance(obj, str):
        return redact_text(obj)
    if isinstance(obj, list):
        return [_redact_json_value(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _redact_json_value(v) for k, v in obj.items()}
    return obj


def redact_json_file(raw: str) -> str:
    """Parse JSON, redact string values, re-serialize.

    Operating on parsed values avoids breaking JSON escape sequences
    (e.g. ``\\"`` inside paths) that raw regex replacement can corrupt.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback to raw text redaction if JSON is already malformed.
        return redact_text(raw)
    return json.dumps(_redact_json_value(data), indent=2, ensure_ascii=False)


def copy_and_redact(case_dir: Path, out_dir: Path) -> tuple[Dict[str, int], Path]:
    stats = {"files_total": 0, "files_text": 0, "files_binary": 0}
    # Output path is now deterministic per case. If an output dir from a prior
    # run exists, delete it and rewrite: redaction content is idempotent, and
    # overwrite cleanly handles partial-failure state from aborted prior runs.
    # This replaces the previous timestamp-suffix collision scheme, which
    # caused redacted_<ts>/ siblings to accumulate inside case_dir and be
    # re-ingested by subsequent rglob walks (incident 2026-04-18).
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for src in case_dir.rglob("*"):
        if src == out_dir or out_dir in src.parents:
            continue
        rel = src.relative_to(case_dir)
        dst = out_dir / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue

        stats["files_total"] += 1
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in TEXT_EXTS:
            stats["files_text"] += 1
            raw = src.read_text(encoding="utf-8", errors="ignore")
            if src.suffix.lower() == ".json":
                dst.write_text(redact_json_file(raw), encoding="utf-8")
            else:
                dst.write_text(redact_text(raw), encoding="utf-8")
        else:
            stats["files_binary"] += 1
            shutil.copy2(src, dst)
    return stats, out_dir


def fails_post_redaction(out_dir: Path) -> bool:
    forbidden = [
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        re.compile(r"\b[A-Za-z]:(?:\\|/)+[^\s,\"']+"),
        re.compile(r"\b(?:raylee|rayleeadmin)\b", re.IGNORECASE),
    ]
    for p in out_dir.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXTS:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for f in forbidden:
            if f.search(text):
                return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Redact case data before assembly/publish.")
    parser.add_argument("--case-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, help="Default: <Cases_Redacted>/<case-name>/redacted (AUTOSOC_REDACTED overrides root)")
    args = parser.parse_args()

    case_dir = args.case_dir
    out_dir = args.output_dir or default_out_dir(case_dir)
    stats, final_out_dir = copy_and_redact(case_dir, out_dir)
    failed = fails_post_redaction(final_out_dir)

    report = {
        "generated_utc": utc_now(),
        "case_dir": str(case_dir),
        "output_dir": str(final_out_dir),
        "stats": stats,
        "pass": not failed,
    }
    (case_dir / "redaction_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"REDACTION_PASS={str(not failed).upper()}")
    print(f"OUTPUT={final_out_dir}")
    if failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
