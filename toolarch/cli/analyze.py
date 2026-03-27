"""The `toolarch analyze` command."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

import typer
from rich.console import Console

console = Console()


class OutputFormat(str, Enum):
    terminal = "terminal"
    html = "html"
    json = "json"


class Lang(str, Enum):
    python = "python"
    java = "java"


def analyze(
    path: Path = typer.Argument(..., help="Root path of the project to analyze."),
    lang: Lang = typer.Option(Lang.python, help="Language to parse."),
    output: OutputFormat = typer.Option(OutputFormat.terminal, help="Output format."),
) -> None:
    """Parse code, build graph, run all analyzers, and output a report."""
    from toolarch.analyzers.cycles import CycleAnalyzer
    from toolarch.analyzers.martin import MartinAnalyzer
    from toolarch.analyzers.readability import ReadabilityAnalyzer
    from toolarch.graph.sqlite_graph import SQLiteGraph
    from toolarch.models import RunSummary
    from toolarch.parser.python_parser import PythonParser
    from toolarch.report.terminal import print_report

    path = path.resolve()
    if not path.exists():
        console.print(f"[red]Error:[/red] Path {path} does not exist.")
        raise typer.Exit(code=1)

    with console.status("[bold green]Parsing code..."):
        parser = PythonParser()
        parse_result = parser.parse(path)

    console.print(
        f"Parsed [cyan]{len(parse_result.nodes)}[/cyan] nodes, "
        f"[cyan]{len(parse_result.edges)}[/cyan] edges."
    )

    graph = SQLiteGraph()
    graph.load(parse_result)

    analyzers = [CycleAnalyzer(), MartinAnalyzer(), ReadabilityAnalyzer()]
    results = []
    for analyzer in analyzers:
        with console.status(f"[bold green]Running {analyzer.name}..."):
            result = analyzer.analyze(graph)
            results.append(result)

    summary = RunSummary(
        root_path=str(path),
        lang=lang.value,
        total_nodes=len(parse_result.nodes),
        total_edges=len(parse_result.edges),
        results=results,
    )

    graph.save_run(summary)

    if output == OutputFormat.terminal:
        print_report(summary)
    elif output == OutputFormat.html:
        from toolarch.report.html import generate_html_report

        out_path = Path("toolarch_report.html")
        generate_html_report(summary, out_path)
        console.print(f"HTML report written to [cyan]{out_path}[/cyan]")
    elif output == OutputFormat.json:
        console.print(summary.model_dump_json(indent=2))
