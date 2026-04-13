#!/usr/bin/env python3
"""Run detection rule unit tests against the live Wazuh manager via SSH.

Walks tests/detection/fixtures/**, for each fixture pipes event.log through
wazuh-logtest on the manager, parses the output, and asserts against
expected.yml. Emits machine- and human-readable summaries into
proof/detection_unit_tests/ and exits non-zero if any fixture fails.

Required environment variables (already used by deploy-wazuh-pack.yml):
  WAZUH_HOST       host/IP of the Wazuh manager
  WAZUH_SSH_USER   ssh user on the manager
  WAZUH_SSH_PORT   ssh port
  WAZUH_SSH_KEY    ssh private key content (not a path)

This is the Phase 1 MVP harness. It validates the currently deployed
ruleset on the manager, not the in-PR bundle. Phase 2 (ephemeral docker
manager built from the PR bundle) is tracked as a follow-up.
"""

from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_ROOT = REPO_ROOT / "tests" / "detection" / "fixtures"
PROOF_DIR = REPO_ROOT / "proof" / "detection_unit_tests"

REQUIRED_ENV = ("WAZUH_HOST", "WAZUH_SSH_USER", "WAZUH_SSH_PORT", "WAZUH_SSH_KEY")

RULE_ID_RE = re.compile(r"^\s*id:\s*'(\d+)'", re.MULTILINE)
LEVEL_RE = re.compile(r"^\s*level:\s*'(\d+)'", re.MULTILINE)
DESCRIPTION_RE = re.compile(r"^\s*description:\s*'([^']*)'", re.MULTILINE)
GROUPS_RE = re.compile(r"^\s*groups:\s*'(\[[^\]]*\])'", re.MULTILINE)
MITRE_RE = re.compile(r"^\s*mitre(?:_id)?(?:s)?:\s*'(\[[^\]]*\])'", re.MULTILINE)


@dataclass
class FixtureResult:
    fixture_id: str
    path: str
    rule_id_expected: str
    rule_id_observed: str | None = None
    level_observed: int | None = None
    passed: bool = False
    errors: list[str] = field(default_factory=list)
    raw_logtest_output: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture_id": self.fixture_id,
            "path": self.path,
            "rule_id_expected": self.rule_id_expected,
            "rule_id_observed": self.rule_id_observed,
            "level_observed": self.level_observed,
            "passed": self.passed,
            "errors": self.errors,
        }


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def load_env() -> dict[str, str]:
    missing = [k for k in REQUIRED_ENV if not os.environ.get(k)]
    if missing:
        die(
            "missing required environment variables: "
            + ", ".join(missing)
            + ". These are the same secrets deploy-wazuh-pack.yml consumes."
        )
    return {k: os.environ[k] for k in REQUIRED_ENV}


def write_ssh_key(key_content: str) -> Path:
    """Write the ssh key to a temp file with 0600 perms and return the path."""
    fd, path_str = tempfile.mkstemp(prefix="wazuh_ssh_", suffix=".key")
    os.close(fd)
    key_path = Path(path_str)
    key_path.write_text(
        key_content if key_content.endswith("\n") else key_content + "\n",
        encoding="utf-8",
    )
    try:
        os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    return key_path


def run_logtest(
    event_text: str,
    env: dict[str, str],
    key_path: Path,
    timeout_seconds: int = 30,
) -> str:
    """Pipe event_text through wazuh-logtest on the manager via ssh."""
    ssh_cmd = [
        "ssh",
        "-i",
        str(key_path),
        "-p",
        env["WAZUH_SSH_PORT"],
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=10",
        f"{env['WAZUH_SSH_USER']}@{env['WAZUH_HOST']}",
        "/var/ossec/bin/wazuh-logtest",
    ]
    result = subprocess.run(
        ssh_cmd,
        input=event_text,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    return combined


def parse_logtest_output(output: str) -> dict[str, Any]:
    """Extract the Phase 3 rule match fields from wazuh-logtest stdout."""
    parsed: dict[str, Any] = {
        "rule_id": None,
        "level": None,
        "description": None,
        "groups": [],
        "mitre_ids": [],
    }

    m = RULE_ID_RE.search(output)
    if m:
        parsed["rule_id"] = m.group(1)

    m = LEVEL_RE.search(output)
    if m:
        try:
            parsed["level"] = int(m.group(1))
        except ValueError:
            pass

    m = DESCRIPTION_RE.search(output)
    if m:
        parsed["description"] = m.group(1)

    m = GROUPS_RE.search(output)
    if m:
        parsed["groups"] = _parse_python_list_literal(m.group(1))

    m = MITRE_RE.search(output)
    if m:
        parsed["mitre_ids"] = _parse_python_list_literal(m.group(1))

    return parsed


def _parse_python_list_literal(raw: str) -> list[str]:
    """Parse "['a', 'b']" or '["a","b"]' into a list of strings.

    wazuh-logtest prints groups/mitre as a Python-ish list literal inside
    single-quoted output; handle both single- and double-quoted inner items.
    """
    inner = raw.strip().strip("[]")
    if not inner:
        return []
    items: list[str] = []
    for chunk in inner.split(","):
        s = chunk.strip().strip("'").strip('"')
        if s:
            items.append(s)
    return items


def assert_fixture(
    expected: dict[str, Any],
    observed: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    expected_rule_id = str(expected.get("rule_id", "")).strip()
    if not expected_rule_id:
        errors.append("expected.yml missing required 'rule_id'")
    elif observed.get("rule_id") != expected_rule_id:
        errors.append(
            f"rule_id mismatch: expected {expected_rule_id}, "
            f"observed {observed.get('rule_id')!r}"
        )

    level_min = expected.get("level_min")
    if level_min is None:
        errors.append("expected.yml missing required 'level_min'")
    else:
        observed_level = observed.get("level")
        if observed_level is None:
            errors.append("level not present in logtest output")
        elif observed_level < int(level_min):
            errors.append(
                f"level below minimum: expected >= {level_min}, "
                f"observed {observed_level}"
            )

    for tid in expected.get("mitre_ids") or []:
        if tid not in (observed.get("mitre_ids") or []):
            errors.append(
                f"missing MITRE technique {tid} in observed "
                f"{observed.get('mitre_ids')}"
            )

    for group in expected.get("groups_contain") or []:
        if group not in (observed.get("groups") or []):
            errors.append(
                f"missing group '{group}' in observed "
                f"{observed.get('groups')}"
            )

    substr = expected.get("description_substring")
    if substr:
        desc = observed.get("description") or ""
        if substr not in desc:
            errors.append(
                f"description substring not found: "
                f"expected to contain {substr!r}, observed {desc!r}"
            )

    return errors


def discover_fixtures() -> list[Path]:
    if not FIXTURES_ROOT.is_dir():
        return []
    return sorted(FIXTURES_ROOT.rglob("expected.yml"))


def run_fixture(
    expected_path: Path,
    env: dict[str, str],
    key_path: Path,
) -> FixtureResult:
    fixture_dir = expected_path.parent
    event_path = fixture_dir / "event.log"
    rel = fixture_dir.relative_to(REPO_ROOT).as_posix()

    result = FixtureResult(
        fixture_id=fixture_dir.name,
        path=rel,
        rule_id_expected="",
    )

    try:
        expected = yaml.safe_load(expected_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        result.errors.append(f"failed to parse expected.yml: {exc}")
        return result

    result.rule_id_expected = str(expected.get("rule_id", "")).strip()

    if not event_path.exists():
        result.errors.append(f"event.log not found next to expected.yml")
        return result

    event_text = event_path.read_text(encoding="utf-8")

    try:
        logtest_output = run_logtest(event_text, env, key_path)
    except subprocess.TimeoutExpired:
        result.errors.append("wazuh-logtest ssh call timed out")
        return result
    except FileNotFoundError:
        result.errors.append("ssh binary not found on runner")
        return result

    result.raw_logtest_output = logtest_output
    observed = parse_logtest_output(logtest_output)
    result.rule_id_observed = observed.get("rule_id")
    result.level_observed = observed.get("level")

    result.errors = assert_fixture(expected, observed)
    result.passed = not result.errors
    return result


def emit_summary(results: list[FixtureResult]) -> None:
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    summary = {
        "generated_at": now,
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "results": [r.to_dict() for r in results],
    }
    (PROOF_DIR / "latest.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    md_lines: list[str] = []
    md_lines.append("# Detection Unit Tests — Layer 1")
    md_lines.append("")
    md_lines.append(f"- Generated: `{now}`")
    md_lines.append(f"- Total: **{len(results)}**")
    md_lines.append(f"- Passed: **{passed}**")
    md_lines.append(f"- Failed: **{failed}**")
    md_lines.append("")
    md_lines.append("| Result | Fixture | Rule | Level | Errors |")
    md_lines.append("|---|---|---|---|---|")
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        lvl = r.level_observed if r.level_observed is not None else "-"
        errs = "; ".join(r.errors) if r.errors else ""
        md_lines.append(
            f"| {mark} | `{r.path}` | {r.rule_id_expected} | {lvl} | {errs} |"
        )
    md_lines.append("")
    (PROOF_DIR / "latest.md").write_text(
        "\n".join(md_lines), encoding="utf-8"
    )


def main() -> int:
    env = load_env()
    fixtures = discover_fixtures()

    if not fixtures:
        print(
            f"no fixtures discovered under {FIXTURES_ROOT.relative_to(REPO_ROOT)} "
            "— harness is wired but nothing to assert"
        )
        emit_summary([])
        return 0

    key_path = write_ssh_key(env["WAZUH_SSH_KEY"])
    try:
        results = [run_fixture(f, env, key_path) for f in fixtures]
    finally:
        try:
            key_path.unlink()
        except OSError:
            pass

    emit_summary(results)

    failed_results = [r for r in results if not r.passed]
    passed = len(results) - len(failed_results)
    print(f"detection unit tests: {passed}/{len(results)} passed")

    if failed_results:
        print("", file=sys.stderr)
        print(
            f"detection unit tests FAILED ({len(failed_results)} "
            f"of {len(results)}):",
            file=sys.stderr,
        )
        for r in failed_results:
            print(f"- {r.path}", file=sys.stderr)
            for err in r.errors:
                print(f"    - {err}", file=sys.stderr)
            raw = r.raw_logtest_output or ""
            print(
                f"    --- raw logtest output ({len(raw)} bytes) ---",
                file=sys.stderr,
            )
            if raw.strip():
                for line in raw.splitlines():
                    print(f"    {line}", file=sys.stderr)
            else:
                print(
                    "    (empty — wazuh-logtest produced no stdout/stderr)",
                    file=sys.stderr,
                )
            print(
                "    ----------------------------------------------",
                file=sys.stderr,
            )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
