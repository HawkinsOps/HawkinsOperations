#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


OPS_ROOT = Path(os.getenv("OPS_ROOT", r"C:\RH\OPS"))
AUTOSOC_ROOT = Path(os.getenv("AUTOSOC_ROOT", str(OPS_ROOT / "30_Projects" / "Active" / "AutoSOC")))
BUILD_ROOT = AUTOSOC_ROOT / "Build"
CONFIG_ROOT = BUILD_ROOT / "Config"
QUEUE_ROOT = BUILD_ROOT / "Queue"
PROCESSED_ROOT = QUEUE_ROOT / "Processed"
CASES_ROOT = BUILD_ROOT / "Cases"
OUTPUT_ROOT = AUTOSOC_ROOT / "Output"
LEDGER_PATH = OUTPUT_ROOT / "ledger.json"
LOGS_ROOT = OPS_ROOT / "50_System" / "Runs" / "Logs"
REPO_ROOT_DEFAULT = OPS_ROOT / "10_Portfolio" / "HawkinsOperations"

POLICY_PATH = CONFIG_ROOT / "policy.yaml"
KNOWN_FPS_PATH = CONFIG_ROOT / "known_fps.yaml"
ENV_PATH = CONFIG_ROOT / ".env"
CURSOR_PATH = QUEUE_ROOT / ".cursor.json"
AGENT_INVENTORY_PATH = CONFIG_ROOT / "agent_inventory.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dirs() -> None:
    for p in (CONFIG_ROOT, QUEUE_ROOT, PROCESSED_ROOT, CASES_ROOT, OUTPUT_ROOT, LOGS_ROOT):
        p.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_env_file(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        data[k.strip()] = v.strip()
    return data


def env_value(name: str, dotenv: Dict[str, str], default: str = "") -> str:
    value = os.getenv(name, "")
    if value:
        return value
    return dotenv.get(name, default)


def load_yaml_json(path: Path, default: Any) -> Any:
    # JSON is valid YAML 1.2. These config files intentionally use JSON-in-YAML
    # to avoid external dependencies.
    if not path.exists():
        return default
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} must be JSON-formatted YAML. Parse error: {exc}") from exc


def slugify(value: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    s = s.strip("-")
    return s or "case"


def load_ledger() -> Dict[str, Any]:
    default = {
        "schema_version": "1.0",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "metrics": {
            "total_cases": 0,
            "auto_closed_benign": 0,
            "auto_closed_known_fp": 0,
            "escalated": 0,
            "review": 0,
            "open_prs": 0,
        },
        "cases": [],
    }
    return read_json(LEDGER_PATH, default)


def save_ledger(ledger: Dict[str, Any]) -> None:
    ledger["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    write_json(LEDGER_PATH, ledger)
