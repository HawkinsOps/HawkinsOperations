#!/usr/bin/env python3
import argparse
import json
import time
import ssl
import urllib.request
import os
from urllib.error import HTTPError, URLError
from pathlib import Path
import shutil
from typing import Any, Dict, List
from datetime import datetime, timezone

from common import CURSOR_PATH, ENV_PATH, PROCESSED_ROOT, QUEUE_ROOT, ensure_dirs, env_value, load_env_file, read_json, utc_now, write_json


def parse_iso_ts(raw: str) -> datetime:
    return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))


def percentile(values: List[int], p: float) -> int:
    if not values:
        return 0
    vals = sorted(values)
    idx = int(round((len(vals) - 1) * p))
    idx = max(0, min(idx, len(vals) - 1))
    return vals[idx]


def load_password(dotenv: Dict[str, str]) -> tuple[str, str]:
    env_pass = os.getenv("WAZUH_INDEXER_PASS", "")
    if env_pass:
        return env_pass, "ENV"

    pass_file = env_value("WAZUH_INDEXER_PASS_FILE", dotenv, "")
    if pass_file:
        secret = Path(pass_file).read_text(encoding="utf-8").strip()
        if secret:
            return secret, "PASS_FILE"
        raise RuntimeError(f"WAZUH_INDEXER_PASS_FILE is set but empty: {pass_file}")

    dotenv_pass = dotenv.get("WAZUH_INDEXER_PASS", "")
    if dotenv_pass:
        allow_legacy = env_value("WAZUH_ALLOW_DOTENV_LEGACY", dotenv, "false").lower() == "true"
        if allow_legacy:
            return dotenv_pass, "DOTENV_LEGACY"
        raise RuntimeError(
            "WAZUH_INDEXER_PASS in .env is blocked by default. "
            "Use runner env var WAZUH_INDEXER_PASS or WAZUH_INDEXER_PASS_FILE. "
            "Set WAZUH_ALLOW_DOTENV_LEGACY=true only as break-glass."
        )
    return "", "MISSING"


def fetch_indexer_alerts(
    dotenv: Dict[str, str], limit: int, mode: str, realtime_window_minutes: int
) -> tuple[List[Dict[str, Any]], Dict[str, str]]:
    host = env_value("WAZUH_INDEXER_HOST", dotenv)
    user = env_value("WAZUH_INDEXER_USER", dotenv)
    password, password_source = load_password(dotenv)
    insecure = env_value("WAZUH_TLS_INSECURE", dotenv, "false").lower() == "true"
    index = env_value("WAZUH_INDEX", dotenv, "wazuh-alerts-*")

    if not host or not user or not password:
        raise RuntimeError(
            "Missing indexer credentials. Set WAZUH_INDEXER_HOST/WAZUH_INDEXER_USER plus "
            "WAZUH_INDEXER_PASS (env) or WAZUH_INDEXER_PASS_FILE."
        )

    cursor = read_json(CURSOR_PATH, {"last_ts": "1970-01-01T00:00:00Z"})
    if mode == "realtime":
        now = datetime.now(timezone.utc).replace(microsecond=0)
        ts_from = (now.timestamp() - max(1, realtime_window_minutes) * 60)
        ts = datetime.fromtimestamp(ts_from, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        range_query = {"gte": ts}
    else:
        range_query = {"gt": cursor.get("last_ts", "1970-01-01T00:00:00Z")}

    body = {
        "size": limit,
        "sort": [{"@timestamp": {"order": "asc"}}],
        "query": {"range": {"@timestamp": range_query}},
    }

    url = f"{host.rstrip('/')}/{index}/_search"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")

    token = (f"{user}:{password}").encode("utf-8")
    import base64

    req.add_header("Authorization", "Basic " + base64.b64encode(token).decode("ascii"))

    ctx = None
    if insecure:
        ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    hits = payload.get("hits", {}).get("hits", [])
    alerts = []
    for hit in hits:
        src = hit.get("_source", {})
        src["_indexer_meta"] = {"_id": hit.get("_id", ""), "_index": hit.get("_index", "")}
        alerts.append(src)
    meta = {"password_source": password_source, "mode": mode}
    return alerts, meta


def fetch_with_retry(
    dotenv: Dict[str, str], limit: int, retries: int, backoff_seconds: float, mode: str, realtime_window_minutes: int
) -> tuple[List[Dict[str, Any]], Dict[str, str]]:
    # Retry transient network/indexer errors; fail fast on auth failures.
    attempt = 1
    while True:
        try:
            return fetch_indexer_alerts(dotenv, limit, mode, realtime_window_minutes)
        except HTTPError as exc:
            if exc.code == 401:
                raise RuntimeError(
                    "Indexer auth failed (401 Unauthorized). "
                    "Check WAZUH_INDEXER_USER/WAZUH_INDEXER_PASS in .env."
                ) from exc
            if attempt > retries:
                raise RuntimeError(f"Indexer HTTP error after {attempt} attempts: {exc}") from exc
            wait_s = backoff_seconds * (2 ** (attempt - 1))
            print(f"RETRY=HTTP_{exc.code}; ATTEMPT={attempt}; WAIT_SECONDS={wait_s:.1f}")
            time.sleep(wait_s)
            attempt += 1
        except URLError as exc:
            if attempt > retries:
                raise RuntimeError(f"Indexer connection error after {attempt} attempts: {exc}") from exc
            wait_s = backoff_seconds * (2 ** (attempt - 1))
            print(f"RETRY=CONNECTION; ATTEMPT={attempt}; WAIT_SECONDS={wait_s:.1f}")
            time.sleep(wait_s)
            attempt += 1


def save_alerts(alerts: List[Dict[str, Any]]) -> int:
    saved = 0
    latest_ts = None
    for alert in alerts:
        ts = alert.get("@timestamp") or utc_now()
        aid = (
            str(alert.get("id", ""))
            or str(alert.get("_id", ""))
            or str(alert.get("_indexer_meta", {}).get("_id", ""))
            or f"alert-{saved+1}"
        )
        name = f"{ts.replace(':', '').replace('-', '').replace('T', '_').replace('Z', '')}_{aid}.json"
        path = QUEUE_ROOT / name
        path.write_text(json.dumps(alert, indent=2), encoding="utf-8")
        saved += 1
        latest_ts = ts

    if latest_ts:
        write_json(CURSOR_PATH, {"last_ts": latest_ts, "updated_utc": utc_now()})
    return saved


def enforce_queue_cap(max_queue_files: int) -> int:
    if max_queue_files <= 0:
        return 0
    queue_files = sorted([p for p in QUEUE_ROOT.glob("*.json") if p.name != ".cursor.json"], key=lambda p: p.stat().st_mtime)
    overflow = len(queue_files) - max_queue_files
    if overflow <= 0:
        return 0

    moved = 0
    for path in queue_files[:overflow]:
        dest = PROCESSED_ROOT / path.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest = dest.with_name(f"{dest.stem}__overflow_{int(time.time())}{dest.suffix}")
        shutil.move(str(path), str(dest))
        moved += 1
    return moved


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll alerts from Wazuh Indexer into AutoSOC queue.")
    parser.add_argument("--limit", type=int, default=100, help="Max alerts per run.")
    parser.add_argument("--sample-alert", type=Path, help="Load alerts from a local JSON file for testing.")
    parser.add_argument("--retries", type=int, default=3, help="Retry count for transient indexer failures.")
    parser.add_argument("--backoff-seconds", type=float, default=2.0, help="Base backoff delay in seconds.")
    parser.add_argument(
        "--max-queue-files",
        type=int,
        default=2000,
        help="Maximum queue JSON files before oldest entries are archived to Queue/Processed.",
    )
    parser.add_argument(
        "--mode",
        choices=["backfill", "realtime"],
        default="backfill",
        help="backfill uses cursor progression; realtime ignores cursor and pulls only recent window.",
    )
    parser.add_argument(
        "--realtime-window-minutes",
        type=int,
        default=60,
        help="Lookback window for realtime mode.",
    )
    args = parser.parse_args()
    safe_limit = max(1, min(int(args.limit), 10000))

    ensure_dirs()
    dotenv = load_env_file(ENV_PATH)

    if args.sample_alert:
        payload = json.loads(args.sample_alert.read_text(encoding="utf-8"))
        alerts = payload if isinstance(payload, list) else [payload]
        fetch_meta = {"password_source": "SAMPLE_ALERT", "mode": "sample"}
    else:
        mode = env_value("WAZUH_MODE", dotenv, args.mode).strip().lower() or "backfill"
        window_minutes = int(env_value("WAZUH_REALTIME_WINDOW_MINUTES", dotenv, str(args.realtime_window_minutes)))
        alerts, fetch_meta = fetch_with_retry(dotenv, safe_limit, args.retries, args.backoff_seconds, mode, window_minutes)

    now_utc = datetime.now(timezone.utc)
    lag_oldest_s = ""
    lag_newest_s = ""
    oldest_event_ts = ""
    p50_delay_s = ""
    p95_delay_s = ""
    if alerts:
        try:
            ts_values = [parse_iso_ts(a.get("@timestamp", utc_now())) for a in alerts]
            oldest = min(ts_values)
            newest = max(ts_values)
            oldest_event_ts = oldest.isoformat().replace("+00:00", "Z")
            lag_oldest_s = str(int((now_utc - oldest).total_seconds()))
            lag_newest_s = str(int((now_utc - newest).total_seconds()))
            delays = [max(0, int((now_utc - ts).total_seconds())) for ts in ts_values]
            p50_delay_s = str(percentile(delays, 0.50))
            p95_delay_s = str(percentile(delays, 0.95))
        except Exception:
            lag_oldest_s = ""
            lag_newest_s = ""
            oldest_event_ts = ""
            p50_delay_s = ""
            p95_delay_s = ""

    saved = save_alerts(alerts)
    archived = enforce_queue_cap(args.max_queue_files)
    print(f"POLLED={len(alerts)}")
    if args.limit != safe_limit:
        print(f"WARN=LIMIT_CLAMPED_FROM_{args.limit}_TO_{safe_limit}")
    print(f"SAVED={saved}")
    print(f"QUEUE_OVERFLOW_ARCHIVED={archived}")
    print(f"QUEUE={QUEUE_ROOT}")
    print(f"SECRET_SOURCE={fetch_meta.get('password_source','UNKNOWN')}")
    print(f"MODE={fetch_meta.get('mode', args.mode)}")
    if fetch_meta.get("password_source") == "DOTENV_LEGACY":
        print("WARN=USING_DOTENV_PASSWORD_LEGACY")
    print(f"OLDEST_EVENT_TS={oldest_event_ts}")
    print(f"LAG_OLDEST_SECONDS={lag_oldest_s}")
    print(f"LAG_NEWEST_SECONDS={lag_newest_s}")
    print(f"P50_DELAY_SECONDS={p50_delay_s}")
    print(f"P95_DELAY_SECONDS={p95_delay_s}")
    print(f"NO_NEW_ALERTS={'TRUE' if saved == 0 else 'FALSE'}")


if __name__ == "__main__":
    main()
