"""
Database layer for pytest-enhanced.

Handles test run storage, retrieval, and statistical queries using SQLite.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from .utils import get_data_dir, utcnow_iso

DB_FILENAME = "results.db"


def _get_db_path() -> Path:
    """
    Retrieves the path of the database file by combining the application data directory
    path with the predefined database filename.

    :return: Full path of the database file.
    :rtype: Path
    """
    return get_data_dir() / DB_FILENAME


def get_connection() -> sqlite3.Connection:
    """
    Creates and returns a connection to the SQLite database.

    The function establishes a connection to the database defined by the path
    retrieved from the `_get_db_path` function. It also sets the row factory
    for the connection to return rows as dictionary-like objects for easier
    access to column data via keys.

    :return: SQLite connection object configured with row_factory set to
             sqlite3.Row
    :rtype: sqlite3.Connection
    """
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db() -> None:
    """
    Ensures that the necessary database tables exist. If the tables `test_runs` and `test_results`
    do not already exist, this function will create them. The `test_runs` table tracks individual
    test runs with unique identifiers, start times, and optional finish times. The `test_results`
    table records individual test results, linking them to the related test run and storing
    information such as test name, status, duration, and optional error messages.

    :param: None
    :return: None
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS test_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            finished_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            test_name TEXT NOT NULL,
            status TEXT NOT NULL,
            duration REAL NOT NULL,
            error_message TEXT,
            FOREIGN KEY(run_id) REFERENCES test_runs(run_id)
        )
    """)

    conn.commit()
    conn.close()


def start_run() -> int:
    """
    Start a new test run and record its start time in the database.

    This function inserts a new entry into the `test_runs` table with the
    current UTC timestamp as the start time. It returns the ID of the newly
    created test run. The database connection is established, used for the
    transaction, and then properly closed.

    :return: The unique identifier of the newly created test run.
    :rtype: int
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO test_runs (started_at) VALUES (?)", (utcnow_iso(),))
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id


def finish_run(run_id: int) -> None:
    """
    Marks a test run as finished by updating the `finished_at` timestamp for the specified
    run ID in the database. This function interacts with the database to record the
    completion time using the current UTC timestamp in ISO format.

    :param run_id: The ID of the test run to mark as finished.
    :type run_id: int
    :return: None
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE test_runs SET finished_at = ? WHERE run_id = ?", (utcnow_iso(), run_id))
    conn.commit()
    conn.close()


def record_test_result(run_id: int, test_name: str, status: str, duration: float, error_message: Optional[str]) -> None:
    """
    Records the result of a test execution into the `test_results` database table. The
    function connects to the database, inserts a new entry with test run details, commits
    the changes, and then closes the connection.

    This is used for tracking results of individual test executions, allowing for later
    analysis or reporting of test outcomes. It supports logging information, including the
    test's run identifier, its name, execution status, duration, and an optional error
    message if applicable.

    :param run_id: Unique identifier of the test run.
    :param test_name: Name of the executed test.
    :param status: Execution result of the test (e.g., "passed", "failed").
    :param duration: Time taken for execution in seconds.
    :param error_message: Optional error message when the test fails.
    :return: None
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO test_results (run_id, test_name, status, duration, error_message)
        VALUES (?, ?, ?, ?, ?)
    """, (run_id, test_name, status, duration, error_message))
    conn.commit()
    conn.close()


def fetch_last_run_id() -> Optional[int]:
    """
    Fetches the last `run_id` from the `test_runs` table in the database.

    This function connects to the database, retrieves the most recent `run_id`
    from the `test_runs` table, and returns it. If no rows are found in the
    table, the function returns `None`.

    :return: The most recently available `run_id` from the `test_runs` table
             or `None` if the table is empty
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
    Fetches the summary of test results for the given run ID from the database.

    The function retrieves test results for a specific run ID, summarizes them
    by their status, and returns a dictionary containing the total count of results
    as well as the counts for passed, failed, and skipped tests.

    :param run_id: The ID of the test run whose results need to be summarized.
    :type run_id: int
    :return: A dictionary containing the summarized counts of test results:
             - total: Total number of test results.
             - passed: Number of passed tests.
             - failed: Number of failed tests.
             - skipped: Number of skipped tests.
    :rtype: Dict[str, int]
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT status, COUNT(*) AS c FROM test_results
        WHERE run_id = ? GROUP BY status
    """, (run_id,))
    data = {row["status"]: row["c"] for row in cur.fetchall()}
    conn.close()
    return {
        "total": sum(data.values()),
        "passed": data.get("passed", 0),
        "failed": data.get("failed", 0),
        "skipped": data.get("skipped", 0),
    }


def fetch_slowest_tests(run_id: int, limit: int = 5) -> List[Tuple[str, float]]:
    """
    Fetch the slowest running tests for a specific test run.

    This function retrieves a list of test names and their execution
    durations in a specified test run, ordered by their duration in
    descending order. The number of tests retrieved can be controlled
    by the `limit` parameter.

    :param run_id: The unique identifier for the test run.
    :param limit: The maximum number of test results to retrieve
        (default is 5).
    :return: A list of tuples, where each tuple contains the name of
        the test and its execution duration.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT test_name, duration
        FROM test_results
        WHERE run_id = ?
        ORDER BY duration DESC
        LIMIT ?
    """, (run_id, limit))
    rows = [(r["test_name"], r["duration"]) for r in cur.fetchall()]
    conn.close()
    return rows


def fetch_flaky_tests(window: int = 20, min_failures: int = 2) -> List[Tuple[str, int, int]]:
    """
    Fetches flaky test results based on a specified number of recent test runs and a minimum number
    of failures.

    The function queries a database to identify tests that have failed in a defined number of recent
    test run IDs and returns a list of test names, their respective failure counts, and total test run
    counts. Tests are filtered to include only those with failure counts greater than or equal to
    `min_failures`, sorted in descending order of failures.

    :param window: The number of most recent test runs to include in the computation.
    :param min_failures: The minimum number of failures a test must have to be included in the result.
    :return: A list of tuples, where each tuple contains the test name, failure count, and total
      number of test runs for each flaky test.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT run_id FROM test_runs ORDER BY run_id DESC LIMIT ?", (window,))
    run_ids = [r["run_id"] for r in cur.fetchall()]
    if not run_ids:
        conn.close()
        return []
    placeholders = ",".join("?" for _ in run_ids)
    cur.execute(f"""
        SELECT test_name,
               SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS fails,
               COUNT(*) AS total
        FROM test_results
        WHERE run_id IN ({placeholders})
        GROUP BY test_name
        HAVING fails >= ?
        ORDER BY fails DESC
    """, (*run_ids, min_failures))
    rows = [(r["test_name"], r["fails"], r["total"]) for r in cur.fetchall()]
    conn.close()
    return rows


def fetch_pass_rate_history(limit: int = 10) -> List[Tuple[int, float]]:
    """
    Fetches the pass rate history of test runs.

    This function retrieves the pass rates for a specified number of recent test
    runs. The pass rate is calculated as the percentage of tests that have passed
    in each test run. The test runs are returned in descending order of their IDs.

    :param limit: The maximum number of test runs to retrieve. Defaults to 10.
    :type limit: int
    :return: A list of tuples, each containing the test run ID and its pass rate
             (as a percentage). The list is ordered from the most recent run to
             the least recent.
    :rtype: List[Tuple[int, float]]
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.run_id,
               SUM(CASE WHEN tr.status='passed' THEN 1 ELSE 0 END)*1.0 / COUNT(*) * 100.0 AS pass_rate
        FROM test_runs r
        JOIN test_results tr ON tr.run_id = r.run_id
        GROUP BY r.run_id
        ORDER BY r.run_id DESC
        LIMIT ?
    """, (limit,))
    result = [(r["run_id"], r["pass_rate"]) for r in cur.fetchall()]
    conn.close()
    return result


def fetch_all_runs(limit: int = 50) -> List[Dict]:
    """
    Fetches a limited number of test run records from the database in descending order
    based on the run ID. Each record includes the run ID, start time, and finish time.
    This method establishes a connection to the database, executes the query, and fetches
    the results before closing the connection.

    :param limit: The maximum number of records to fetch. Defaults to 50.
    :type limit: int
    :return: A list of dictionaries, each representing a test run record with the attributes
        'run_id', 'started_at', and 'finished_at'.
    :rtype: List[Dict]
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT run_id, started_at, finished_at FROM test_runs ORDER BY run_id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def fetch_tests_for_run(run_id: int) -> List[Dict]:
    """
    Fetches a list of test details for a specific test run ID.

    This function connects to a database, executes a query to retrieve test
    results associated with the provided run ID, and returns them as a list
    of dictionaries. The returned dictionaries include details about the
    test name, status, duration, and error message (if any).

    :param run_id: The unique identifier for the test run.
    :type run_id: int
    :return: A list of dictionaries containing test details for the given run ID.
    :rtype: List[Dict]
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT test_name, status, duration, error_message FROM test_results WHERE run_id = ?", (run_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]
