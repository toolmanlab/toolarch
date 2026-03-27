"""ToolArch CLI entry point."""

import typer

from toolarch.cli.analyze import analyze
from toolarch.cli.check import check
from toolarch.cli.report import report

app = typer.Typer(
    name="toolarch",
    help="Architecture intelligence for your codebase.",
    no_args_is_help=True,
)

app.command()(analyze)
app.command()(check)
app.command()(report)

if __name__ == "__main__":
    app()
