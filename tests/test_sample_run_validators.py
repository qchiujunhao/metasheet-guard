from __future__ import annotations

from pathlib import Path

from metasheet_guard.io.csv import read_table
from metasheet_guard.schema.loader import load_schema
from metasheet_guard.validators.sample_run import SampleRunValidator


def _codes(path: str) -> list[str]:
    table = read_table(Path(path))
    schema = load_schema("bulk-rnaseq")
    return [issue.code for issue in SampleRunValidator().run(table, schema)]


def test_multirun_sample_and_lane_detected() -> None:
    codes = _codes("examples/valid/bulk_rnaseq_multilane.csv")

    assert "MULTIRUN_SAMPLE_DETECTED" in codes
    assert "LANE_PATTERN_DETECTED" in codes


def test_technical_as_biological_replicate_detected() -> None:
    assert "TECHNICAL_AS_BIOLOGICAL_REPLICATE" in _codes(
        "examples/broken/technical_replicate_as_biological.csv"
    )
