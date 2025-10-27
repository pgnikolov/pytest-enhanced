from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
from typing import Optional


def get_data_dir() -> Path:
    """
    Gets the directory path used for storing pytest enhanced data.

    This function creates a subdirectory named `.pytest_enhanced` in the current
    working directory if it does not already exist. The created or existing
    directory path is then returned.

    :return: A ``Path`` object representing the `.pytest_enhanced` directory.
    :rtype: Path
    """
    p = Path(os.getcwd()) / ".pytest_enhanced"
    p.mkdir(exist_ok=True)
    return p


def utcnow_iso() -> str:
    """
    Gets the current UTC time as an ISO 8601 formatted string.

    This function retrieves the current UTC time with the microseconds
    removed and represents it as a string formatted in ISO 8601.

    :return: The current UTC time in ISO 8601 format.
    :rtype: str
    """
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def format_duration(seconds: float) -> str:
    """
    Formats a given duration in seconds to a string representation with a precision of two
    decimal places.

    :param seconds: Duration in seconds to format.
    :type seconds: float
    :return: A formatted string representing the duration with two decimal places followed
        by "s" for seconds.
    :rtype: str
    """
    return f"{seconds:.2f}s"


def safe_str(value: Optional[str]) -> str:
    """
    Returns a safe string representation of the input value. This function ensures
    that a `None` value is converted to an empty string, avoiding potential errors
    when `None` is encountered in contexts that require a string.

    :param value: The input value, which may either be a string or `None`.
    :type value: Optional[str]
    :return: The original string if not `None`, otherwise an empty string.
    :rtype: str
    """
    return value if value is not None else ""
