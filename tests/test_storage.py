import os
import sqlite3
from pathlib import Path

from pytest_enhanced import storage


def test_db_creation_tmpdir(tmp_path, monkeypatch):
    """
    Test the creation of the database in a temporary directory and validate its
    structure. The function ensures that a database file is created in the
    temporary path and verifies the existence of required tables in the database.

    :param tmp_path: Temporary path provided for storing files during the test.
        This is a fixture provided by pytest for generating isolated directories
        for testing.
    :param monkeypatch: A fixture provided by pytest to safely modify and
        restore attributes and environment behaviors during the test.
    :return: None
    """
    # redirect data dir to temp
    monkeypatch.chdir(tmp_path)

    storage.ensure_db()
    db_path = tmp_path / ".pytest_enhanced" / "results.db"
    assert db_path.exists()

    # sanity check tables
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert "test_runs" in tables
    assert "test_results" in tables
    conn.close()
