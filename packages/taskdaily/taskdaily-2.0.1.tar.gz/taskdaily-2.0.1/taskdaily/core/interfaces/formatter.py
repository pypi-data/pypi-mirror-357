"""Interface for output formatters."""

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from ..models.project import Project


class FormatterInterface(ABC):
    """Interface for output formatters."""

    @abstractmethod
    def format_tasks(
        self, projects: List[Project], log_date: date, is_report: bool = False
    ) -> str:
        """Format tasks for output.

        Args:
            projects: List of projects to format
            log_date: Date of the log
            is_report: Whether this is an EOD report

        Returns:
            Formatted string ready for output
        """
        pass
