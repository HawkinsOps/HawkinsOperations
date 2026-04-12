"""Sigma rule validation tests.

Runs three checks across every rule under ../sigma/:

1. parse  — YAML loads and SigmaRule.from_dict accepts it
2. convert — rule compiles to Splunk SPL via the HawkinsOps pipeline
3. fixture — selected rules match a hand-authored positive event
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from sigma.collection import SigmaCollection
from sigma.processing.resolver import ProcessingPipelineResolver
from sigma.processing.pipeline import ProcessingPipeline
from sigma.backends.splunk import SplunkBackend

ROOT = Path(__file__).resolve().parents[1]
SIGMA_DIR = ROOT / "sigma"
PIPELINE_PATH = ROOT / "ci" / "splunk-pipeline.yml"
FIXTURES_DIR = Path(__file__).parent / "fixtures"

RULE_FILES = sorted(p for p in SIGMA_DIR.rglob("*.yml") if p.is_file())


def _load_pipeline() -> ProcessingPipeline:
    return ProcessingPipelineResolver({
        "splunk": ProcessingPipeline.from_yaml(PIPELINE_PATH.read_text(encoding="utf-8"))
    }).resolve(["splunk"])


@pytest.fixture(scope="session")
def backend() -> SplunkBackend:
    return SplunkBackend(processing_pipeline=_load_pipeline())


def test_rule_corpus_is_not_empty():
    assert RULE_FILES, f"no Sigma rules found under {SIGMA_DIR}"


@pytest.mark.parametrize("rule_path", RULE_FILES, ids=lambda p: p.relative_to(SIGMA_DIR).as_posix())
def test_rule_parses(rule_path: Path):
    data = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{rule_path} did not parse as a mapping"
    SigmaCollection.from_dicts([data])


@pytest.mark.parametrize("rule_path", RULE_FILES, ids=lambda p: p.relative_to(SIGMA_DIR).as_posix())
def test_rule_converts_to_splunk(rule_path: Path, backend: SplunkBackend):
    collection = SigmaCollection.from_yaml(rule_path.read_text(encoding="utf-8"))
    queries = backend.convert(collection)
    assert queries and all(q.strip() for q in queries), f"{rule_path} produced empty SPL"


def _event_matches_selection(event: dict, selection: dict) -> bool:
    """Minimal Sigma-selection matcher sufficient for fixture smoke tests.

    Supports bare equality and the |endswith / |startswith modifiers used by
    the kerberoasting fixture. Not a general Sigma evaluator.
    """
    for raw_key, expected in selection.items():
        if "|" in raw_key:
            field, modifier = raw_key.split("|", 1)
        else:
            field, modifier = raw_key, "eq"

        actual = event.get(field)
        if actual is None:
            return False

        expected_values = expected if isinstance(expected, list) else [expected]
        matched = False
        for value in expected_values:
            if modifier == "eq" and str(actual) == str(value):
                matched = True
            elif modifier == "endswith" and str(actual).endswith(str(value)):
                matched = True
            elif modifier == "startswith" and str(actual).startswith(str(value)):
                matched = True
            if matched:
                break
        if not matched:
            return False
    return True


def test_kerberoasting_fixture_matches_selection():
    rule = yaml.safe_load(
        (SIGMA_DIR / "credential-access" / "kerberoasting.yml").read_text(encoding="utf-8")
    )
    event = json.loads((FIXTURES_DIR / "kerberoasting_4769_rc4.json").read_text(encoding="utf-8"))

    selection = rule["detection"]["selection"]
    assert _event_matches_selection(event, selection), (
        "kerberoasting positive fixture did not match rule 'selection' block"
    )
