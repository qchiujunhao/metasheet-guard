from __future__ import annotations

from metasheet_guard.export.deseq2 import export_deseq2_design


def test_deseq2_export(tmp_path) -> None:
    output = tmp_path / "design.tsv"

    export_deseq2_design("examples/valid/bulk_rnaseq_paired.csv", output)

    text = output.read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith("sample\tcondition")
    assert "CTRL_1\tcontrol" in text
