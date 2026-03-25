from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

EVENT_BLOCK_RE = re.compile(r"(?s)<Event\b.*?</Event>")


def _get_text(node: ET.Element | None) -> str:
    if node is None or node.text is None:
        return ""
    return node.text.strip()


def parse_event_xml(event_xml: str) -> dict[str, str]:
    event_xml = event_xml.strip()
    root = ET.fromstring(event_xml)
    system = root.find("{*}System")
    event_data = root.find("{*}EventData")

    event_id = ""
    if system is not None:
        event_id = _get_text(system.find("{*}EventID"))

    data_map: dict[str, str] = {}
    if event_data is not None:
        for data in event_data.findall("{*}Data"):
            name = data.attrib.get("Name", "").strip()
            if name:
                data_map[name] = _get_text(data)

    return {
        "EventID": event_id,
        "NewProcessName": data_map.get("NewProcessName", ""),
        "ParentProcessName": data_map.get("ParentProcessName", ""),
        "CommandLine": data_map.get("CommandLine", ""),
    }


def parse_events_from_text(raw_text: str) -> tuple[list[dict[str, str]], int]:
    events: list[dict[str, str]] = []
    errors = 0

    for event_xml in EVENT_BLOCK_RE.findall(raw_text):
        try:
            events.append(parse_event_xml(event_xml))
        except ET.ParseError:
            errors += 1

    return events, errors


def summarize_top_processes(events: list[dict[str, str]], top_n: int = 10) -> list[dict[str, Any]]:
    counts = Counter()
    for ev in events:
        proc = ev.get("NewProcessName", "").strip()
        if proc:
            counts[proc] += 1

    return [{"NewProcessName": name, "count": count} for name, count in counts.most_common(top_n)]


def run_cli() -> int:
    parser = argparse.ArgumentParser(
        description="Parse Windows Security XML events and extract EventID/4688 process fields."
    )
    parser.add_argument("--in", dest="in_path", required=True, help="Path to raw XML event text file")
    parser.add_argument("--out-json", dest="out_json", required=True, help="Destination JSON output path")
    parser.add_argument("--top", type=int, default=10, help="Top N process names for summary table")
    args = parser.parse_args()

    in_path = Path(args.in_path)
    out_path = Path(args.out_json)
    raw_text = in_path.read_text(encoding="utf-8")
    events, parse_errors = parse_events_from_text(raw_text)

    payload = {
        "source_file": str(in_path),
        "total_events_parsed": len(events),
        "parse_errors": parse_errors,
        "events": events,
        "summary": {
            "eventid_4688_count": sum(1 for ev in events if ev.get("EventID") == "4688"),
            "top_process_launches": summarize_top_processes(events, top_n=args.top),
        },
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Parsed events: {len(events)}")
    print(f"Parse errors: {parse_errors}")
    print("Top process launches:")
    for row in payload["summary"]["top_process_launches"]:
        print(f"  {row['count']:>5}  {row['NewProcessName']}")
    print(f"JSON written: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
