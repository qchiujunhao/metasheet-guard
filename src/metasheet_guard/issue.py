"""Issue model used by validators and reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class Issue:
    """A validation issue with stable machine-readable metadata."""

    code: str
    severity: Severity
    message: str
    suggestion: str | None = None
    row: int | None = None
    column: str | None = None
    sample_id: str | None = None
    run_id: str | None = None
    file_path: str | None = None
    repairable: bool = False

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation without empty optional fields."""

        return {key: value for key, value in asdict(self).items() if value is not None}
