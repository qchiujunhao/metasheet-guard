"""Conservative safe-repair engine."""

from __future__ import annotations

import re
from pathlib import Path

from metasheet_guard.io.csv import SheetTable, read_table
from metasheet_guard.repair.provenance import RepairChange, RepairResult
from metasheet_guard.schema.loader import Schema, load_schema

FASTQ_EXTENSION_RE = re.compile(r"\.(fastq|fq)(\.gz)?$", re.IGNORECASE)


def repair_sheet(
    sheet: SheetTable | str | Path,
    schema: Schema | str | Path = "generic-ngs",
    safe_only: bool = True,
    dry_run: bool = False,
) -> RepairResult:
    """Apply deterministic safe repairs and return auditable provenance."""

    del safe_only
    table = read_table(sheet) if isinstance(sheet, str | Path) else sheet
    schema_obj = load_schema(schema) if not isinstance(schema, Schema) else schema
    alias_to_canonical = {
        alias: column.name
        for column in schema_obj.columns.values()
        for alias in column.aliases
    }

    columns, header_changes = _repair_headers(table.headers, alias_to_canonical)
    rows: list[dict[str, str]] = []
    changes: list[RepairChange] = header_changes[:]

    for row in table.rows:
        if not any(value.strip() for value in row.values):
            changes.append(
                RepairChange(
                    row=row.line_number,
                    column="*",
                    old="",
                    new="",
                    rule="remove_empty_row",
                )
            )
            if dry_run:
                rows.append(_row_to_dict(columns, row.values))
            continue

        repaired_row = _row_to_dict(columns, row.values)
        row_changes = _repair_values(repaired_row, row.line_number)
        changes.extend(row_changes)
        rows.append(repaired_row if not dry_run else _row_to_dict(columns, row.values))

    return RepairResult(rows=rows, columns=columns, changes=changes)


def _repair_headers(
    headers: list[str], alias_to_canonical: dict[str, str]
) -> tuple[list[str], list[RepairChange]]:
    trimmed = [header.strip() for header in headers]
    existing = set(trimmed)
    repaired: list[str] = []
    changes: list[RepairChange] = []
    for header in headers:
        new = header.strip()
        if new in alias_to_canonical and alias_to_canonical[new] not in existing:
            new = alias_to_canonical[new]
        repaired.append(new)
        if new != header:
            changes.append(
                RepairChange(
                    row=1,
                    column=header,
                    old=header,
                    new=new,
                    rule="normalize_column_name",
                )
            )
    return repaired, changes


def _row_to_dict(columns: list[str], values: list[str]) -> dict[str, str]:
    return {
        column: values[index] if index < len(values) else ""
        for index, column in enumerate(columns)
        if column
    }


def _repair_values(row: dict[str, str], line_number: int) -> list[RepairChange]:
    changes: list[RepairChange] = []
    for column, value in list(row.items()):
        new = value.strip()
        if column == "sample":
            new = re.sub(r"\s+", "_", new)
        elif column == "condition":
            new = new.lower()
        elif column in {"fastq_1", "fastq_2"}:
            new = FASTQ_EXTENSION_RE.sub(
                lambda match: match.group(0).lower(),
                new,
            )
        if new != value:
            rule = "trim_whitespace"
            if column == "sample":
                rule = "normalize_sample_id"
            elif column == "condition":
                rule = "trim_and_lowercase"
            elif column in {"fastq_1", "fastq_2"}:
                rule = "normalize_fastq_extension_case"
            row[column] = new
            changes.append(
                RepairChange(
                    row=line_number,
                    column=column,
                    old=value,
                    new=new,
                    rule=rule,
                )
            )
    return changes
