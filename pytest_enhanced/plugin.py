from __future__ import annotations
import pytest
from typing import Optional
from .storage import ensure_db, start_run, finish_run, record_test_result

# Глобален идентификатор на текущия run
CURRENT_RUN_ID: Optional[int] = None


def pytest_addoption(parser):
    """
    Add a custom command-line option to pytest for enabling enhanced analytics logging.

    The function integrates a new option into pytest's CLI interface, allowing users
    to specify whether they want to enable the enhanced analytics logging functionality.
    It modifies pytest's default behavior by registering the "--enhanced" flag.

    :param parser: The configuration parser used by pytest to define and process
                   command-line options.
    :type parser: pytest.Parser
    :return: None
    """
    group = parser.getgroup("pytest-enhanced")
    group.addoption(
        "--enhanced",
        action="store_true",
        default=False,
        help="Enable pytest-enhanced analytics logging.",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """
    This hook implementation is executed at the beginning of a test session. It initializes
    a global run identifier for the current session. If the `--enhanced` CLI option is
    enabled, it ensures the database setup is complete and starts a new test run, setting
    its identifier globally. If the option is not enabled, no test run ID is set.

    :param session: An instance of a pytest Session object representing the current test
                    session.
    """
    global CURRENT_RUN_ID
    config = session.config
    if config.getoption("--enhanced"):
        ensure_db()
        CURRENT_RUN_ID = start_run()
    else:
        CURRENT_RUN_ID = None


@pytest.hookimpl()
def pytest_runtest_logreport(report: pytest.TestReport):
    """
    Process a test log report and record the result, including status, duration,
    and optional error message for a specific test. This hook is intended to
    handle and process the log report generated during the `pytest` test execution.

    The function evaluates the status of the test (e.g., passed, failed, skipped),
    extracts necessary information, and records it using the `record_test_result`
    function if a test run ID is active. It ignores setup and teardown steps,
    processing only the `call` phase of the test.

    :param report: The test report object from `pytest`, which contains information
        about the executed test, including the node identifier, duration, and
        potential errors.
    :return: None
    """
    global CURRENT_RUN_ID
    if CURRENT_RUN_ID is None:
        return
    if report.when != "call":
        return

    test_name = report.nodeid
    duration = getattr(report, "duration", 0.0)

    if report.failed:
        status = "failed"
        err = str(report.longrepr)[:500] if report.longrepr else "Unknown failure"
    elif report.skipped:
        status = "skipped"
        err = str(report.longrepr)[:500] if report.longrepr else None
    else:
        status = "passed"
        err = None

    record_test_result(
        run_id=CURRENT_RUN_ID,
        test_name=test_name,
        status=status,
        duration=duration,
        error_message=err,
    )


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """
    This function is executed at the very end of a pytest session. It ensures cleanup tasks
    are performed by concluding and resetting any currently active test run.

    :param session: Provides information about the pytest session object.
    :type session: _pytest.main.Session
    :param exitstatus: An integer representing the exit status/result of the pytest session.
    :type exitstatus: int
    :return: None
    """
    global CURRENT_RUN_ID
    if CURRENT_RUN_ID is not None:
        finish_run(CURRENT_RUN_ID)
        CURRENT_RUN_ID = None
