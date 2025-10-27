from __future__ import annotations

from typing import Dict, List, Tuple

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .utils import format_duration


console = Console()


def _render_header(run_id: int, pass_rate: float, summary: Dict[str, int]) -> None:
    """
    Generates and renders a header section for a pytest enhanced report. This header
    includes information such as the run ID, total number of tests, the count of tests
    that passed, failed, or were skipped, and the pass rate percentage. The output
    is formatted and displayed using styled text for enhanced readability.

    :param run_id: The unique identifier for the test run.
    :type run_id: int
    :param pass_rate: The percentage of tests that passed in the run.
    :type pass_rate: float
    :param summary: A dictionary containing the summary of test results. Expected
        keys are "total", "passed", "failed", and "skipped".
    :type summary: Dict[str, int]
    :return: This function does not return any value. It directly prints the styled
        output using the console.
    :rtype: None
    """
    total = summary["total"]
    passed = summary["passed"]
    failed = summary["failed"]
    skipped = summary["skipped"]

    header_text = Text()
    header_text.append("📊 Pytest Enhanced Report", style="bold magenta")
    header_text.append(f" — Run #{run_id}\n", style="magenta")
    header_text.append("──────────────────────────────────────────\n", style="dim")
    header_text.append(f"Total tests: {total}\n", style="bold")
    header_text.append(f"Passed: {passed}  |  Failed: {failed}  |  Skipped: {skipped}\n")
    header_text.append(f"Pass rate: {pass_rate:.1f}%\n")

    console.print(Panel(header_text, expand=False, border_style="magenta"))


def _render_slowest(slow_tests: List[Tuple[str, float]]) -> None:
    """
    Renders a panel or table displaying the slowest tests and their average durations.
    If no slow tests are recorded, a message panel is displayed instead.

    :param slow_tests: A list of tuples where each tuple contains the name of the
        test as a string and its average duration as a float.
    :return: This function does not return a value. It performs operations that
        print content to the console.
    """
    if not slow_tests:
        console.print(Panel("No slow tests recorded.", title="🐢 Slowest tests", border_style="yellow"))
        return

    table = Table(title="🐢 Slowest tests", title_style="yellow", expand=False, box=None)
    table.add_column("Test name", style="bold")
    table.add_column("Avg duration", justify="right")

    for test_name, dur in slow_tests:
        table.add_row(test_name, format_duration(dur))

    console.print(table)


def _render_flaky(flaky_tests: List[Tuple[str, int, int]]) -> None:
    """
    Renders a report for flaky tests in a formatted table. If the list of flaky tests
    is empty, a message indicating no flaky tests detected is displayed instead.

    :param flaky_tests: A list of tuples where each tuple contains:
                        - Test name (str): Name of the test
                        - Fails (int): Number of test failures
                        - Total (int): Total number of test runs
    :return: None
    """
    if not flaky_tests:
        console.print(Panel("No flaky tests detected (min 2 fails in last 20 runs).",
                            title="🔥 Flaky tests", border_style="red"))
        return

    table = Table(title="🔥 Flaky tests", title_style="red", expand=False, box=None)
    table.add_column("Test name", style="bold")
    table.add_column("Fails", justify="right")
    table.add_column("Total runs seen", justify="right")
    table.add_column("Instability %", justify="right")

    for test_name, fails, total in flaky_tests:
        instability = (fails / total) * 100.0 if total else 0.0
        table.add_row(test_name, str(fails), str(total), f"{instability:.1f}%")

    console.print(table)


def _render_history(history: List[Tuple[int, float]]) -> None:
    """
    Renders a visual representation of the pass rate history. If the history
    is empty, it displays a message indicating the absence of data. For
    non-empty history, it displays a trend line and detailed pass rate
    information for each run.

    The trend line uses colored blocks to indicate performance:
    green for pass rates >= 90% and red otherwise.

    :param history: List of tuples where each tuple contains a run ID (int)
        and pass rate (float).
    :type history: List[Tuple[int, float]]

    :return: None
    """
    if not history:
        console.print(Panel("No history yet.", title="📈 Pass rate history", border_style="blue"))
        return

    # reverse so oldest first visually
    hist_rev = list(reversed(history))

    # make a simple block graph: pass >= 90 => green block, else red block
    blocks = []
    for _, rate in hist_rev:
        if rate >= 90.0:
            blocks.append("🟩")
        else:
            blocks.append("🟥")

    trend_line = "".join(blocks)
    detail_lines = []
    for run_id, rate in hist_rev:
        detail_lines.append(f"Run {run_id}: {rate:.1f}%")

    panel_text = f"{trend_line}\n" + "\n".join(detail_lines)
    console.print(Panel(panel_text, title="📈 Pass rate trend", border_style="blue"))


def render_full_report(stats: Dict) -> None:
    """
    Renders the complete test report by invoking sub-rendering methods for different
    sections. The report is generated for a given set of test statistics, which
    include header information, slow tests data, flaky tests data, and test
    history. It also provides a tip on improving test stability. This function does
    not return any value.

    :param stats: A dictionary containing the test statistics required for rendering
                  the report. It includes keys such as "run_id" for the test run
                  identifier, "pass_rate" for the test success percentage, "summary"
                  for aggregated test details, "slow_tests" for timing details of
                  slow tests, "flaky_tests" for unstable test information, and
                  "history" for past test results and data.
    :type stats: Dict
    :return: None
    """
    _render_header(
        run_id=stats["run_id"],
        pass_rate=stats["pass_rate"],
        summary=stats["summary"],
    )
    _render_slowest(stats["slow_tests"])
    _render_flaky(stats["flaky_tests"])
    _render_history(stats["history"])

    console.print(
        "\nTip: Unstable tests usually depend on timing, randomness, or external services.\n",
        style="dim",
    )
