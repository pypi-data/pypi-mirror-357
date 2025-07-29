"""Slack formatter for TaskDaily."""

from datetime import date
from typing import List

from ..core.interfaces.formatter import FormatterInterface
from ..core.models.project import Project


class SlackFormatter(FormatterInterface):
    """Formatter for Slack messages."""

    def __init__(self, status_info: dict):
        """Initialize formatter with status info.

        Args:
            status_info: Dictionary mapping status keys to info
        """
        self.status_info = status_info
        # Create reverse lookup for status by emoji
        self.status_by_emoji = {
            info["emoji"]: status_key for status_key, info in status_info.items()
        }

    def format_tasks(
        self, projects: List[Project], log_date: date, is_report: bool = False
    ) -> str:
        """Format tasks for Slack output.

        Args:
            projects: List of projects to format
            log_date: Date of the log
            is_report: Whether this is an EOD report

        Returns:
            Formatted Slack message
        """
        # Format header
        header = self._format_header(log_date.strftime("%Y-%m-%d"), is_report)

        # Format each project
        sections = [header]
        for project in projects:
            if not project.tasks:
                continue

            # Format project header
            project_header = f"{project.emoji} {project.name}"
            sections.append(project_header)

            # Format tasks
            task_lines = []
            for task in project.tasks:
                # Get status key from emoji
                status_key = self.status_by_emoji.get(task.status_emoji)

                # Skip planned tasks in reports
                if (
                    is_report
                    and status_key
                    and not self.status_info[status_key]["show_in_report"]
                ):
                    continue

                # Format task line
                checkbox = "●" if task.is_completed else "○"
                task_line = f"  {checkbox} {task.content} {task.status_emoji}".strip()
                task_lines.append(task_line)

            if task_lines:
                sections.extend(task_lines)
                sections.append("-" * 45)

        return "\n".join(sections)

    def _format_header(self, date_str: str, is_report: bool) -> str:
        """Format message header for Slack.

        Args:
            date_str: Date string
            is_report: Whether this is an EOD report

        Returns:
            Formatted header string
        """
        header_text = "EOD REPORT" if is_report else "DAILY PLAN"
        return f"{'=' * 30}\n{header_text} - {date_str}\n{'=' * 30}"
