"""Table-structure validators for Milestone 1."""

from __future__ import annotations

from metasheet_guard.io.csv import SheetTable
from metasheet_guard.issue import Issue
from metasheet_guard.schema.loader import Schema


class RequiredColumnsValidator:
    """Check that every schema-required column is present."""

    def run(self, table: SheetTable, schema: Schema) -> list[Issue]:
        present = set(table.column_names)
        issues: list[Issue] = []
        for column in schema.required_columns:
            if column not in present:
                issues.append(
                    Issue(
                        code="REQUIRED_COLUMN_MISSING",
                        severity="error",
                        message=f"Required column '{column}' is missing.",
                        suggestion=(
                            f"Add a '{column}' column or use a schema that matches "
                            "the sample sheet."
                        ),
                        column=column,
                    )
                )
        return issues


class DuplicateColumnsValidator:
    """Check for duplicate column names after trimming surrounding whitespace."""

    def run(self, table: SheetTable, schema: Schema) -> list[Issue]:
        del schema
        return [
            Issue(
                code="DUPLICATE_COLUMN_NAME",
                severity="error",
                message=f"Column '{column}' appears more than once.",
                suggestion="Rename or remove duplicate columns before validation.",
                row=1,
                column=column,
            )
            for column in table.duplicate_columns
        ]


class ColumnAliasValidator:
    """Detect columns that are known aliases for schema-defined canonical names."""

    def run(self, table: SheetTable, schema: Schema) -> list[Issue]:
        alias_to_canonical = {
            alias: column.name
            for column in schema.columns.values()
            for alias in column.aliases
        }
        issues: list[Issue] = []
        for column in table.column_names:
            canonical = alias_to_canonical.get(column)
            if canonical is None:
                continue
            issues.append(
                Issue(
                    code="COLUMN_ALIAS_DETECTED",
                    severity="warning",
                    message=(
                        f"Column '{column}' is a known alias for canonical "
                        f"column '{canonical}'."
                    ),
                    suggestion=(
                        f"Rename '{column}' to '{canonical}' before export or "
                        "repair the sheet once alias repair is available."
                    ),
                    row=1,
                    column=column,
                    repairable=True,
                )
            )
        return issues


class EmptyRequiredValuesValidator:
    """Check that required columns contain values in every data row."""

    def run(self, table: SheetTable, schema: Schema) -> list[Issue]:
        issues: list[Issue] = []
        for column in schema.required_columns:
            if not table.has_column(column):
                continue
            for row in table.rows:
                value = table.value(row, column)
                if value is None or not value.strip():
                    issues.append(
                        Issue(
                            code="EMPTY_REQUIRED_VALUE",
                            severity="error",
                            message=(
                                f"Required column '{column}' is empty on row "
                                f"{row.line_number}."
                            ),
                            suggestion="Fill the value or remove the incomplete row.",
                            row=row.line_number,
                            column=column,
                        )
                    )
        return issues


def run_table_validators(table: SheetTable, schema: Schema) -> list[Issue]:
    """Run the Milestone 1 table validators in a stable order."""

    validators = [
        DuplicateColumnsValidator(),
        ColumnAliasValidator(),
        RequiredColumnsValidator(),
        EmptyRequiredValuesValidator(),
    ]
    issues: list[Issue] = []
    for validator in validators:
        issues.extend(validator.run(table, schema))
    return issues
