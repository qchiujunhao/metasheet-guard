"""Workflow export readiness checks."""

from __future__ import annotations

from metasheet_guard.io.csv import SheetTable
from metasheet_guard.issue import Issue


def export_readiness(table: SheetTable, issues: list[Issue]) -> dict[str, bool]:
    """Compute simple export readiness flags from columns and blocking issues."""

    has_errors = any(issue.severity == "error" for issue in issues)
    columns = set(table.column_names)
    return {
        "nf-core-rnaseq": (
            {"sample", "fastq_1", "strandedness"}.issubset(columns) and not has_errors
        ),
        "snakemake": {"sample", "fastq_1"}.issubset(columns) and not has_errors,
        "deseq2-design": {"sample", "condition"}.issubset(columns) and not has_errors,
    }


def export_readiness_issues(table: SheetTable, issues: list[Issue]) -> list[Issue]:
    """Create informational or blocking export readiness issues."""

    readiness = export_readiness(table, issues)
    extra: list[Issue] = []
    if "strandedness" not in table.column_names:
        extra.append(
            Issue(
                code="NFCORE_RNASEQ_MISSING_STRANDEDNESS",
                severity="warning",
                message="nf-core/rnaseq export requires strandedness.",
                suggestion=(
                    "Add strandedness values: forward, reverse, unstranded, or auto."
                ),
                column="strandedness",
            )
        )
    if any(issue.severity == "error" for issue in issues):
        extra.append(
            Issue(
                code="EXPORT_BLOCKED_BY_ERRORS",
                severity="error",
                message="Workflow export is blocked by validation errors.",
                suggestion="Resolve blocking errors before exporting workflow inputs.",
            )
        )
    if readiness["nf-core-rnaseq"]:
        extra.append(
            Issue(
                code="NFCORE_RNASEQ_READY",
                severity="info",
                message="The sheet has the minimal fields for nf-core/rnaseq export.",
                suggestion="Run export before launching the workflow.",
            )
        )
    if readiness["snakemake"]:
        extra.append(
            Issue(
                code="SNAKEMAKE_READY",
                severity="info",
                message="The sheet has the minimal fields for Snakemake export.",
                suggestion="Run export to generate a workflow-ready table or config.",
            )
        )
    if readiness["deseq2-design"]:
        extra.append(
            Issue(
                code="DESEQ2_DESIGN_READY",
                severity="info",
                message="The sheet has the minimal fields for DESeq2 design export.",
                suggestion="Run export with --target deseq2-design.",
            )
        )
    return extra
