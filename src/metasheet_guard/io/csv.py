"""CSV and TSV sample sheet reader."""

from __future__ import annotations

import csv
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TableRow:
    """A row from a sample sheet with both positional and name-based access."""

    line_number: int
    values: list[str]
    by_column: dict[str, str]


@dataclass(frozen=True)
class SheetTable:
    """A parsed delimited sample sheet.

    Headers are preserved exactly for duplicate-column validation. Header lookups
    use stripped names because accidental surrounding whitespace is common in
    manually edited sample sheets.
    """

    path: Path
    delimiter: str
    headers: list[str]
    rows: list[TableRow]

    @property
    def column_names(self) -> list[str]:
        return [header.strip() for header in self.headers]

    @property
    def duplicate_columns(self) -> list[str]:
        counts = Counter(self.column_names)
        return sorted(
            column for column, count in counts.items() if column and count > 1
        )

    def has_column(self, column: str) -> bool:
        return column in self.column_names

    def first_column_index(self, column: str) -> int | None:
        for index, header in enumerate(self.column_names):
            if header == column:
                return index
        return None

    def value(self, row: TableRow, column: str) -> str | None:
        index = self.first_column_index(column)
        if index is None or index >= len(row.values):
            return None
        return row.values[index]

    def records(self) -> list[dict[str, str]]:
        """Return rows as dictionaries keyed by stripped column names."""

        return [row.by_column for row in self.rows]


def read_table(path: str | Path, delimiter: str | None = None) -> SheetTable:
    """Read a CSV or TSV sample sheet while preserving duplicate headers."""

    table_path = Path(path)
    text = table_path.read_text(encoding="utf-8-sig")
    if not text.strip():
        raise ValueError(f"Sample sheet is empty: {table_path}")

    delimiter = delimiter or _detect_delimiter(table_path, text)
    reader = csv.reader(text.splitlines(), delimiter=delimiter)
    raw_rows = list(reader)
    if not raw_rows:
        raise ValueError(f"Sample sheet has no rows: {table_path}")

    headers = raw_rows[0]
    rows: list[TableRow] = []
    for line_number, values in enumerate(raw_rows[1:], start=2):
        by_column = {
            header.strip(): values[index] if index < len(values) else ""
            for index, header in enumerate(headers)
            if header.strip()
        }
        rows.append(
            TableRow(line_number=line_number, values=values, by_column=by_column)
        )

    return SheetTable(
        path=table_path,
        delimiter=delimiter,
        headers=headers,
        rows=rows,
    )


def _detect_delimiter(path: Path, text: str) -> str:
    suffix = path.suffix.lower()
    if suffix in {".tsv", ".tab"}:
        return "\t"
    if suffix == ".csv":
        return ","

    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",\t")
    except csv.Error:
        return ","
    return dialect.delimiter


def write_table(
    rows: Iterable[dict[str, object]],
    path: str | Path,
    columns: list[str] | None = None,
    delimiter: str = ",",
) -> None:
    """Write dictionaries to a CSV or TSV file with stable column order."""

    row_list = [dict(row) for row in rows]
    if columns is None:
        seen: list[str] = []
        for row in row_list:
            for column in row:
                if column not in seen:
                    seen.append(column)
        columns = seen

    output_path = Path(path)
    if output_path.parent != Path("."):
        output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter=delimiter)
        writer.writeheader()
        for row in row_list:
            writer.writerow({column: row.get(column, "") for column in columns})
