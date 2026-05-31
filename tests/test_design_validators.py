from __future__ import annotations

from pathlib import Path

from metasheet_guard.io.csv import read_table
from metasheet_guard.schema.loader import load_schema
from metasheet_guard.validators.design import DesignValidator


def _codes(path: str) -> list[str]:
    table = read_table(Path(path))
    schema = load_schema("bulk-rnaseq")
    return [issue.code for issue in DesignValidator().run(table, schema)]


def test_batch_condition_confounding_detected() -> None:
    assert "BATCH_CONDITION_CONFOUNDED" in _codes(
        "examples/broken/batch_condition_confounding.csv"
    )


def test_balanced_batch_example_not_confounded() -> None:
    assert "BATCH_CONDITION_CONFOUNDED" not in _codes(
        "examples/valid/bulk_rnaseq_with_batch.csv"
    )


def test_mixed_strandedness_detected() -> None:
    assert "STRANDEDNESS_MIXED_WITHIN_COMPARISON" in _codes(
        "examples/broken/mixed_strandedness.csv"
    )
