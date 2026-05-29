"""YAML schema loader for bundled and user-provided schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any

import yaml


class SchemaError(ValueError):
    """Raised when a schema cannot be loaded or is structurally invalid."""


@dataclass(frozen=True)
class ColumnSpec:
    """Column-level schema metadata used by validators and future repair rules."""

    name: str
    type: str = "string"
    pattern: str | None = None
    aliases: list[str] = field(default_factory=list)
    values: list[str] = field(default_factory=list)
    repair: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Schema:
    """A loaded MetaSheet-Guard schema."""

    name: str
    version: str
    required_columns: list[str]
    recommended_columns: list[str]
    columns: dict[str, ColumnSpec]
    rules: dict[str, list[str]]
    source: str


def load_schema(schema: str | Path | Schema) -> Schema:
    """Load a bundled schema by name or a user-provided YAML schema by path."""

    if isinstance(schema, Schema):
        return schema

    source_path = _resolve_schema_path(schema)
    with source_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    if not isinstance(raw, dict):
        raise SchemaError(f"Schema must be a mapping: {source_path}")

    return _build_schema(raw, source=str(source_path))


def _resolve_schema_path(schema: str | Path) -> Path:
    candidate = Path(schema)
    if candidate.exists():
        return candidate

    if candidate.suffix in {".yaml", ".yml"}:
        raise SchemaError(f"Schema file does not exist: {schema}")

    bundled = resources.files("metasheet_guard.schemas").joinpath(f"{schema}.yaml")
    if not bundled.is_file():
        raise SchemaError(f"Unknown bundled schema: {schema}")
    return Path(str(bundled))


def _build_schema(raw: dict[str, Any], source: str) -> Schema:
    required_keys = ["name", "version", "required_columns", "columns"]
    missing = [key for key in required_keys if key not in raw]
    if missing:
        raise SchemaError(f"Schema is missing required keys: {', '.join(missing)}")

    if not isinstance(raw["required_columns"], list):
        raise SchemaError("Schema required_columns must be a list")
    if not isinstance(raw["columns"], dict):
        raise SchemaError("Schema columns must be a mapping")

    column_specs = {
        name: ColumnSpec(
            name=name,
            type=str(spec.get("type", "string")),
            pattern=spec.get("pattern"),
            aliases=list(spec.get("aliases", [])),
            values=list(spec.get("values", [])),
            repair=dict(spec.get("repair", {})),
        )
        for name, spec in raw["columns"].items()
        if isinstance(spec, dict)
    }

    missing_specs = [
        column for column in raw["required_columns"] if column not in column_specs
    ]
    if missing_specs:
        raise SchemaError(
            "Required columns are missing column specifications: "
            + ", ".join(missing_specs)
        )

    return Schema(
        name=str(raw["name"]),
        version=str(raw["version"]),
        required_columns=list(raw["required_columns"]),
        recommended_columns=list(raw.get("recommended_columns", [])),
        columns=column_specs,
        rules={
            group: list(rule_names)
            for group, rule_names in dict(raw.get("rules", {})).items()
            if isinstance(rule_names, list)
        },
        source=source,
    )
