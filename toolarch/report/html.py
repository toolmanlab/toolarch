"""HTML report generation using Jinja2."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

from jinja2 import Template

from toolarch.models import RunSummary


def generate_html_report(summary: RunSummary, output_path: Path) -> None:
    """Render the analysis summary to an HTML file."""
    template_path = files("toolarch.report.templates").joinpath("report.html.j2")
    template_text = template_path.read_text()
    template = Template(template_text)

    html = template.render(
        summary=summary,
        results=summary.results,
    )
    output_path.write_text(html, encoding="utf-8")
