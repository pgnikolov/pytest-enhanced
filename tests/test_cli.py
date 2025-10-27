from typer.testing import CliRunner

from pytest_enhanced import storage
from pytest_enhanced.cli import app


def test_cli_report_no_data(tmp_path, monkeypatch):
    """
    Test the "report" command of the CLI when no data exists in the database.

    This test ensures that the "report" command correctly handles cases
    where no test run data is available in the database. It verifies that
    the command exits with a non-zero exit code and outputs the appropriate
    message informing the user that no test runs were found.

    :param tmp_path: Temporary file path provided by the pytest fixture.
    :type tmp_path: pathlib.Path
    :param monkeypatch: Fixture to patch and modify functionalities or
        environment for testing purposes.
    :return: None
    """
    monkeypatch.chdir(tmp_path)
    storage.ensure_db()

    runner = CliRunner()
    result = runner.invoke(app, ["report"])
    assert result.exit_code != 0
    assert "No test runs found" in result.stdout


def test_cli_report_with_data(tmp_path, monkeypatch):
    """
    Function to test the CLI report generation with recorded data in the storage system.
    This function simulates a test scenario where test results are persisted,
    retrieved, and reported using the CLI application.

    :param tmp_path: Temporary directory path provided as a fixture.
    :type tmp_path: pathlib.Path
    :param monkeypatch: pytest fixture used for safely patching and modifying behavior during the test.
    :type monkeypatch: pytest.MonkeyPatch
    :return: None
    """
    monkeypatch.chdir(tmp_path)
    storage.ensure_db()

    run_id = storage.start_run()
    storage.record_test_result(run_id, "t1", "passed", 0.2, None)
    storage.record_test_result(run_id, "t2", "failed", 1.0, "bad")
    storage.finish_run(run_id)

    runner = CliRunner()
    result = runner.invoke(app, ["report"])

    # Should succeed
    assert result.exit_code == 0
    assert "Pytest Enhanced Report" in result.stdout
    assert "Passed:" in result.stdout
    assert "Failed:" in result.stdout
