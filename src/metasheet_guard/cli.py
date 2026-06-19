"""Command-line interface for MetaSheet-Guard."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from metasheet_guard import __version__, export_sheet, validate
from metasheet_guard.io.csv import read_table
from metasheet_guard.io.sra import import_sra_runinfo
from metasheet_guard.repair import repair_sheet
from metasheet_guard.report.html import write_html_report
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
schema_app = typer.Typer(help="Inspect bundled schemas.", no_args_is_help=True)
import_app = typer.Typer(help="Import external metadata tables.", no_args_is_help=True)
demo_app = typer.Typer(help="Create and run small local demos.", no_args_is_help=True)
app.add_typer(schema_app, name="schema")
app.add_typer(import_app, name="import")
app.add_typer(demo_app, name="demo")


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
            help="FASTQ root directory used to resolve relative FASTQ paths.",
        ),
    ] = None,
    json_path: Annotated[
        Path | None,
        typer.Option(
            "--json",
            help="Write a machine-readable JSON validation report.",
        ),
    ] = None,
    html_path: Annotated[
        Path | None,
        typer.Option(
            "--html",
            help="Write a static HTML validation report.",
        ),
    ] = None,
) -> None:
    """Validate a CSV or TSV sequencing analysis sample sheet."""

    schema_obj = load_schema(schema)
    table = read_table(path)
    result = validate(table, schema=schema_obj, root=root)

    if json_path is not None:
        write_json_report(result, json_path)
    if html_path is not None:
        write_html_report(result, html_path)

    console.print(
        "[bold]Validation complete[/bold]: "
        f"{result.summary['errors']} error(s), "
        f"{result.summary['warnings']} warning(s), "
        f"{result.summary['infos']} info issue(s)."
    )

    if result.has_blocking_errors:
        raise typer.Exit(code=1)


@app.command()
def repair(
    path: Annotated[
        Path,
        typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True),
    ],
    schema: Annotated[
        str,
        typer.Option("--schema", "-s", help="Bundled schema name or YAML schema path."),
    ] = "generic-ngs",
    out: Annotated[
        Path, typer.Option("--out", help="Repaired output CSV path.")
    ] = Path("clean.csv"),
    changes: Annotated[
        Path,
        typer.Option("--changes", help="Repair provenance JSON path."),
    ] = Path("changes.json"),
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Report repairs without changing output rows."),
    ] = False,
    safe_only: Annotated[
        bool,
        typer.Option(
            "--safe-only/--allow-suggestions", help="Apply only safe repairs."
        ),
    ] = True,
) -> None:
    """Apply conservative safe repairs and write changes.json provenance."""

    try:
        result = repair_sheet(path, schema=schema, safe_only=safe_only, dry_run=dry_run)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    result.to_csv(out)
    result.write_changes(changes)
    console.print(
        f"Wrote {out} and {changes} with {len(result.changes)} recorded change(s)."
    )


@app.command()
def export(
    path: Annotated[
        Path,
        typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True),
    ],
    target: Annotated[
        str,
        typer.Option(
            "--target",
            help="Export target: nf-core-rnaseq, deseq2-design, snakemake, canonical.",
        ),
    ],
    out: Annotated[Path, typer.Option("--out", help="Output path.")],
) -> None:
    """Export a cleaned sample sheet for a downstream workflow."""

    export_sheet(path, target=target, output=out)
    console.print(f"Wrote {target} export to {out}.")


@import_app.command("sra-runinfo")
def import_sra_runinfo_command(
    path: Annotated[
        Path,
        typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True),
    ],
    out: Annotated[Path, typer.Option("--out", help="Canonical CSV output path.")],
    schema: Annotated[
        str,
        typer.Option(
            "--schema", help="Accepted for command symmetry; currently unused."
        ),
    ] = "generic-ngs",
) -> None:
    """Convert an SRA-like RunInfo CSV into a canonical sample sheet."""

    del schema
    import_sra_runinfo(path, out)
    console.print(f"Wrote canonical sample sheet to {out}.")


@schema_app.command("show")
def schema_show(name: str) -> None:
    """Print a bundled or user-provided schema as loaded YAML-like data."""

    schema = load_schema(name)
    console.print(schema)


@schema_app.command("list")
def schema_list() -> None:
    """List bundled schemas."""

    console.print("generic-ngs")
    console.print("bulk-rnaseq")


@demo_app.command("init")
def demo_init() -> None:
    """Show where bundled examples live."""

    console.print("Use examples/valid and examples/broken in this repository.")


@demo_app.command("run")
def demo_run() -> None:
    """Run the missing-required-column demo."""

    demo_path = Path("examples/broken/missing_required_column.csv")
    report_path = Path("report.json")
    schema_obj = load_schema("bulk-rnaseq")
    table = read_table(demo_path)
    result = validate(table, schema=schema_obj)
    write_json_report(result, report_path)
    console.print(f"Wrote demo report to {report_path}.")
    if result.has_blocking_errors:
        raise typer.Exit(code=1)
