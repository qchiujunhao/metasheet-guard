"""Command-line interface for MetaSheet-Guard."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from metasheet_guard import __version__, validate
from metasheet_guard.io.csv import read_table
from metasheet_guard.report.json import write_json_report
from metasheet_guard.schema.loader import load_schema

app = typer.Typer(
    add_completion=False,
    help=(
        "Experimental-design-aware quality control for sequencing analysis "
        "sample sheets."
    ),
    no_args_is_help=True,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"metasheet-guard {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            help="Show the installed MetaSheet-Guard version and exit.",
            is_eager=True,
        ),
    ] = False,
) -> None:
    """MetaSheet-Guard command group."""


@app.command()
def check(
    path: Annotated[
        Path,
        typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True),
    ],
    schema: Annotated[
        str,
        typer.Option(
            "--schema",
            "-s",
            help="Bundled schema name or path to a YAML schema file.",
        ),
    ] = "generic-ngs",
    root: Annotated[
        Path | None,
        typer.Option(
            "--root",
            help=(
                "FASTQ root directory. Accepted for CLI compatibility; "
                "unused in Milestone 1."
            ),
        ),
    ] = None,
    json_path: Annotated[
        Path | None,
        typer.Option(
            "--json",
            help="Write a machine-readable JSON validation report.",
        ),
    ] = None,
) -> None:
    """Validate a CSV or TSV sequencing analysis sample sheet."""

    del root
    schema_obj = load_schema(schema)
    table = read_table(path)
    result = validate(table, schema=schema_obj)

    if json_path is not None:
        write_json_report(result, json_path)

    console.print(
        "[bold]Validation complete[/bold]: "
        f"{result.summary['errors']} error(s), "
        f"{result.summary['warnings']} warning(s), "
        f"{result.summary['infos']} info issue(s)."
    )

    if result.has_blocking_errors:
        raise typer.Exit(code=1)
