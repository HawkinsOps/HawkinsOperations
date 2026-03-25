from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = REPO_ROOT / "data" / "metrics.json"


def load_metrics() -> dict:
    try:
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"metrics file not found: {METRICS_PATH}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"metrics file is not valid JSON: {exc}")


def expect_int(value: object, path: str, errors: list[str]) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(f"{path} must be a non-negative integer")


def expect_str(value: object, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string")


def expect_mapping(value: object, path: str, errors: list[str]) -> dict:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return {}
    return value


def validate_iso8601(value: str, path: str, errors: list[str]) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{path} must be an ISO-8601 timestamp")


def main() -> int:
    data = load_metrics()
    errors: list[str] = []

    running_totals = expect_mapping(data.get("running_totals"), "running_totals", errors)
    # Only fields with provable integer values are required here.
    # auto_closed_benign, known_fp, review, staged_pending are not validated —
    # their exact integer counts were not recorded at the March 20 canonical lock.
    for field in ("total_cases", "escalated"):
        expect_int(running_totals.get(field), f"running_totals.{field}", errors)

    host_coverage = data.get("host_coverage")
    expect_str(host_coverage, "host_coverage", errors)
    if isinstance(host_coverage, str) and not re.fullmatch(r"\d+/\d+", host_coverage):
        errors.append("host_coverage must use the N/N format")

    heartbeat = data.get("heartbeat")
    expect_str(heartbeat, "heartbeat", errors)
    if isinstance(heartbeat, str) and heartbeat not in {"SUCCESS", "FAIL", "WARN"}:
        errors.append("heartbeat must be one of SUCCESS, FAIL, WARN")

    expect_int(data.get("reconciliation_mismatch"), "reconciliation_mismatch", errors)

    last_updated = data.get("last_updated")
    expect_str(last_updated, "last_updated", errors)
    if isinstance(last_updated, str):
        validate_iso8601(last_updated, "last_updated", errors)

    stress_test_window = expect_mapping(data.get("stress_test_window"), "stress_test_window", errors)
    expect_str(stress_test_window.get("profile"), "stress_test_window.profile", errors)
    expect_str(stress_test_window.get("baseline_window"), "stress_test_window.baseline_window", errors)
    expect_int(stress_test_window.get("queue_backlog_target"), "stress_test_window.queue_backlog_target", errors)

    latency_targets = expect_mapping(
        stress_test_window.get("latency_targets_ms"),
        "stress_test_window.latency_targets_ms",
        errors,
    )
    expect_int(
        latency_targets.get("per_event_under_load"),
        "stress_test_window.latency_targets_ms.per_event_under_load",
        errors,
    )
    expect_int(
        latency_targets.get("with_backlog"),
        "stress_test_window.latency_targets_ms.with_backlog",
        errors,
    )

    simulated_pressure = expect_mapping(
        stress_test_window.get("simulated_rule_pressure"),
        "stress_test_window.simulated_rule_pressure",
        errors,
    )
    for field in (
        "rule_60227_pct_increase",
        "rule_92151_pct_increase",
        "sysmon_module_load_noise_pct_increase",
    ):
        expect_int(simulated_pressure.get(field), f"stress_test_window.simulated_rule_pressure.{field}", errors)

    detection_inventory = expect_mapping(data.get("detection_inventory"), "detection_inventory", errors)
    for field in ("sigma", "wazuh_files", "wazuh_rule_blocks", "splunk", "ir_playbooks"):
        expect_int(detection_inventory.get(field), f"detection_inventory.{field}", errors)

    if errors:
        print("metrics validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"metrics validation passed: {METRICS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
