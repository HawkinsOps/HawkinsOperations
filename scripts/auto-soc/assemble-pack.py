#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict

from common import utc_now


def get_nested(data: Dict[str, Any], path: str, default: Any = "") -> Any:
    cur = data
    for part in path.split("."):
        if not isinstance(cur, dict):
            return default
        cur = cur.get(part)
        if cur is None:
            return default
    return cur


def sanitize_public_ref(path_value: str, case_dir: Path) -> str:
    value = str(path_value or "").strip()
    if not value:
        return "artifacts/unknown"
    normalized = value.replace("\\", "/")

    # Remove drive prefix for safety.
    normalized = re.sub(r"^[A-Za-z]:/", "", normalized)

    # Remove case directory prefix if present.
    case_norm = str(case_dir).replace("\\", "/").rstrip("/")
    if case_norm and case_norm in normalized:
        normalized = normalized.split(case_norm, 1)[1].lstrip("/")

    filename = Path(normalized).name
    if not filename:
        filename = "unknown"
    return f"artifacts/{filename}"


def assert_no_absolute_paths(pack_dir: Path) -> None:
    leaks = []
    abs_path = re.compile(r"[A-Za-z]:(?:\\|/)")
    for file_path in pack_dir.rglob("*"):
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(text.splitlines(), start=1):
            if abs_path.search(line) or "C:\\RH\\" in line or "C:/RH/" in line:
                leaks.append(f"{file_path}:{i}: {line.strip()}")
                if len(leaks) >= 10:
                    break
        if len(leaks) >= 10:
            break
    if leaks:
        raise RuntimeError(
            "Absolute path leak detected in generated pack output:\n"
            + "\n".join(leaks)
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble report pack from redacted case data.")
    parser.add_argument("--case-dir", type=Path, required=True)
    parser.add_argument("--redacted-dir", type=Path, help="Default: <case-dir>/redacted")
    parser.add_argument("--pack-dir", type=Path, help="Default: <case-dir>/pack")
    args = parser.parse_args()

    case_dir = args.case_dir
    redacted = args.redacted_dir
    if redacted is None:
        report = case_dir / "redaction_report.json"
        if report.exists():
            rpt = json.loads(report.read_text(encoding="utf-8"))
            out = rpt.get("output_dir", "")
            if out:
                redacted = Path(out)
    if redacted is None:
        # Prefer the newest timestamped redaction output when available.
        redacted_dirs = sorted(
            [p for p in case_dir.glob("redacted*") if p.is_dir()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if redacted_dirs:
            redacted = redacted_dirs[0]
    if redacted is None:
        redacted = case_dir / "redacted"
    pack = args.pack_dir or (case_dir / "pack")
    pack.mkdir(parents=True, exist_ok=True)

    triage = json.loads((case_dir / "triage.json").read_text(encoding="utf-8"))
    alert = json.loads((redacted / "alert.raw.json").read_text(encoding="utf-8"))

    case_id = triage["case_id"]
    rule_id = get_nested(alert, "rule.id", "")
    level = get_nested(alert, "rule.level", 0)
    desc = get_nested(alert, "rule.description", "")
    agent = get_nested(alert, "agent.name", "")
    disposition = triage["disposition"]
    redacted_dir_ref = sanitize_public_ref(str(redacted), case_dir)
    alert_ref = sanitize_public_ref(str(redacted / "alert.raw.json"), case_dir)
    triage_ref = sanitize_public_ref(str(case_dir / "triage.json"), case_dir)
    redaction_ref = sanitize_public_ref(str(case_dir / "redaction_report.json"), case_dir)

    (pack / "00_one_pager.md").write_text(
        "\n".join(
            [
                f"# One Pager: {case_id}",
                "",
                f"- Generated UTC: {utc_now()}",
                f"- Agent: {agent}",
                f"- Rule: {rule_id} (Level {level})",
                f"- Disposition: {disposition}",
                f"- Reason: {triage.get('reason','')}",
                "",
                "## Executive Summary",
                f"Alert triaged and processed by AutoSOC. Description: {desc}.",
            ]
        ),
        encoding="utf-8",
    )

    (pack / "01_full_report.md").write_text(
        "\n".join(
            [
                f"# Full Report: {case_id}",
                "",
                "## Detection",
                f"- Rule ID: {rule_id}",
                f"- Level: {level}",
                f"- Description: {desc}",
                "",
                "## Triage Decision",
                f"- Disposition: {disposition}",
                f"- Reason: {triage.get('reason','')}",
                "",
                "## Evidence Paths",
                f"- Redacted source: {redacted_dir_ref}",
                f"- Alert artifact: {alert_ref}",
            ]
        ),
        encoding="utf-8",
    )

    ts = alert.get("@timestamp", utc_now())
    (pack / "02_timeline.csv").write_text(
        f"timestamp_utc,phase,action,evidence_ref,notes\n{ts},triage,disposition,alert.raw.json,{disposition}\n",
        encoding="utf-8",
    )

    (pack / "03_queries.md").write_text(
        "\n".join(
            [
                "# Queries",
                "",
                "## Rule Filter",
                f"- rule.id: {rule_id}",
                "## Agent Filter",
                f"- agent.name: {agent}",
            ]
        ),
        encoding="utf-8",
    )

    (pack / "evidence_index.md").write_text(
        "\n".join(
            [
                "# Evidence Index",
                "",
                f"- alert.raw.json: {alert_ref}",
                f"- triage.json: {triage_ref}",
                f"- redaction_report.json: {redaction_ref}",
            ]
        ),
        encoding="utf-8",
    )

    (pack / "closure_report.md").write_text(
        "\n".join(
            [
                "# Closure Report",
                "",
                f"- Case: {case_id}",
                f"- Status: {'CLOSED' if disposition.startswith('AUTO_CLOSE') else 'ESCALATED'}",
                f"- Disposition: {disposition}",
                f"- Closed UTC: {utc_now()}",
            ]
        ),
        encoding="utf-8",
    )

    assert_no_absolute_paths(pack)

    print(f"PACK_DIR={pack}")
    print("PACK_READY=TRUE")


if __name__ == "__main__":
    main()
