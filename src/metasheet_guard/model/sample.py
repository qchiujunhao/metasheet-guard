"""Biological sample model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BiologicalSample:
    sample_id: str
    subject_id: str | None = None
    organism: str | None = None
    tissue: str | None = None
    genotype: str | None = None
    sex: str | None = None
    condition: str | None = None
    biological_replicate: str | None = None
    batch: str | None = None
    attributes: dict[str, str] = field(default_factory=dict)
