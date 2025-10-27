from __future__ import annotations

import typer
from rich.console import Console

from .analysis import get_session_stats, get_flaky_tests, get_slowest_tests
from .report import render_full_report

app = typer.Typer(help="pytest-enhanced: analyze pytest stability and performance")
console = Console()


@app.command()
def report():
    """
    Generate and display a detailed test report based on session statistics.

    This command retrieves session statistics and uses this data to generate a
    comprehensive report. If no session statistics are found, the command will
    terminate with an appropriate message.

    :raises typer.Exit: If no session statistics are available.
    :return: None
    """
    stats = get_session_stats()
    if stats is None:
        console.print("[red]No test runs found.[/red] Did you run pytest with [bold]--enhanced[/bold]?")
        raise typer.Exit(code=1)

    render_full_report(stats)


@app.command()
def flaky():
    """
    Retrieve and display a list of flaky tests based on recent run results.

    This function identifies flaky tests that have failed at least twice
    in the last 20 runs. If no such tests are found, a success message
    is displayed and the program exits. Otherwise, it formats the data
    into a visually appealing table and prints it to the console.

    :raises typer.Exit: If no flaky tests are found.
    :return: None
    """
    flakes = get_flaky_tests()

    if not flakes:
        console.print("[green]No flaky tests found (>=2 fails in last 20 runs).[/green]")
        raise typer.Exit()

    from rich.table import Table
    table = Table(title="🔥 Flaky tests", title_style="red", box=None)
    table.add_column("Test name", style="bold")
    table.add_column("Fails", justify="right")
    table.add_column("Total runs seen", justify="right")
    table.add_column("Instability %", justify="right")

    for test_name, fails, total in flakes:
        pct = (fails / total * 100.0) if total else 0.0
        table.add_row(test_name, str(fails), str(total), f"{pct:.1f}%")

    console.print(table)


@app.command()
def slow():
    """
    Display the slowest tests recorded.

    This command retrieves and displays a list of the slowest tests recorded, if any exist. It
    shows the test names alongside their respective durations in a tabular format using the
    Rich library. If no slow tests are recorded, a message is printed, and the application
    exits.

    :raises typer.Exit: If no slow tests are recorded.
    """
    slows = get_slowest_tests()
    if not slows:
        console.print("[yellow]No slow tests recorded.[/yellow]")
        raise typer.Exit()

    from rich.table import Table
    from .utils import format_duration

    table = Table(title="🐢 Slowest tests", title_style="yellow", box=None)
    table.add_column("Test name", style="bold")
    table.add_column("Duration", justify="right")

    for test_name, dur in slows:
        table.add_row(test_name, format_duration(dur))

    console.print(table)
