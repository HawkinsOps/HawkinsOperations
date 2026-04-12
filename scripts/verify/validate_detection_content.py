#!/usr/bin/env python3
"""Validate HawkinsOperations detection content (Sigma YAML + Wazuh XML).

Scope (Branch A Step 1 — narrow, deterministic, auditable):

Sigma (.yml/.yaml under content/detection-rules/sigma/):
  - Required top-level fields: title, id, description, logsource, detection
  - id must be a syntactically valid UUIDv4 (RFC 4122 shape AND version/variant bits)
  - id must be globally unique across the Sigma tree
  - logsource must be a mapping and logsource.product must be present and non-empty

Wazuh (.xml under content/detection-rules/wazuh/rules/):
  - File must be parseable as XML (wrapped in a synthetic root to tolerate
    multiple top-level <group> blocks and leading/trailing comments)
  - Each <rule> element must carry id and level attributes
  - id must be numeric
  - rule id must be globally unique across the Wazuh tree
  - Each <rule> must contain a non-empty <description>

Non-goals (explicit): MITRE mapping policy, Sigma detection-logic correctness,
false-positive policy, level thresholds, naming conventions. Those are
out-of-scope until policy is decided.

Exit codes:
  0 — no hard failures
  1 — one or more hard failures
"""

from __future__ import annotations

import re
import sys
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parents[2]
SIGMA_ROOT = REPO_ROOT / "content" / "detection-rules" / "sigma"
WAZUH_ROOT = REPO_ROOT / "content" / "detection-rules" / "wazuh" / "rules"

SIGMA_REQUIRED_FIELDS = ("title", "id", "description", "logsource", "detection")


@dataclass
class Findings:
    sigma_files: int = 0
    wazuh_files: int = 0
    wazuh_rule_blocks: int = 0
    failures: List[Tuple[str, Path, str]] = field(default_factory=list)

    def add(self, category: str, path: Path, reason: str) -> None:
        self.failures.append((category, path, reason))

    def by_category(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for cat, _, _ in self.failures:
            counts[cat] = counts.get(cat, 0) + 1
        return counts


def is_uuid_v4(value: str) -> bool:
    """True iff value is a well-formed UUIDv4 (version=4 AND RFC 4122 variant)."""
    if not isinstance(value, str):
        return False
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    if parsed.version != 4:
        return False
    # Variant bits: 10xx (RFC 4122). uuid.UUID.variant returns the string 'specified in RFC 4122'.
    if parsed.variant != uuid.RFC_4122:
        return False
    # Guard against normalization: require canonical lowercase hyphenated form match.
    return str(parsed) == value.lower()


def validate_sigma(findings: Findings) -> None:
    if not SIGMA_ROOT.exists():
        findings.add("sigma_tree_missing", SIGMA_ROOT, "Sigma root directory not found")
        return

    seen_ids: Dict[str, Path] = {}
    files = sorted(list(SIGMA_ROOT.rglob("*.yml")) + list(SIGMA_ROOT.rglob("*.yaml")))
    findings.sigma_files = len(files)

    for path in files:
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            findings.add("sigma_read_error", path, f"read failure: {exc}")
            continue

        try:
            doc = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            findings.add("sigma_yaml_parse", path, f"YAML parse error: {exc}")
            continue

        if not isinstance(doc, dict):
            findings.add("sigma_not_mapping", path, "top-level YAML is not a mapping")
            continue

        for field_name in SIGMA_REQUIRED_FIELDS:
            if field_name not in doc:
                findings.add("sigma_missing_field", path, f"missing required field '{field_name}'")
            elif doc[field_name] in (None, ""):
                findings.add("sigma_empty_field", path, f"required field '{field_name}' is empty")

        rule_id = doc.get("id")
        if rule_id is not None:
            if not isinstance(rule_id, str):
                findings.add("sigma_id_type", path, f"id must be string, got {type(rule_id).__name__}")
            elif not is_uuid_v4(rule_id):
                findings.add("sigma_id_not_uuidv4", path, f"id '{rule_id}' is not a valid UUIDv4")
            else:
                prior = seen_ids.get(rule_id)
                if prior is not None:
                    findings.add(
                        "sigma_id_duplicate",
                        path,
                        f"id '{rule_id}' already used by {prior.relative_to(REPO_ROOT)}",
                    )
                else:
                    seen_ids[rule_id] = path

        logsource = doc.get("logsource")
        if logsource is None:
            # Already flagged by missing_field check; skip duplicate report.
            continue
        if not isinstance(logsource, dict):
            findings.add("sigma_logsource_type", path, "logsource must be a mapping")
            continue
        product = logsource.get("product")
        if product is None or (isinstance(product, str) and product.strip() == ""):
            findings.add("sigma_logsource_product_missing", path, "logsource.product is missing or empty")


WAZUH_ID_NUMERIC_RE = re.compile(r"^\d+$")


def validate_wazuh(findings: Findings) -> None:
    if not WAZUH_ROOT.exists():
        findings.add("wazuh_tree_missing", WAZUH_ROOT, "Wazuh rules root directory not found")
        return

    seen_rule_ids: Dict[str, Path] = {}
    files = sorted(WAZUH_ROOT.rglob("*.xml"))
    findings.wazuh_files = len(files)

    for path in files:
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            findings.add("wazuh_read_error", path, f"read failure: {exc}")
            continue

        # Wazuh rule files frequently contain multiple top-level <group> blocks and
        # leading/trailing comment blocks. Wrap in a synthetic root so ElementTree
        # can parse them without requiring content edits.
        wrapped = f"<__root__>{raw}</__root__>"
        try:
            root = ET.fromstring(wrapped)
        except ET.ParseError as exc:
            findings.add("wazuh_xml_parse", path, f"XML parse error: {exc}")
            continue

        rules_in_file = root.findall(".//rule")
        if not rules_in_file:
            findings.add("wazuh_no_rule_block", path, "no <rule> element found")
            continue

        for rule in rules_in_file:
            findings.wazuh_rule_blocks += 1

            rule_id = rule.attrib.get("id")
            level = rule.attrib.get("level")

            if rule_id is None:
                findings.add("wazuh_rule_missing_id", path, "<rule> missing id attribute")
            elif not WAZUH_ID_NUMERIC_RE.match(rule_id):
                findings.add("wazuh_rule_id_nonnumeric", path, f"<rule> id '{rule_id}' is not numeric")
            else:
                prior = seen_rule_ids.get(rule_id)
                if prior is not None and prior != path:
                    findings.add(
                        "wazuh_rule_id_duplicate",
                        path,
                        f"rule id '{rule_id}' already used by {prior.relative_to(REPO_ROOT)}",
                    )
                elif prior is not None and prior == path:
                    findings.add(
                        "wazuh_rule_id_duplicate_in_file",
                        path,
                        f"rule id '{rule_id}' duplicated within same file",
                    )
                else:
                    seen_rule_ids[rule_id] = path

            if level is None:
                findings.add(
                    "wazuh_rule_missing_level",
                    path,
                    f"<rule id='{rule_id or '?'}'> missing level attribute",
                )

            description_el = rule.find("description")
            if description_el is None or (description_el.text or "").strip() == "":
                findings.add(
                    "wazuh_rule_missing_description",
                    path,
                    f"<rule id='{rule_id or '?'}'> missing or empty <description>",
                )


def print_summary(findings: Findings) -> None:
    print("=" * 72)
    print("HawkinsOps Detection Content Validator")
    print("=" * 72)
    print(f"Sigma files scanned:       {findings.sigma_files}")
    print(f"Wazuh files scanned:       {findings.wazuh_files}")
    print(f"Wazuh <rule> blocks seen:  {findings.wazuh_rule_blocks}")
    print()

    if not findings.failures:
        print("RESULT: PASS — no hard failures")
        return

    print(f"RESULT: FAIL — {len(findings.failures)} hard failure(s)")
    print()
    print("Failures by category:")
    for cat, count in sorted(findings.by_category().items()):
        print(f"  {cat:40s} {count}")
    print()
    print("Details:")
    for cat, path, reason in findings.failures:
        try:
            rel = path.relative_to(REPO_ROOT)
        except ValueError:
            rel = path
        print(f"  [{cat}] {rel}: {reason}")


def main() -> int:
    findings = Findings()
    validate_sigma(findings)
    validate_wazuh(findings)
    print_summary(findings)
    return 1 if findings.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
