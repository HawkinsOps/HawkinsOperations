#!/usr/bin/env python3
"""
Deploy HawkinsOps SPL detection rules as Splunk saved searches.
Reads all .spl files from content/detection-rules/splunk/ and POSTs each
rule block as a named saved search via the Splunk REST API.

Usage:
    python scripts/deploy-splunk-saved-searches.py [--dry-run]
"""

import os
import re
import sys
import ssl
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
SPLUNK_HOST = os.environ.get("SPLUNK_HOST", "192.168.8.248")
SPLUNK_PORT = int(os.environ.get("SPLUNK_PORT", "8089"))
SPLUNK_USER = os.environ.get("SPLUNK_USER", "admin")
SPLUNK_PASS = os.environ.get("SPLUNK_PASS", "")
SPL_DIR     = Path(__file__).parent.parent / "content" / "detection-rules" / "splunk"
APP         = "search"
# ─────────────────────────────────────────────────────────────────────────────

BASE_URL = f"https://{SPLUNK_HOST}:{SPLUNK_PORT}"

# Skip SSL verification for self-signed cert on lab instance
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def splunk_request(method: str, path: str, data: dict | None = None) -> dict:
    url = f"{BASE_URL}{path}"
    creds = f"{SPLUNK_USER}:{SPLUNK_PASS}"
    import base64
    auth = base64.b64encode(creds.encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        # 409 = already exists — treat as success, we'll update instead
        if e.code == 409:
            return {"_conflict": True, "raw": raw}
        print(f"  HTTP {e.code}: {raw[:200]}", file=sys.stderr)
        raise


def parse_spl_file(path: Path) -> list[dict]:
    """
    Parse a .spl file into a list of rule dicts:
      { name, mitre, description, search }

    Handles two block styles:
      Style A (most files):
        # ========================================
        # Rule Name
        # MITRE: T####
        # ========================================
        <SPL query>

      Style B (collection_exfiltration_impact.spl):
        # Rule Name - T####
        <SPL query>
    """
    text = path.read_text(encoding="utf-8")
    tactic = path.stem.replace("_detections", "").replace("_", " ").title()
    rules = []

    # Style A: match full header block + query
    # Pattern: divider, rule name, optional MITRE line, divider, then SPL lines
    style_a = re.finditer(
        r"# [=]{30,}\n"           # opening divider
        r"# (?P<name>[^\n]+)\n"   # rule name
        r"(?:# MITRE: (?P<mitre>T\d{4}(?:\.\d{3})?)\n)?"  # optional MITRE
        r"# [=]{30,}\n"           # closing divider
        r"(?P<spl>(?:(?!# [=]{30,})[\s\S])*?)"  # SPL (stops at next divider or style-b header or EOF)
        r"(?=# [=]{30,}|# [A-Z][^\n]+ - T\d{4}|\Z)",
        text,
    )
    found_a = False
    for m in style_a:
        rule_name = m.group("name").strip()
        # Skip file-level headers
        if re.match(r"(HawkinsOps|Author|Updated|COLLECTION|EXFILTRATION|IMPACT)", rule_name):
            continue
        mitre = m.group("mitre") or ""
        search = m.group("spl").strip()
        # Strip inline comments
        search = "\n".join(l for l in search.splitlines() if not l.strip().startswith("#"))
        search = search.strip()
        if not search:
            continue
        found_a = True
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", rule_name).strip("_")
        description = f"HawkinsOps | {tactic} | {rule_name}"
        if mitre:
            description += f" | {mitre}"
        rules.append({
            "name": f"HawkinsOps_{slug}",
            "rule_name": rule_name,
            "mitre": mitre,
            "description": description,
            "search": search,
            "tactic": tactic,
        })

    if found_a:
        return rules

    # Style B: "# Rule Name - T####\n<SPL>\n\n"
    style_b = re.finditer(
        r"# (?P<name>[^\n]+?) - (?P<mitre>T\d{4}(?:\.\d{3})?)\n"
        r"(?P<spl>(?:(?!# ).+\n?)+)",
        text,
    )
    for m in style_b:
        rule_name = m.group("name").strip()
        mitre = m.group("mitre")
        search = m.group("spl").strip()
        if not search:
            continue
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", rule_name).strip("_")
        description = f"HawkinsOps | {tactic} | {rule_name} | {mitre}"
        rules.append({
            "name": f"HawkinsOps_{slug}",
            "rule_name": rule_name,
            "mitre": mitre,
            "description": description,
            "search": search,
            "tactic": tactic,
        })

    return rules


def search_exists(name: str) -> bool:
    try:
        result = splunk_request(
            "GET",
            f"/servicesNS/{SPLUNK_USER}/{APP}/saved/searches/{urllib.parse.quote(name)}?output_mode=json"
        )
        return bool(result.get("entry"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def deploy_rule(rule: dict, dry_run: bool = False) -> str:
    name = rule["name"]
    if dry_run:
        return f"[DRY RUN] Would deploy: {name}"

    payload = {
        "name": name,
        "search": rule["search"],
        "description": rule["description"],
        "is_scheduled": "0",
        "output_mode": "json",
    }

    exists = search_exists(name)

    if exists:
        # Update existing
        endpoint = f"/servicesNS/{SPLUNK_USER}/{APP}/saved/searches/{urllib.parse.quote(name)}"
        update_payload = {k: v for k, v in payload.items() if k != "name"}
        update_payload["output_mode"] = "json"
        splunk_request("POST", endpoint, update_payload)
        return f"  updated  {name}"
    else:
        # Create new
        endpoint = f"/servicesNS/{SPLUNK_USER}/{APP}/saved/searches"
        try:
            splunk_request("POST", endpoint, payload)
            return f"  created  {name}"
        except Exception:
            result = splunk_request("POST", endpoint, payload)
            if result.get("_conflict"):
                return f"  conflict {name} (already exists)"
            raise


def main():
    dry_run = "--dry-run" in sys.argv
    spl_files = sorted(SPL_DIR.glob("*.spl"))

    if not spl_files:
        print(f"No .spl files found in {SPL_DIR}", file=sys.stderr)
        sys.exit(1)

    total_deployed = 0
    total_failed = 0

    for spl_file in spl_files:
        rules = parse_spl_file(spl_file)
        print(f"\n{spl_file.name}  ({len(rules)} rules)")
        for rule in rules:
            try:
                status = deploy_rule(rule, dry_run=dry_run)
                print(f"  {status}")
                total_deployed += 1
            except Exception as exc:
                print(f"  FAILED   {rule['name']}: {exc}", file=sys.stderr)
                total_failed += 1

    print(f"\n{'-'*50}")
    print(f"Deployed: {total_deployed}  |  Failed: {total_failed}")
    if dry_run:
        print("(dry run — no changes made)")
    sys.exit(1 if total_failed else 0)


if __name__ == "__main__":
    main()
