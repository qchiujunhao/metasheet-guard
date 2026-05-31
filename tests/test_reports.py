from __future__ import annotations

import json
from pathlib import Path

from metasheet_guard.issue import Issue
from metasheet_guard.report.html import write_html_report
from metasheet_guard.report.json import write_json_report
from metasheet_guard.result import ValidationResult


def test_write_json_report(tmp_path: Path) -> None:
    result = ValidationResult.from_issues(
        [
            Issue(
                code="REQUIRED_COLUMN_MISSING",
                severity="error",
                message="Required column 'condition' is missing.",
                column="condition",
            )
        ],
        row_count=2,
        column_count=2,
    )
    output = tmp_path / "report.json"

    write_json_report(result, output)

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["summary"]["errors"] == 1
    assert report["issues"][0]["code"] == "REQUIRED_COLUMN_MISSING"
    assert report["repairs"] == []


def test_write_html_report(tmp_path: Path) -> None:
    result = ValidationResult.from_issues(
        [
            Issue(
                code="BATCH_CONDITION_CONFOUNDED",
                severity="warning",
                message="condition is perfectly confounded with batch.",
            )
        ],
        row_count=4,
        column_count=5,
    )
    output = tmp_path / "report.html"

    write_html_report(result, output)

    html = output.read_text(encoding="utf-8")
    assert "MetaSheet-Guard validation report" in html
    assert "BATCH_CONDITION_CONFOUNDED" in html
