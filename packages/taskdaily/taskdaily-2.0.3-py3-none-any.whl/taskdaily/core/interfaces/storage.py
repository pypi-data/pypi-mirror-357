from abc import ABC, abstractmethod
from datetime import date
from typing import Optional


class StorageInterface(ABC):
    """Interface for storage backends."""

    @abstractmethod
    def save_daily_log(self, content: str, log_date: date) -> None:
        """Save daily log content for a specific date.

        Args:
            content: Content to save
            log_date: Date to save the content for
        """
        pass

    @abstractmethod
    def load_daily_log(self, log_date: date) -> Optional[str]:
        """Load daily log content for a specific date.

        Args:
            log_date: Date to load content for

        Returns:
            Content string if log exists, None otherwise
        """
        pass

    @abstractmethod
    def find_last_log_date(self, before_date: date) -> Optional[date]:
        """Find the most recent log date before the given date.

        Args:
            before_date: Date to search before

        Returns:
            Most recent log date if found, None otherwise
        """
        pass
