"""nf-core/rnaseq sample sheet exporter."""

from __future__ import annotations

from pathlib import Path

from metasheet_guard.io.csv import SheetTable, read_table, write_table

NFCORE_COLUMNS = ["sample", "fastq_1", "fastq_2", "strandedness"]


def export_nfcore_rnaseq(sheet: SheetTable | str | Path, output: str | Path) -> None:
    table = read_table(sheet) if isinstance(sheet, str | Path) else sheet
    _require_columns(table, ["sample", "fastq_1", "strandedness"])
    rows = [
        {column: row.get(column, "") for column in NFCORE_COLUMNS}
        for row in table.records()
    ]
    write_table(rows, output, columns=NFCORE_COLUMNS)


def _require_columns(table: SheetTable, columns: list[str]) -> None:
    missing = [column for column in columns if column not in table.column_names]
    if missing:
        raise ValueError(
            "Cannot export nf-core/rnaseq sample sheet; missing columns: "
            + ", ".join(missing)
        )
