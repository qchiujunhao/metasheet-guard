"""Public API for MetaSheet-Guard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from metasheet_guard.io.csv import SheetTable, read_table
from metasheet_guard.report.json import write_json_report
from metasheet_guard.result import ValidationResult
from metasheet_guard.schema.loader import Schema, load_schema
from metasheet_guard.validators.table import run_table_validators

__version__ = "0.1.0"


def read_sheet(path: str | Path) -> SheetTable:
    """Read a CSV or TSV sample sheet into a table object."""

    return read_table(path)


def validate(
    sheet: SheetTable | str | Path,
    schema: Schema | str | Path = "generic-ngs",
    **_: Any,
) -> ValidationResult:
    """Validate a sample sheet with the currently implemented rule set."""

    table = read_table(sheet) if isinstance(sheet, str | Path) else sheet
    schema_obj = load_schema(schema) if not isinstance(schema, Schema) else schema
    issues = run_table_validators(table, schema_obj)
    return ValidationResult.from_issues(
        issues=issues,
        row_count=len(table.rows),
        column_count=len(table.headers),
    )


__all__ = [
    "Schema",
    "SheetTable",
    "ValidationResult",
    "__version__",
    "read_sheet",
    "validate",
    "write_json_report",
]
