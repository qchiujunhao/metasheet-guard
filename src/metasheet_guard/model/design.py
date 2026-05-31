"""Experimental design model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExperimentalDesign:
    primary_factor: str = "condition"
    condition_column: str = "condition"
    batch_column: str | None = "batch"
    replicate_column: str | None = "replicate"
    covariates: list[str] = field(default_factory=list)
    blocking_factors: list[str] = field(default_factory=list)
    comparison_groups: list[str] = field(default_factory=list)
