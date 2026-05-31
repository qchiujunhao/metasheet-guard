"""Public API for MetaSheet-Guard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from metasheet_guard.export import (
    export_canonical,
    export_deseq2_design,
    export_nfcore_rnaseq,
    export_snakemake,
)
from metasheet_guard.io.csv import SheetTable, read_table
from metasheet_guard.repair import repair_sheet
from metasheet_guard.report.json import write_json_report
from metasheet_guard.result import ValidationResult
from metasheet_guard.schema.loader import Schema, load_schema
from metasheet_guard.validators import run_validators

__version__ = "0.1.0"


def read_sheet(path: str | Path) -> SheetTable:
    """Read a CSV or TSV sample sheet into a table object."""

    return read_table(path)


def validate(
    sheet: SheetTable | str | Path,
    schema: Schema | str | Path = "generic-ngs",
    root: str | Path | None = None,
    include_export_readiness: bool = True,
    **_: Any,
) -> ValidationResult:
    """Validate a sample sheet with the currently implemented rule set."""

    table = read_table(sheet) if isinstance(sheet, str | Path) else sheet
    schema_obj = load_schema(schema) if not isinstance(schema, Schema) else schema
    issues, readiness = run_validators(
        table,
        schema_obj,
        root=root,
        include_export_readiness=include_export_readiness,
    )
    return ValidationResult.from_issues(
        issues=issues,
        row_count=len(table.rows),
        column_count=len(table.headers),
        export_readiness=readiness,
    )


def export_sheet(
    sheet: SheetTable | str | Path,
    target: str,
    output: str | Path,
) -> None:
    """Export a sample sheet to a supported workflow target."""

    if target == "nf-core-rnaseq":
        export_nfcore_rnaseq(sheet, output)
    elif target == "deseq2-design":
        export_deseq2_design(sheet, output)
    elif target == "snakemake":
        export_snakemake(sheet, output)
    elif target in {"canonical", "generic"}:
        export_canonical(sheet, output)
    else:
        raise ValueError(f"Unsupported export target: {target}")


__all__ = [
    "Schema",
    "SheetTable",
    "ValidationResult",
    "__version__",
    "read_sheet",
    "export_sheet",
    "repair_sheet",
    "validate",
    "write_json_report",
]
