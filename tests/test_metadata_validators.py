from __future__ import annotations

from pathlib import Path

from metasheet_guard.io.csv import read_table
from metasheet_guard.schema.loader import load_schema
from metasheet_guard.validators.metadata import MetadataValidator


def _codes(path: str) -> list[str]:
    table = read_table(Path(path))
    schema = load_schema("bulk-rnaseq")
    return [issue.code for issue in MetadataValidator().run(table, schema)]


def test_sample_id_spaces_detected() -> None:
    assert "SAMPLE_ID_SPACE" in _codes("examples/broken/sample_id_spaces.csv")


def test_condition_case_mixed_detected() -> None:
    codes = _codes("examples/broken/condition_case_mixed.csv")

    assert "CONDITION_CASE_MIXED" in codes
    assert "CONDITION_WHITESPACE" in codes


def test_same_sample_condition_conflict_detected() -> None:
    codes = _codes("examples/broken/conflicting_sample_condition.csv")

    assert "SAME_SAMPLE_MULTIPLE_CONDITIONS" in codes
    assert "SAMPLE_METADATA_CONFLICT" in codes
