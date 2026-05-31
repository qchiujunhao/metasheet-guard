from __future__ import annotations

import yaml

from metasheet_guard.export.snakemake import export_snakemake


def test_snakemake_export(tmp_path) -> None:
    output = tmp_path / "config.yaml"

    export_snakemake("examples/valid/bulk_rnaseq_paired.csv", output)

    payload = yaml.safe_load(output.read_text(encoding="utf-8"))
    assert "CTRL_1" in payload["samples"]
