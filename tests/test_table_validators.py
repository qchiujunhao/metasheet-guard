from __future__ import annotations

from pathlib import Path

from metasheet_guard.io.csv import read_table
from metasheet_guard.schema.loader import load_schema
from metasheet_guard.validators.table import run_table_validators


def _codes(path: Path) -> list[str]:
    table = read_table(path)
    schema = load_schema("bulk-rnaseq")
    return [issue.code for issue in run_table_validators(table, schema)]


def test_missing_required_column_is_error(tmp_path: Path) -> None:
    path = tmp_path / "missing.csv"
    path.write_text("sample,fastq_1\nS1,S1_R1.fastq.gz\n", encoding="utf-8")

    codes = _codes(path)

    assert "REQUIRED_COLUMN_MISSING" in codes


def test_duplicate_column_is_error(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.csv"
    path.write_text(
        "sample,condition,condition,fastq_1\nS1,control,control,S1_R1.fastq.gz\n",
        encoding="utf-8",
    )

    codes = _codes(path)

    assert "DUPLICATE_COLUMN_NAME" in codes


def test_empty_required_value_is_error(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("sample,condition,fastq_1\nS1,,S1_R1.fastq.gz\n", encoding="utf-8")

    codes = _codes(path)

    assert "EMPTY_REQUIRED_VALUE" in codes


def test_valid_example_has_no_milestone_1_issues() -> None:
    table = read_table(Path("examples/valid/bulk_rnaseq_paired.csv"))
    schema = load_schema("bulk-rnaseq")

    issues = run_table_validators(table, schema)

    assert issues == []
