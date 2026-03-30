#!/usr/bin/env python3
import importlib.util
import shutil
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

spec = importlib.util.spec_from_file_location("redact_module", SCRIPT_DIR / "redact.py")
redact = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(redact)


class RedactionTests(unittest.TestCase):
    def _tmpdir(self) -> Path:
        base = SCRIPT_DIR / "tests" / ".tmp-redact"
        if base.exists():
            shutil.rmtree(base, ignore_errors=True)
        base.mkdir(parents=True, exist_ok=True)
        return base

    def test_redact_text_masks_sensitive_tokens(self) -> None:
        raw = (
            "ip=192.168.8.254 path=C:\\RH\\OPS\\secret\\file.txt "
            "host=HO-HONEYPOT-01 user=raylee email=test@example.com"
        )
        out = redact.redact_text(raw)
        self.assertIn("[REDACTED_IP]", out)
        self.assertIn("[REDACTED_PATH]", out)
        self.assertIn("[REDACTED_HOST]", out)
        self.assertIn("[REDACTED_USER]", out)
        self.assertIn("[REDACTED_EMAIL]", out)

    def test_fails_post_redaction_detects_absolute_path_leak(self) -> None:
        td = self._tmpdir()
        p = td / "artifact.txt"
        p.write_text("leak C:\\RH\\OPS\\30_Projects\\Active\\AutoSOC\\Build\\Cases", encoding="utf-8")
        self.assertTrue(redact.fails_post_redaction(td))
        shutil.rmtree(td, ignore_errors=True)

    def test_copy_and_redact_produces_clean_text(self) -> None:
        td = self._tmpdir()
        case_dir = td / "case"
        out_dir = case_dir / "redacted"
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "alert.raw.json").write_text(
            '{"source":"HO-GRAFANA-01","path":"C:\\\\RH\\\\OPS","ip":"10.0.0.5"}',
            encoding="utf-8",
        )
        _stats, final_out = redact.copy_and_redact(case_dir, out_dir)
        text = (final_out / "alert.raw.json").read_text(encoding="utf-8")
        self.assertIn("[REDACTED_HOST]", text)
        self.assertIn("[REDACTED_PATH]", text)
        self.assertIn("[REDACTED_IP]", text)
        self.assertFalse(redact.fails_post_redaction(final_out))
        shutil.rmtree(td, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
