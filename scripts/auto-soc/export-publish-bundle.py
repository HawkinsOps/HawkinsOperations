#!/usr/bin/env python3
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from common import AUTOSOC_ROOT, OUTPUT_ROOT, read_json, utc_now


def main() -> None:
    parser = argparse.ArgumentParser(description="Build curated publish bundle from allowlist.")
    parser.add_argument("--allowlist", type=Path, default=AUTOSOC_ROOT / "Build" / "Config" / "publish_allowlist.json")
    parser.add_argument("--out-dir", type=Path, default=OUTPUT_ROOT / "publish_bundle")
    parser.add_argument("--manifest", type=Path, default=OUTPUT_ROOT / "publish_bundle_manifest.json")
    args = parser.parse_args()

    data = read_json(args.allowlist, {"publish_paths": []})
    items = data.get("publish_paths", [])
    copied = []
    missing = []

    target_out = args.out_dir
    if target_out.exists():
        try:
            shutil.rmtree(target_out)
        except Exception:
            suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            target_out = target_out.parent / f"{target_out.name}_{suffix}"
    target_out.mkdir(parents=True, exist_ok=True)

    for rel in items:
        src = AUTOSOC_ROOT / rel
        if not src.exists():
            missing.append(str(rel))
            continue
        dst = target_out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(str(rel))

    manifest = {
        "generated_utc": utc_now(),
        "allowlist": str(args.allowlist),
        "out_dir": str(target_out),
        "copied": copied,
        "missing": missing,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"PUBLISH_BUNDLE={target_out}")
    print(f"MANIFEST={args.manifest}")
    print(f"COPIED={len(copied)}")
    print(f"MISSING={len(missing)}")


if __name__ == "__main__":
    main()
