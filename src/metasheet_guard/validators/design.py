"""Experimental design validators."""

from __future__ import annotations

from collections import Counter, defaultdict

from metasheet_guard.io.csv import SheetTable
from metasheet_guard.issue import Issue
from metasheet_guard.schema.loader import Schema


class DesignValidator:
    """Detect simple experimental design risks."""

    def run(self, table: SheetTable, schema: Schema) -> list[Issue]:
        del schema
        rows = table.records()
        issues: list[Issue] = []
        issues.extend(_condition_issues(rows))
        issues.extend(_batch_condition_issues(rows))
        issues.extend(_covariate_issues(rows, "sex", "SEX_CONFOUNDED_WITH_CONDITION"))
        issues.extend(
            _covariate_issues(rows, "tissue", "TISSUE_CONFOUNDED_WITH_CONDITION")
        )
        issues.extend(_missing_covariate_issues(rows))
        issues.extend(_strandedness_issues(rows))
        issues.extend(_organism_issues(rows))
        return issues


def _condition_issues(rows: list[dict[str, str]]) -> list[Issue]:
    conditions = [row.get("condition", "").strip() for row in rows]
    conditions = [condition for condition in conditions if condition]
    if not conditions:
        return []
    counts = Counter(conditions)
    issues: list[Issue] = []
    if len(counts) == 1:
        issues.append(
            Issue(
                code="CONDITION_SINGLE_LEVEL",
                severity="warning",
                message="Only one condition level is present.",
                suggestion="Differential comparisons require at least two conditions.",
                column="condition",
            )
        )
    for condition, count in counts.items():
        if count < 2:
            issues.append(
                Issue(
                    code="CONDITION_NO_REPLICATES",
                    severity="warning",
                    message=f"Condition '{condition}' has fewer than two samples.",
                    suggestion=(
                        "Add biological replicates or treat results as exploratory."
                    ),
                    column="condition",
                )
            )
    if len(counts) > 1 and min(counts.values()) > 0:
        largest = max(counts.values())
        smallest = min(counts.values())
        if largest >= smallest * 2:
            issues.append(
                Issue(
                    code="CONDITION_REPLICATE_IMBALANCE",
                    severity="warning",
                    message="Condition replicate counts are imbalanced.",
                    suggestion="Check whether group imbalance is expected.",
                    column="condition",
                )
            )
    return issues


def _batch_condition_issues(rows: list[dict[str, str]]) -> list[Issue]:
    if not any(row.get("batch", "").strip() for row in rows):
        return []
    return _confounding_issues(
        rows=rows,
        factor="condition",
        covariate="batch",
        complete_code="BATCH_CONDITION_CONFOUNDED",
        partial_code="BATCH_CONDITION_PARTIAL_CONFOUNDING",
        complete_message="condition is perfectly confounded with batch.",
        partial_message="condition is partially confounded with batch.",
    )


def _covariate_issues(
    rows: list[dict[str, str]], covariate: str, complete_code: str
) -> list[Issue]:
    if not any(row.get(covariate, "").strip() for row in rows):
        return []
    return _confounding_issues(
        rows=rows,
        factor="condition",
        covariate=covariate,
        complete_code=complete_code,
        partial_code=f"{covariate.upper()}_PARTIAL_CONFOUNDING",
        complete_message=f"{covariate} is confounded with condition.",
        partial_message=f"{covariate} is partially confounded with condition.",
        include_partial=False,
    )


def _confounding_issues(
    rows: list[dict[str, str]],
    factor: str,
    covariate: str,
    complete_code: str,
    partial_code: str,
    complete_message: str,
    partial_message: str,
    include_partial: bool = True,
) -> list[Issue]:
    pairs = [
        (row.get(factor, "").strip(), row.get(covariate, "").strip())
        for row in rows
        if row.get(factor, "").strip() and row.get(covariate, "").strip()
    ]
    if not pairs:
        return []
    factor_to_covariates: dict[str, set[str]] = defaultdict(set)
    covariate_to_factors: dict[str, set[str]] = defaultdict(set)
    for factor_value, covariate_value in pairs:
        factor_to_covariates[factor_value].add(covariate_value)
        covariate_to_factors[covariate_value].add(factor_value)

    complete = (
        len(factor_to_covariates) > 1
        and all(len(values) == 1 for values in factor_to_covariates.values())
        and all(len(values) == 1 for values in covariate_to_factors.values())
    )
    if complete:
        return [
            Issue(
                code=complete_code,
                severity="warning",
                message=complete_message,
                suggestion=(
                    "Downstream analysis may not distinguish biological effects "
                    "from the confounded variable."
                ),
                column=covariate,
            )
        ]
    if include_partial and any(
        len(values) == 1 for values in covariate_to_factors.values()
    ):
        return [
            Issue(
                code=partial_code,
                severity="warning",
                message=partial_message,
                suggestion="Inspect the design matrix before downstream modeling.",
                column=covariate,
            )
        ]
    return []


def _missing_covariate_issues(rows: list[dict[str, str]]) -> list[Issue]:
    issues: list[Issue] = []
    for covariate in ("batch", "sex", "tissue"):
        missing_by_condition: dict[str, bool] = defaultdict(bool)
        present_by_condition: dict[str, bool] = defaultdict(bool)
        for row in rows:
            condition = row.get("condition", "").strip()
            if not condition:
                continue
            if row.get(covariate, "").strip():
                present_by_condition[condition] = True
            else:
                missing_by_condition[condition] = True
        if present_by_condition and any(missing_by_condition.values()):
            issues.append(
                Issue(
                    code="COVARIATE_MISSING_IN_ONE_GROUP",
                    severity="warning",
                    message=f"Covariate '{covariate}' is missing for some samples.",
                    suggestion="Fill covariates consistently across comparison groups.",
                    column=covariate,
                )
            )
    return issues


def _strandedness_issues(rows: list[dict[str, str]]) -> list[Issue]:
    by_condition: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        condition = row.get("condition", "").strip()
        strandedness = row.get("strandedness", "").strip()
        if condition and strandedness:
            by_condition[condition].add(strandedness)
    return [
        Issue(
            code="STRANDEDNESS_MIXED_WITHIN_COMPARISON",
            severity="warning",
            message=f"Condition '{condition}' has mixed strandedness values.",
            suggestion="Confirm library strandedness before RNA-seq workflow export.",
            column="strandedness",
        )
        for condition, values in by_condition.items()
        if len(values) > 1
    ]


def _organism_issues(rows: list[dict[str, str]]) -> list[Issue]:
    organisms = {
        row.get("organism", "").strip()
        for row in rows
        if row.get("organism", "").strip()
    }
    if len(organisms) <= 1:
        return []
    return [
        Issue(
            code="ORGANISM_MIXED_WITHIN_PROJECT",
            severity="warning",
            message="Multiple organisms are present in one project.",
            suggestion="Confirm that mixed-organism analysis is intended.",
            column="organism",
        )
    ]
