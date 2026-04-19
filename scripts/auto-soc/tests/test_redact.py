#!/usr/bin/env python3
import importlib.util
import os
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


class _AutosocRedactedEnv:
    """Context helper: isolate AUTOSOC_REDACTED to a tmp path per test."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._prev: str | None = None

    def __enter__(self) -> Path:
        self._prev = os.environ.get("AUTOSOC_REDACTED")
        os.environ["AUTOSOC_REDACTED"] = str(self.path)
        # Re-read the module-level REDACTED_ROOT so default_out_dir sees the new root.
        redact.REDACTED_ROOT = Path(os.environ["AUTOSOC_REDACTED"])
        return self.path

    def __exit__(self, *_exc) -> None:
        if self._prev is None:
            os.environ.pop("AUTOSOC_REDACTED", None)
        else:
            os.environ["AUTOSOC_REDACTED"] = self._prev
        redact.REDACTED_ROOT = Path(
            os.environ.get("AUTOSOC_REDACTED", str(redact.CASES_ROOT.parent / "Cases_Redacted"))
        )


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

    def test_default_out_dir_is_outside_case_dir(self) -> None:
        """New default: <AUTOSOC_REDACTED>/<case_name>/redacted — not a child of case_dir."""
        td = self._tmpdir()
        case_dir = td / "case_abc"
        case_dir.mkdir(parents=True, exist_ok=True)
        with _AutosocRedactedEnv(td / "Cases_Redacted"):
            out = redact.default_out_dir(case_dir)
        self.assertEqual(out, td / "Cases_Redacted" / "case_abc" / "redacted")
        # Must NOT be a descendant of case_dir.
        self.assertFalse(case_dir in out.parents)
        shutil.rmtree(td, ignore_errors=True)

    def test_repeat_run_overwrites_not_timestamp_suffixes(self) -> None:
        """Second run on same case must reuse the same out_dir (overwrite),
        not create redacted_<ts>/ siblings. Direct regression test for
        incident 2026-04-18."""
        td = self._tmpdir()
        case_dir = td / "case"
        out_dir = td / "out" / "redacted"
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "alert.raw.json").write_text(
            '{"source":"HO-GRAFANA-01","ip":"10.0.0.5"}',
            encoding="utf-8",
        )
        _stats1, final1 = redact.copy_and_redact(case_dir, out_dir)
        _stats2, final2 = redact.copy_and_redact(case_dir, out_dir)
        self.assertEqual(final1, out_dir)
        self.assertEqual(final2, out_dir)
        # No timestamped sibling should exist next to out_dir.
        siblings = [p for p in out_dir.parent.glob("redacted*") if p.is_dir()]
        self.assertEqual(siblings, [out_dir])
        shutil.rmtree(td, ignore_errors=True)

    def test_output_dir_not_nested_inside_case_dir_on_main_invocation(self) -> None:
        """End-to-end: running the default redact path on a case dir must not
        create any redacted*/ directory inside the case dir."""
        td = self._tmpdir()
        case_dir = td / "case_e2e"
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "alert.raw.json").write_text('{"ip":"10.0.0.1"}', encoding="utf-8")
        with _AutosocRedactedEnv(td / "Cases_Redacted"):
            out = redact.default_out_dir(case_dir)
            redact.copy_and_redact(case_dir, out)
        nested = [p for p in case_dir.glob("redacted*") if p.is_dir()]
        self.assertEqual(nested, [], f"redact leaked into case_dir: {nested}")
        shutil.rmtree(td, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
