import time
import random

def test_always_pass():
    """
    A simple test function that always passes. This function is typically used to
    verify that the test framework is correctly set up and functioning.

    :return: None
    """
    assert True

def test_random_fail():
    """
    Tests the functionality of random selection between two boolean values.

    This function uses the `random.choice` method to select randomly
    between `True` and `False`. The test asserts that the result is
    one of these boolean values.

    :raises AssertionError: If the result of `random.choice` does not match
                            either `True` or `False`.
    :return: None
    """
    assert random.choice([True, False])

def test_slow_one():
    """
    Performs a unit test that deliberately sleeps for a defined duration
    to simulate a slow-running test. The test always passes as it asserts
    a static truth value.

    :return: None
    """
    time.sleep(1.2)
    assert True
