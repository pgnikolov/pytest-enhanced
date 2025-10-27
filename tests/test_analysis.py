from pytest_enhanced import storage, analysis


def test_session_stats_empty(tmp_path, monkeypatch):
    """
    Test function for verifying behavior of `get_session_stats` when no session data
    exists in the database. Ensures the function returns None in such scenarios.

    :param tmp_path: A pathlib.Path object representing a temporary directory
                     where the database will be created.
    :param monkeypatch: A pytest fixture used to patch `os.chdir` to change the working
                        directory to the temporary path.
    :return: None
    """
    monkeypatch.chdir(tmp_path)
    storage.ensure_db()
    assert analysis.get_session_stats() is None


def test_session_stats_basic(tmp_path, monkeypatch):
    """
    Executes a basic test case for verifying session statistics functionality. It tests the
    recording of test results into a database, calculation of session summary, and inclusion
    of expected analytical data in the session statistics summary.

    :param tmp_path: Temporary file path fixture for creating isolated file storage for
        the test run.
    :param monkeypatch: Monkeypatch fixture for dynamically modifying or overriding functionality
        during the test execution.
    :return: None
    """
    monkeypatch.chdir(tmp_path)
    storage.ensure_db()

    run_id = storage.start_run()

    storage.record_test_result(run_id, "t1", "passed", 0.5, None)
    storage.record_test_result(run_id, "t2", "failed", 1.2, "boom")
    storage.record_test_result(run_id, "t3", "skipped", 0.0, "skip")
    storage.finish_run(run_id)

    stats = analysis.get_session_stats()
    assert stats is not None
    assert stats["summary"]["total"] == 3
    assert stats["summary"]["failed"] == 1
    assert stats["summary"]["passed"] == 1
    assert stats["summary"]["skipped"] == 1
    assert "slow_tests" in stats
    assert "flaky_tests" in stats
    assert "history" in stats
