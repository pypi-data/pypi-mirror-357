from datetime import datetime, tzinfo
from pathlib import Path


def format_ctime(path: Path, time_format: str, tz: tzinfo) -> str:
    """
    Formats the creation time of a file as a string.

    Args:
        path: file path
        time_format: time format string
        tz: timezone to use for formatting
    Returns:
        str: formatted creation time
    """
    ctime = path.stat().st_ctime
    date = datetime.fromtimestamp(ctime, tz)
    return date.strftime(time_format)