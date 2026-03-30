#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from common import CASES_ROOT, LEDGER_PATH, OUTPUT_ROOT, POLICY_PATH, load_ledger, load_yaml_json, save_ledger, utc_now


def extract_rule_id(case_id: str) -> str:
    match = re.search(r"__rule(\d+)__", str(case_id))
    return match.group(1) if match else ""


def load_review_rule_ids() -> set[str]:
    policy = load_yaml_json(POLICY_PATH, {})
    return {str(x) for x in policy.get("review_rule_ids", [])}


def write_summary(case_dir: Path, disposition: str, reason: str, processed_utc: str) -> None:
    triage_path = case_dir / "triage.json"
    if not triage_path.exists():
        return
    triage = json.loads(triage_path.read_text(encoding="utf-8"))
    triage["disposition"] = disposition
    triage["reason"] = reason
    triage["status"] = "PROCESSED"
    triage["processed_utc"] = processed_utc
    triage["retroactive_reclassify_utc"] = processed_utc
    triage_path.write_text(json.dumps(triage, indent=2), encoding="utf-8")

    summary = {
        "case_id": triage.get("case_id", case_dir.name),
        "disposition": disposition,
        "reason": reason,
        "processed_utc": processed_utc,
        "note": "Retroactive backlog cleanup reclassified this pending escalation into the review lane.",
    }
    (case_dir / "disposition_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (case_dir / "review_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Retroactively reclassify pending staged ESCALATE backlog into REVIEW when policy now defines those rules as review-tier.")
    parser.add_argument("--execute", action="store_true", help="Write changes to ledger and case triage files.")
    args = parser.parse_args()

    ledger = load_ledger()
    review_rule_ids = load_review_rule_ids()
    cases: List[Dict[str, Any]] = ledger.get("cases", [])
    targets: List[Dict[str, Any]] = []

    for case in cases:
        if str(case.get("disposition", "")).upper() != "ESCALATE":
            continue
        if str(case.get("status", "")).upper() != "TRIAGED":
            continue
        if case.get("repo_path"):
            continue
        case_id = str(case.get("case_id", ""))
        if not case_id:
            continue
        rule_id = extract_rule_id(case_id)
        if rule_id not in review_rule_ids:
            continue
        targets.append(case)

    out = {
        "generated_utc": utc_now(),
        "execute": bool(args.execute),
        "review_rule_ids_count": len(review_rule_ids),
        "target_count": len(targets),
        "target_rule_counts": {},
        "sample_case_ids": [str(c.get("case_id", "")) for c in targets[:25]],
    }

    rule_counts: Dict[str, int] = {}
    for case in targets:
        rule_id = extract_rule_id(str(case.get("case_id", "")))
        rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
    out["target_rule_counts"] = dict(sorted(rule_counts.items(), key=lambda kv: (-kv[1], kv[0])))

    report_json = OUTPUT_ROOT / "retroactive_review_backlog_cleanup_latest.json"
    report_md = OUTPUT_ROOT / "retroactive_review_backlog_cleanup_latest.md"

    if args.execute and targets:
        processed_utc = utc_now()
        metrics = ledger.setdefault("metrics", {})
        metrics["escalated"] = max(0, int(metrics.get("escalated", 0)) - len(targets))
        metrics["review"] = int(metrics.get("review", 0)) + len(targets)

        for case in targets:
            case["disposition"] = "REVIEW"
            case["status"] = "PROCESSED"
            case["updated_utc"] = processed_utc
            case["retroactive_reclassify_utc"] = processed_utc
            case_id = str(case.get("case_id", ""))
            write_summary(CASES_ROOT / case_id, "REVIEW", "retroactive backlog cleanup: rule now in review tier", processed_utc)

        save_ledger(ledger)
        out["executed_utc"] = processed_utc

    report_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    lines = [
        "# Retroactive Review Backlog Cleanup",
        "",
        f"- Generated UTC: {out['generated_utc']}",
        f"- Execute: {out['execute']}",
        f"- Target count: {out['target_count']}",
        "",
        "## Rule Counts",
        "",
    ]
    if out["target_rule_counts"]:
        for rule_id, count in out["target_rule_counts"].items():
            lines.append(f"- rule {rule_id}: {count}")
    else:
        lines.append("- none")
    lines.extend(["", "## Sample Case IDs", ""])
    if out["sample_case_ids"]:
        for case_id in out["sample_case_ids"]:
            lines.append(f"- `{case_id}`")
    else:
        lines.append("- none")
    report_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"TARGET_COUNT={out['target_count']}")
    print(f"REPORT_JSON={report_json}")
    print(f"REPORT_MD={report_md}")


if __name__ == "__main__":
    main()
