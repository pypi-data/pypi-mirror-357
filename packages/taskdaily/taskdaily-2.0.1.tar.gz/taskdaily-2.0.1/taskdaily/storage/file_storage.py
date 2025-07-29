import os
from datetime import date
from pathlib import Path
from typing import Optional

from ..core.interfaces.storage import StorageInterface
from ..utils.date import get_date_path


class FileStorage(StorageInterface):
    """File-based storage backend."""

    def __init__(self, base_dir: Optional[str] = None):
        """Initialize file storage.

        Args:
            base_dir: Base directory for storing files
        """
        self.base_dir = (
            Path(base_dir) if base_dir else Path.home() / ".taskdaily" / "tasks"
        )
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_daily_log(self, content: str, log_date: date) -> None:
        """Save daily log content for a specific date.

        Args:
            content: Content to save
            log_date: Date to save the content for
        """
        file_path = self._get_file_path(log_date)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    def load_daily_log(self, log_date: date) -> Optional[str]:
        """Load daily log content for a specific date.

        Args:
            log_date: Date to load content for

        Returns:
            Content string if log exists, None otherwise
        """
        file_path = self._get_file_path(log_date)
        if file_path.exists():
            return file_path.read_text()
        return None

    def find_last_log_date(self, before_date: date) -> Optional[date]:
        """Find the most recent log date before the given date.

        Args:
            before_date: Date to search before

        Returns:
            Most recent log date if found, None otherwise
        """
        # Get all log files
        log_files = []
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith(".md"):
                    log_files.append(Path(root) / file)

        # Find the most recent date before the given date
        last_date = None
        for file_path in log_files:
            try:
                file_date = self._parse_date_from_path(file_path)
                if (
                    file_date
                    and file_date < before_date
                    and (not last_date or file_date > last_date)
                ):
                    last_date = file_date
            except ValueError:
                continue

        return last_date

    def _get_file_path(self, log_date: date) -> Path:
        """Get file path for a specific date.

        Args:
            log_date: Date to get path for

        Returns:
            Path object for the log file
        """
        year = f"{log_date.year}"
        month = f"{log_date.month:02d}"
        day = f"{log_date.day:02d}"
        filename = f"{year}-{month}-{day}.md"
        return self.base_dir / year / month / day / filename

    def _parse_date_from_path(self, file_path: Path) -> Optional[date]:
        """Parse date from file path.

        Args:
            file_path: Path to parse date from

        Returns:
            Date object if path is valid, None otherwise
        """
        try:
            # Extract date from filename (YYYY-MM-DD.md)
            filename = file_path.name
            if filename.endswith(".md"):
                date_str = filename[:-3]  # Remove .md
                year, month, day = map(int, date_str.split("-"))
                return date(year, month, day)
        except (ValueError, TypeError):
            pass
        return None
