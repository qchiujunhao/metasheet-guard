"""Canonical CSV exporter."""

from __future__ import annotations

from pathlib import Path

from metasheet_guard.io.csv import SheetTable, read_table, write_table


def export_canonical(sheet: SheetTable | str | Path, output: str | Path) -> None:
    table = read_table(sheet) if isinstance(sheet, str | Path) else sheet
    write_table(table.records(), output, columns=table.column_names)
