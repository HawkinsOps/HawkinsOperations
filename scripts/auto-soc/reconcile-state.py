#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from common import OUTPUT_ROOT, REPO_ROOT_DEFAULT, load_ledger, utc_now, write_json


def load_content_incidents(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"incidents": []}
    return json.loads(path.read_text(encoding="utf-8"))


def unique_sorted(values: List[str]) -> List[str]:
    return sorted(set(values))


def is_autosoc_case_id(case_id: str) -> bool:
    # AutoSOC case IDs include a suffix segment after description:
    # YYYY-MM-DD__agent__rule12345__description__event-or-seq
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}__.+__rule\d+__.+__.+$", str(case_id)))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reconcile AutoSOC ledger escalations with repo incident folders and content/incidents.json."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT_DEFAULT)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any mismatch is detected.",
    )
    args = parser.parse_args()

    ledger = load_ledger()
    cases = ledger.get("cases", [])
    escalated = [c for c in cases if c.get("disposition") == "ESCALATE"]

    ledger_escalate_ids = unique_sorted([str(c.get("case_id", "")) for c in escalated if c.get("case_id")])
    ledger_escalated_status_ids = unique_sorted(
        [str(c.get("case_id", "")) for c in escalated if c.get("status") == "ESCALATED" and c.get("case_id")]
    )
    pending_escalate_ids = unique_sorted([x for x in ledger_escalate_ids if x not in ledger_escalated_status_ids])
    staging_root = OUTPUT_ROOT / "escalation_staging"
    staged_pending_ids = unique_sorted(
        [case_id for case_id in pending_escalate_ids if (staging_root / f"{case_id}.json").exists()]
    )
    unstaged_pending_ids = unique_sorted([x for x in pending_escalate_ids if x not in staged_pending_ids])
    missing_repo_path_ids = unique_sorted(
        [str(c.get("case_id", "")) for c in escalated if c.get("status") == "ESCALATED" and not c.get("repo_path") and c.get("case_id")]
    )

    # Published AutoSOC incidents live under content/incident-response/incidents in the portfolio repo.
    # Keep a fallback to the older incident-response/incidents layout so historical or transitional
    # repo structures do not silently break reconciliation.
    incident_roots = [
        args.repo_root / "content" / "incident-response" / "incidents",
        args.repo_root / "incident-response" / "incidents",
    ]
    repo_ids: List[str] = []
    for incidents_root in incident_roots:
        if not incidents_root.exists():
            continue
        for year_dir in incidents_root.iterdir():
            if not year_dir.is_dir():
                continue
            for case_dir in year_dir.iterdir():
                if case_dir.is_dir():
                    repo_ids.append(case_dir.name)
    repo_ids = unique_sorted(repo_ids)

    content_path = args.repo_root / "content" / "incidents.json"
    content_data = load_content_incidents(content_path)
    content_ids = unique_sorted([str(i.get("id", "")) for i in content_data.get("incidents", []) if i.get("id")])

    # Reconciliation scope should cover active AutoSOC-tracked incidents:
    # IDs referenced by ledger escalations and/or content index.
    repo_ids_autosoc = unique_sorted(
        [x for x in repo_ids if is_autosoc_case_id(x) and (x in content_ids or x in ledger_escalated_status_ids)]
    )

    in_ledger_not_repo = unique_sorted([x for x in ledger_escalated_status_ids if x not in repo_ids_autosoc])
    in_repo_not_ledger = unique_sorted([x for x in repo_ids_autosoc if x not in ledger_escalated_status_ids])
    in_ledger_not_content = unique_sorted([x for x in ledger_escalated_status_ids if x not in content_ids])
    in_content_not_ledger = unique_sorted([x for x in content_ids if x not in ledger_escalated_status_ids])
    in_repo_not_content = unique_sorted([x for x in repo_ids_autosoc if x not in content_ids])
    in_content_not_repo = unique_sorted([x for x in content_ids if x not in repo_ids_autosoc])

    counts = {
        "ledger_total_cases": int(ledger.get("metrics", {}).get("total_cases", 0)),
        "ledger_escalated_metric": int(ledger.get("metrics", {}).get("escalated", 0)),
        "ledger_escalate_ids": len(ledger_escalate_ids),
        "ledger_escalated_status_ids": len(ledger_escalated_status_ids),
        "ledger_pending_escalate_ids": len(pending_escalate_ids),
        "ledger_pending_escalate_ids_staged": len(staged_pending_ids),
        "ledger_pending_escalate_ids_unstaged": len(unstaged_pending_ids),
        "ledger_escalated_missing_repo_path": len(missing_repo_path_ids),
        "repo_incident_dirs": len(repo_ids),
        "repo_incident_dirs_autosoc_scoped": len(repo_ids_autosoc),
        "content_incidents": len(content_ids),
    }

    mismatches = {
        "in_ledger_not_repo": in_ledger_not_repo,
        "in_repo_not_ledger": in_repo_not_ledger,
        "in_ledger_not_content": in_ledger_not_content,
        "in_content_not_ledger": in_content_not_ledger,
        "in_repo_not_content": in_repo_not_content,
        "in_content_not_repo": in_content_not_repo,
        "ledger_escalated_missing_repo_path_ids": missing_repo_path_ids,
        "ledger_pending_escalate_ids": unstaged_pending_ids,
        "ledger_pending_escalate_ids_staged_under_contract": staged_pending_ids,
    }
    # Treat the live AutoSOC contract as forward-looking:
    # - escalations that should already be published must reconcile to repo/content
    # - pending escalations must at least be staged under contract
    # Historical repo/content incidents that are not present in the current live
    # ledger are expected and should remain visible in the report, but they are
    # not hard failures for the active runtime health signal.
    hard_mismatch_keys = [
        "in_ledger_not_repo",
        "in_ledger_not_content",
        "ledger_escalated_missing_repo_path_ids",
        "ledger_pending_escalate_ids",
    ]
    mismatch_count = sum(len(mismatches[key]) for key in hard_mismatch_keys)

    report = {
        "generated_utc": utc_now(),
        "repo_root": str(args.repo_root),
        "counts": counts,
        "mismatch_count": mismatch_count,
        "mismatches": mismatches,
    }

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_ROOT / "reconciliation_latest.json"
    md_path = OUTPUT_ROOT / "reconciliation_latest.md"
    write_json(json_path, report)

    lines = [
        "# AutoSOC Reconciliation",
        "",
        f"- Generated UTC: {report['generated_utc']}",
        f"- Repo root: `{report['repo_root']}`",
        "",
        "## Counts",
        "",
    ]
    for k, v in counts.items():
        lines.append(f"- {k}: {v}")
    lines.extend(["", f"## Mismatch Summary", "", f"- mismatch_count: {mismatch_count}", ""])
    for key, values in mismatches.items():
        lines.append(f"### {key} ({len(values)})")
        if values:
            for item in values[:25]:
                lines.append(f"- `{item}`")
            if len(values) > 25:
                lines.append(f"- ... +{len(values) - 25} more")
        else:
            lines.append("- none")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"RECONCILE_JSON={json_path}")
    print(f"RECONCILE_MD={md_path}")
    print(f"MISMATCH_COUNT={mismatch_count}")
    if args.strict and mismatch_count > 0:
        raise SystemExit(5)


if __name__ == "__main__":
    main()
