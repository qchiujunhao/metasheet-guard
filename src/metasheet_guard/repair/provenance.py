"""Repair provenance models."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from metasheet_guard.io.csv import write_table


@dataclass(frozen=True)
class RepairChange:
    row: int | None
    column: str
    old: str
    new: str
    rule: str
    repair_level: str = "safe"
    confidence: str = "high"

    def to_dict(self) -> dict[str, object]:
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass(frozen=True)
class RepairResult:
    rows: list[dict[str, str]]
    columns: list[str]
    changes: list[RepairChange] = field(default_factory=list)

    def to_csv(self, path: str | Path) -> None:
        write_table(self.rows, path, columns=self.columns)

    def write_changes(self, path: str | Path) -> None:
        output_path = Path(path)
        if output_path.parent != Path("."):
            output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps([change.to_dict() for change in self.changes], indent=2) + "\n",
            encoding="utf-8",
        )
