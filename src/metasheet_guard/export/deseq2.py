"""DESeq2 design table exporter."""

from __future__ import annotations

from pathlib import Path

from metasheet_guard.io.csv import SheetTable, read_table, write_table

BASE_COLUMNS = ["sample", "condition"]
OPTIONAL_COLUMNS = ["batch", "replicate", "sex", "tissue", "genotype", "organism"]


def export_deseq2_design(sheet: SheetTable | str | Path, output: str | Path) -> None:
    table = read_table(sheet) if isinstance(sheet, str | Path) else sheet
    missing = [column for column in BASE_COLUMNS if column not in table.column_names]
    if missing:
        raise ValueError(
            "Cannot export DESeq2 design; missing columns: " + ", ".join(missing)
        )
    columns = BASE_COLUMNS + [
        column for column in OPTIONAL_COLUMNS if column in table.column_names
    ]
    rows = [
        {column: row.get(column, "") for column in columns} for row in table.records()
    ]
    write_table(rows, output, columns=columns, delimiter="\t")
