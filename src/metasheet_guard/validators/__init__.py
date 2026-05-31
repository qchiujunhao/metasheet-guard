"""Validation rules."""

from pathlib import Path

from metasheet_guard.io.csv import SheetTable
from metasheet_guard.issue import Issue
from metasheet_guard.schema.loader import Schema
from metasheet_guard.validators.design import DesignValidator
from metasheet_guard.validators.export_readiness import (
    export_readiness,
    export_readiness_issues,
)
from metasheet_guard.validators.fastq import FastqValidator
from metasheet_guard.validators.metadata import MetadataValidator
from metasheet_guard.validators.sample_run import SampleRunValidator
from metasheet_guard.validators.table import (
    ColumnAliasValidator,
    DuplicateColumnsValidator,
    EmptyRequiredValuesValidator,
    RequiredColumnsValidator,
    run_table_validators,
)


def run_validators(
    table: SheetTable,
    schema: Schema,
    root: str | Path | None = None,
    include_export_readiness: bool = True,
) -> tuple[list[Issue], dict[str, bool]]:
    """Run all implemented validators and return issues plus readiness flags."""

    issues: list[Issue] = []
    issues.extend(run_table_validators(table, schema))
    issues.extend(MetadataValidator().run(table, schema))
    issues.extend(FastqValidator(root=root).run(table, schema))
    issues.extend(SampleRunValidator().run(table, schema))
    issues.extend(DesignValidator().run(table, schema))
    readiness = export_readiness(table, issues)
    if include_export_readiness:
        issues.extend(export_readiness_issues(table, issues))
        readiness = export_readiness(table, issues)
    return issues, readiness


__all__ = [
    "ColumnAliasValidator",
    "DesignValidator",
    "DuplicateColumnsValidator",
    "EmptyRequiredValuesValidator",
    "FastqValidator",
    "MetadataValidator",
    "RequiredColumnsValidator",
    "SampleRunValidator",
    "export_readiness",
    "export_readiness_issues",
    "run_validators",
    "run_table_validators",
]
