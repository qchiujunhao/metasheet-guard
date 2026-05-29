"""Base protocols for validators."""

from __future__ import annotations

from typing import Protocol

from metasheet_guard.io.csv import SheetTable
from metasheet_guard.issue import Issue
from metasheet_guard.schema.loader import Schema


class Validator(Protocol):
    """Protocol implemented by all validators."""

    def run(self, table: SheetTable, schema: Schema) -> list[Issue]:
        """Return issues detected by the validator."""
