from __future__ import annotations

from pathlib import Path

from metasheet_guard.io.csv import read_table
from metasheet_guard.model import Project


def test_project_model_groups_multilane_sample() -> None:
    table = read_table(Path("examples/valid/bulk_rnaseq_multilane.csv"))

    project = Project.from_table(table)

    assert {sample.sample_id for sample in project.samples} == {
        "CTRL_1",
        "CTRL_2",
        "TREAT_1",
        "TREAT_2",
    }
    assert len(project.runs) == 5
    assert len(project.files) == 10
