from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from .utils import get_data_dir, utcnow_iso


DB_FILENAME = "results.db"


def _get_db_path() -> Path:
    """
    Retrieves the full file path to the database.

    This function constructs the absolute file path to the database file by
    accessing the data directory and appending the database file name. It
    ensures the path points to the expected database location, combining the
    base data directory with the predefined database file name.

    :return: The full `Path` object pointing to the database file.
    :rtype: Path
    """
    return get_data_dir() / DB_FILENAME


def get_connection() -> sqlite3.Connection:
    """
    Creates and returns a connection to the SQLite3 database.

    The function establishes a connection to the database using the `_get_db_path`
    to identify the database path and sets the `row_factory` of the connection to
    `sqlite3.Row` for enabling dictionary-like row access.

    :return: SQLite3 database connection.
    :rtype: sqlite3.Connection
    """
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db() -> None:
    """
    Ensures that the necessary database tables for storing test run and test result
    information exist. If the required tables do not exist, they are created.

    :raises Exception: If there is an issue during the database operation.
    :return: None
    """
    conn = get_connection()
    cur = conn.cursor()

    # test_runs: one row per pytest session
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS test_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            finished_at TEXT
        )
        """
    )

    # test_results: each test function result in that run
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            test_name TEXT NOT NULL,
            status TEXT NOT NULL,
            duration REAL NOT NULL,
            error_message TEXT,
            FOREIGN KEY(run_id) REFERENCES test_runs(run_id)
        )
        """
    )

    conn.commit()
    conn.close()


def start_run() -> int:
    """
    Start a new test run by recording the current timestamp in the database.

    This function establishes a connection to the database, inserts a new test run with
    the current timestamp, and commits the transaction. The identifier of the newly
    created test run is then returned.

    :return: The identifier of the newly created test run.
    :rtype: int
    """
    conn = get_connection()
    cur = conn.cursor()
    ts = utcnow_iso()
    cur.execute(
        "INSERT INTO test_runs (started_at) VALUES (?)",
        (ts,),
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id


def finish_run(run_id: int) -> None:
    """
    Marks a test run as finished by updating the `finished_at` timestamp in the database
    for the given run ID.

    :param run_id: Identifier of the test run to be marked as finished
    :type run_id: int
    :return: None
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE test_runs SET finished_at = ? WHERE run_id = ?",
        (utcnow_iso(), run_id),
    )
    conn.commit()
    conn.close()


def record_test_result(
    run_id: int,
    test_name: str,
    status: str,
    duration: float,
    error_message: Optional[str],
) -> None:
    """
    Records the result of a test execution into the database. This method stores information
    about a particular test run, such as its identifier, name, execution status, duration,
    and any potential error messages. The data is inserted into the `test_results` table
    within a connected database instance.

    :param run_id: The unique identifier for the test run.
    :param test_name: The name of the test being executed.
    :param status: The current status of the test (e.g., "passed", "failed").
    :param duration: The total time taken to execute the test, in seconds.
    :param error_message: The error message, if any, associated with the test; otherwise None.

    :return: This method does not return anything.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO test_results (run_id, test_name, status, duration, error_message)
        VALUES (?, ?, ?, ?, ?)
        """,
        (run_id, test_name, status, duration, error_message),
    )
    conn.commit()
    conn.close()


def fetch_last_run_id() -> Optional[int]:
    """
    Fetches the latest `run_id` from the `test_runs` table in the database.

    This function retrieves the `run_id` of the most recently executed test run
    from the `test_runs` table, ordered in descending order. If there are no
    entries in the table, it returns `None`.

    :return: The latest `run_id` if available, otherwise `None`.
    :rtype: Optional[int]
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT run_id FROM test_runs ORDER BY run_id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row["run_id"] if row else None


def fetch_run_summary(run_id: int) -> Dict[str, int]:
    """
    Fetches a summary of a test run by its `run_id`. The summary includes the total
    number of test cases and their respective statuses: passed, failed, and skipped.

    :param run_id: The ID of the test run to summarize.
    :return: A dictionary containing the total number of test cases and their counts
             for each status: passed, failed, and skipped.
    :rtype: Dict[str, int]
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT status, COUNT(*) AS c
        FROM test_results
        WHERE run_id = ?
        GROUP BY status
        """,
        (run_id,),
    )
    data = {row["status"]: row["c"] for row in cur.fetchall()}
    conn.close()

    total = sum(data.values())
    passed = data.get("passed", 0)
    failed = data.get("failed", 0)
    skipped = data.get("skipped", 0)

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
    }


def fetch_slowest_tests(run_id: int, limit: int = 5) -> List[Tuple[str, float]]:
    """
    Fetches the slowest test results for a given test run.

    This function connects to the database, retrieves the test results for the
    specified run ID, and returns the specified number of slowest tests based on
    their duration. The results are sorted in descending order of duration.

    :param run_id: The unique identifier for a test run.
    :param limit: The maximum number of slowest test results to retrieve.
    :return: A list of tuples where each tuple contains the test name and its
        duration, sorted by duration in descending order.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT test_name, duration
        FROM test_results
        WHERE run_id = ?
        ORDER BY duration DESC
        LIMIT ?
        """,
        (run_id, limit),
    )
    rows = [(r["test_name"], r["duration"]) for r in cur.fetchall()]
    conn.close()
    return rows


def fetch_flaky_tests(window: int = 20, min_failures: int = 2) -> List[Tuple[str, int, int]]:
    """
    Fetches a list of flaky tests based on their failure count over the latest test runs.

    This function queries a database to retrieve test statistics for a specified number
    of recent test runs, identifying tests that have failed a minimum number of times.
    It returns a list of test cases that meet or exceed the failure threshold,
    sorted by the number of failures in descending order.

    :param window: The number of recent test runs to consider for analyzing flaky tests.
    :param min_failures: The minimum number of failures required to include a test as flaky.
    :return: A list of tuples representing flaky tests.
        Each tuple contains the test name, the number of failures, and the total number
        of test executions during the queried runs.
    """
    conn = get_connection()
    cur = conn.cursor()

    # get last N run_ids
    cur.execute(
        "SELECT run_id FROM test_runs ORDER BY run_id DESC LIMIT ?",
        (window,),
    )
    run_ids = [row["run_id"] for row in cur.fetchall()]
    if not run_ids:
        conn.close()
        return []

    placeholders = ",".join("?" for _ in run_ids)

    # gather statuses per test_name
    cur.execute(
        f"""
        SELECT test_name,
               SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS fails,
               COUNT(*) AS total
        FROM test_results
        WHERE run_id IN ({placeholders})
        GROUP BY test_name
        HAVING fails >= ?
        ORDER BY fails DESC
        """,
        (*run_ids, min_failures),
    )
    rows = [(r["test_name"], r["fails"], r["total"]) for r in cur.fetchall()]
    conn.close()
    return rows


def fetch_pass_rate_history(limit: int = 10) -> List[Tuple[int, float]]:
    """
    Fetches the historical test pass rates, limited by the specified number of
    results. This function queries the database for test run data, calculating
    the pass rate for each test run based on the number of passed tests over the
    total tests within each run.

    :param limit: The maximum number of test runs to fetch pass rate data for.
                  Defaults to 10.
    :return: A list of tuples, where each tuple contains a run ID and its
             corresponding pass rate percentage.
    :rtype: List[Tuple[int, float]]
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.run_id,
               SUM(CASE WHEN tr.status='passed' THEN 1 ELSE 0 END)*1.0
               / COUNT(*) * 100.0 AS pass_rate
        FROM test_runs r
        JOIN test_results tr ON tr.run_id = r.run_id
        GROUP BY r.run_id
        ORDER BY r.run_id DESC
        LIMIT ?
        """,
        (limit,),
    )
    result = [(row["run_id"], row["pass_rate"]) for row in cur.fetchall()]
    conn.close()
    return result
