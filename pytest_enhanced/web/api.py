from fastapi import FastAPI
from fastapi.responses import JSONResponse
from ..storage import fetch_all_runs, fetch_tests_for_run, fetch_flaky_tests, fetch_slowest_tests

app = FastAPI(title="Pytest Enhanced Dashboard", version="0.1")


@app.get("/")
def index():
    """
    Handles the root endpoint of the application.

    This endpoint provides a simple response to confirm that the API
    is up and running.

    :return: A JSON response with a message indicating the API is operational
    :rtype: dict
    """
    return {"message": "Pytest Enhanced API is running 🚀"}


@app.get("/runs")
def get_runs(limit: int = 20):
    """
    Fetches and returns a list of available runs. The number of runs returned
    can be controlled using the `limit` parameter.

    :param limit: Specifies the maximum number of runs to fetch.
    :type limit: int
    :return: A dictionary containing a list of runs.
    :rtype: dict
    """
    runs = fetch_all_runs(limit=limit)
    return {"runs": runs}


@app.get("/runs/{run_id}")
def get_run_details(run_id: int):
    """
    Fetch the details of a test run by its unique identifier.

    This endpoint retrieves information about a specific test run, including
    its associated tests. The response includes the run ID and a list of
    tests related to the specified run.

    :param run_id: Identifier for the test run to retrieve details for.
    :type run_id: int
    :return: A dictionary containing the test run ID and the associated tests.
    :rtype: dict
    """
    tests = fetch_tests_for_run(run_id)
    return {"run_id": run_id, "tests": tests}


@app.get("/flaky")
def get_flaky():
    """
    Fetches a list of flaky tests based on specific criteria.

    The function retrieves a list of flaky tests observed within a defined
    time window and meeting a minimum failure threshold. Flaky tests are
    those that fail inconsistently and thus need to be tracked for further
    analysis or resolution.

    :raises ValueError: If any of the parameters in the fetching function
                        are invalid or if the fetching process fails.
    :raises RuntimeError: If there is an unexpected issue during data
                          retrieval or processing.

    :return: A dictionary containing the list of flaky tests that satisfy
             the specified criteria.
    :rtype: dict
    """
    data = fetch_flaky_tests(window=30, min_failures=2)
    return {"flaky": data}


@app.get("/slow/{run_id}")
def get_slowest(run_id: int):
    """
    Fetches the slowest tests for a given run.

    Retrieves and returns the details of the slowest tests associated
    with a specific test run ID. The number of tests returned is limited
    to the top 10 slowest.

    :param run_id: The unique identifier of the test run.
    :type run_id: int
    :return: A dictionary containing the run ID and a list of the slowest tests.
    :rtype: dict
    """
    data = fetch_slowest_tests(run_id, limit=10)
    return {"run_id": run_id, "slowest": data}
