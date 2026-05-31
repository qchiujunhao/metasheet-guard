from __future__ import annotations

from metasheet_guard.io.sra import import_sra_runinfo


def test_sra_runinfo_import(tmp_path) -> None:
    output = tmp_path / "canonical.csv"

    import_sra_runinfo("examples/sra_runinfo/SraRunInfo.csv", output)

    text = output.read_text(encoding="utf-8")
    assert "sample,run_id,condition,fastq_1,fastq_2" in text
    assert "SRR000001_1.fastq.gz" in text
