from __future__ import annotations

import json

import pytest

from metasheet_guard.repair import repair_sheet


def test_safe_repair_records_changes(tmp_path) -> None:
    result = repair_sheet(
        "examples/broken/condition_case_mixed.csv", schema="bulk-rnaseq"
    )
    clean = tmp_path / "clean.csv"
    changes = tmp_path / "changes.json"

    result.to_csv(clean)
    result.write_changes(changes)

    assert clean.exists()
    payload = json.loads(changes.read_text(encoding="utf-8"))
    rules = {change["rule"] for change in payload}
    assert "trim_and_lowercase" in rules
    assert "normalize_fastq_extension_case" in rules


def test_suggested_repairs_fail_explicitly() -> None:
    with pytest.raises(ValueError, match="Suggested repairs are not implemented"):
        repair_sheet(
            "examples/broken/condition_case_mixed.csv",
            schema="bulk-rnaseq",
            safe_only=False,
        )
