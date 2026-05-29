from __future__ import annotations

import json

from typer.testing import CliRunner

from metasheet_guard.cli import app

runner = CliRunner()


def test_help_works() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "check" in result.output


def test_check_valid_example_exits_zero() -> None:
    result = runner.invoke(
        app,
        [
            "check",
            "examples/valid/bulk_rnaseq_paired.csv",
            "--schema",
            "bulk-rnaseq",
        ],
    )

    assert result.exit_code == 0


def test_check_missing_required_column_writes_json_report(tmp_path) -> None:
    output = tmp_path / "report.json"

    result = runner.invoke(
        app,
        [
            "check",
            "examples/broken/missing_required_column.csv",
            "--schema",
            "bulk-rnaseq",
            "--json",
            str(output),
        ],
    )

    assert result.exit_code == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["issues"][0]["code"] == "REQUIRED_COLUMN_MISSING"
    assert report["issues"][0]["severity"] == "error"
