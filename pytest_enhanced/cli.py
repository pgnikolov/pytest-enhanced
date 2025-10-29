"""
CLI interface for pytest-enhanced.

Provides commands for reporting, flaky test detection,
slow test analysis, and data export.
"""

from __future__ import annotations
import typer, json, csv
from pathlib import Path
from typing import Optional
from rich.console import Console
from .analysis import get_session_stats, get_flaky_tests, get_slowest_tests
from .report import render_full_report
from .storage import fetch_all_runs, fetch_tests_for_run
from .utils import format_duration
from .web.server import run_server

app = typer.Typer(help="pytest-enhanced: analyze pytest stability and performance")
console = Console()


@app.command()
def report():
    """
    Generates and displays a comprehensive report based on session statistics.

    This command retrieves session statistics generated during pytest runs
    executed with the `--enhanced` flag. If no test runs are available in the
    current session, a message will be printed, and the program will exit with an
    error status.

    :raises typer.Exit: If no test runs are found, exits the command with a non-zero
        status after printing an appropriate message.
    :return: None
    """
    stats = get_session_stats()
    if stats is None:
        console.print("[red]No test runs found.[/red] Run pytest with [bold]--enhanced[/bold].")
        raise typer.Exit(1)
    render_full_report(stats)


@app.command()
def flaky():
    """
    Displays a list of flaky tests with their statistics or a message indicating no
    flaky tests were found. A test is considered flaky if it has failed at least twice
    in the last 20 runs. Outputs results in a formatted table using the `rich`
    library.

    Raises an exit code using `typer.Exit` if no flaky tests are found.

    :param flakes: List of tuples where each tuple contains the test name (str),
        the number of failed runs (int), and the total runs (int). Derived from the
        `get_flaky_tests` logic.
    :raises typer.Exit: Exits the application with an appropriate message if no flaky
        tests are found.
    """
    flakes = get_flaky_tests()
    if not flakes:
        console.print("[green]No flaky tests found (>=2 fails in last 20 runs).[/green]")
        raise typer.Exit()

    from rich.table import Table
    table = Table(title="🔥 Flaky tests", title_style="red", box=None)
    table.add_column("Test name", style="bold")
    table.add_column("Fails", justify="right")
    table.add_column("Total runs", justify="right")
    table.add_column("Instability %", justify="right")

    for name, fails, total in flakes:
        pct = (fails / total * 100.0) if total else 0.0
        table.add_row(name, str(fails), str(total), f"{pct:.1f}%")
    console.print(table)


@app.command()
def slow():
    """
    Prints the slowest tests recorded, if any, in a formatted table.

    This function retrieves the slowest test records and displays them in a
    styled table using the `rich` library. If no slow tests have been recorded,
    an appropriate message is shown, and the program exits.

    :param slows: List of tuples containing test name and duration of the
                  slow tests. Retrieved from the `get_slowest_tests` function.

    :raises typer.Exit: Raised when there are no slow tests recorded to exit
                        gracefully after notifying the user.
    :return: None
    """
    slows = get_slowest_tests()
    if not slows:
        console.print("[yellow]No slow tests recorded.[/yellow]")
        raise typer.Exit()

    from rich.table import Table
    table = Table(title="🐢 Slowest tests", title_style="yellow", box=None)
    table.add_column("Test name", style="bold")
    table.add_column("Duration", justify="right")

    for name, dur in slows:
        table.add_row(name, format_duration(dur))
    console.print(table)


@app.command()
def export(
        format: str = typer.Option("csv", "--format", "-f", help="Export format: csv or json"),
        output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
        limit: int = typer.Option(50, "--limit", "-l", help="Number of recent runs to include"),
):
    """
    Exports test results from a database in a specified format (csv or json).

    This method retrieves a specific number of the most recent test runs and their
    associated test data from the database, formats the data, and saves it to an
    output file. If no output path is provided, a default filename with the
    appropriate extension will be used.

    :param format: The export format, either "csv" or "json".
    :param output: The path to the output file where the results will be saved.
                   If not provided, a default filename is used.
    :param limit: The number of recent test runs to include in the export.
    :return: None
    """
    runs = fetch_all_runs(limit=limit)
    if not runs:
        typer.echo("No test runs found in database.")
        raise typer.Exit(0)

    all_data = []
    for run in runs:
        run_id = run["run_id"]
        tests = fetch_tests_for_run(run_id)
        for t in tests:
            all_data.append({
                "run_id": run_id,
                "started_at": run["started_at"],
                "finished_at": run.get("finished_at", ""),
                "test_name": t["test_name"],
                "status": t["status"],
                "duration": t["duration"],
                "error_message": t["error_message"] or "",
            })

    if not output:
        output = Path(f"pytest_enhanced_export.{format.lower()}")
    format = format.lower()

    if format == "json":
        with open(output, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2)
    elif format == "csv":
        keys = all_data[0].keys()
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_data)
    else:
        typer.echo("❌ Unsupported format. Use --format csv or --format json.")
        raise typer.Exit(1)

    typer.echo(f"✅ Exported {len(all_data)} test results to {output}")


@app.command()
def web(
        host: str = typer.Option("127.0.0.1", help="Host to bind the web server."),
        port: int = typer.Option(8000, help="Port for the web server.")
):
    """
    Starts a web server with specified host and port options.

    :param host: The host address to bind the web server, default is "127.0.0.1".
    :param port: The port number for the web server, default is 8000.
    :return: None
    """
    typer.echo(f"🌐 Starting web dashboard at http://{host}:{port}")
    run_server(host=host, port=port)

@app.command()
def html(output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output HTML file path")):
    """
    Generate an HTML report and optionally save it to the specified output file.

    This command utilizes the ``export_html_report`` function from the
    ``html_report`` module to generate the HTML report. If an output file
    path is provided, the generated report will be saved to the specified
    location.

    :param output: Optional; Path to the output HTML file. If not provided,
        the report will not be saved to a file.
    :return: None
    """
    from .html_report import export_html_report
    export_html_report(output)
