from __future__ import annotations

from pathlib import Path

import pytest

from metasheet_guard.schema.loader import SchemaError, load_schema


def test_load_bundled_schema_by_name() -> None:
    schema = load_schema("bulk-rnaseq")

    assert schema.name == "bulk-rnaseq"
    assert schema.required_columns == ["sample", "fastq_1", "condition"]
    assert "condition" in schema.columns


def test_load_schema_from_path(tmp_path: Path) -> None:
    schema_path = tmp_path / "custom.yaml"
    schema_path.write_text(
        """
name: custom
version: 0.1.0
required_columns:
  - sample
columns:
  sample:
    type: string
""",
        encoding="utf-8",
    )

    schema = load_schema(schema_path)

    assert schema.name == "custom"
    assert schema.required_columns == ["sample"]


def test_schema_loader_rejects_missing_required_keys(tmp_path: Path) -> None:
    schema_path = tmp_path / "bad.yaml"
    schema_path.write_text("name: bad\n", encoding="utf-8")

    with pytest.raises(SchemaError):
        load_schema(schema_path)
