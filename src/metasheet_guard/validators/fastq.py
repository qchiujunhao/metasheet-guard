"""FASTQ and file-level validators."""

from __future__ import annotations

import gzip
import re
from collections import defaultdict
from pathlib import Path

from metasheet_guard.io.csv import SheetTable
from metasheet_guard.issue import Issue
from metasheet_guard.schema.loader import Schema

FASTQ_SUFFIXES = (".fastq.gz", ".fq.gz", ".fastq", ".fq")
READ_RE = re.compile(r"([_-])R([12])([_.-]|$)", re.IGNORECASE)


class FastqValidator:
    """Validate FASTQ path fields and paired-end naming consistency."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else None

    def run(self, table: SheetTable, schema: Schema) -> list[Issue]:
        del schema
        issues: list[Issue] = []
        rows = table.records()
        issues.extend(self._row_issues(table, rows))
        issues.extend(_duplicate_fastq_issues(rows))
        issues.extend(_mixed_layout_issues(rows))
        return issues

    def _row_issues(self, table: SheetTable, rows: list[dict[str, str]]) -> list[Issue]:
        issues: list[Issue] = []
        for row_number, row in enumerate(rows, start=2):
            sample = row.get("sample", "").strip() or None
            fastq_1 = row.get("fastq_1", "").strip()
            fastq_2 = row.get("fastq_2", "").strip()

            if not fastq_1:
                issues.append(
                    Issue(
                        code="FASTQ_1_MISSING",
                        severity="error",
                        message=f"fastq_1 is missing on row {row_number}.",
                        suggestion="Provide an R1 FASTQ path for every row.",
                        row=row_number,
                        column="fastq_1",
                        sample_id=sample,
                    )
                )

            if table.has_column("fastq_2") and fastq_1 and not fastq_2:
                issues.append(
                    Issue(
                        code="FASTQ_2_MISSING_FOR_PAIRED",
                        severity="error",
                        message=f"fastq_2 is missing on row {row_number}.",
                        suggestion=(
                            "Fill fastq_2 or remove the column for single-end data."
                        ),
                        row=row_number,
                        column="fastq_2",
                        sample_id=sample,
                    )
                )

            for column, value in (("fastq_1", fastq_1), ("fastq_2", fastq_2)):
                if not value:
                    continue
                issues.extend(self._path_issues(value, column, row_number, sample))

            if fastq_1 and fastq_2:
                issues.extend(_pair_issues(fastq_1, fastq_2, row_number, sample))
        return issues

    def _path_issues(
        self, value: str, column: str, row_number: int, sample: str | None
    ) -> list[Issue]:
        issues: list[Issue] = []
        path = _resolve_path(value, self.root)
        lower_name = value.lower()
        if not lower_name.endswith(FASTQ_SUFFIXES):
            issues.append(
                Issue(
                    code="FASTQ_EXTENSION_INVALID",
                    severity="error",
                    message=f"FASTQ path '{value}' has an unsupported extension.",
                    suggestion="Use .fastq.gz, .fq.gz, .fastq, or .fq.",
                    row=row_number,
                    column=column,
                    sample_id=sample,
                    file_path=value,
                )
            )
        if not path.exists():
            issues.append(
                Issue(
                    code="FASTQ_PATH_NOT_FOUND",
                    severity="error",
                    message=f"FASTQ path does not exist: {value}",
                    suggestion=(
                        "Check the path or pass --root with the FASTQ directory."
                    ),
                    row=row_number,
                    column=column,
                    sample_id=sample,
                    file_path=value,
                )
            )
            return issues
        if path.stat().st_size == 0:
            issues.append(
                Issue(
                    code="FASTQ_EMPTY_FILE",
                    severity="error",
                    message=f"FASTQ file is empty: {value}",
                    suggestion="Replace empty FASTQ files before workflow execution.",
                    row=row_number,
                    column=column,
                    sample_id=sample,
                    file_path=value,
                )
            )
        if lower_name.endswith(".gz") and not _gzip_readable(path):
            issues.append(
                Issue(
                    code="FASTQ_GZIP_INVALID",
                    severity="error",
                    message=f"Gzip FASTQ file is not readable: {value}",
                    suggestion="Regenerate or replace the corrupt gzip file.",
                    row=row_number,
                    column=column,
                    sample_id=sample,
                    file_path=value,
                )
            )
        return issues


def _resolve_path(value: str, root: Path | None) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (root / path) if root is not None else path


def _gzip_readable(path: Path) -> bool:
    try:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            handle.read(1)
    except OSError:
        return False
    return True


def _pair_issues(
    fastq_1: str, fastq_2: str, row_number: int, sample: str | None
) -> list[Issue]:
    issues: list[Issue] = []
    name_1 = Path(fastq_1).name
    name_2 = Path(fastq_2).name
    if _read_direction(name_1) == "R2" or _read_direction(name_2) == "R1":
        issues.append(
            Issue(
                code="FASTQ_PAIR_SUSPECTED_SWAP",
                severity="warning",
                message=f"R1/R2 naming appears swapped on row {row_number}.",
                suggestion=(
                    "Check whether fastq_1 points to R1 and fastq_2 points to R2."
                ),
                row=row_number,
                sample_id=sample,
            )
        )
    if _pair_key(name_1) != _pair_key(name_2):
        issues.append(
            Issue(
                code="FASTQ_PAIR_NAME_MISMATCH",
                severity="error",
                message=f"FASTQ pair names do not match on row {row_number}.",
                suggestion="Pair R1 and R2 files from the same sample/run/lane.",
                row=row_number,
                sample_id=sample,
            )
        )
    return issues


def _read_direction(name: str) -> str | None:
    match = READ_RE.search(name)
    if not match:
        return None
    return f"R{match.group(2)}".upper()


def _pair_key(name: str) -> str:
    stem = name
    for suffix in FASTQ_SUFFIXES:
        if stem.lower().endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return READ_RE.sub(r"\1R\3", stem).lower()


def _duplicate_fastq_issues(rows: list[dict[str, str]]) -> list[Issue]:
    path_to_samples: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        sample = row.get("sample", "").strip()
        for column in ("fastq_1", "fastq_2"):
            path = row.get(column, "").strip()
            if path:
                path_to_samples[path].add(sample)

    issues: list[Issue] = []
    for path, samples in path_to_samples.items():
        if len(samples) > 1:
            issues.append(
                Issue(
                    code="FASTQ_DUPLICATED_ACROSS_SAMPLES",
                    severity="error",
                    message=(
                        f"FASTQ path '{path}' is assigned to multiple samples: "
                        + ", ".join(sorted(samples))
                    ),
                    suggestion="Each FASTQ file should belong to one sample identity.",
                    file_path=path,
                )
            )
    return issues


def _mixed_layout_issues(rows: list[dict[str, str]]) -> list[Issue]:
    layouts = ["paired" if row.get("fastq_2", "").strip() else "single" for row in rows]
    issues: list[Issue] = []
    if len(set(layouts)) > 1:
        issues.append(
            Issue(
                code="MIXED_SINGLE_PAIRED_LAYOUT",
                severity="warning",
                message="The sheet mixes single-end and paired-end rows.",
                suggestion="Confirm that mixed library layouts are intentional.",
            )
        )

    by_condition: dict[str, set[str]] = defaultdict(set)
    for row, layout in zip(rows, layouts, strict=False):
        condition = row.get("condition", "").strip()
        if condition:
            by_condition[condition].add(layout)
    for condition, condition_layouts in by_condition.items():
        if len(condition_layouts) > 1:
            issues.append(
                Issue(
                    code="MIXED_LAYOUT_WITHIN_CONDITION",
                    severity="warning",
                    message=f"Condition '{condition}' mixes single and paired layouts.",
                    suggestion=(
                        "Check whether this technical difference biases comparison."
                    ),
                    column="condition",
                )
            )
    return issues
