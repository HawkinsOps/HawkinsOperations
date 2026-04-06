#!/usr/bin/env python3
import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from common import (
    AGENT_INVENTORY_PATH,
    CASES_ROOT,
    KNOWN_FPS_PATH,
    LEDGER_PATH,
    POLICY_PATH,
    PROCESSED_ROOT,
    QUEUE_ROOT,
    ensure_dirs,
    load_ledger,
    load_yaml_json,
    save_ledger,
    slugify,
    utc_now,
)


def get_nested(data: Dict[str, Any], path: str, default: Any = "") -> Any:
    cur = data
    for p in path.split("."):
        if not isinstance(cur, dict):
            return default
        cur = cur.get(p)
        if cur is None:
            return default
    return cur


def load_policy() -> Dict[str, Any]:
    default = {
        "thresholds": {
            "auto_close_benign_max_level": 3,
            "auto_close_known_fp_max_level": 13,
            "escalate_min_level": 12,
            "protected_agent_min_level_escalate": 7,
        },
        "always_escalate_rule_ids": ["100053"],
        "always_escalate_groups": ["rootkit", "malware", "ransomware", "data_exfiltration", "sql_injection"],
        "protected_agents": ["HO-SR-01", "HO-Wazuh-01", "ho-sr-01", "ho-sr-wm-01"],
        "auto_close_rule_ids": ["67027", "60118", "67023", "60642", "5501", "5502"],
        "review_rule_ids": [
            "202",
            "203",
            "204",
            "533",
            "553",
            "554",
            "5710",
            "594",
            "750",
            "752",
            "2902",
            "2904",
            "60104",
            "60132",
            "60227",
            "60702",
            "60789",
            "61102",
            "92151",
            "92153",
            "19004",
            "19005",
            "19007",
            "19014",
            "23503",
            "23504",
            "23505",
            "40704",
        ],
        "rule_overrides": [
            {
                "rule_ids": ["60227"],
                "agent_names": ["HOWE01", "HO-WE-01", "win-hawkinsops"],
                "provider_names": ["Microsoft-Windows-Security-Auditing"],
                "contains_any": [
                    "HP DeskJet 2800 series",
                    "HP0E6B66",
                    "CR270QB",
                    "AMD High Definition Audio Device",
                    "Bluetooth LE Generic Attribute Service",
                    "Generic Access Profile",
                    "Device Information Service",
                    "Bluetooth Low Energy GATT compliant HID device",
                    "Avrcp Transport",
                    "JL_SPP",
                    "iPhone",
                    "Generic Attribute Profile",
                    "Standard Serial over Bluetooth link",
                    "Service Discovery Service",
                    "Wireless iAP",
                    "MMDEVAPI",
                    "PRINTENUM",
                    "DAFWSDProvider",
                    "WSDPrintDevice",
                    "PrintQueue",
                    "Microsoft Print to PDF",
                    "Generic Monitor",
                ],
                "disposition": "AUTO_CLOSE_KNOWN_FP",
                "reason": "Known workstation external-device churn from monitor, audio endpoint, and printer enumeration",
            },
            {
                "rule_ids": ["60104"],
                "agent_names": ["HOWE01", "HO-WE-01", "win-hawkinsops"],
                "provider_names": ["Microsoft-Windows-Security-Auditing"],
                "contains_all": ["Microsoft Software Key Storage Provider", "Key2WrapEncryptionKey", "0x80090016"],
                "disposition": "AUTO_CLOSE_KNOWN_FP",
                "reason": "Known Windows key-storage open-key failure noise on workstation",
            },
            {
                "rule_ids": ["61102"],
                "agent_names": ["HOWE01", "HO-WE-01", "win-hawkinsops"],
                "provider_names": ["Microsoft-Windows-DistributedCOM"],
                "contains_all": ["2147942403"],
                "contains_any": [
                    "LinkedIn\\\\LinkedIn.exe",
                    "HPPrinterControl",
                    "HPPrinterDriver",
                ],
                "disposition": "AUTO_CLOSE_KNOWN_FP",
                "reason": "Known workstation DCOM app-launch noise from LinkedIn and HP printer Windows apps",
            },
            {
                "rule_ids": ["2902"],
                "agent_names": ["HO-HONEYPOT-01", "ho-fs-01"],
                "locations": ["/var/log/dpkg.log"],
                "contains_any": ["status installed"],
                "disposition": "AUTO_CLOSE_KNOWN_FP",
                "reason": "Known package installation churn during routine apt/dpkg maintenance on Linux hosts",
            },
            {
                "rule_ids": ["2904"],
                "agent_names": ["HO-HONEYPOT-01", "ho-fs-01"],
                "locations": ["/var/log/dpkg.log"],
                "contains_any": ["status half-configured"],
                "disposition": "AUTO_CLOSE_KNOWN_FP",
                "reason": "Known transient dpkg half-configured churn during routine apt/dpkg maintenance on Linux hosts",
            }
        ],
        "sysmon": {
            "escalate_event_ids": [1, 3, 10],
            "require_sysmon_source": True,
            "source_markers": ["sysmon", "microsoft-windows-sysmon"],
            "tiering": {
                "enabled": True,
                "event_dispositions": {
                    "1": "REVIEW",
                    "3": "REVIEW",
                    "10": "ESCALATE",
                },
                "event3_high_risk_contains_any": [
                    "rundll32.exe",
                    "regsvr32.exe",
                    "mshta.exe",
                    "powershell.exe",
                    "pwsh.exe",
                    "certutil.exe",
                    "bitsadmin",
                ],
            },
            "suppressions": [
                {
                    "rule_ids": ["92151"],
                    "agent_names": ["HOWE01", "HO-WE-01", "win-hawkinsops"],
                    "contains_any": ["\\program files\\powershell\\7\\pwsh.exe"],
                    "reason": "Known PowerShell 7 automation host module-load noise on workstation",
                },
                {
                    "rule_ids": ["92153"],
                    "agent_names": ["HOWE01", "HO-WE-01", "win-hawkinsops"],
                    "contains_any": [
                        "\\windows\\system32\\backgroundtaskhost.exe",
                        "\\windows\\system32\\taskhostw.exe",
                        "\\windows\\system32\\svchost.exe",
                        "\\windows\\system32\\runtimebroker.exe",
                        "\\windows\\uus\\packages\\preview\\amd64\\mousocoreworker.exe",
                    ],
                    "reason": "Known Windows service-host VaultCli module-load noise on workstation",
                },
            ],
        },
        "defaults": {"disposition": "ESCALATE"},
    }
    return load_yaml_json(POLICY_PATH, default)


def load_known_fps() -> List[Dict[str, Any]]:
    data = load_yaml_json(KNOWN_FPS_PATH, {"rules": []})
    return data.get("rules", [])


def normalize_agent_value(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    v = raw.lower()
    if "." in v:
        v = v.split(".", 1)[0]
    return v


def load_agent_alias_map() -> Dict[str, str]:
    default: Dict[str, str] = {}
    data = load_yaml_json(AGENT_INVENTORY_PATH, {"vms": []})
    for vm in data.get("vms", []):
        hostname = str(vm.get("hostname", "")).strip()
        if not hostname:
            continue
        canonical = normalize_agent_value(hostname)
        aliases = {
            canonical,
            canonical.replace("_", "-"),
            canonical.replace("-", "_"),
        }
        if canonical.endswith("-01"):
            aliases.add(canonical[:-3])
        for alias in aliases:
            if alias:
                default[alias] = canonical
    return default


def extract_agent_name(alert: Dict[str, Any], alias_map: Dict[str, str]) -> str:
    candidates = [
        str(get_nested(alert, "agent.name", "")),
        str(get_nested(alert, "agent.hostname", "")),
        str(get_nested(alert, "host.hostname", "")),
        str(get_nested(alert, "manager.name", "")),
    ]
    location = str(get_nested(alert, "location", ""))
    if location:
        candidates.append(location)
    for raw in candidates:
        n = normalize_agent_value(raw)
        if not n:
            continue
        if n in alias_map:
            return alias_map[n]
        for token in re.split(r"[^a-z0-9._-]+", n):
            t = normalize_agent_value(token)
            if t in alias_map:
                return alias_map[t]
        return n
    return "unknown-agent"


def match_known_fp(alert: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[bool, str]:
    rule_id = str(get_nested(alert, "rule.id", ""))
    agent = str(get_nested(alert, "_autosoc.agent", "") or get_nested(alert, "agent.name", ""))
    haystack = json.dumps(alert).lower()
    for r in rules:
        rid = str(r.get("rule_id", ""))
        if rid and rid != rule_id:
            continue
        expected_agent = str(r.get("agent", ""))
        if expected_agent and expected_agent.lower() != agent.lower():
            continue
        contains = str(r.get("contains", "")).lower()
        if contains and contains not in haystack:
            continue
        return True, str(r.get("reason", "known false positive"))
    return False, ""


def determine_disposition(alert: Dict[str, Any], policy: Dict[str, Any], known_fps: List[Dict[str, Any]]) -> Tuple[str, str]:
    level = int(get_nested(alert, "rule.level", 0) or 0)
    rule_id = str(get_nested(alert, "rule.id", ""))
    agent = str(get_nested(alert, "_autosoc.agent", "") or get_nested(alert, "agent.name", ""))
    groups = get_nested(alert, "rule.groups", [])
    if isinstance(groups, str):
        groups = [g.strip() for g in groups.split(",") if g.strip()]
    groups_lower = {str(g).lower() for g in groups}

    is_fp, reason = match_known_fp(alert, known_fps)
    if is_fp:
        return "AUTO_CLOSE_KNOWN_FP", reason

    t = policy.get("thresholds", {})
    always_escalate_ids = {str(x) for x in policy.get("always_escalate_rule_ids", [])}
    always_escalate_groups = {str(x).lower() for x in policy.get("always_escalate_groups", [])}
    protected_agents = {str(x).lower() for x in policy.get("protected_agents", [])}
    auto_close_rule_ids = {str(x) for x in policy.get("auto_close_rule_ids", [])}
    review_rule_ids = {str(x) for x in policy.get("review_rule_ids", [])}
    rule_overrides = policy.get("rule_overrides", [])
    sysmon_cfg = policy.get("sysmon", {})
    sysmon_escalate_event_ids = {int(x) for x in sysmon_cfg.get("escalate_event_ids", [])}
    require_sysmon_source = bool(sysmon_cfg.get("require_sysmon_source", True))
    sysmon_markers = {str(x).lower() for x in sysmon_cfg.get("source_markers", ["sysmon", "microsoft-windows-sysmon"])}
    sysmon_suppressions = sysmon_cfg.get("suppressions", [])
    sysmon_tiering = sysmon_cfg.get("tiering", {})
    sysmon_tiering_enabled = bool(sysmon_tiering.get("enabled", False))
    sysmon_event_dispositions = {
        str(k): str(v).upper() for k, v in dict(sysmon_tiering.get("event_dispositions", {})).items()
    }
    event3_high_risk_contains_any = [
        str(x).lower() for x in sysmon_tiering.get("event3_high_risk_contains_any", []) if str(x).strip()
    ]

    def extract_sysmon_event_id(a: Dict[str, Any]) -> int:
        candidates = [
            get_nested(a, "data.win.system.eventID", ""),
            get_nested(a, "data.win.system.event_id", ""),
            get_nested(a, "data.win.eventdata.eventID", ""),
            get_nested(a, "win.system.eventID", ""),
            get_nested(a, "event_id", ""),
        ]
        for raw in candidates:
            if raw == "":
                continue
            try:
                return int(str(raw).strip())
            except ValueError:
                continue
        return 0

    def is_sysmon_source(a: Dict[str, Any]) -> bool:
        source_fields = [
            str(get_nested(a, "data.win.system.providerName", "")),
            str(get_nested(a, "data.win.system.channel", "")),
            str(get_nested(a, "location", "")),
            str(get_nested(a, "decoder.name", "")),
            str(get_nested(a, "rule.description", "")),
        ]
        hay = " ".join(source_fields).lower()
        if any(m in hay for m in sysmon_markers):
            return True
        if "sysmon" in groups_lower:
            return True
        return False

    def alert_haystack(a: Dict[str, Any]) -> str:
        return json.dumps(a).lower().replace("\\\\", "\\")

    def text_conditions_match(a: Dict[str, Any], contains_any: List[Any], contains_all: List[Any]) -> bool:
        haystack = alert_haystack(a)
        any_fragments = [str(x).lower().replace("\\\\", "\\") for x in contains_any if str(x).strip()]
        all_fragments = [str(x).lower().replace("\\\\", "\\") for x in contains_all if str(x).strip()]
        if any_fragments and not any(fragment in haystack for fragment in any_fragments):
            return False
        if all_fragments and not all(fragment in haystack for fragment in all_fragments):
            return False
        return True

    def normalize_rule_id(v: Any) -> str:
        raw = str(v).strip()
        digits = re.sub(r"\D+", "", raw)
        return digits if digits else raw.lower()

    def suppression_matches(s: Dict[str, Any], a: Dict[str, Any], sysmon_event_id: int) -> bool:
        def normalize_rule_id(v: Any) -> str:
            raw = str(v).strip()
            digits = re.sub(r"\D+", "", raw)
            return digits if digits else raw.lower()

        suppression_rule_ids = {normalize_rule_id(x) for x in s.get("rule_ids", [])}
        if suppression_rule_ids and normalize_rule_id(rule_id) not in suppression_rule_ids:
            return False

        suppression_event_ids = set()
        for x in s.get("event_ids", []):
            try:
                suppression_event_ids.add(int(x))
            except (TypeError, ValueError):
                continue
        if suppression_event_ids and sysmon_event_id not in suppression_event_ids:
            return False

        suppression_agents = {str(x).lower() for x in s.get("agent_names", [])}
        if suppression_agents and agent.lower() not in suppression_agents:
            return False

        if not text_conditions_match(a, s.get("contains_any", []), s.get("contains_all", [])):
            return False

        return True

    def override_matches(o: Dict[str, Any], a: Dict[str, Any]) -> bool:
        override_rule_ids = {normalize_rule_id(x) for x in o.get("rule_ids", [])}
        if override_rule_ids and normalize_rule_id(rule_id) not in override_rule_ids:
            return False

        override_agents = {normalize_agent_value(x) for x in o.get("agent_names", [])}
        if override_agents and normalize_agent_value(agent) not in override_agents:
            return False

        override_locations = {str(x).lower() for x in o.get("locations", [])}
        if override_locations:
            location = str(get_nested(a, "location", "")).lower()
            if location not in override_locations:
                return False

        override_provider_names = {str(x).lower() for x in o.get("provider_names", [])}
        if override_provider_names:
            provider = str(get_nested(a, "data.win.system.providerName", "")).lower()
            if provider not in override_provider_names:
                return False

        min_level = o.get("min_level")
        if min_level is not None and level < int(min_level):
            return False
        max_level = o.get("max_level")
        if max_level is not None and level > int(max_level):
            return False

        if not text_conditions_match(a, o.get("contains_any", []), o.get("contains_all", [])):
            return False

        return True

    if rule_id in always_escalate_ids:
        return "ESCALATE", "rule in always_escalate_rule_ids"
    if groups_lower.intersection(always_escalate_groups):
        return "ESCALATE", "rule group in always_escalate_groups"
    for override in rule_overrides:
        if override_matches(override, alert):
            disposition = str(override.get("disposition", "")).upper()
            reason = str(override.get("reason", "")).strip() or "rule override match"
            if disposition in {"ESCALATE", "REVIEW", "AUTO_CLOSE_BENIGN", "AUTO_CLOSE_KNOWN_FP"}:
                return disposition, reason
    sysmon_event_id = extract_sysmon_event_id(alert)
    for suppression in sysmon_suppressions:
        if suppression_matches(suppression, alert, sysmon_event_id):
            reason = str(suppression.get("reason", "sysmon suppression match"))
            return "AUTO_CLOSE_KNOWN_FP", reason
    if sysmon_tiering_enabled and is_sysmon_source(alert) and sysmon_event_id > 0:
        event_disp = sysmon_event_dispositions.get(str(sysmon_event_id), "").upper()
        if sysmon_event_id == 3 and event_disp == "REVIEW":
            haystack = json.dumps(alert).lower()
            if any(fragment in haystack for fragment in event3_high_risk_contains_any):
                return "ESCALATE", "sysmon event_id 3 high-risk image fragment match"
        if event_disp in {"ESCALATE", "REVIEW", "AUTO_CLOSE_BENIGN", "AUTO_CLOSE_KNOWN_FP"}:
            return event_disp, f"sysmon tiering event_id {sysmon_event_id} -> {event_disp}"
    if sysmon_event_id in sysmon_escalate_event_ids:
        if (not require_sysmon_source) or is_sysmon_source(alert):
            return "ESCALATE", f"sysmon event_id {sysmon_event_id} in sysmon.escalate_event_ids"
    if rule_id in review_rule_ids:
        return "REVIEW", "rule in review_rule_ids"
    if agent.lower() in protected_agents and level >= int(t.get("protected_agent_min_level_escalate", 7)):
        return "ESCALATE", "protected agent level threshold"
    if rule_id in auto_close_rule_ids:
        return "AUTO_CLOSE_BENIGN", "rule in auto_close_rule_ids"

    if level <= int(t.get("auto_close_benign_max_level", 5)):
        return "AUTO_CLOSE_BENIGN", "below benign threshold"
    if level >= int(t.get("escalate_min_level", 10)):
        return "ESCALATE", "level meets escalation threshold"
    return policy.get("defaults", {}).get("disposition", "ESCALATE"), "policy default"


def make_case_id(alert: Dict[str, Any]) -> str:
    ts_raw = str(alert.get("@timestamp", utc_now()))
    try:
        dt = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
    except ValueError:
        dt = datetime.utcnow()
    date_part = dt.strftime("%Y-%m-%d")
    agent = str(get_nested(alert, "_autosoc.agent", "") or get_nested(alert, "agent.name", "unknown-agent"))
    rule_id = str(get_nested(alert, "rule.id", "unknown-rule"))
    alert_id = str(alert.get("id", "") or get_nested(alert, "_indexer_meta._id", "") or "")
    suffix = slugify(alert_id)[:20] if alert_id else ""
    base = f"{date_part}_{slugify(agent)}_r{rule_id}"
    return f"{base}_{suffix}" if suffix else base


def update_metrics(ledger: Dict[str, Any], disposition: str) -> None:
    metrics = ledger.setdefault("metrics", {})
    metrics["total_cases"] = int(metrics.get("total_cases", 0)) + 1
    if disposition == "AUTO_CLOSE_BENIGN":
        metrics["auto_closed_benign"] = int(metrics.get("auto_closed_benign", 0)) + 1
    elif disposition == "AUTO_CLOSE_KNOWN_FP":
        metrics["auto_closed_known_fp"] = int(metrics.get("auto_closed_known_fp", 0)) + 1
    elif disposition == "ESCALATE":
        metrics["escalated"] = int(metrics.get("escalated", 0)) + 1
    elif disposition == "REVIEW":
        metrics["review"] = int(metrics.get("review", 0)) + 1


def case_exists(ledger: Dict[str, Any], case_id: str) -> bool:
    return any(c.get("case_id") == case_id for c in ledger.get("cases", []))


def main() -> None:
    parser = argparse.ArgumentParser(description="Triage queued AutoSOC alerts.")
    parser.add_argument("--max-alerts", type=int, default=200)
    args = parser.parse_args()

    ensure_dirs()
    policy = load_policy()
    known_fps = load_known_fps()
    alias_map = load_agent_alias_map()
    ledger = load_ledger()

    queue_files = sorted(p for p in QUEUE_ROOT.glob("*.json") if p.name != ".cursor.json")[: args.max_alerts]
    processed = 0
    for alert_path in queue_files:
        alert = json.loads(alert_path.read_text(encoding="utf-8"))
        canonical_agent = extract_agent_name(alert, alias_map)
        alert.setdefault("_autosoc", {})
        alert["_autosoc"]["agent"] = canonical_agent
        disposition, reason = determine_disposition(alert, policy, known_fps)
        case_id = make_case_id(alert)
        case_root = CASES_ROOT / case_id
        case_root.mkdir(parents=True, exist_ok=True)

        (case_root / "alert.raw.json").write_text(json.dumps(alert, indent=2), encoding="utf-8")
        triage = {
            "case_id": case_id,
            "created_utc": utc_now(),
            "disposition": disposition,
            "reason": reason,
            "rule": {"id": get_nested(alert, "rule.id", ""), "level": int(get_nested(alert, "rule.level", 0) or 0)},
            "agent": {
                "name": canonical_agent,
                "raw_name": get_nested(alert, "agent.name", ""),
                "raw_hostname": get_nested(alert, "agent.hostname", ""),
            },
            "status": "TRIAGED",
            "source_alert_file": str(alert_path),
        }
        (case_root / "triage.json").write_text(json.dumps(triage, indent=2), encoding="utf-8")

        processed_path = PROCESSED_ROOT / alert_path.name
        shutil.move(str(alert_path), str(processed_path))

        if not case_exists(ledger, case_id):
            update_metrics(ledger, disposition)
            ledger.setdefault("cases", []).append(
                {"case_id": case_id, "disposition": disposition, "created_utc": triage["created_utc"], "status": "TRIAGED"}
            )
        processed += 1

    save_ledger(ledger)
    print(f"TRIAGED={processed}")
    print(f"LEDGER={LEDGER_PATH}")


if __name__ == "__main__":
    main()
