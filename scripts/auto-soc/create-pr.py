#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from common import OUTPUT_ROOT, REPO_ROOT_DEFAULT, load_ledger, save_ledger, utc_now


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_incidents_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        data = {"incidents": []}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data
    return json.loads(path.read_text(encoding="utf-8"))


def run_cmd(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


def assert_no_absolute_paths(pack_dir: Path) -> None:
    leaks = []
    abs_path = re.compile(r"[A-Za-z]:(?:\\|/)")
    for file_path in pack_dir.rglob("*"):
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(text.splitlines(), start=1):
            if abs_path.search(line) or "C:\\RH\\" in line or "C:/RH/" in line:
                leaks.append(f"{file_path}:{i}: {line.strip()}")
                if len(leaks) >= 10:
                    break
        if len(leaks) >= 10:
            break
    if leaks:
        raise RuntimeError(
            "Absolute path leak detected in pack. Refusing repo copy:\n"
            + "\n".join(leaks)
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Create incident repo artifact and optional GitHub PR.")
    parser.add_argument("--case-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT_DEFAULT)
    parser.add_argument("--open-pr", action="store_true", help="Create branch/commit/push/PR.")
    parser.add_argument(
        "--allow-repo-copy",
        action="store_true",
        help="Allow writing escalation artifacts directly into portfolio repo (disabled by default).",
    )
    args = parser.parse_args()

    case_dir = args.case_dir
    triage = load_json(case_dir / "triage.json")
    if triage.get("disposition") != "ESCALATE":
        print("SKIP_PR=TRUE")
        print("REASON=Disposition is not ESCALATE")
        return

    case_id = triage["case_id"]
    year = case_id[:4]
    pack_dir = case_dir / "pack"
    if not pack_dir.exists():
        raise RuntimeError(f"Missing pack directory: {pack_dir}")
    assert_no_absolute_paths(pack_dir)

    # Enforce publish-bundle contract by default: no direct runtime->repo writes.
    if not args.allow_repo_copy:
        staging_dir = OUTPUT_ROOT / "escalation_staging"
        staging_dir.mkdir(parents=True, exist_ok=True)
        staging_path = staging_dir / f"{case_id}.json"
        staging = {
            "generated_utc": utc_now(),
            "case_id": case_id,
            "disposition": "ESCALATE",
            "case_dir": str(case_dir),
            "pack_dir": str(pack_dir),
            "repo_root": str(args.repo_root),
            "contract": "repo_write_blocked_by_default_use_publish_bundle_promotion",
        }
        staging_path.write_text(json.dumps(staging, indent=2), encoding="utf-8")
        if args.open_pr:
            raise RuntimeError(
                "--open-pr requires --allow-repo-copy under current contract. "
                "Use publish bundle promotion path for curated repo updates."
            )
        print("PR_READY=TRUE")
        print("REPO_COPY=BLOCKED_BY_CONTRACT")
        print(f"ESCALATION_STAGING={staging_path}")
        return

    dest = args.repo_root / "incident-response" / "incidents" / year / case_id
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(pack_dir, dest, dirs_exist_ok=True)

    incidents_path = args.repo_root / "content" / "incidents.json"
    incidents = ensure_incidents_json(incidents_path)
    entry = {
        "id": case_id,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "status": "ESCALATED",
        "path": f"incident-response/incidents/{year}/{case_id}",
    }
    existing = incidents.setdefault("incidents", [])
    replaced = False
    for i, inc in enumerate(existing):
        if inc.get("id") == case_id:
            existing[i] = entry
            replaced = True
            break
    if not replaced:
        existing.append(entry)
    incidents_path.write_text(json.dumps(incidents, indent=2), encoding="utf-8")

    ledger = load_ledger()
    for c in ledger.get("cases", []):
        if c.get("case_id") == case_id:
            c["status"] = "ESCALATED"
            c["repo_path"] = str(dest)
            c["updated_utc"] = utc_now()
    save_ledger(ledger)

    if not args.open_pr:
        print(f"PR_READY=TRUE")
        print(f"REPO_DEST={dest}")
        return

    branch = f"autosoc/{case_id}"
    title = f"AutoSOC: escalate {case_id}"
    body = f"Automated escalation for case `{case_id}`."
    run_cmd(["git", "checkout", "-b", branch], args.repo_root)
    run_cmd(["git", "add", str(dest), str(incidents_path)], args.repo_root)
    run_cmd(["git", "commit", "-m", f"Add: AutoSOC escalated case {case_id}"], args.repo_root)
    run_cmd(["git", "push", "-u", "origin", branch], args.repo_root)
    run_cmd(["gh", "pr", "create", "--title", title, "--body", body, "--base", "main", "--head", branch], args.repo_root)

    print("PR_CREATED=TRUE")


if __name__ == "__main__":
    main()
