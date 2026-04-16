#!/usr/bin/env python3
"""Validate detection rule content (Sigma + Wazuh).

Fails if any rule file is structurally broken. Complements verify-counts.ps1,
which only counts files — this script checks that each file is actually a
well-formed rule the relevant engine would accept.

Sigma (PyYAML):
  - parses as YAML
  - top-level is a mapping
  - required keys: title, id, logsource, detection
  - id is a UUID
  - detection is a mapping containing a 'condition' key
  - logsource is a mapping with at least one of product/service/category
  - level (if present) is in the standard sigma severity set
  - rule ids are unique across the tree

Wazuh (stdlib xml.etree.ElementTree):
  - file parses as XML
  - root element is <group>
  - contains at least one <rule id="...">
  - every rule/@id is an integer in [100000, 199999]
  - every rule has a non-empty <description>
  - rule ids are unique across the tree

Splunk is intentionally out of scope for this validator — see
scripts/verify/README.md for the justification.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SIGMA_DIR = REPO_ROOT / "content" / "detection-rules" / "sigma"
WAZUH_RULES_DIR = REPO_ROOT / "content" / "detection-rules" / "wazuh" / "rules"
EXCEPTIONS_PATH = REPO_ROOT / "scripts" / "verify" / "validation_exceptions.yml"

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
SIGMA_LEVELS = {"informational", "low", "medium", "high", "critical"}
WAZUH_ID_MIN = 100000
WAZUH_ID_MAX = 199999


def load_sigma_duplicate_allowlist() -> dict[str, frozenset[str]]:
    """Return {uuid: frozenset(repo-relative forward-slash paths)} from the
    exceptions file. Missing file returns an empty dict — strict mode."""
    if not EXCEPTIONS_PATH.exists():
        return {}
    raw = yaml.safe_load(EXCEPTIONS_PATH.read_text(encoding="utf-8")) or {}
    entries = raw.get("sigma_duplicate_ids") or []
    out: dict[str, frozenset[str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        uid = entry.get("id")
        files = entry.get("files") or []
        if isinstance(uid, str) and isinstance(files, list):
            out[uid] = frozenset(str(f).replace("\\", "/") for f in files)
    return out


def validate_sigma(
    sigma_root: Path,
    dup_allowlist: dict[str, frozenset[str]],
) -> tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    if not sigma_root.is_dir():
        return [f"sigma: directory not found: {sigma_root}"], []

    files = sorted(
        list(sigma_root.rglob("*.yml")) + list(sigma_root.rglob("*.yaml"))
    )
    if not files:
        return [f"sigma: no rule files under {sigma_root}"], []

    id_to_paths: dict[str, List[Path]] = {}

    for path in files:
        rel = path.relative_to(REPO_ROOT)
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"sigma {rel}: YAML parse error: {exc}")
            continue

        if not isinstance(doc, dict):
            errors.append(f"sigma {rel}: top-level must be a mapping")
            continue

        for key in ("title", "id", "logsource", "detection"):
            if key not in doc:
                errors.append(f"sigma {rel}: missing required key '{key}'")

        rid = doc.get("id")
        if isinstance(rid, str):
            if not UUID_RE.match(rid):
                errors.append(f"sigma {rel}: id '{rid}' is not a UUID")
            else:
                id_to_paths.setdefault(rid, []).append(path)
        elif rid is not None:
            errors.append(f"sigma {rel}: id must be a string UUID")

        logsource = doc.get("logsource")
        if logsource is not None:
            if not isinstance(logsource, dict):
                errors.append(f"sigma {rel}: logsource must be a mapping")
            elif not any(
                k in logsource for k in ("product", "service", "category")
            ):
                errors.append(
                    f"sigma {rel}: logsource must define at least one of "
                    f"product/service/category"
                )

        detection = doc.get("detection")
        if detection is not None:
            if not isinstance(detection, dict):
                errors.append(f"sigma {rel}: detection must be a mapping")
            elif "condition" not in detection:
                errors.append(f"sigma {rel}: detection is missing 'condition'")
            else:
                condition_str = detection["condition"]
                if isinstance(condition_str, str):
                    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_*]*", condition_str)
                    keywords = {"and", "or", "not", "1", "of", "all", "them"}
                    det_keys = {k for k in detection if k != "condition"}
                    for token in tokens:
                        if token.lower() in keywords:
                            continue
                        if token.endswith("*"):
                            prefix = token[:-1]
                            if not any(k.startswith(prefix) for k in det_keys):
                                errors.append(
                                    f"sigma {rel}: condition references "
                                    f"'{token}' but no detection key matches "
                                    f"that wildcard pattern"
                                )
                        elif token not in det_keys:
                            errors.append(
                                f"sigma {rel}: condition references '{token}' "
                                f"but it is not a key in detection"
                            )

        level = doc.get("level")
        if level is not None and level not in SIGMA_LEVELS:
            errors.append(
                f"sigma {rel}: level '{level}' is not one of "
                f"{sorted(SIGMA_LEVELS)}"
            )

        # --- advisory field-quality warnings ---
        status = doc.get("status")
        if status is None:
            warnings.append(f"sigma {rel}: missing recommended field 'status'")
        elif status not in ("experimental", "test", "stable", "deprecated"):
            warnings.append(
                f"sigma {rel}: status '{status}' is not one of "
                f"experimental/test/stable/deprecated"
            )

        description = doc.get("description")
        if not isinstance(description, str) or not description.strip():
            warnings.append(
                f"sigma {rel}: missing or empty recommended field 'description'"
            )

        if level is None:
            warnings.append(f"sigma {rel}: missing recommended field 'level'")

        falsepositives = doc.get("falsepositives")
        if not isinstance(falsepositives, list):
            warnings.append(
                f"sigma {rel}: missing recommended field 'falsepositives'"
            )

        tags = doc.get("tags")
        if not isinstance(tags, list):
            warnings.append(f"sigma {rel}: missing recommended field 'tags'")
        elif not any(
            str(t).lower().startswith("attack.t") for t in tags
        ):
            warnings.append(
                f"sigma {rel}: tags should contain at least one ATT&CK "
                f"technique (attack.tNNNN)"
            )

    # Resolve duplicate-id collisions against the allowlist.
    for rid, paths in sorted(id_to_paths.items()):
        if len(paths) < 2:
            continue
        rels_posix = sorted(
            str(p.relative_to(REPO_ROOT)).replace("\\", "/") for p in paths
        )
        allowed_set = dup_allowlist.get(rid)
        involved_set = frozenset(rels_posix)
        if allowed_set is not None and involved_set == allowed_set:
            warnings.append(
                f"sigma: duplicate id '{rid}' is in the known-exceptions "
                f"allowlist ({len(rels_posix)} files): "
                f"{', '.join(rels_posix)}"
            )
        else:
            if allowed_set is not None:
                extra = sorted(involved_set - allowed_set)
                missing = sorted(allowed_set - involved_set)
                detail = []
                if extra:
                    detail.append(f"unlisted files: {', '.join(extra)}")
                if missing:
                    detail.append(f"listed but not seen: {', '.join(missing)}")
                errors.append(
                    f"sigma: duplicate id '{rid}' collision set does not "
                    f"match allowlist — {'; '.join(detail)}"
                )
            else:
                errors.append(
                    f"sigma: duplicate id '{rid}' across {len(rels_posix)} "
                    f"files: {', '.join(rels_posix)}"
                )

    return errors, warnings


def validate_wazuh(wazuh_root: Path) -> tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    if not wazuh_root.is_dir():
        return [f"wazuh: directory not found: {wazuh_root}"], []

    files = sorted(wazuh_root.glob("*.xml"))
    if not files:
        return [f"wazuh: no rule files under {wazuh_root}"], []

    ids_seen: dict[str, Path] = {}

    for path in files:
        rel = path.relative_to(REPO_ROOT)
        try:
            root = ET.fromstring(path.read_text(encoding="utf-8"))
        except ET.ParseError as exc:
            errors.append(f"wazuh {rel}: XML parse error: {exc}")
            continue

        if root.tag != "group":
            errors.append(
                f"wazuh {rel}: root tag is <{root.tag}>, expected <group>"
            )
            continue

        rules = root.findall(".//rule[@id]")
        if not rules:
            errors.append(f"wazuh {rel}: no <rule id=\"...\"> elements found")
            continue

        for rule in rules:
            rid = rule.get("id", "")
            try:
                rid_int = int(rid)
            except ValueError:
                errors.append(
                    f"wazuh {rel}: rule id '{rid}' is not an integer"
                )
                continue

            if not (WAZUH_ID_MIN <= rid_int <= WAZUH_ID_MAX):
                errors.append(
                    f"wazuh {rel}: rule id {rid_int} outside allowed local "
                    f"range [{WAZUH_ID_MIN}, {WAZUH_ID_MAX}]"
                )

            if rid in ids_seen:
                errors.append(
                    f"wazuh {rel}: duplicate rule id {rid} "
                    f"(also in {ids_seen[rid].relative_to(REPO_ROOT)})"
                )
            else:
                ids_seen[rid] = path

            desc = rule.find("description")
            if desc is None or not (desc.text or "").strip():
                errors.append(
                    f"wazuh {rel}: rule id {rid} missing or empty "
                    f"<description>"
                )

            for sid_tag in ("if_sid", "if_matched_sid"):
                for sid_el in rule.findall(sid_tag):
                    sid_text = (sid_el.text or "").strip()
                    try:
                        int(sid_text)
                    except ValueError:
                        errors.append(
                            f"wazuh {rel}: rule id {rid} <{sid_tag}> value "
                            f"'{sid_text}' is not an integer"
                        )

    return errors, warnings


def main() -> int:
    dup_allowlist = load_sigma_duplicate_allowlist()

    sigma_errors, sigma_warnings = validate_sigma(SIGMA_DIR, dup_allowlist)
    wazuh_errors, wazuh_warnings = validate_wazuh(WAZUH_RULES_DIR)

    errors = sigma_errors + wazuh_errors
    warnings = sigma_warnings + wazuh_warnings

    if warnings:
        print(f"detection content validation warnings ({len(warnings)}):")
        for w in warnings:
            print(f"- {w}")
        print()

    if errors:
        print(
            f"detection content validation FAILED ({len(errors)} errors):",
            file=sys.stderr,
        )
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print("detection content validation passed")
    print(f"  sigma dir            : {SIGMA_DIR.relative_to(REPO_ROOT)}")
    print(f"  wazuh dir            : {WAZUH_RULES_DIR.relative_to(REPO_ROOT)}")
    print(f"  allowlisted dup ids  : {len(dup_allowlist)}")
    print(f"  warnings emitted     : {len(warnings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
