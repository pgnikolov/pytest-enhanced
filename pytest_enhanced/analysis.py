from __future__ import annotations

from typing import Dict, List, Tuple, Optional

from .storage import (
    fetch_last_run_id,
    fetch_run_summary,
    fetch_slowest_tests,
    fetch_flaky_tests,
    fetch_pass_rate_history,
)


def get_session_stats() -> Optional[Dict]:
    """
    Fetches and calculates session statistics based on the latest test run.

    This function retrieves the latest run ID and fetches associated data to
    compile session statistics. The statistics include summary details, pass
    rate, a list of the slowest tests, flaky test information, and pass rate
    history.

    :raises KeyError: Raised if any expected key is missing in the fetched data.

    :return: A dictionary containing session statistics, or None if no run ID
        is available.
    :rtype: Optional[Dict]
    """
    run_id = fetch_last_run_id()
    if run_id is None:
        return None

    summary = fetch_run_summary(run_id)
    total = summary["total"] or 1  # avoid div by zero
    pass_rate = (summary["passed"] / total) * 100.0

    slow = fetch_slowest_tests(run_id, limit=5)
    flaky = fetch_flaky_tests(window=20, min_failures=2)
    hist = fetch_pass_rate_history(limit=10)

    return {
        "run_id": run_id,
        "summary": summary,
        "pass_rate": pass_rate,
        "slow_tests": slow,
        "flaky_tests": flaky,
        "history": hist,
    }


def get_flaky_tests() -> List[Tuple[str, int, int]]:
    """
    Retrieves a list of tests identified as flaky. Flaky tests are tests that do not
    consistently pass and may fail intermittently due to reasons other than code
    issues. The fetch operation uses configurable criteria, such as the window
    size and minimum failures.

    :return: A list of tuples where each tuple contains the test name (str), the
        number of failures (int), and the failure window (int).
    :rtype: List[Tuple[str, int, int]]
    """
    return fetch_flaky_tests(window=20, min_failures=2)


def get_slowest_tests() -> List[Tuple[str, float]]:
    """
    Retrieve the slowest tests from the most recent test run.

    This function fetches the identifier of the most recent test run and
    retrieves the ten slowest tests from that run, along with their execution times.
    If there is no recent test run available, it returns an empty list.

    :return: A list of tuples where each tuple consists of the test name and
        its execution time in seconds. Returns an empty list if no test data
        is found.
    :rtype: List[Tuple[str, float]]
    """
    run_id = fetch_last_run_id()
    if run_id is None:
        return []
    return fetch_slowest_tests(run_id, limit=10)
