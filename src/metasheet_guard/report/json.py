"""JSON validation report writer."""

from __future__ import annotations

import json
from pathlib import Path

from metasheet_guard.result import ValidationResult


def write_json_report(result: ValidationResult, path: str | Path) -> None:
    """Write a machine-readable validation report."""

    output_path = Path(path)
    if output_path.parent != Path("."):
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
