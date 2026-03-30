#!/usr/bin/env python3
import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from common import CASES_ROOT, LOGS_ROOT, utc_now


def parse_dt(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def read_triage(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_window_stats(triage_files: List[Path], start_dt: datetime, end_dt: datetime, top_n: int) -> Dict[str, Any]:
    rows: List[Dict[str, str]] = []
    disp_counts = Counter()
    rule_counts = Counter()
    reason_counts = Counter()

    for path in triage_files:
        t = read_triage(path)
        created_utc = str(t.get("created_utc", "")).strip()
        if not created_utc:
            continue
        try:
            created_dt = parse_dt(created_utc)
        except ValueError:
            continue
        if created_dt < start_dt or created_dt >= end_dt:
            continue

        rule_id = str(t.get("rule", {}).get("id", ""))
        disposition = str(t.get("disposition", ""))
        reason = str(t.get("reason", ""))
        case_id = str(t.get("case_id", ""))

        rows.append(
            {
                "case_id": case_id,
                "rule_id": rule_id,
                "disposition": disposition,
                "reason": reason,
                "created_utc": created_utc,
            }
        )
        disp_counts[disposition] += 1
        rule_counts[rule_id] += 1
        reason_counts[reason] += 1

    total = sum(disp_counts.values())
    escalated = disp_counts.get("ESCALATE", 0)
    review = disp_counts.get("REVIEW", 0)
    auto_closed_benign = disp_counts.get("AUTO_CLOSE_BENIGN", 0)
    auto_closed_known_fp = disp_counts.get("AUTO_CLOSE_KNOWN_FP", 0)
    escalation_rate = round((escalated / total) * 100, 2) if total else 0.0

    return {
        "window_start_utc": start_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "window_end_utc": end_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "totals": {
            "cases": total,
            "escalated": escalated,
            "review": review,
            "auto_closed_benign": auto_closed_benign,
            "auto_closed_known_fp": auto_closed_known_fp,
            "escalation_rate_pct": escalation_rate,
        },
        "top_rules": [{"rule_id": rid, "count": cnt} for rid, cnt in rule_counts.most_common(top_n)],
        "top_reasons": [{"reason": reason, "count": cnt} for reason, cnt in reason_counts.most_common(top_n)],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate daily AutoSOC triage quality report.")
    parser.add_argument("--window-hours", type=int, default=24, help="Include triage records from the last N hours.")
    parser.add_argument("--top-n", type=int, default=15, help="Top N noisy rules to list.")
    parser.add_argument(
        "--compare-previous",
        action="store_true",
        help="Compare current window with the immediately previous window of the same size.",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Write a chart-ready summary CSV row (append mode) for trend tracking.",
    )
    parser.add_argument(
        "--csv-path",
        type=Path,
        default=None,
        help="Optional CSV output path. Defaults to out-dir/autosoc-triage-quality-history.csv",
    )
    parser.add_argument("--out-dir", type=Path, default=LOGS_ROOT.parent / "Reports")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    window_hours = max(1, args.window_hours)
    current_start = now - timedelta(hours=window_hours)
    current_end = now

    triage_files = list(CASES_ROOT.rglob("triage.json"))
    current = compute_window_stats(triage_files, current_start, current_end, args.top_n)
    previous = None
    deltas = None
    if args.compare_previous:
        previous_start = current_start - timedelta(hours=window_hours)
        previous_end = current_start
        previous = compute_window_stats(triage_files, previous_start, previous_end, args.top_n)
        deltas = {
            "cases": current["totals"]["cases"] - previous["totals"]["cases"],
            "escalated": current["totals"]["escalated"] - previous["totals"]["escalated"],
            "review": current["totals"]["review"] - previous["totals"]["review"],
            "auto_closed_benign": current["totals"]["auto_closed_benign"] - previous["totals"]["auto_closed_benign"],
            "auto_closed_known_fp": current["totals"]["auto_closed_known_fp"] - previous["totals"]["auto_closed_known_fp"],
            "escalation_rate_pct": round(
                current["totals"]["escalation_rate_pct"] - previous["totals"]["escalation_rate_pct"], 2
            ),
        }

    payload = {
        "generated_utc": utc_now(),
        "window_hours": window_hours,
        "current": current,
        "previous": previous,
        "deltas": deltas,
    }

    stamp = now.strftime("%m-%d-%Y")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_json = args.out_dir / f"autosoc-triage-quality-{stamp}.json"
    out_md = args.out_dir / f"autosoc-triage-quality-{stamp}.md"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# AutoSOC Triage Quality Report")
    lines.append("")
    lines.append(f"- Generated UTC: {payload['generated_utc']}")
    lines.append(f"- Window: last {window_hours} hours")
    lines.append(f"- Total triaged: {current['totals']['cases']}")
    lines.append(f"- Escalated: {current['totals']['escalated']}")
    lines.append(f"- Review: {current['totals']['review']}")
    lines.append(f"- Auto-closed benign: {current['totals']['auto_closed_benign']}")
    lines.append(f"- Auto-closed known FP: {current['totals']['auto_closed_known_fp']}")
    lines.append(f"- Escalation rate: {current['totals']['escalation_rate_pct']}%")
    if deltas is not None:
        lines.append("")
        lines.append("## Comparison vs Previous Window")
        lines.append(f"- Cases delta: {deltas['cases']:+d}")
        lines.append(f"- Escalated delta: {deltas['escalated']:+d}")
        lines.append(f"- Review delta: {deltas['review']:+d}")
        lines.append(f"- Auto-closed benign delta: {deltas['auto_closed_benign']:+d}")
        lines.append(f"- Auto-closed known FP delta: {deltas['auto_closed_known_fp']:+d}")
        lines.append(f"- Escalation rate delta: {deltas['escalation_rate_pct']:+.2f} pts")
    lines.append("")
    lines.append("## Top Rules")
    for item in current["top_rules"]:
        lines.append(f"- Rule {item['rule_id']}: {item['count']}")
    lines.append("")
    lines.append("## Top Reasons")
    for item in current["top_reasons"]:
        lines.append(f"- {item['reason']}: {item['count']}")

    out_md.write_text("\n".join(lines), encoding="utf-8")

    csv_path = args.csv_path if args.csv_path else args.out_dir / "autosoc-triage-quality-history.csv"
    if args.csv:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "generated_utc": payload["generated_utc"],
            "window_hours": window_hours,
            "current_cases": current["totals"]["cases"],
            "current_escalated": current["totals"]["escalated"],
            "current_review": current["totals"]["review"],
            "current_auto_closed_benign": current["totals"]["auto_closed_benign"],
            "current_auto_closed_known_fp": current["totals"]["auto_closed_known_fp"],
            "current_escalation_rate_pct": current["totals"]["escalation_rate_pct"],
            "delta_cases": (deltas or {}).get("cases", 0),
            "delta_escalated": (deltas or {}).get("escalated", 0),
            "delta_review": (deltas or {}).get("review", 0),
            "delta_auto_closed_benign": (deltas or {}).get("auto_closed_benign", 0),
            "delta_auto_closed_known_fp": (deltas or {}).get("auto_closed_known_fp", 0),
            "delta_escalation_rate_pct": (deltas or {}).get("escalation_rate_pct", 0.0),
        }
        write_header = not csv_path.exists() or csv_path.stat().st_size == 0
        with csv_path.open("a", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(row.keys()))
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    print(f"QUALITY_MD={out_md}")
    print(f"QUALITY_JSON={out_json}")
    if args.csv:
        print(f"QUALITY_CSV={csv_path}")
    print(f"QUALITY_TOTAL={current['totals']['cases']}")
    print(f"QUALITY_ESCALATION_RATE={current['totals']['escalation_rate_pct']}")
    if deltas is not None:
        print(f"QUALITY_ESCALATION_RATE_DELTA={deltas['escalation_rate_pct']:+.2f}")


if __name__ == "__main__":
    main()
