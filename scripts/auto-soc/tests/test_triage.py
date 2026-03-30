#!/usr/bin/env python3
import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

spec = importlib.util.spec_from_file_location("triage_module", SCRIPT_DIR / "triage.py")
triage = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(triage)


class TriagePolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = {
            "thresholds": {
                "auto_close_benign_max_level": 3,
                "auto_close_known_fp_max_level": 13,
                "escalate_min_level": 12,
                "protected_agent_min_level_escalate": 7,
            },
            "always_escalate_rule_ids": ["100053", "5715"],
            "always_escalate_groups": ["rootkit", "malware", "ransomware"],
            "protected_agents": ["HO-SR-01", "HO-Wazuh-01", "ho-sr-01", "ho-sr-wm-01"],
            "auto_close_rule_ids": ["67027", "60118", "67023", "60642", "5501", "5502"],
            "review_rule_ids": [
                "202",
                "203",
                "204",
                "533",
                "553",
                "554",
                "5710",
                "594",
                "750",
                "752",
                "2902",
                "2904",
                "60104",
                "60132",
                "60227",
                "60702",
                "60789",
                "61102",
                "92151",
                "92153",
                "550",
                "19004",
                "19005",
                "19007",
                "19014",
                "23503",
                "23504",
                "23505",
                "40704",
            ],
            "rule_overrides": [
                {
                    "rule_ids": ["60227"],
                    "agent_names": ["HOWE01", "HO-WE-01", "win-hawkinsops"],
                    "provider_names": ["Microsoft-Windows-Security-Auditing"],
                    "contains_any": ["HP DeskJet 2800 series", "CR270QB", "MMDEVAPI", "Microsoft Print to PDF"],
                    "disposition": "AUTO_CLOSE_KNOWN_FP",
                    "reason": "Known workstation external-device churn from monitor, audio endpoint, and printer enumeration",
                },
                {
                    "rule_ids": ["60104"],
                    "agent_names": ["HOWE01", "HO-WE-01", "win-hawkinsops"],
                    "provider_names": ["Microsoft-Windows-Security-Auditing"],
                    "contains_all": ["Microsoft Software Key Storage Provider", "Key2WrapEncryptionKey", "0x80090016"],
                    "disposition": "AUTO_CLOSE_KNOWN_FP",
                    "reason": "Known Windows key-storage open-key failure noise on workstation",
                },
                {
                    "rule_ids": ["61102"],
                    "agent_names": ["HOWE01", "HO-WE-01", "win-hawkinsops"],
                    "provider_names": ["Microsoft-Windows-DistributedCOM"],
                    "contains_all": ["2147942403"],
                    "contains_any": ["LinkedIn\\\\LinkedIn.exe", "HPPrinterControl", "HPPrinterDriver"],
                    "disposition": "AUTO_CLOSE_KNOWN_FP",
                    "reason": "Known workstation DCOM app-launch noise from LinkedIn and HP printer Windows apps",
                },
                {
                    "rule_ids": ["2902"],
                    "agent_names": ["HO-HONEYPOT-01", "ho-fs-01"],
                    "locations": ["/var/log/dpkg.log"],
                    "contains_any": ["status installed"],
                    "disposition": "AUTO_CLOSE_KNOWN_FP",
                    "reason": "Known package installation churn during routine apt/dpkg maintenance on Linux hosts",
                },
                {
                    "rule_ids": ["2904"],
                    "agent_names": ["HO-HONEYPOT-01", "ho-fs-01"],
                    "locations": ["/var/log/dpkg.log"],
                    "contains_any": ["status half-configured"],
                    "disposition": "AUTO_CLOSE_KNOWN_FP",
                    "reason": "Known transient dpkg half-configured churn during routine apt/dpkg maintenance on Linux hosts",
                },
            ],
            "sysmon": {
                "escalate_event_ids": [1, 3, 10],
                "require_sysmon_source": True,
                "source_markers": ["sysmon", "microsoft-windows-sysmon"],
                "tiering": {
                    "enabled": True,
                    "event_dispositions": {"1": "REVIEW", "3": "REVIEW", "10": "ESCALATE"},
                    "event3_high_risk_contains_any": [
                        "rundll32.exe",
                        "regsvr32.exe",
                        "mshta.exe",
                        "powershell.exe",
                        "pwsh.exe",
                    ],
                },
                "suppressions": [
                    {
                        "rule_ids": ["92151"],
                        "agent_names": ["HOWE01", "HO-WE-01", "win-hawkinsops"],
                        "contains_any": ["\\program files\\powershell\\7\\pwsh.exe"],
                        "reason": "Known PowerShell 7 automation host module-load noise on workstation",
                    },
                    {
                        "rule_ids": ["92153"],
                        "agent_names": ["HOWE01", "HO-WE-01", "win-hawkinsops"],
                        "contains_any": [
                            "\\windows\\system32\\backgroundtaskhost.exe",
                            "\\windows\\system32\\taskhostw.exe",
                            "\\windows\\system32\\svchost.exe",
                            "\\windows\\system32\\runtimebroker.exe",
                            "\\windows\\uus\\packages\\preview\\amd64\\mousocoreworker.exe",
                        ],
                        "reason": "Known Windows service-host VaultCli module-load noise on workstation",
                    }
                ],
            },
            "defaults": {"disposition": "ESCALATE"},
        }
        self.known_fps = [
            {
                "rule_id": "100052",
                "agent": "HOWE01",
                "contains": "hosts.ics",
                "reason": "Known ICS-managed hosts.ics false positive",
            }
        ]

    def test_known_fp_overrides_level(self) -> None:
        alert = {
            "rule": {"id": "100052", "level": 12, "description": "Critical system file modified"},
            "agent": {"name": "HOWE01"},
            "full_log": r"C:\Windows\System32\drivers\etc\hosts.ics modified",
        }
        disp, reason = triage.determine_disposition(alert, self.policy, self.known_fps)
        self.assertEqual(disp, "AUTO_CLOSE_KNOWN_FP")
        self.assertIn("Known ICS-managed", reason)

    def test_always_escalate_rule(self) -> None:
        alert = {
            "rule": {"id": "100053", "level": 13, "description": "Rootkit or backdoor detected", "groups": ["rootkit"]},
            "agent": {"name": "ho-sr-01"},
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "ESCALATE")
        self.assertIn("always_escalate_rule_ids", reason)

    def test_invalid_user_ssh_attempt_routes_to_review(self) -> None:
        alert = {
            "rule": {"id": "5710", "level": 10, "description": "sshd: Attempt to login using a non-existent user"},
            "agent": {"name": "ho-honeypot-01"},
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "REVIEW")
        self.assertIn("review_rule_ids", reason)

    def test_ssh_auth_success_remains_always_escalate(self) -> None:
        alert = {
            "rule": {"id": "5715", "level": 10, "description": "sshd: authentication success"},
            "agent": {"name": "ho-sr-wm-01"},
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "ESCALATE")
        self.assertIn("always_escalate_rule_ids", reason)

    def test_vulnerability_detector_rule_routes_to_review(self) -> None:
        alert = {
            "rule": {"id": "23504", "level": 10, "description": "CVE-2025-54287 affects lxd"},
            "agent": {"name": "ho-fs-01"},
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "REVIEW")
        self.assertIn("review_rule_ids", reason)

    def test_auto_close_noisy_rule(self) -> None:
        alert = {"rule": {"id": "67027", "level": 3, "description": "A process was created."}, "agent": {"name": "HOWE01"}}
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "AUTO_CLOSE_BENIGN")
        self.assertIn("auto_close_rule_ids", reason)

    def test_review_rule_routes_to_review(self) -> None:
        alert = {
            "rule": {"id": "60227", "level": 8, "description": "New external device"},
            "agent": {"name": "HOWE01"},
            "data": {"win": {"system": {"providerName": "Microsoft-Windows-Security-Auditing"}, "eventdata": {"deviceDescription": "Unknown USB Device"}}},
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "REVIEW")
        self.assertIn("review_rule_ids", reason)

    def test_rule_override_auto_closes_known_workstation_device_churn(self) -> None:
        alert = {
            "rule": {"id": "60227", "level": 8, "description": "New external device"},
            "agent": {"name": "HOWE01"},
            "data": {
                "win": {
                    "system": {"providerName": "Microsoft-Windows-Security-Auditing"},
                    "eventdata": {"deviceDescription": "HP DeskJet 2800 series PCL-3 (V4)"},
                }
            },
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "AUTO_CLOSE_KNOWN_FP")
        self.assertIn("external-device churn", reason)

    def test_rule_override_auto_closes_known_windows_key_storage_noise(self) -> None:
        alert = {
            "rule": {"id": "60104", "level": 5, "description": "Windows audit failure event"},
            "agent": {"name": "HOWE01"},
            "data": {
                "win": {
                    "system": {"providerName": "Microsoft-Windows-Security-Auditing"},
                    "eventdata": {
                        "providerName": "Microsoft Software Key Storage Provider",
                        "keyName": "Key2WrapEncryptionKey",
                        "returnCode": "0x80090016",
                    },
                }
            },
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "AUTO_CLOSE_KNOWN_FP")
        self.assertIn("key-storage open-key failure", reason)

    def test_rule_override_auto_closes_known_dcom_app_launch_noise(self) -> None:
        alert = {
            "rule": {"id": "61102", "level": 5, "description": "Windows System error event"},
            "agent": {"name": "HOWE01"},
            "data": {
                "win": {
                    "system": {
                        "providerName": "Microsoft-Windows-DistributedCOM",
                        "message": "\"Unable to start a DCOM Server\" \"2147942403\" while starting \"C:\\Program Files\\WindowsApps\\7EE7776C.LinkedInforWindows_3.0.43.0_x64__w1wdnht996qgy\\LinkedIn\\LinkedIn.exe\""
                    },
                    "eventdata": {
                        "param1": "\"C:\\Program Files\\WindowsApps\\7EE7776C.LinkedInforWindows_3.0.43.0_x64__w1wdnht996qgy\\LinkedIn\\LinkedIn.exe\"",
                        "param2": "2147942403",
                    },
                }
            },
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "AUTO_CLOSE_KNOWN_FP")
        self.assertIn("DCOM app-launch noise", reason)

    def test_rule_override_auto_closes_known_dpkg_install_churn(self) -> None:
        alert = {
            "rule": {"id": "2902", "level": 7, "description": "New dpkg (Debian Package) installed."},
            "agent": {"name": "HO-HONEYPOT-01"},
            "location": "/var/log/dpkg.log",
            "full_log": "2026-03-15 06:20:49 status installed man-db:amd64 2.10.2-1",
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "AUTO_CLOSE_KNOWN_FP")
        self.assertIn("package installation churn", reason)

    def test_rule_override_auto_closes_known_dpkg_half_configured_churn(self) -> None:
        alert = {
            "rule": {"id": "2904", "level": 7, "description": "Dpkg (Debian Package) half configured."},
            "agent": {"name": "ho-fs-01"},
            "location": "/var/log/dpkg.log",
            "full_log": "2026-03-15 06:20:49 status half-configured bsdextrautils:amd64 1:2.37.2-4ubuntu3.5",
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "AUTO_CLOSE_KNOWN_FP")
        self.assertIn("half-configured churn", reason)

    def test_review_rule_on_protected_agent_stays_review(self) -> None:
        alert = {"rule": {"id": "2902", "level": 7, "description": "New package installed"}, "agent": {"name": "HO-Wazuh-01"}}
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "REVIEW")
        self.assertIn("review_rule_ids", reason)

    def test_protected_agent_escalates_when_rule_is_not_review(self) -> None:
        alert = {"rule": {"id": "99998", "level": 7, "description": "Protected host elevated event"}, "agent": {"name": "HO-Wazuh-01"}}
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "ESCALATE")
        self.assertIn("protected agent", reason)

    def test_case_id_contains_event_suffix_when_available(self) -> None:
        alert = {
            "@timestamp": "2026-03-02T17:00:30Z",
            "id": "evt-known-fp-2",
            "rule": {"id": "100052", "description": "Critical system file modified"},
            "agent": {"name": "HOWE01"},
        }
        case_id = triage.make_case_id(alert)
        self.assertIn("evt-known-fp-2", case_id)

    def test_sysmon_event_id_3_reviews_when_source_matches(self) -> None:
        alert = {
            "rule": {"id": "61603", "level": 7, "description": "Sysmon - Event 3"},
            "agent": {"name": "HOWE01"},
            "data": {"win": {"system": {"eventID": "3", "providerName": "Microsoft-Windows-Sysmon"}}},
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "REVIEW")
        self.assertIn("sysmon tiering event_id 3", reason)

    def test_sysmon_event_id_does_not_escalate_without_sysmon_source(self) -> None:
        alert = {
            "rule": {"id": "99999", "level": 4, "description": "Other provider event"},
            "agent": {"name": "HOWE01"},
            "data": {"win": {"system": {"eventID": "3", "providerName": "Security-Auditing"}}},
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "ESCALATE")
        self.assertIn("policy default", reason)

    def test_sysmon_event_id_10_escalates_in_tiering(self) -> None:
        alert = {
            "rule": {"id": "61610", "level": 6, "description": "Sysmon - Event 10"},
            "agent": {"name": "HOWE01"},
            "data": {"win": {"system": {"eventID": "10", "providerName": "Microsoft-Windows-Sysmon"}}},
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "ESCALATE")
        self.assertIn("sysmon tiering event_id 10", reason)

    def test_sysmon_event_id_3_high_risk_escalates(self) -> None:
        alert = {
            "rule": {"id": "61603", "level": 7, "description": "Sysmon - Event 3"},
            "agent": {"name": "HOWE01"},
            "data": {
                "win": {
                    "system": {"eventID": "3", "providerName": "Microsoft-Windows-Sysmon"},
                    "eventdata": {"image": r"C:\Windows\System32\rundll32.exe"},
                }
            },
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "ESCALATE")
        self.assertIn("high-risk image fragment", reason)

    def test_sysmon_suppression_auto_closes_known_python_noise(self) -> None:
        alert = {
            "rule": {"id": "92151", "level": 10, "description": "Binary loaded by powershell automation library"},
            "agent": {"name": "HOWE01"},
            "data": {
                "win": {
                    "system": {"eventID": "7", "providerName": "Microsoft-Windows-Sysmon"},
                    "eventdata": {"image": r"C:\Program Files\PowerShell\7\pwsh.exe", "company": "Microsoft Corporation"},
                }
            },
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "AUTO_CLOSE_KNOWN_FP")
        self.assertIn("PowerShell 7 automation host", reason)

    def test_sysmon_suppression_applies_by_rule_id_for_known_noise(self) -> None:
        alert = {
            "rule": {"id": "92153", "level": 10, "description": "Suspicious process loaded VaultCli.dll module"},
            "agent": {"name": "HOWE01"},
            "data": {
                "win": {
                    "system": {"eventID": "7", "providerName": "Microsoft-Windows-Security-Auditing"},
                    "eventdata": {"image": r"C:\Windows\System32\svchost.exe", "company": "Microsoft Corporation"},
                }
            },
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "AUTO_CLOSE_KNOWN_FP")
        self.assertIn("Windows service-host VaultCli", reason)

    def test_sysmon_suppression_auto_closes_runtimebroker_vaultcli_noise(self) -> None:
        alert = {
            "rule": {"id": "92153", "level": 10, "description": "Suspicious process loaded VaultCli.dll module"},
            "agent": {"name": "HOWE01"},
            "data": {
                "win": {
                    "system": {"eventID": "7", "providerName": "Microsoft-Windows-Sysmon"},
                    "eventdata": {"image": r"C:\Windows\System32\RuntimeBroker.exe", "company": "Microsoft Corporation"},
                }
            },
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "AUTO_CLOSE_KNOWN_FP")
        self.assertIn("Windows service-host VaultCli", reason)

    def test_non_suppressed_sysmon_noise_falls_to_review(self) -> None:
        alert = {
            "rule": {"id": "92151", "level": 10, "description": "Binary loaded by powershell automation library"},
            "agent": {"name": "HOWE01"},
            "data": {
                "win": {
                    "system": {"eventID": "7", "providerName": "Microsoft-Windows-Sysmon"},
                    "eventdata": {"image": r"C:\Temp\weird-loader.exe", "company": "Unknown"},
                }
            },
        }
        disp, reason = triage.determine_disposition(alert, self.policy, [])
        self.assertEqual(disp, "REVIEW")
        self.assertIn("review_rule_ids", reason)

    def test_extract_agent_name_uses_alias_map(self) -> None:
        alias_map = {
            "ho-honeypot-01": "ho-honeypot-01",
            "ho-grafana-01": "ho-grafana-01",
        }
        alert = {"agent": {"hostname": "HO-HONEYPOT-01.local"}}
        self.assertEqual(triage.extract_agent_name(alert, alias_map), "ho-honeypot-01")

    def test_protected_agent_escalates_with_canonical_agent_field(self) -> None:
        policy = dict(self.policy)
        policy["protected_agents"] = ["HO-GRAFANA-01"]
        alert = {
            "rule": {"id": "2902", "level": 8, "description": "New package installed"},
            "_autosoc": {"agent": "ho-grafana-01"},
        }
        disp, reason = triage.determine_disposition(alert, policy, [])
        self.assertEqual(disp, "REVIEW")
        self.assertIn("review_rule_ids", reason)


if __name__ == "__main__":
    unittest.main()
