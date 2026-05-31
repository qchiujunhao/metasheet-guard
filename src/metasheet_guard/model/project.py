"""Canonical project model built from a sample sheet."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from metasheet_guard.io.csv import SheetTable, read_table
from metasheet_guard.model.design import ExperimentalDesign
from metasheet_guard.model.file import FileRecord
from metasheet_guard.model.run import SequencingRun
from metasheet_guard.model.sample import BiologicalSample

LANE_RE = re.compile(r"(?:^|[_-])(L\d{3})(?:[_-]|$)", re.IGNORECASE)


@dataclass(frozen=True)
class Project:
    samples: list[BiologicalSample] = field(default_factory=list)
    runs: list[SequencingRun] = field(default_factory=list)
    files: list[FileRecord] = field(default_factory=list)
    design: ExperimentalDesign = field(default_factory=ExperimentalDesign)
    rows: list[dict[str, str]] = field(default_factory=list)

    @classmethod
    def from_csv(cls, path: str | Path) -> Project:
        return cls.from_table(read_table(path))

    @classmethod
    def from_table(cls, table: SheetTable) -> Project:
        rows = table.records()
        samples: dict[str, BiologicalSample] = {}
        runs: list[SequencingRun] = []
        files: list[FileRecord] = []

        for index, row in enumerate(rows, start=1):
            sample_id = _clean(row.get("sample")) or f"row_{index}"
            if sample_id not in samples:
                samples[sample_id] = BiologicalSample(
                    sample_id=sample_id,
                    subject_id=_clean(row.get("subject_id")),
                    organism=_clean(row.get("organism")),
                    tissue=_clean(row.get("tissue")),
                    genotype=_clean(row.get("genotype")),
                    sex=_clean(row.get("sex")),
                    condition=_clean(row.get("condition")),
                    biological_replicate=_clean(row.get("replicate")),
                    batch=_clean(row.get("batch")),
                    attributes={
                        key: value
                        for key, value in row.items()
                        if key
                        not in {
                            "sample",
                            "subject_id",
                            "organism",
                            "tissue",
                            "genotype",
                            "sex",
                            "condition",
                            "replicate",
                            "batch",
                        }
                    },
                )

            run_id = (
                _clean(row.get("run_id")) or _clean(row.get("run")) or f"row_{index}"
            )
            fastq_1 = _clean(row.get("fastq_1"))
            fastq_2 = _clean(row.get("fastq_2"))
            lane = _clean(row.get("lane")) or _lane_from_paths(fastq_1, fastq_2)
            runs.append(
                SequencingRun(
                    run_id=run_id,
                    sample_id=sample_id,
                    lane=lane,
                    platform=_clean(row.get("platform")),
                    instrument=_clean(row.get("instrument")),
                    library_strategy=_clean(row.get("library_strategy")),
                    library_layout=_clean(row.get("library_layout")),
                    strandedness=_clean(row.get("strandedness")),
                    attributes=row,
                )
            )
            if fastq_1:
                files.append(
                    FileRecord(
                        file_id=f"{run_id}:R1",
                        sample_id=sample_id,
                        run_id=run_id,
                        path=fastq_1,
                        read_direction="R1",
                    )
                )
            if fastq_2:
                files.append(
                    FileRecord(
                        file_id=f"{run_id}:R2",
                        sample_id=sample_id,
                        run_id=run_id,
                        path=fastq_2,
                        read_direction="R2",
                    )
                )

        return cls(samples=list(samples.values()), runs=runs, files=files, rows=rows)

    def sample_rows(self) -> dict[str, list[dict[str, str]]]:
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in self.rows:
            sample_id = _clean(row.get("sample"))
            if sample_id:
                grouped[sample_id].append(row)
        return dict(grouped)


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _lane_from_paths(*paths: str | None) -> str | None:
    for path in paths:
        if not path:
            continue
        match = LANE_RE.search(Path(path).name)
        if match:
            return match.group(1).upper()
    return None
