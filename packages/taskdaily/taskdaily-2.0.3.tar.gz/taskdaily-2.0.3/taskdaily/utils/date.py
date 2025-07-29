import os
from datetime import datetime, date
from typing import Tuple, Optional


def get_date_parts(date_obj: datetime) -> Tuple[str, str, str]:
    """Extract year, month, and day from datetime object."""
    return (date_obj.strftime("%Y"), date_obj.strftime("%m"), date_obj.strftime("%d"))


def parse_date(date_str: Optional[str]) -> date:
    """Parse date string into date object.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        Date object

    Raises:
        ValueError: If date string is invalid
    """
    if not date_str:
        return datetime.now().date()

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")


def get_file_path(date: datetime) -> str:
    """Get the file path for a given date."""
    year = str(date.year)
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"

    return os.path.join(year, month, day, f"{year}-{month}-{day}.md")


def get_date_path(date_obj: date) -> str:
    """Get path components for a date.

    Args:
        date_obj: Date object

    Returns:
        Path string in YYYY/MM/DD format
    """
    return f"{date_obj.year}/{date_obj.month:02d}/{date_obj.day:02d}"
