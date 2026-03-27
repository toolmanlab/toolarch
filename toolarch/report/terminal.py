"""Rich terminal report output."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from toolarch.models import RunSummary, Severity

console = Console()


def print_report(summary: RunSummary) -> None:
    """Print a formatted terminal report."""
    # Header
    console.print()
    console.print(
        Panel(
            f"[bold]ToolArch Analysis Report[/bold]\n"
            f"Path: {summary.root_path}\n"
            f"Language: {summary.lang}\n"
            f"Nodes: {summary.total_nodes} | Edges: {summary.total_edges} | "
            f"Issues: {summary.total_issues}",
            border_style="blue",
        )
    )

    # Per-analyzer results
    for result in summary.results:
        _print_analyzer_result(result, summary)

    # Summary footer
    if summary.high_severity_count > 0:
        console.print(
            f"\n[red bold]!! {summary.high_severity_count} high-severity issue(s) found.[/red bold]"
        )
    else:
        console.print("\n[green]No high-severity issues.[/green]")
    console.print()


def _print_analyzer_result(result, summary: RunSummary) -> None:
    severity_style = {
        Severity.HIGH: "red bold",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "dim",
        Severity.INFO: "blue",
    }

    console.print(f"\n[bold cyan]── {result.analyzer} ──[/bold cyan]")
    if result.summary:
        console.print(f"  {result.summary}")

    # Issues
    if result.issues:
        tree = Tree("[bold]Issues")
        for issue in result.issues:
            style = severity_style.get(issue.severity, "")
            label = f"[{style}][{issue.severity.value.upper()}][/{style}] {issue.message}"
            if issue.location:
                label += f" ({issue.location})"
            tree.add(label)
        console.print(tree)

    # Metrics: show top 10 worst if applicable
    if result.metrics:
        # Filter to the primary metric for this analyzer
        primary_metrics = result.metrics
        if result.analyzer == "martin":
            primary_metrics = [m for m in result.metrics if m.name == "distance"]
            primary_metrics.sort(key=lambda m: m.value, reverse=True)
        elif result.analyzer == "readability":
            primary_metrics.sort(key=lambda m: m.value)

        top_n = primary_metrics[:10]
        if top_n:
            table = Table(title=f"Top {len(top_n)} by {result.analyzer}", show_lines=False)
            table.add_column("Node ID", style="dim", max_width=14)
            table.add_column("Metric")
            table.add_column("Value", justify="right")
            for m in top_n:
                table.add_row(m.node_id, m.name, f"{m.value:.2f}")
            console.print(table)
