from __future__ import annotations

from pathlib import Path

from metasheet_guard.io.csv import read_table


def test_read_csv_table(tmp_path: Path) -> None:
    path = tmp_path / "sheet.csv"
    path.write_text("sample,condition\nS1,control\n", encoding="utf-8")

    table = read_table(path)

    assert table.delimiter == ","
    assert table.headers == ["sample", "condition"]
    assert table.rows[0].line_number == 2
    assert table.value(table.rows[0], "condition") == "control"


def test_read_tsv_table(tmp_path: Path) -> None:
    path = tmp_path / "sheet.tsv"
    path.write_text("sample\tcondition\nS1\tcontrol\n", encoding="utf-8")

    table = read_table(path)

    assert table.delimiter == "\t"
    assert table.value(table.rows[0], "sample") == "S1"


def test_duplicate_headers_are_preserved(tmp_path: Path) -> None:
    path = tmp_path / "sheet.csv"
    path.write_text("sample,sample,condition\nS1,S1_dup,control\n", encoding="utf-8")

    table = read_table(path)

    assert table.headers == ["sample", "sample", "condition"]
    assert table.duplicate_columns == ["sample"]
