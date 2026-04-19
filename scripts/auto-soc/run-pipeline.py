#!/usr/bin/env python3
import argparse
import ctypes
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from common import CASES_ROOT, LEDGER_PATH, LOGS_ROOT, OUTPUT_ROOT, QUEUE_ROOT, ensure_dirs, read_json, utc_now, write_json


SCRIPT_DIR = Path(__file__).resolve().parent
LOCK_PATH = OUTPUT_ROOT / "pipeline.lock.json"
RUN_METRICS_PATH = OUTPUT_ROOT / "run_metrics_latest.json"
RUN_METRICS_HISTORY_PATH = OUTPUT_ROOT / "run_metrics_history.jsonl"
HEARTBEAT_PATH = OUTPUT_ROOT / "heartbeat.json"
HEARTBEAT_HISTORY_PATH = OUTPUT_ROOT / "heartbeat_history.jsonl"
RECONCILE_JSON_PATH = OUTPUT_ROOT / "reconciliation_latest.json"
COVERAGE_JSON_PATH = OUTPUT_ROOT / "coverage_latest.json"

# Per-step subprocess guardrails. The timeout is the hard last-resort kill;
# the warn threshold is an early-detection signal (structured log only, no kill).
# Sized after the 2026-04-18 redact-hang incident: 600s = 2 scheduler intervals,
# generous enough for legitimate batch cases (seen: <1s on a 30-50 file case,
# ~60-90s projected worst-case at 5k files), tight enough that a hang gets
# surfaced within a single missed run rather than cascading for hours.
STEP_TIMEOUT_SECONDS = 600
STEP_WARN_SECONDS = 30


def hide_console_window() -> None:
    if os.name != "nt":
        return
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        # Window hiding is a UX improvement only; do not block the pipeline.
        pass


def run_step(cmd: list[str], log_path: Path) -> tuple[int, str]:
    start = time.monotonic()
    rc: int
    combined: str
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=STEP_TIMEOUT_SECONDS)
        combined = (proc.stdout or "") + (proc.stderr or "")
        rc = proc.returncode
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout if isinstance(e.stdout, str) else (e.stdout.decode("utf-8", errors="ignore") if e.stdout else "")
        stderr = e.stderr if isinstance(e.stderr, str) else (e.stderr.decode("utf-8", errors="ignore") if e.stderr else "")
        # subprocess.run already killed the child process at timeout; we just
        # record the elapsed time and surface a non-zero rc so the caller's
        # finalize("FAILED", <stage>, rc) path fires.
        combined = (
            f"STEP_TIMEOUT seconds={STEP_TIMEOUT_SECONDS} cmd={' '.join(cmd)}\n"
            f"{stdout}{stderr}"
        )
        rc = 124  # conventional timeout exit code
    elapsed = time.monotonic() - start
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"\n$ {' '.join(cmd)}\n")
        if elapsed >= STEP_WARN_SECONDS:
            log.write(f"STEP_SLOW elapsed_seconds={elapsed:.1f} threshold={STEP_WARN_SECONDS}\n")
        if combined:
            log.write(combined)
    return rc, combined


def parse_kv(output: str) -> dict[str, str]:
    kv: dict[str, str] = {}
    for raw in output.splitlines():
        line = raw.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        kv[key.strip()] = value.strip()
    return kv


def queue_depth() -> int:
    return len([p for p in QUEUE_ROOT.glob("*.json") if p.name != ".cursor.json"])


def metric(ledger: dict, key: str) -> int:
    try:
        return int(ledger.get("metrics", {}).get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0


def acquire_lock(lock_ttl_seconds: int) -> None:
    now = time.time()
    if LOCK_PATH.exists():
        try:
            data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
            started = float(data.get("started_epoch", 0))
            age = max(0, int(now - started))
            if age <= lock_ttl_seconds:
                raise RuntimeError(f"Existing pipeline lock detected (age={age}s): {LOCK_PATH}")
        except json.JSONDecodeError:
            pass
        # stale or malformed lock
        LOCK_PATH.unlink(missing_ok=True)

    lock = {
        "pid": os.getpid(),
        "started_utc": utc_now(),
        "started_epoch": now,
        "host": os.environ.get("COMPUTERNAME", ""),
    }
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    # O_EXCL to avoid race if two schedulers fire together.
    fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(lock, f, indent=2)
    except Exception:
        os.close(fd)
        raise


def release_lock() -> None:
    try:
        LOCK_PATH.unlink(missing_ok=True)
    except OSError:
        pass


def prune_old_logs(keep_days: int) -> int:
    if keep_days <= 0:
        return 0
    removed = 0
    cutoff = datetime.now().timestamp() - (keep_days * 86400)
    for path in LOGS_ROOT.glob("auto-soc-*.log"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1
        except OSError:
            # Do not fail pipeline just because an old log is locked.
            continue
    return removed


def main() -> None:
    hide_console_window()
    parser = argparse.ArgumentParser(description="AutoSOC orchestrator: poll -> triage -> redact -> assemble -> PR.")
    parser.add_argument("--sample-alert", type=Path, help="Optional local sample alert JSON for testing.")
    parser.add_argument("--open-pr", action="store_true", help="Attempt PR creation for escalated cases.")
    parser.add_argument(
        "--reconcile-only",
        action="store_true",
        help="Skip ingest/triage/pack stages and run only tests + reconciliation + coverage + heartbeat.",
    )
    parser.add_argument(
        "--mode",
        choices=["backfill", "realtime"],
        default="realtime",
        help="Poller mode (backfill cursor drain or realtime window).",
    )
    parser.add_argument(
        "--realtime-window-minutes",
        type=int,
        default=60,
        help="Lookback window for realtime mode.",
    )
    parser.add_argument("--skip-tests", action="store_true", help="Skip unittest preflight (not recommended).")
    parser.add_argument(
        "--reconcile-strict",
        dest="reconcile_strict",
        action="store_true",
        help="Fail run when ledger/repo/content reconciliation detects mismatches (default).",
    )
    parser.add_argument(
        "--no-reconcile-strict",
        dest="reconcile_strict",
        action="store_false",
        help="Emergency bypass for reconciliation strict failure gate.",
    )
    parser.add_argument(
        "--lock-ttl-seconds",
        type=int,
        default=5400,
        help="Treat an existing pipeline lock newer than this as active and abort.",
    )
    parser.add_argument("--log-retention-days", type=int, default=30, help="Delete auto-soc logs older than N days.")
    parser.add_argument(
        "--freshness-p95-max-seconds",
        type=int,
        default=3600,
        help="Freshness SLO threshold for poller p95 delay; heartbeat marks FAIL when exceeded.",
    )
    parser.add_argument(
        "--freshness-oldest-max-seconds",
        type=int,
        default=7200,
        help="Freshness SLO threshold for oldest event lag; heartbeat marks FAIL when exceeded.",
    )
    parser.set_defaults(reconcile_strict=False)
    args = parser.parse_args()

    ensure_dirs()
    acquire_lock(args.lock_ttl_seconds)
    LOGS_ROOT.mkdir(parents=True, exist_ok=True)
    removed = prune_old_logs(args.log_retention_days)
    log_path = LOGS_ROOT / f"auto-soc-{datetime.now().strftime('%m-%d-%Y')}.log"
    run_start = time.time()
    step_seconds: dict[str, float] = {}
    with log_path.open("a", encoding="utf-8") as log:
        log.write(
            f"RUN_UTC={datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')}\n"
        )
        log.write(f"LOG_PRUNE_REMOVED={removed}\n")
    run_id = f"autosoc-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{os.getpid()}"
    start_utc = utc_now()
    poll_kv: dict[str, str] = {}
    cases_processed = 0
    case_dirs_scanned = 0
    ledger_before = read_json(LEDGER_PATH, {"metrics": {}})
    queue_start = queue_depth()

    def finalize(status: str, fail_stage: str = "", exit_code: int = 0) -> None:
        run_seconds = round(time.time() - run_start, 3)
        ledger_after = read_json(LEDGER_PATH, {"metrics": {}})
        queue_end = queue_depth()
        pipeline_mode = "reconcile_only" if args.reconcile_only else "full"

        triaged = max(0, metric(ledger_after, "total_cases") - metric(ledger_before, "total_cases"))
        escalated = max(0, metric(ledger_after, "escalated") - metric(ledger_before, "escalated"))
        auto_benign = max(0, metric(ledger_after, "auto_closed_benign") - metric(ledger_before, "auto_closed_benign"))
        auto_known_fp = max(
            0, metric(ledger_after, "auto_closed_known_fp") - metric(ledger_before, "auto_closed_known_fp")
        )

        recon = read_json(RECONCILE_JSON_PATH, {})
        coverage = read_json(COVERAGE_JSON_PATH, {})
        mismatch_count = int(recon.get("mismatch_count", -1)) if recon else -1
        missing_hosts = int(coverage.get("missing_hosts", -1)) if coverage else -1
        present_hosts = int(coverage.get("present_hosts", -1)) if coverage else -1
        p95 = int(poll_kv.get("P95_DELAY_SECONDS", "-1") or -1) if poll_kv else -1
        lag_oldest = int(poll_kv.get("LAG_OLDEST_SECONDS", "-1") or -1) if poll_kv else -1
        freshness_status = "UNKNOWN"
        if p95 >= 0 or lag_oldest >= 0:
            freshness_status = "PASS"
            if p95 >= 0 and p95 > args.freshness_p95_max_seconds:
                freshness_status = "FAIL"
            if lag_oldest >= 0 and lag_oldest > args.freshness_oldest_max_seconds:
                freshness_status = "FAIL"

        heartbeat = {
            "run_id": run_id,
            "start_utc": start_utc,
            "end_utc": utc_now(),
            "duration_seconds": run_seconds,
            "status": status,
            "pipeline_mode": pipeline_mode,
            "fail_stage": fail_stage or "",
            "mode": "reconcile_only" if args.reconcile_only else ("sample" if args.sample_alert else "live"),
            "log_path": str(log_path),
            "counts": {
                "triaged": triaged,
                "escalated": escalated,
                "auto_closed_benign": auto_benign,
                "auto_closed_known_fp": auto_known_fp,
                "cases_scanned": case_dirs_scanned,
                "cases_processed": cases_processed,
            },
            "queue": {"depth_start": queue_start, "depth_end": queue_end},
            "reconciliation": {
                "strict_enabled": bool(args.reconcile_strict),
                "status": "PASS" if mismatch_count == 0 else ("FAIL" if mismatch_count >= 0 else "UNKNOWN"),
                "mismatch_count": mismatch_count,
                "report_json": str(RECONCILE_JSON_PATH),
            },
            "coverage": {
                "status": "PASS" if missing_hosts == 0 else ("FAIL" if missing_hosts >= 0 else "UNKNOWN"),
                "missing_hosts": missing_hosts,
                "present_hosts": present_hosts,
                "report_json": str(COVERAGE_JSON_PATH),
            },
            "freshness": {
                "status": freshness_status,
                "p95_max_seconds": args.freshness_p95_max_seconds,
                "oldest_max_seconds": args.freshness_oldest_max_seconds,
                "p95_delay_seconds": p95 if p95 >= 0 else "",
                "lag_oldest_seconds": lag_oldest if lag_oldest >= 0 else "",
            },
            "poller": {
                "secret_source": poll_kv.get("SECRET_SOURCE", ""),
                "mode": poll_kv.get("MODE", args.mode),
                "oldest_event_ts": poll_kv.get("OLDEST_EVENT_TS", ""),
                "lag_oldest_seconds": poll_kv.get("LAG_OLDEST_SECONDS", ""),
                "lag_newest_seconds": poll_kv.get("LAG_NEWEST_SECONDS", ""),
                "p50_delay_seconds": poll_kv.get("P50_DELAY_SECONDS", ""),
                "p95_delay_seconds": poll_kv.get("P95_DELAY_SECONDS", ""),
                "no_new_alerts": poll_kv.get("NO_NEW_ALERTS", ""),
                "polled": poll_kv.get("POLLED", ""),
                "saved": poll_kv.get("SAVED", ""),
            },
            "steps": step_seconds,
        }
        write_json(HEARTBEAT_PATH, heartbeat)
        with HEARTBEAT_HISTORY_PATH.open("a", encoding="utf-8") as out:
            out.write(json.dumps(heartbeat) + "\n")

        metrics = {
            "generated_utc": heartbeat["end_utc"],
            "run_seconds": run_seconds,
            "steps": step_seconds,
            "cases_scanned": case_dirs_scanned,
            "cases_processed": cases_processed,
            "mode": heartbeat["mode"],
            "pipeline_mode": pipeline_mode,
            "status": status,
            "fail_stage": heartbeat["fail_stage"],
        }
        write_json(RUN_METRICS_PATH, metrics)
        with RUN_METRICS_HISTORY_PATH.open("a", encoding="utf-8") as out:
            out.write(json.dumps(metrics) + "\n")

        if exit_code != 0:
            print(f"FAIL={fail_stage}; LOG={log_path}")
            raise SystemExit(exit_code)

        print(f"RUN_SECONDS={run_seconds}")
        print(f"PIPELINE_MODE={pipeline_mode}")
        print(f"CASES_SCANNED={case_dirs_scanned}")
        print(f"CASES_PROCESSED={cases_processed}")
        print("PIPELINE_DONE=TRUE")
        print(f"HEARTBEAT={HEARTBEAT_PATH}")
        print(f"LOG={log_path}")
        return

    if not args.skip_tests:
        tests_cmd = [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(SCRIPT_DIR / "tests"),
            "-p",
            "test_*.py",
            "-v",
        ]
        t0 = time.time()
        tests_rc, _tests_out = run_step(tests_cmd, log_path)
        step_seconds["tests"] = round(time.time() - t0, 3)
        if tests_rc != 0:
            finalize("FAILED", "tests", 10)

    if args.reconcile_only:
        case_dirs_scanned = len([p for p in CASES_ROOT.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))]) if CASES_ROOT.exists() else 0
        reconcile_cmd = [sys.executable, str(SCRIPT_DIR / "reconcile-state.py")]
        if args.reconcile_strict:
            reconcile_cmd.append("--strict")
        t0 = time.time()
        reconcile_rc, _reconcile_out = run_step(reconcile_cmd, log_path)
        step_seconds["reconcile"] = round(time.time() - t0, 3)
        if reconcile_rc != 0:
            finalize("FAILED", "reconcile", 6)

        t0 = time.time()
        _coverage_rc, _coverage_out = run_step(
            [sys.executable, str(SCRIPT_DIR / "coverage-check.py"), "--window-hours", "168"],
            log_path,
        )
        step_seconds["coverage_check"] = round(time.time() - t0, 3)
        finalize("SUCCESS", "", 0)
        return

    if not args.reconcile_only:
        poll_cmd = [sys.executable, str(SCRIPT_DIR / "poll-alerts.py")]
        if args.sample_alert:
            poll_cmd += ["--sample-alert", str(args.sample_alert)]
        else:
            poll_cmd += ["--mode", args.mode, "--realtime-window-minutes", str(args.realtime_window_minutes)]
        t0 = time.time()
        poll_rc, poll_out = run_step(poll_cmd, log_path)
        poll_kv = parse_kv(poll_out)
        step_seconds["poll_alerts"] = round(time.time() - t0, 3)
        if poll_rc != 0:
            finalize("FAILED", "poll-alerts", 1)

        t0 = time.time()
        triage_rc, _triage_out = run_step([sys.executable, str(SCRIPT_DIR / "triage.py")], log_path)
        step_seconds["triage"] = round(time.time() - t0, 3)
        if triage_rc != 0:
            finalize("FAILED", "triage", 1)

        # Emit a rolling triage quality report for tuning and operations visibility.
        t0 = time.time()
        run_step(
            [
                sys.executable,
                str(SCRIPT_DIR / "triage-quality.py"),
                "--window-hours",
                "24",
                "--compare-previous",
                "--csv",
            ],
            log_path,
        )
        step_seconds["triage_quality"] = round(time.time() - t0, 3)
        t0 = time.time()
        run_step(
            [
                "pwsh",
                "-NoProfile",
                "-File",
                str(SCRIPT_DIR / "render-triage-quality-chart.ps1"),
            ],
            log_path,
        )
        step_seconds["triage_quality_chart"] = round(time.time() - t0, 3)

        # Skip dot- or underscore-prefixed case dirs (quarantine/forensic-hold
        # convention). Added after 2026-04-18 incident where .FORENSIC_HOLD_*
        # entries were still enumerated on Windows (no hidden-attribute semantics).
        case_dirs = sorted([p for p in CASES_ROOT.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))], key=lambda p: p.stat().st_mtime)
        case_dirs_scanned = len(case_dirs)

        t_case = time.time()
        for case_dir in case_dirs:
            triage_json = case_dir / "triage.json"
            if not triage_json.exists():
                continue
            triage = json.loads(triage_json.read_text(encoding="utf-8"))
            if triage.get("status") == "PROCESSED":
                continue
            disposition = str(triage.get("disposition", "")).upper()
            if disposition != "ESCALATE":
                summary = {
                    "case_id": triage.get("case_id", case_dir.name),
                    "disposition": disposition or "UNKNOWN",
                    "reason": triage.get("reason", ""),
                    "processed_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                    "note": "Pack generation skipped by policy (non-ESCALATE).",
                }
                (case_dir / "disposition_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
                if disposition in {"AUTO_CLOSE_BENIGN", "AUTO_CLOSE_KNOWN_FP"}:
                    (case_dir / "auto_close_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
                elif disposition == "REVIEW":
                    (case_dir / "review_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
                triage["status"] = "PROCESSED"
                triage["processed_utc"] = summary["processed_utc"]
                triage_json.write_text(json.dumps(triage, indent=2), encoding="utf-8")
                cases_processed += 1
                continue
            if (case_dir / "pack").exists() and (case_dir / "redaction_report.json").exists():
                continue
            redact_rc, _redact_out = run_step(
                [sys.executable, str(SCRIPT_DIR / "redact.py"), "--case-dir", str(case_dir)],
                log_path,
            )
            if redact_rc != 0:
                finalize("FAILED", "redact", 2)
            assemble_rc, _assemble_out = run_step(
                [sys.executable, str(SCRIPT_DIR / "assemble-pack.py"), "--case-dir", str(case_dir)],
                log_path,
            )
            if assemble_rc != 0:
                finalize("FAILED", "assemble", 3)
            pr_cmd = [sys.executable, str(SCRIPT_DIR / "create-pr.py"), "--case-dir", str(case_dir)]
            if args.open_pr:
                pr_cmd.append("--open-pr")
            pr_rc, _pr_out = run_step(pr_cmd, log_path)
            if pr_rc != 0:
                finalize("FAILED", "create-pr", 4)
            triage["status"] = "PROCESSED"
            triage["processed_utc"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            triage_json.write_text(json.dumps(triage, indent=2), encoding="utf-8")
            cases_processed += 1
        step_seconds["cases_processing"] = round(time.time() - t_case, 3)

    reconcile_cmd = [sys.executable, str(SCRIPT_DIR / "reconcile-state.py")]
    if args.reconcile_strict:
        reconcile_cmd.append("--strict")
    t0 = time.time()
    reconcile_rc, _reconcile_out = run_step(reconcile_cmd, log_path)
    step_seconds["reconcile"] = round(time.time() - t0, 3)
    if reconcile_rc != 0:
        finalize("FAILED", "reconcile", 6)

    t0 = time.time()
    _coverage_rc, _coverage_out = run_step([sys.executable, str(SCRIPT_DIR / "coverage-check.py"), "--window-hours", "168"], log_path)
    step_seconds["coverage_check"] = round(time.time() - t0, 3)
    finalize("SUCCESS", "", 0)


if __name__ == "__main__":
    try:
        main()
    finally:
        release_lock()
