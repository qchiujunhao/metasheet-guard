"""Validation result model and summary helpers."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from metasheet_guard.issue import Issue


@dataclass(frozen=True)
class ValidationResult:
    """A complete validation result for one sample sheet."""

    summary: dict[str, int]
    issues: list[Issue] = field(default_factory=list)
    export_readiness: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def from_issues(
        cls,
        issues: Iterable[Issue],
        row_count: int = 0,
        column_count: int = 0,
        export_readiness: dict[str, bool] | None = None,
    ) -> ValidationResult:
        issue_list = list(issues)
        summary = {
            "rows": row_count,
            "columns": column_count,
            "errors": sum(issue.severity == "error" for issue in issue_list),
            "warnings": sum(issue.severity == "warning" for issue in issue_list),
            "infos": sum(issue.severity == "info" for issue in issue_list),
        }
        return cls(
            summary=summary,
            issues=issue_list,
            export_readiness=export_readiness or {},
        )

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def infos(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "info"]

    @property
    def has_blocking_errors(self) -> bool:
        return bool(self.errors)

    def to_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "issues": [issue.to_dict() for issue in self.issues],
            "repairs": [],
            "export_readiness": self.export_readiness,
        }
