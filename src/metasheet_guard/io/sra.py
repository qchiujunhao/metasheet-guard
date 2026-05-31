"""SRA RunInfo importer."""

from __future__ import annotations

from pathlib import Path

from metasheet_guard.io.csv import read_table, write_table


def import_sra_runinfo(path: str | Path, output: str | Path) -> None:
    table = read_table(path)
    rows: list[dict[str, str]] = []
    for row in table.records():
        run = row.get("Run", "").strip() or row.get("run", "").strip()
        sample = (
            row.get("SampleName", "").strip()
            or row.get("Sample Name", "").strip()
            or row.get("BioSample", "").strip()
            or run
        )
        layout = (
            row.get("LibraryLayout", "").strip()
            or row.get("Library Layout", "").strip()
        ).upper()
        canonical = {
            "sample": sample,
            "run_id": run,
            "condition": row.get("condition", "").strip(),
            "fastq_1": f"{run}_1.fastq.gz" if run else "",
            "fastq_2": f"{run}_2.fastq.gz" if layout == "PAIRED" and run else "",
            "library_layout": layout.lower() if layout else "",
            "library_strategy": row.get("LibraryStrategy", "").strip(),
            "platform": row.get("Platform", "").strip(),
        }
        rows.append(canonical)
    write_table(
        rows,
        output,
        columns=[
            "sample",
            "run_id",
            "condition",
            "fastq_1",
            "fastq_2",
            "library_layout",
            "library_strategy",
            "platform",
        ],
    )
