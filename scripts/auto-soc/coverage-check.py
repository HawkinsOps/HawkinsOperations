#!/usr/bin/env python3
import argparse
import glob
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Set

from common import AGENT_INVENTORY_PATH, OUTPUT_ROOT, PROCESSED_ROOT, read_json, utc_now, write_json

# Legacy token remaps observed in historical alerts.
# These normalize prior host labels to current canonical inventory hostnames.
LEGACY_TOKEN_HOST_MAP = {
    "howe01": "ho-we-01",
    "ho-sr-01": "ho-runner-01",
    "ho-sr-wm-01": "ho-wazuh-01",
}

PROCESSED_HOST_CANDIDATE_FIELDS = [
    "agent.name",
    "agent.hostname",
    "host.hostname",
    "manager.name",
    "location",
]


def norm(value: str) -> str:
    s = str(value or "").strip().lower()
    if "." in s:
        s = s.split(".", 1)[0]
    return s.replace("_", "-")


def alias_set(hostname: str) -> Set[str]:
    c = norm(hostname)
    aliases = {c}
    if c.endswith("-01"):
        aliases.add(c[:-3])
    aliases.add(c.replace("-", "_"))
    return {a for a in aliases if a}


def host_aliases(hostname: str, explicit_aliases: list[str]) -> Set[str]:
    aliases = set(alias_set(hostname))
    for raw in explicit_aliases or []:
        n = norm(raw)
        if n:
            aliases.add(n)
    return aliases


def build_required_hosts(inv: dict) -> Dict[str, Set[str]]:
    required: Dict[str, Set[str]] = {}
    policy = inv.get("coverage_policy", {}) if isinstance(inv, dict) else {}
    include_hosts = {
        norm(x) for x in policy.get("include_in_required_coverage", []) if str(x).strip()
    }
    exclude_hosts = {
        norm(x) for x in policy.get("exclude_from_required_coverage", []) if str(x).strip()
    }

    def add_host(hostname: str, explicit_aliases: list[str]) -> None:
        h = str(hostname or "").strip()
        if not h:
            return
        hn = norm(h)
        if hn in exclude_hosts:
            return
        if include_hosts and hn not in include_hosts:
            return
        required[h] = host_aliases(h, explicit_aliases)

    for vm in inv.get("vms", []):
        add_host(vm.get("hostname", ""), vm.get("aliases", []) if isinstance(vm, dict) else [])

    for ep in inv.get("endpoints", []):
        if not isinstance(ep, dict):
            continue
        if not bool(ep.get("coverage_required", True)):
            continue
        add_host(ep.get("hostname", ""), ep.get("aliases", []))

    return required


def parse_ts(raw: str) -> datetime:
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check machine coverage in recent AutoSOC processed alerts.")
    parser.add_argument("--window-hours", type=int, default=168, help="Lookback window in hours (default 168 = 7 days).")
    args = parser.parse_args()

    inv = read_json(AGENT_INVENTORY_PATH, {"vms": []})
    required = build_required_hosts(inv)
    host_norm_to_canonical: Dict[str, str] = {norm(h): h for h in required}

    applied_legacy_mappings: Dict[str, str] = {}
    for token, target_host_norm in LEGACY_TOKEN_HOST_MAP.items():
        target_canonical = host_norm_to_canonical.get(norm(target_host_norm))
        if target_canonical:
            required[target_canonical].add(norm(token))
            applied_legacy_mappings[norm(token)] = target_canonical

    cutoff = datetime.now(timezone.utc) - timedelta(hours=args.window_hours)
    seen = Counter()
    seen_raw = Counter()
    host_hits = Counter()
    field_non_empty_counts = Counter()
    field_token_counts: dict[str, Counter] = {
        field: Counter() for field in PROCESSED_HOST_CANDIDATE_FIELDS
    }
    scanned = 0
    for p in glob.glob(str(PROCESSED_ROOT / "*.json")):
        scanned += 1
        try:
            a = json.loads(Path(p).read_text(encoding="utf-8"))
        except Exception:
            continue
        ts = parse_ts(a.get("@timestamp", ""))
        if ts < cutoff:
            continue
        candidates_by_field = {
            "agent.name": str(a.get("agent", {}).get("name", "")),
            "agent.hostname": str(a.get("agent", {}).get("hostname", "")),
            "host.hostname": str(a.get("host", {}).get("hostname", "")),
            "manager.name": str(a.get("manager", {}).get("name", "")),
            "location": str(a.get("location", "")),
        }
        normalized = []
        for field in PROCESSED_HOST_CANDIDATE_FIELDS:
            raw = candidates_by_field.get(field, "")
            n = norm(raw)
            if not n:
                continue
            normalized.append(n)
            seen[n] += 1
            seen_raw[raw] += 1
            field_non_empty_counts[field] += 1
            field_token_counts[field][n] += 1
        if not normalized:
            continue
        for host, aliases in required.items():
            if any(n in aliases for n in normalized):
                host_hits[host] += 1

    missing = []
    present = []
    for host, aliases in required.items():
        hits = int(host_hits.get(host, 0))
        entry = {"hostname": host, "aliases": sorted(aliases), "recent_hits": hits}
        if hits > 0:
            present.append(entry)
        else:
            missing.append(entry)

    report = {
        "generated_utc": utc_now(),
        "window_hours": args.window_hours,
        "coverage_basis": {
            "source": "processed_queue",
            "processed_root": str(PROCESSED_ROOT),
            "timestamp_field": "@timestamp",
            "cutoff_utc": cutoff.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "host_candidate_fields": PROCESSED_HOST_CANDIDATE_FIELDS,
            "matching": "normalized exact token match against canonical host + aliases + LEGACY_TOKEN_HOST_MAP",
        },
        "processed_files_scanned": scanned,
        "required_hosts": len(required),
        "present_hosts": len(present),
        "missing_hosts": len(missing),
        "required_coverage_percent": round((len(present) / len(required) * 100.0), 2) if required else 100.0,
        "present": sorted(present, key=lambda x: x["hostname"].lower()),
        "missing": sorted(missing, key=lambda x: x["hostname"].lower()),
        "legacy_token_host_map_applied": applied_legacy_mappings,
        "top_seen_agent_tokens": seen.most_common(20),
        "field_diagnostics": {
            "field_non_empty_counts": {
                field: int(field_non_empty_counts.get(field, 0))
                for field in PROCESSED_HOST_CANDIDATE_FIELDS
            },
            "top_tokens_by_field": {
                field: counts.most_common(10)
                for field, counts in field_token_counts.items()
            },
        },
    }

    json_path = OUTPUT_ROOT / "coverage_latest.json"
    md_path = OUTPUT_ROOT / "coverage_latest.md"
    write_json(json_path, report)

    lines = [
        "# AutoSOC Coverage Check",
        "",
        f"- Generated UTC: {report['generated_utc']}",
        f"- Window hours: {report['window_hours']}",
        f"- Coverage source: {report['coverage_basis']['source']}",
        f"- Processed root: {report['coverage_basis']['processed_root']}",
        f"- Cutoff UTC: {report['coverage_basis']['cutoff_utc']}",
        f"- Host candidate fields: {', '.join(report['coverage_basis']['host_candidate_fields'])}",
        f"- Processed files scanned: {report['processed_files_scanned']}",
        f"- Required hosts: {report['required_hosts']}",
        f"- Present hosts: {report['present_hosts']}",
        f"- Missing hosts: {report['missing_hosts']}",
        f"- Required coverage: {report['required_coverage_percent']}%",
        "",
        "## Field Diagnostics",
    ]
    for field in PROCESSED_HOST_CANDIDATE_FIELDS:
        lines.append(f"- {field}: non_empty={report['field_diagnostics']['field_non_empty_counts'][field]}")
    lines.extend([
        "",
        "## Missing Hosts",
    ])
    if missing:
        for m in missing:
            lines.append(f"- {m['hostname']} (aliases: {', '.join(m['aliases'])})")
    else:
        lines.append("- none")
    lines.extend(["", "## Present Hosts"])
    if present:
        for p in present:
            lines.append(f"- {p['hostname']} (recent_hits={p['recent_hits']})")
    else:
        lines.append("- none")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"COVERAGE_JSON={json_path}")
    print(f"COVERAGE_MD={md_path}")
    print(f"MISSING_HOSTS={report['missing_hosts']}")


if __name__ == "__main__":
    main()
