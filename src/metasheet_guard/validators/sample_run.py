"""Sample, sequencing-run, and lane relationship validators."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from metasheet_guard.io.csv import SheetTable
from metasheet_guard.issue import Issue
from metasheet_guard.model.project import LANE_RE
from metasheet_guard.schema.loader import Schema


class SampleRunValidator:
    """Validate sample/run/lane relationships."""

    def run(self, table: SheetTable, schema: Schema) -> list[Issue]:
        del schema
        rows = table.records()
        issues: list[Issue] = []
        issues.extend(_multirun_issues(rows))
        issues.extend(_lane_issues(rows))
        issues.extend(_run_id_issues(rows))
        issues.extend(_replicate_label_issues(rows))
        return issues


def _multirun_issues(rows: list[dict[str, str]]) -> list[Issue]:
    counts = Counter(row.get("sample", "").strip() for row in rows)
    return [
        Issue(
            code="MULTIRUN_SAMPLE_DETECTED",
            severity="info",
            message=f"Sample '{sample}' appears in {count} rows/runs.",
            suggestion="Confirm whether rows are lanes or technical replicates.",
            sample_id=sample,
        )
        for sample, count in sorted(counts.items())
        if sample and count > 1
    ]


def _lane_issues(rows: list[dict[str, str]]) -> list[Issue]:
    issues: list[Issue] = []
    sample_lane_metadata: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    for row_number, row in enumerate(rows, start=2):
        sample = row.get("sample", "").strip()
        lane = row.get("lane", "").strip() or _lane_from_row(row)
        if lane:
            issues.append(
                Issue(
                    code="LANE_PATTERN_DETECTED",
                    severity="info",
                    message=f"Lane '{lane}' detected for sample '{sample}'.",
                    suggestion=(
                        "Represent lanes as technical runs, not biological samples."
                    ),
                    row=row_number,
                    sample_id=sample,
                )
            )
            sample_lane_metadata[(sample, lane)].add(
                (row.get("condition", "").strip(), row.get("batch", "").strip())
            )
    for (sample, lane), metadata_values in sample_lane_metadata.items():
        if len(metadata_values) > 1:
            issues.append(
                Issue(
                    code="LANE_METADATA_INCONSISTENT",
                    severity="error",
                    message=(
                        f"Sample '{sample}' lane '{lane}' has inconsistent metadata."
                    ),
                    suggestion=(
                        "Lanes for the same sample should share biological metadata."
                    ),
                    sample_id=sample,
                )
            )
    return issues


def _run_id_issues(rows: list[dict[str, str]]) -> list[Issue]:
    run_to_samples: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        run_id = (row.get("run_id") or row.get("run") or "").strip()
        sample = row.get("sample", "").strip()
        if run_id and sample:
            run_to_samples[run_id].add(sample)
    return [
        Issue(
            code="RUN_ID_DUPLICATED_WITH_DIFFERENT_SAMPLE",
            severity="error",
            message=(
                f"Run ID '{run_id}' is assigned to multiple samples: "
                + ", ".join(sorted(samples))
            ),
            suggestion="Run IDs should identify one sample/run relationship.",
            run_id=run_id,
        )
        for run_id, samples in sorted(run_to_samples.items())
        if len(samples) > 1
    ]


def _replicate_label_issues(rows: list[dict[str, str]]) -> list[Issue]:
    issues: list[Issue] = []
    label_to_samples: dict[tuple[str, str], set[str]] = defaultdict(set)
    sample_to_replicates: dict[str, set[str]] = defaultdict(set)
    sample_metadata: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
    for row in rows:
        sample = row.get("sample", "").strip()
        condition = row.get("condition", "").strip()
        replicate = row.get("replicate", "").strip()
        if sample and condition and replicate:
            label_to_samples[(condition, replicate)].add(sample)
            sample_to_replicates[sample].add(replicate)
        if sample:
            sample_metadata[sample].add(
                (
                    row.get("condition", "").strip(),
                    row.get("batch", "").strip(),
                    row.get("tissue", "").strip(),
                )
            )
    for (condition, replicate), samples in label_to_samples.items():
        if len(samples) > 1:
            issues.append(
                Issue(
                    code="BIOLOGICAL_REPLICATE_LABEL_REUSED",
                    severity="warning",
                    message=(
                        f"Replicate label '{replicate}' in condition '{condition}' "
                        "is used by multiple samples."
                    ),
                    suggestion=(
                        "Use sample-unique biological replicate labels if needed."
                    ),
                    column="replicate",
                )
            )
    for sample, replicates in sample_to_replicates.items():
        if len(replicates) > 1:
            issues.append(
                Issue(
                    code="TECHNICAL_AS_BIOLOGICAL_REPLICATE",
                    severity="warning",
                    message=f"Sample '{sample}' has multiple replicate labels.",
                    suggestion=(
                        "Check whether technical runs were mislabeled as biological "
                        "replicates."
                    ),
                    sample_id=sample,
                )
            )
    for sample, metadata_values in sample_metadata.items():
        if len(metadata_values) > 1:
            issues.append(
                Issue(
                    code="TECHNICAL_REPLICATE_METADATA_CONFLICT",
                    severity="error",
                    message=(
                        f"Technical rows for sample '{sample}' have metadata conflicts."
                    ),
                    suggestion=(
                        "Resolve metadata before combining technical replicates."
                    ),
                    sample_id=sample,
                )
            )

    counts = Counter(row.get("sample", "").strip() for row in rows if row.get("sample"))
    if counts:
        sorted_counts = sorted(counts.values())
        median = sorted_counts[len(sorted_counts) // 2]
        for sample, count in counts.items():
            if median and count > median * 3:
                issues.append(
                    Issue(
                        code="SAMPLE_RUN_COUNT_OUTLIER",
                        severity="warning",
                        message=(
                            f"Sample '{sample}' has {count} rows, much more than "
                            f"the project median of {median}."
                        ),
                        suggestion=(
                            "Check for duplicated rows or unusual run structure."
                        ),
                        sample_id=sample,
                    )
                )
    return issues


def _lane_from_row(row: dict[str, str]) -> str | None:
    for column in ("fastq_1", "fastq_2"):
        value = row.get(column, "")
        match = LANE_RE.search(Path(value).name)
        if match:
            return match.group(1).upper()
    return None
