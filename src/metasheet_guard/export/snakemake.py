"""Snakemake config exporter."""

from __future__ import annotations

from pathlib import Path

import yaml

from metasheet_guard.io.csv import SheetTable, read_table


def export_snakemake(sheet: SheetTable | str | Path, output: str | Path) -> None:
    table = read_table(sheet) if isinstance(sheet, str | Path) else sheet
    missing = [
        column for column in ["sample", "fastq_1"] if column not in table.column_names
    ]
    if missing:
        raise ValueError(
            "Cannot export Snakemake config; missing columns: " + ", ".join(missing)
        )
    samples: dict[str, list[dict[str, str]]] = {}
    for row in table.records():
        sample = row.get("sample", "")
        samples.setdefault(sample, []).append(
            {
                "fastq_1": row.get("fastq_1", ""),
                "fastq_2": row.get("fastq_2", ""),
                "condition": row.get("condition", ""),
                "batch": row.get("batch", ""),
            }
        )
    output_path = Path(output)
    if output_path.parent != Path("."):
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump({"samples": samples}, sort_keys=True),
        encoding="utf-8",
    )
