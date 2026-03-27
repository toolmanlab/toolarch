"""The `toolarch report` command — regenerate reports from last run."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

import typer
from rich.console import Console

console = Console()


class ReportFormat(str, Enum):
    terminal = "terminal"
    html = "html"


def report(
    fmt: ReportFormat = typer.Option(
        ReportFormat.terminal, "--format", help="Report output format."
    ),
    last: bool = typer.Option(True, "--last/--no-last", help="Use the last analysis run."),
) -> None:
    """Regenerate a report from the last analysis run."""
    from toolarch.graph.sqlite_graph import SQLiteGraph
    from toolarch.report.terminal import print_report

    graph = SQLiteGraph()
    summary = graph.load_last_run()

    if summary is None:
        console.print("[yellow]No previous analysis run found.[/yellow] Run `toolarch analyze` first.")
        raise typer.Exit(code=1)

    if fmt == ReportFormat.terminal:
        print_report(summary)
    elif fmt == ReportFormat.html:
        from toolarch.report.html import generate_html_report

        out_path = Path("toolarch_report.html")
        generate_html_report(summary, out_path)
        console.print(f"HTML report written to [cyan]{out_path}[/cyan]")
