from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from .utils import get_data_dir, utcnow_iso

DB_FILENAME = "results.db"


def _get_db_path() -> Path:
    """Return the full file path to the database."""
    return get_data_dir() / DB_FILENAME


def get_connection() -> sqlite3.Connection:
    """Create and return a SQLite connection."""
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db() -> None:
    """Ensure required tables exist."""
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO test_runs (started_at) VALUES (?)", (utcnow_iso(),))
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id


def finish_run(run_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE test_runs SET finished_at = ? WHERE run_id = ?", (utcnow_iso(), run_id))
    conn.commit()
    conn.close()


def record_test_result(run_id: int, test_name: str, status: str, duration: float, error_message: Optional[str]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO test_results (run_id, test_name, status, duration, error_message)
        VALUES (?, ?, ?, ?, ?)
    """, (run_id, test_name, status, duration, error_message))
    conn.commit()
    conn.close()


def fetch_last_run_id() -> Optional[int]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT run_id FROM test_runs ORDER BY run_id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row["run_id"] if row else None


def fetch_run_summary(run_id: int) -> Dict[str, int]:
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT run_id, started_at, finished_at FROM test_runs ORDER BY run_id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def fetch_tests_for_run(run_id: int) -> List[Dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT test_name, status, duration, error_message FROM test_results WHERE run_id = ?", (run_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]
