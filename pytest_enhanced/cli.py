from __future__ import annotations
import typer, json, csv
from pathlib import Path
from typing import Optional
from rich.console import Console
from .analysis import get_session_stats, get_flaky_tests, get_slowest_tests
from .report import render_full_report
from .storage import fetch_all_runs, fetch_tests_for_run
from .utils import format_duration

app = typer.Typer(help="pytest-enhanced: analyze pytest stability and performance")
console = Console()


@app.command()
def report():
    stats = get_session_stats()
    if stats is None:
        console.print("[red]No test runs found.[/red] Run pytest with [bold]--enhanced[/bold].")
        raise typer.Exit(1)
    render_full_report(stats)


@app.command()
def flaky():
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
    """Export historical pytest analytics data in CSV or JSON format."""
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
