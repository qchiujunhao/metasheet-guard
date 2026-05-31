from __future__ import annotations

from metasheet_guard.export.nfcore_rnaseq import export_nfcore_rnaseq


def test_nfcore_export(tmp_path) -> None:
    output = tmp_path / "nfcore.csv"

    export_nfcore_rnaseq("examples/valid/bulk_rnaseq_paired.csv", output)

    text = output.read_text(encoding="utf-8")
    assert text.splitlines()[0] == "sample,fastq_1,fastq_2,strandedness"
    assert "CTRL_1" in text
