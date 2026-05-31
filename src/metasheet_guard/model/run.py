"""Sequencing run model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SequencingRun:
    run_id: str
    sample_id: str
    lane: str | None = None
    platform: str | None = None
    instrument: str | None = None
    library_strategy: str | None = None
    library_layout: str | None = None
    strandedness: str | None = None
    attributes: dict[str, str] = field(default_factory=dict)
