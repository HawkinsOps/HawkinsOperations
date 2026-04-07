#!/usr/bin/env python3
"""Fail on drift between VERIFIED_COUNTS.md and website claim surfaces."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def parse_verified_counts_md(md_path: Path) -> Dict[str, int]:
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    patterns = {
        "sigma": re.compile(r"\|\s*\*\*Sigma\*\*.*?\|\s*\*\*(\d+)\*\*\s+rules", re.IGNORECASE),
        "splunk": re.compile(
            r"\|\s*\*\*Splunk\*\*.*?\|\s*\*\*\d+\*\*\s+files,\s*\*\*(\d+)\*\*\s+detection searches",
            re.IGNORECASE,
        ),
        "wazuh_pair": re.compile(
            r"\|\s*\*\*Wazuh\*\*.*?\|\s*\*\*(\d+)\*\*\s+files,\s*\*\*(\d+)\*\*\s+rule blocks",
            re.IGNORECASE,
        ),
        "ir": re.compile(r"\|\s*\*\*IR Playbooks\*\*.*?\|\s*\*\*(\d+)\*\*\s+playbooks", re.IGNORECASE),
    }

    out: Dict[str, int] = {}
    for line in lines:
        m = patterns["sigma"].search(line)
        if m:
            out["sigma"] = int(m.group(1))
            continue
        m = patterns["splunk"].search(line)
        if m:
            out["splunk"] = int(m.group(1))
            continue
        m = patterns["wazuh_pair"].search(line)
        if m:
            out["wazuh_xml_files"] = int(m.group(1))
            out["wazuh"] = int(m.group(2))
            continue
        m = patterns["ir"].search(line)
        if m:
            out["ir"] = int(m.group(1))
            continue

    required = ("sigma", "splunk", "wazuh_xml_files", "wazuh", "ir")
    missing = [k for k in required if k not in out]
    if missing:
        raise ValueError(f"Missing keys from VERIFIED_COUNTS.md parse: {', '.join(missing)}")
    out["detections"] = out["sigma"] + out["splunk"] + out["wazuh"]
    return out


def load_json_counts(path: Path) -> Dict[str, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    counts = data.get("counts")
    if not isinstance(counts, dict):
        raise ValueError(f"'counts' object not found in {path}")

    return {k: int(v) for k, v in counts.items() if isinstance(v, int)}


def compare_counts(expected: Dict[str, int], actual: Dict[str, int], label: str) -> List[str]:
    errors: List[str] = []
    for key in ("detections", "sigma", "splunk", "wazuh", "wazuh_xml_files", "ir"):
        if key not in actual:
            errors.append(f"{label}: missing key '{key}'")
            continue
        if actual[key] != expected[key]:
            errors.append(
                f"{label}: key '{key}' mismatch (expected {expected[key]}, got {actual[key]})"
            )
    return errors


def scan_hardcoded_claim_numbers(site_root: Path, truth: Dict[str, int]) -> List[Tuple[Path, int, str]]:
    claim_files = sorted(
        [
            p
            for p in site_root.rglob("*")
            if p.is_file() and p.suffix.lower() in {".html", ".txt", ".md"}
        ]
    )
    values = sorted(set(truth.values()), reverse=True)
    token_re = re.compile(r"\b(" + "|".join(re.escape(str(v)) for v in values) + r")\b")
    claim_context_re = re.compile(
        r"verified|detection|sigma|wazuh|splunk|playbook|rule blocks|rules|queries|inventory|counts?",
        re.IGNORECASE,
    )
    issues: List[Tuple[Path, int, str]] = []

    # Patterns that embed claim numbers inside dates or ratios (false positives).
    date_re = re.compile(r"\d{2}-\d{2}-\d{4}|\d{4}-\d{2}-\d{2}")
    ratio_re = re.compile(r"\b\d+/\d+\b")

    for path in claim_files:
        if not path.exists():
            continue
        in_comment = False
        in_template = False
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            # Track multi-line HTML comments.
            if "<!--" in stripped:
                if "-->" not in stripped.split("<!--", 1)[1]:
                    in_comment = True
                    continue
                if stripped.startswith("<!--") and stripped.endswith("-->"):
                    continue
            if in_comment:
                if "-->" in stripped:
                    in_comment = False
                continue
            # Skip <template> and <svg> content (hidden DOM / layout coordinates).
            if "<template" in stripped.lower() or "<svg" in stripped.lower():
                in_template = True
                continue
            if "</template>" in stripped.lower() or "</svg>" in stripped.lower():
                in_template = False
                continue
            if in_template:
                continue
            # Skip <pre>/<code> blocks (terminal output, not claims).
            if "<pre" in stripped.lower() and "</pre>" not in stripped.lower():
                in_template = True
                continue
            if "</pre>" in stripped.lower():
                in_template = False
                continue
            # Handled by scan_data_verified_fallbacks() with key-aware validation.
            if "data-verified" in line:
                continue
            # data-ops spans are runtime-bound (same as data-verified).
            if "data-ops" in line:
                continue
            # Mask dates and ratios so embedded digits don't false-positive.
            masked = date_re.sub("__DATE__", line)
            masked = ratio_re.sub("__RATIO__", masked)
            if token_re.search(masked) and claim_context_re.search(masked):
                issues.append((path, lineno, line.strip()))
    return issues


def scan_data_verified_fallbacks(site_root: Path, truth: Dict[str, int]) -> List[str]:
    html_files = sorted(p for p in site_root.rglob("*.html") if p.is_file())
    errors: List[str] = []
    # Matches: data-verified="key">value<
    token_re = re.compile(r'data-verified="([a-z_]+)">\s*([^<]+?)\s*<', re.IGNORECASE)
    allowed_placeholders = {"0", "-", "—"}

    for path in html_files:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for m in token_re.finditer(line):
                key = m.group(1)
                raw_value = m.group(2).strip()

                if key not in truth:
                    errors.append(f"{path}:{lineno}: unknown data-verified key '{key}'")
                    continue

                if raw_value.isdigit():
                    actual = int(raw_value)
                    expected = truth[key]
                    if actual != expected:
                        errors.append(
                            f"{path}:{lineno}: data-verified '{key}' fallback mismatch "
                            f"(expected {expected}, got {actual})"
                        )
                    continue

                if raw_value not in allowed_placeholders:
                    errors.append(
                        f"{path}:{lineno}: data-verified '{key}' has invalid fallback '{raw_value}' "
                        f"(use expected number or placeholder 0/-/—)"
                    )

    return errors


def run_generator() -> None:
    subprocess.run(
        [sys.executable, "scripts/generate_verified_counts.py"],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Regenerate JSON artifacts before running checks.",
    )
    parser.add_argument(
        "--markdown",
        default="PROOF_PACK/VERIFIED_COUNTS.md",
        help="Verified markdown source path.",
    )
    parser.add_argument(
        "--canonical-json",
        default="PROOF_PACK/verified_counts.json",
        help="Canonical generated JSON path.",
    )
    parser.add_argument(
        "--site-json",
        default="site/assets/verified-counts.json",
        help="Site-consumed JSON path.",
    )
    parser.add_argument(
        "--site-root",
        default="site",
        help="Site root path.",
    )
    args = parser.parse_args()

    if args.refresh:
        run_generator()

    expected = parse_verified_counts_md(Path(args.markdown))
    errors: List[str] = []

    canonical_path = Path(args.canonical_json)
    site_path = Path(args.site_json)

    if not canonical_path.exists():
        errors.append(f"Missing canonical JSON: {canonical_path}")
    else:
        errors.extend(compare_counts(expected, load_json_counts(canonical_path), str(canonical_path)))

    if not site_path.exists():
        errors.append(f"Missing site JSON: {site_path}")
    else:
        errors.extend(compare_counts(expected, load_json_counts(site_path), str(site_path)))

    hardcoded = scan_hardcoded_claim_numbers(Path(args.site_root), expected)
    for path, lineno, line in hardcoded:
        errors.append(f"Hard-coded claim number in {path}:{lineno}: {line}")
    errors.extend(scan_data_verified_fallbacks(Path(args.site_root), expected))

    if errors:
        print("DRIFT SCAN: FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("DRIFT SCAN: PASS")
    print(json.dumps(expected, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
