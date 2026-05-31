"""Static HTML report writer."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from jinja2 import Template

from metasheet_guard.result import ValidationResult


def write_html_report(result: ValidationResult, path: str | Path) -> None:
    template_text = (
        resources.files("metasheet_guard.report.templates")
        .joinpath("report.html.j2")
        .read_text(encoding="utf-8")
    )
    template = Template(template_text)
    output_path = Path(path)
    if output_path.parent != Path("."):
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        template.render(report=result.to_dict()),
        encoding="utf-8",
    )
