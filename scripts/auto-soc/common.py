#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


# Path resolution: Z:-native layout by default, with legacy OPS_ROOT override
# for rollback. If OPS_ROOT is set, the old C:\RH\OPS hierarchy is reconstructed;
# otherwise everything resolves under Z:\AutoSOC\ with the current on-disk layout.
_LEGACY_OPS_ROOT = os.getenv("OPS_ROOT")
if _LEGACY_OPS_ROOT:
    OPS_ROOT = Path(_LEGACY_OPS_ROOT)
    AUTOSOC_ROOT = Path(os.getenv("AUTOSOC_ROOT", str(OPS_ROOT / "30_Projects" / "Active" / "AutoSOC")))
    BUILD_ROOT = AUTOSOC_ROOT / "Build"
    CONFIG_ROOT = Path(os.getenv("AUTOSOC_CONFIG", str(BUILD_ROOT / "Config")))
    _DATA_ROOT = Path(os.getenv("AUTOSOC_DATA", str(BUILD_ROOT)))
    QUEUE_ROOT = _DATA_ROOT / "Queue"
    CASES_ROOT = _DATA_ROOT / "Cases"
    OUTPUT_ROOT = Path(os.getenv("AUTOSOC_OUTPUT", str(AUTOSOC_ROOT / "Output")))
    LOGS_ROOT = Path(os.getenv("AUTOSOC_LOGS", str(OPS_ROOT / "50_System" / "Runs" / "Logs")))
    REPO_ROOT_DEFAULT = Path(os.getenv("AUTOSOC_REPO", str(OPS_ROOT / "10_Portfolio" / "HawkinsOperations")))
else:
    AUTOSOC_ROOT = Path(os.getenv("AUTOSOC_ROOT", r"Z:\AutoSOC"))
    OPS_ROOT = AUTOSOC_ROOT  # legacy alias; scripts referencing OPS_ROOT still resolve
    BUILD_ROOT = AUTOSOC_ROOT  # legacy alias; BUILD_ROOT is flattened in Z: layout
    CONFIG_ROOT = Path(os.getenv("AUTOSOC_CONFIG", str(AUTOSOC_ROOT / "config")))
    _DATA_ROOT = Path(os.getenv("AUTOSOC_DATA", str(AUTOSOC_ROOT / "data")))
    QUEUE_ROOT = _DATA_ROOT / "Queue"
    CASES_ROOT = _DATA_ROOT / "Cases"
    OUTPUT_ROOT = Path(os.getenv("AUTOSOC_OUTPUT", str(_DATA_ROOT / "Output")))
    LOGS_ROOT = Path(os.getenv("AUTOSOC_LOGS", str(AUTOSOC_ROOT / "logs" / "Runtime")))
    REPO_ROOT_DEFAULT = Path(os.getenv("AUTOSOC_REPO", r"R:\GitHub\HawkinsOperations"))

PROCESSED_ROOT = QUEUE_ROOT / "Processed"
LEDGER_PATH = OUTPUT_ROOT / "ledger.json"

POLICY_PATH = CONFIG_ROOT / "policy.yaml"
KNOWN_FPS_PATH = CONFIG_ROOT / "known_fps.yaml"
ENV_PATH = CONFIG_ROOT / ".env"
CURSOR_PATH = QUEUE_ROOT / ".cursor.json"
AGENT_INVENTORY_PATH = CONFIG_ROOT / "agent_inventory.json"

# Secrets live under the config tree. The DPAPI blob is produced by
# Z:\AutoSOC\scripts\set-wazuh-credential.ps1 and consumed by
# Z:\AutoSOC\scripts\get-wazuh-credential.ps1 (invoked via subprocess from
# poll-alerts.py). The plaintext passfile is retained as a legacy fallback.
SECRETS_DIR = Path(os.getenv("AUTOSOC_SECRETS", str(CONFIG_ROOT / "secrets")))
PASS_DPAPI_PATH = Path(os.getenv("WAZUH_INDEXER_PASS_DPAPI", str(SECRETS_DIR / "wazuh_indexer_pass.dpapi")))
GET_CREDENTIAL_SCRIPT = Path(os.getenv("AUTOSOC_GET_CRED_SCRIPT", str(AUTOSOC_ROOT / "scripts" / "get-wazuh-credential.ps1")))


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
