"""FASTQ and file-level metadata model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FileRecord:
    file_id: str
    sample_id: str
    run_id: str | None
    path: str
    file_type: str = "fastq"
    read_direction: str | None = None
    checksum: str | None = None
    exists: bool | None = None
    is_gzip_readable: bool | None = None
