from pathlib import Path
import json
import unittest

from tools.python3.xml4688_parser import parse_events_from_text, summarize_top_processes


class Xml4688ParserTests(unittest.TestCase):
    def test_parse_sample_events(self) -> None:
        sample = Path("tools/python3/samples/windows_security_4688_sample.xml").read_text(encoding="utf-8")
        events, errors = parse_events_from_text(sample)

        self.assertEqual(errors, 0)
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0]["EventID"], "4688")
        self.assertIn("powershell.exe", events[0]["NewProcessName"])
        self.assertIn("explorer.exe", events[0]["ParentProcessName"])

    def test_top_process_summary(self) -> None:
        sample = Path("tools/python3/samples/windows_security_4688_sample.xml").read_text(encoding="utf-8")
        events, errors = parse_events_from_text(sample)
        self.assertEqual(errors, 0)

        top = summarize_top_processes(events, top_n=2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0]["count"], 1)

    def test_cli_json_shape(self) -> None:
        sample = Path("tools/python3/samples/windows_security_4688_sample.xml")
        out = Path("tools/python3/samples/windows_security_4688_sample_output_test.json")
        try:
            from tools.python3.xml4688_parser import run_cli
            import sys

            old_argv = sys.argv
            sys.argv = [
                "xml4688_parser.py",
                "--in",
                str(sample),
                "--out-json",
                str(out),
                "--top",
                "5",
            ]
            try:
                rc = run_cli()
            finally:
                sys.argv = old_argv

            self.assertEqual(rc, 0)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["eventid_4688_count"], 2)
            self.assertGreaterEqual(len(payload["events"]), 3)
        finally:
            if out.exists():
                out.unlink()


if __name__ == "__main__":
    unittest.main()

