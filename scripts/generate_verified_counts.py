#!/usr/bin/env python3
"""Generate canonical verified-count JSON from PROOF_PACK/VERIFIED_COUNTS.md."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple


@dataclass
class Ref:
    line: int
    heading: str


def parse_verified_counts_md(md_path: Path) -> Tuple[Dict[str, int], Dict[str, Ref]]:
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    heading = ""
    refs: Dict[str, Ref] = {}
    counts: Dict[str, int] = {}

    sigma_re = re.compile(r"\|\s*\*\*Sigma\*\*.*?\|\s*\*\*(\d+)\*\*\s+rules", re.IGNORECASE)
    splunk_re = re.compile(
        r"\|\s*\*\*Splunk\*\*.*?\|\s*\*\*(\d+)\*\*\s+files,\s*\*\*(\d+)\*\*\s+detection searches",
        re.IGNORECASE,
    )
    wazuh_re = re.compile(
        r"\|\s*\*\*Wazuh\*\*.*?\|\s*\*\*(\d+)\*\*\s+files,\s*\*\*(\d+)\*\*\s+rule blocks",
        re.IGNORECASE,
    )
    ir_re = re.compile(
        r"\|\s*\*\*IR Playbooks\*\*.*?\|\s*\*\*(\d+)\*\*\s+playbooks",
        re.IGNORECASE,
    )

    for idx, line in enumerate(lines, start=1):
        if line.startswith("## "):
            heading = line[3:].strip()

        m = sigma_re.search(line)
        if m:
            counts["sigma"] = int(m.group(1))
            refs["sigma"] = Ref(line=idx, heading=heading)
            continue

        m = splunk_re.search(line)
        if m:
            counts["splunk_spl_files"] = int(m.group(1))
            counts["splunk"] = int(m.group(2))
            refs["splunk_spl_files"] = Ref(line=idx, heading=heading)
            refs["splunk"] = Ref(line=idx, heading=heading)
            continue

        m = wazuh_re.search(line)
        if m:
            counts["wazuh_xml_files"] = int(m.group(1))
            counts["wazuh"] = int(m.group(2))
            refs["wazuh_xml_files"] = Ref(line=idx, heading=heading)
            refs["wazuh"] = Ref(line=idx, heading=heading)
            continue

        m = ir_re.search(line)
        if m:
            counts["ir"] = int(m.group(1))
            refs["ir"] = Ref(line=idx, heading=heading)
            continue

    required = ("sigma", "splunk", "splunk_spl_files", "wazuh_xml_files", "wazuh", "ir")
    missing = [k for k in required if k not in counts]
    if missing:
        raise ValueError(
            "Could not parse required counts from markdown. Missing keys: "
            + ", ".join(missing)
        )

    counts["detections"] = counts["sigma"] + counts["splunk"] + counts["wazuh"]
    refs["detections"] = refs["wazuh"]
    return counts, refs


def build_payload(md_path: Path) -> dict:
    counts, refs = parse_verified_counts_md(md_path)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "generated_at_utc": generated_at,
        "source_path": "PROOF_PACK/VERIFIED_COUNTS.md",
        "counts": counts,
        "source_refs": {
            key: {
                "file": "PROOF_PACK/VERIFIED_COUNTS.md",
                "line": ref.line,
                "heading": ref.heading,
            }
            for key, ref in refs.items()
        },
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def update_detection_counts(path: Path, counts: Dict[str, int]) -> None:
    if not path.exists():
        return

    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("detections")
    if not isinstance(rows, list):
        return

    id_to_key = {
        "sigma": "sigma",
        "wazuh": "wazuh",
        "splunk": "splunk",
        "ir-playbooks": "ir",
    }
    changed = False
    for row in rows:
        row_id = row.get("id")
        key = id_to_key.get(row_id)
        if not key:
            continue
        value = counts[key]
        if row.get("count") != value:
            row["count"] = value
            changed = True

    if changed:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="PROOF_PACK/VERIFIED_COUNTS.md",
        help="Input markdown path.",
    )
    parser.add_argument(
        "--output",
        default="PROOF_PACK/verified_counts.json",
        help="Canonical output JSON path.",
    )
    parser.add_argument(
        "--site-output",
        default="site/assets/verified-counts.json",
        help="Site-consumed output JSON path.",
    )
    parser.add_argument(
        "--sync-detections-json",
        default="site/assets/data/detections.json",
        help="Update detection summary counts in this file if present.",
    )
    args = parser.parse_args()

    md_path = Path(args.input)
    if not md_path.exists():
        raise SystemExit(f"Input file not found: {md_path}")

    payload = build_payload(md_path)
    write_json(Path(args.output), payload)
    write_json(Path(args.site_output), payload)
    update_detection_counts(Path(args.sync_detections_json), payload["counts"])

    print(f"Wrote {args.output}")
    print(f"Wrote {args.site_output}")
    print(f"Synced {args.sync_detections_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
