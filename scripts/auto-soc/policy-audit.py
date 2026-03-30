#!/usr/bin/env python3
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

from common import KNOWN_FPS_PATH, OUTPUT_ROOT, POLICY_PATH, PROCESSED_ROOT, load_yaml_json, utc_now
from triage import determine_disposition


def read_alert(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Weekly policy audit for AutoSOC triage tuning.")
    parser.add_argument("--max-files", type=int, default=500, help="Recent processed alert files to inspect.")
    parser.add_argument("--min-recommend-count", type=int, default=5, help="Recommend classification when count >= N.")
    parser.add_argument("--out-md", type=Path, default=OUTPUT_ROOT / "policy_audit_latest.md")
    parser.add_argument("--out-json", type=Path, default=OUTPUT_ROOT / "policy_audit_latest.json")
    args = parser.parse_args()

    policy = load_yaml_json(POLICY_PATH, {})
    known_fps = load_yaml_json(KNOWN_FPS_PATH, {"rules": []}).get("rules", [])

    files = sorted(
        [p for p in PROCESSED_ROOT.glob("*.json") if not p.name.startswith(".cursor") and not p.name.startswith(".")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[: args.max_files]

    totals = Counter()
    by_rule = defaultdict(lambda: {"count": 0, "max_level": 0, "agents": Counter(), "desc": ""})
    by_bucket_rule = defaultdict(Counter)
    by_bucket_group = defaultdict(Counter)
    unclassified = Counter()

    for f in files:
        alert = read_alert(f)
        rule_id = str(alert.get("rule", {}).get("id", ""))
        level = int(alert.get("rule", {}).get("level", 0) or 0)
        agent = str(alert.get("agent", {}).get("name", ""))
        desc = str(alert.get("rule", {}).get("description", ""))
        groups = alert.get("rule", {}).get("groups", [])
        if isinstance(groups, str):
            groups = [g.strip() for g in groups.split(",") if g.strip()]
        if not rule_id and not desc:
            continue

        rec = by_rule[rule_id]
        rec["count"] += 1
        rec["max_level"] = max(rec["max_level"], level)
        rec["agents"][agent] += 1
        rec["desc"] = desc

        disposition, _reason = determine_disposition(alert, policy, known_fps)
        bucket = "unclassified"
        if disposition == "AUTO_CLOSE_KNOWN_FP":
            totals["known_fp"] += 1
            bucket = "known_fp"
        elif disposition == "AUTO_CLOSE_BENIGN":
            totals["auto_close"] += 1
            bucket = "auto_close"
        elif disposition == "REVIEW":
            totals["review"] += 1
            bucket = "review"
        elif disposition == "ESCALATE":
            totals["always_escalate"] += 1
            bucket = "always_escalate"
        else:
            totals["unclassified"] += 1
            unclassified[rule_id] += 1
        by_bucket_rule[bucket][rule_id] += 1
        for g in groups:
            by_bucket_group[bucket][str(g).lower()] += 1

    recommendations = []
    for rid, count in unclassified.most_common():
        if count < args.min_recommend_count:
            continue
        info = by_rule[rid]
        recommended_bucket = "review_rule_ids"
        if info["max_level"] >= 12:
            recommended_bucket = "always_escalate_rule_ids"
        elif info["max_level"] <= 3:
            recommended_bucket = "auto_close_rule_ids"
        recommendations.append(
            {
                "rule_id": rid,
                "count": count,
                "max_level": info["max_level"],
                "description": info["desc"],
                "top_agent": info["agents"].most_common(1)[0][0] if info["agents"] else "",
                "recommended_bucket": recommended_bucket,
            }
        )

    candidate_suppressions = [
        r for r in recommendations if r.get("recommended_bucket") == "auto_close_rule_ids"
    ][:10]
    candidate_always_escalate = [
        r for r in recommendations if r.get("recommended_bucket") == "always_escalate_rule_ids"
    ][:10]

    out_json = {
        "generated_utc": utc_now(),
        "source_files": len(files),
        "totals": dict(totals),
        "top_by_bucket_rule": {
            bucket: counter.most_common(10) for bucket, counter in by_bucket_rule.items()
        },
        "top_by_bucket_group": {
            bucket: counter.most_common(10) for bucket, counter in by_bucket_group.items()
        },
        "top_rules": [
            {
                "rule_id": rid,
                "count": info["count"],
                "max_level": info["max_level"],
                "description": info["desc"],
                "top_agents": info["agents"].most_common(3),
            }
            for rid, info in sorted(by_rule.items(), key=lambda kv: kv[1]["count"], reverse=True)[:25]
        ],
        "recommendations": recommendations,
        "candidate_suppressions": candidate_suppressions,
        "candidate_always_escalate": candidate_always_escalate,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out_json, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# AutoSOC Policy Audit")
    lines.append("")
    lines.append(f"- Generated UTC: {out_json['generated_utc']}")
    lines.append(f"- Processed alerts reviewed: {out_json['source_files']}")
    lines.append(f"- Known FP classified: {totals.get('known_fp', 0)}")
    lines.append(f"- Always-escalate classified: {totals.get('always_escalate', 0)}")
    lines.append(f"- Auto-close classified: {totals.get('auto_close', 0)}")
    lines.append(f"- Review-tier classified: {totals.get('review', 0)}")
    lines.append(f"- Unclassified: {totals.get('unclassified', 0)}")
    lines.append("")
    lines.append("## Weekly Tuning Signal")
    lines.append("Top 10 always-escalate rules:")
    for rid, cnt in out_json["top_by_bucket_rule"].get("always_escalate", []):
        lines.append(f"- Rule {rid}: {cnt}")
    if not out_json["top_by_bucket_rule"].get("always_escalate"):
        lines.append("- none")
    lines.append("")
    lines.append("Top 10 auto-close rules:")
    for rid, cnt in out_json["top_by_bucket_rule"].get("auto_close", []):
        lines.append(f"- Rule {rid}: {cnt}")
    if not out_json["top_by_bucket_rule"].get("auto_close"):
        lines.append("- none")
    lines.append("")
    lines.append("Top 10 always-escalate groups:")
    for grp, cnt in out_json["top_by_bucket_group"].get("always_escalate", []):
        lines.append(f"- Group {grp}: {cnt}")
    if not out_json["top_by_bucket_group"].get("always_escalate"):
        lines.append("- none")
    lines.append("")
    lines.append("Top 10 auto-close groups:")
    for grp, cnt in out_json["top_by_bucket_group"].get("auto_close", []):
        lines.append(f"- Group {grp}: {cnt}")
    if not out_json["top_by_bucket_group"].get("auto_close"):
        lines.append("- none")
    lines.append("")
    lines.append("## Recommended Rule Classification Updates")
    if not recommendations:
        lines.append("- No recommendations above threshold.")
    else:
        for r in recommendations:
            lines.append(
                f"- Rule {r['rule_id']} (count={r['count']}, max_level={r['max_level']}, "
                f"top_agent={r['top_agent']}): add to `{r['recommended_bucket']}`"
            )
    lines.append("")
    lines.append("## Candidate Suppressions (top 10)")
    if not candidate_suppressions:
        lines.append("- none")
    else:
        for r in candidate_suppressions:
            lines.append(f"- Rule {r['rule_id']} (count={r['count']}, max_level={r['max_level']})")
    lines.append("")
    lines.append("## Candidate Always-Escalate Adds (top 10)")
    if not candidate_always_escalate:
        lines.append("- none")
    else:
        for r in candidate_always_escalate:
            lines.append(f"- Rule {r['rule_id']} (count={r['count']}, max_level={r['max_level']})")
    lines.append("")
    lines.append("## Top Rules")
    for item in out_json["top_rules"][:10]:
        lines.append(f"- {item['rule_id']}: count={item['count']}, max_level={item['max_level']} - {item['description']}")

    args.out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"AUDIT_MD={args.out_md}")
    print(f"AUDIT_JSON={args.out_json}")
    print(f"RECOMMENDATIONS={len(recommendations)}")


if __name__ == "__main__":
    main()
