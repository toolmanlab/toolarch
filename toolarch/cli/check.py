"""The `toolarch check` command — CI mode with exit codes."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def check(
    path: Path = typer.Argument(".", help="Root path of the project to check."),
    rules: str = typer.Option(
        "cycles,martin",
        help="Comma-separated list of rules to check: cycles, layers, martin.",
    ),
    fail_on_error: bool = typer.Option(
        True, "--fail-on-error/--no-fail-on-error", help="Exit non-zero on issues."
    ),
) -> None:
    """Run architecture checks in CI mode."""
    from toolarch.analyzers.cycles import CycleAnalyzer
    from toolarch.analyzers.layers import LayerAnalyzer
    from toolarch.analyzers.martin import MartinAnalyzer
    from toolarch.graph.sqlite_graph import SQLiteGraph
    from toolarch.models import Severity
    from toolarch.parser.python_parser import PythonParser

    path = path.resolve()
    rule_set = {r.strip() for r in rules.split(",")}

    analyzer_map = {
        "cycles": CycleAnalyzer,
        "layers": LayerAnalyzer,
        "martin": MartinAnalyzer,
    }

    parser = PythonParser()
    parse_result = parser.parse(path)

    graph = SQLiteGraph()
    graph.load(parse_result)

    total_issues = 0
    for rule_name in sorted(rule_set):
        cls = analyzer_map.get(rule_name)
        if cls is None:
            console.print(f"[yellow]Warning:[/yellow] Unknown rule '{rule_name}', skipping.")
            continue
        result = cls().analyze(graph)
        high = [i for i in result.issues if i.severity == Severity.HIGH]
        if high:
            console.print(f"[red]FAIL[/red] {rule_name}: {len(high)} high-severity issue(s)")
            for issue in high:
                console.print(f"  - {issue.message}")
            total_issues += len(high)
        else:
            console.print(f"[green]PASS[/green] {rule_name}")

    if total_issues > 0 and fail_on_error:
        raise typer.Exit(code=1)
