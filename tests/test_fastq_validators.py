from __future__ import annotations

from pathlib import Path

from metasheet_guard.io.csv import read_table
from metasheet_guard.schema.loader import load_schema
from metasheet_guard.validators.fastq import FastqValidator


def _codes(path: str) -> list[str]:
    table = read_table(Path(path))
    schema = load_schema("bulk-rnaseq")
    return [issue.code for issue in FastqValidator().run(table, schema)]


def test_valid_fastq_paths_pass_file_checks() -> None:
    assert _codes("examples/valid/bulk_rnaseq_paired.csv") == []


def test_missing_fastq_2_detected() -> None:
    assert "FASTQ_2_MISSING_FOR_PAIRED" in _codes("examples/broken/missing_fastq_2.csv")


def test_duplicate_fastq_detected() -> None:
    assert "FASTQ_DUPLICATED_ACROSS_SAMPLES" in _codes(
        "examples/broken/duplicate_fastq_across_samples.csv"
    )


def test_pair_name_mismatch_detected(tmp_path: Path) -> None:
    path = tmp_path / "bad_pair.csv"
    path.write_text(
        "sample,condition,fastq_1,fastq_2\n"
        "S1,control,examples/fastq/CTRL_1_L001_R1.fastq.gz,"
        "examples/fastq/TREAT_1_L001_R2.fastq.gz\n",
        encoding="utf-8",
    )

    assert "FASTQ_PAIR_NAME_MISMATCH" in _codes(str(path))
