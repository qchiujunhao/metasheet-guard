"""Sample ID and biological metadata validators."""

from __future__ import annotations

import re
from collections import defaultdict

from metasheet_guard.io.csv import SheetTable
from metasheet_guard.issue import Issue
from metasheet_guard.schema.loader import Schema

SAMPLE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


class MetadataValidator:
    """Validate sample identifiers and metadata consistency."""

    def run(self, table: SheetTable, schema: Schema) -> list[Issue]:
        del schema
        issues: list[Issue] = []
        rows = table.records()
        issues.extend(_sample_id_issues(rows))
        issues.extend(_condition_issues(rows, table))
        issues.extend(_same_sample_conflicts(rows))
        return issues


def _sample_id_issues(rows: list[dict[str, str]]) -> list[Issue]:
    issues: list[Issue] = []
    by_lower: dict[str, set[str]] = defaultdict(set)
    for row_number, row in enumerate(rows, start=2):
        sample = row.get("sample", "")
        if not sample:
            continue
        stripped = sample.strip()
        by_lower[stripped.lower()].add(stripped)
        if any(char.isspace() for char in stripped):
            issues.append(
                Issue(
                    code="SAMPLE_ID_SPACE",
                    severity="warning",
                    message=f"Sample ID '{sample}' contains whitespace.",
                    suggestion="Replace whitespace in sample IDs with underscores.",
                    row=row_number,
                    column="sample",
                    sample_id=stripped,
                    repairable=True,
                )
            )
        if not SAMPLE_ID_RE.match(stripped):
            issues.append(
                Issue(
                    code="SAMPLE_ID_ILLEGAL_CHAR",
                    severity="error",
                    message=f"Sample ID '{sample}' contains unsupported characters.",
                    suggestion="Use letters, numbers, dot, underscore, or dash only.",
                    row=row_number,
                    column="sample",
                    sample_id=stripped,
                )
            )
    for values in by_lower.values():
        if len(values) > 1:
            issues.append(
                Issue(
                    code="SAMPLE_ID_CASE_COLLISION",
                    severity="error",
                    message=(
                        "Sample IDs differ only by case: " + ", ".join(sorted(values))
                    ),
                    suggestion="Rename samples so case-insensitive IDs are unique.",
                    column="sample",
                )
            )
    return issues


def _condition_issues(rows: list[dict[str, str]], table: SheetTable) -> list[Issue]:
    issues: list[Issue] = []
    if not table.has_column("condition"):
        return issues

    by_lower: dict[str, set[str]] = defaultdict(set)
    for row_number, row in enumerate(rows, start=2):
        condition = row.get("condition", "")
        if not condition.strip():
            issues.append(
                Issue(
                    code="MISSING_CONDITION",
                    severity="error",
                    message=f"Condition is missing on row {row_number}.",
                    suggestion="Fill the condition for every biological sample.",
                    row=row_number,
                    column="condition",
                )
            )
            continue
        if condition != condition.strip():
            issues.append(
                Issue(
                    code="CONDITION_WHITESPACE",
                    severity="warning",
                    message=f"Condition '{condition}' has surrounding whitespace.",
                    suggestion="Trim condition labels before analysis.",
                    row=row_number,
                    column="condition",
                    repairable=True,
                )
            )
        by_lower[condition.strip().lower()].add(condition.strip())
    for values in by_lower.values():
        if len(values) > 1:
            issues.append(
                Issue(
                    code="CONDITION_CASE_MIXED",
                    severity="warning",
                    message=(
                        "Condition labels differ only by case: "
                        + ", ".join(sorted(values))
                    ),
                    suggestion="Normalize condition labels to a single case.",
                    column="condition",
                    repairable=True,
                )
            )

    if not table.has_column("replicate"):
        if (
            len(
                {
                    row.get("condition", "").strip()
                    for row in rows
                    if row.get("condition")
                }
            )
            > 1
        ):
            issues.append(
                Issue(
                    code="MISSING_REPLICATE",
                    severity="warning",
                    message=(
                        "No replicate column is present for a condition comparison."
                    ),
                    suggestion="Add a biological replicate column when available.",
                    column="replicate",
                )
            )
    else:
        for row_number, row in enumerate(rows, start=2):
            if (
                row.get("condition", "").strip()
                and not row.get("replicate", "").strip()
            ):
                issues.append(
                    Issue(
                        code="MISSING_REPLICATE",
                        severity="warning",
                        message=f"Replicate is missing on row {row_number}.",
                        suggestion="Fill biological replicate labels where known.",
                        row=row_number,
                        column="replicate",
                    )
                )
    return issues


def _same_sample_conflicts(rows: list[dict[str, str]]) -> list[Issue]:
    issues: list[Issue] = []
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        sample = row.get("sample", "").strip()
        if sample:
            grouped[sample].append(row)

    conflict_codes = {
        "condition": "SAME_SAMPLE_MULTIPLE_CONDITIONS",
        "tissue": "SAME_SAMPLE_MULTIPLE_TISSUES",
        "genotype": "SAME_SAMPLE_MULTIPLE_GENOTYPES",
        "sex": "SAMPLE_METADATA_CONFLICT",
    }
    for sample, sample_rows in grouped.items():
        for column, code in conflict_codes.items():
            values = {
                row.get(column, "").strip()
                for row in sample_rows
                if row.get(column, "").strip()
            }
            if len(values) <= 1:
                continue
            issues.append(
                Issue(
                    code=code,
                    severity="error",
                    message=(
                        f"Sample '{sample}' has conflicting {column} values: "
                        + ", ".join(sorted(values))
                    ),
                    suggestion=(
                        "Do not auto-repair biological metadata conflicts; inspect "
                        "the sample identity and metadata source."
                    ),
                    column=column,
                    sample_id=sample,
                )
            )
            if code != "SAMPLE_METADATA_CONFLICT":
                issues.append(
                    Issue(
                        code="SAMPLE_METADATA_CONFLICT",
                        severity="error",
                        message=f"Sample '{sample}' has conflicting metadata.",
                        suggestion="Resolve metadata conflicts before analysis.",
                        column=column,
                        sample_id=sample,
                    )
                )
    return issues
