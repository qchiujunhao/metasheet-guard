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


def test_check_writes_html_report(tmp_path) -> None:
    output = tmp_path / "report.html"

    result = runner.invoke(
        app,
        [
            "check",
            "examples/broken/batch_condition_confounding.csv",
            "--schema",
            "bulk-rnaseq",
            "--html",
            str(output),
        ],
    )

    assert result.exit_code == 0
    html = output.read_text(encoding="utf-8")
    assert "MetaSheet-Guard validation report" in html
    assert "BATCH_CONDITION_CONFOUNDED" in html


def test_schema_list_command() -> None:
    result = runner.invoke(app, ["schema", "list"])

    assert result.exit_code == 0
    assert "generic-ngs" in result.output
    assert "bulk-rnaseq" in result.output


def test_repair_command_writes_outputs(tmp_path) -> None:
    clean = tmp_path / "clean.csv"
    changes = tmp_path / "changes.json"

    result = runner.invoke(
        app,
        [
            "repair",
            "examples/broken/condition_case_mixed.csv",
            "--schema",
            "bulk-rnaseq",
            "--out",
            str(clean),
            "--changes",
            str(changes),
        ],
    )

    assert result.exit_code == 0
    assert clean.exists()
    payload = json.loads(changes.read_text(encoding="utf-8"))
    assert any(change["rule"] == "trim_and_lowercase" for change in payload)


def test_repair_allow_suggestions_fails_clearly(tmp_path) -> None:
    result = runner.invoke(
        app,
        [
            "repair",
            "examples/broken/condition_case_mixed.csv",
            "--schema",
            "bulk-rnaseq",
            "--out",
            str(tmp_path / "clean.csv"),
            "--changes",
            str(tmp_path / "changes.json"),
            "--allow-suggestions",
        ],
    )

    assert result.exit_code == 1
    assert "Suggested repairs are not implemented yet" in result.output


def test_export_command_writes_nfcore_samplesheet(tmp_path) -> None:
    output = tmp_path / "nfcore.csv"

    result = runner.invoke(
        app,
        [
            "export",
            "examples/valid/bulk_rnaseq_paired.csv",
            "--target",
            "nf-core-rnaseq",
            "--out",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert output.read_text(encoding="utf-8").splitlines()[0] == (
        "sample,fastq_1,fastq_2,strandedness"
    )


def test_import_sra_runinfo_command(tmp_path) -> None:
    output = tmp_path / "canonical.csv"

    result = runner.invoke(
        app,
        [
            "import",
            "sra-runinfo",
            "examples/sra_runinfo/SraRunInfo.csv",
            "--out",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert "SRR000001_1.fastq.gz" in output.read_text(encoding="utf-8")
