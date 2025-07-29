"""Email formatter for TaskDaily."""

from datetime import date
from typing import List

from ..core.interfaces.formatter import FormatterInterface
from ..core.models.project import Project


class EmailFormatter(FormatterInterface):
    """Formatter for HTML email messages."""

    def __init__(self, status_info: dict):
        """Initialize formatter with status info.

        Args:
            status_info: Dictionary mapping status keys to info
        """
        self.status_info = status_info

    def format_tasks(
        self, projects: List[Project], log_date: date, is_report: bool = False
    ) -> str:
        """Format tasks for email output.

        Args:
            projects: List of projects to format
            log_date: Date of the log
            is_report: Whether this is an EOD report

        Returns:
            Formatted HTML email message
        """
        # Format header
        header = self._format_header(log_date.strftime("%Y-%m-%d"), is_report)

        # Format each project
        sections = [header]
        for project in projects:
            if not project.tasks:
                continue

            # Format project header
            project_header = f"<h3>{project.emoji} {project.name}</h3>"

            # Format tasks
            task_lines = []
            for task in project.tasks:
                # Skip planned tasks in reports
                if (
                    is_report
                    and task.status in self.status_info
                    and not self.status_info[task.status]["show_in_report"]
                ):
                    continue

                # Format task line
                checkbox = "☑" if task.is_completed else "☐"
                status_emoji = (
                    self.status_info[task.status]["emoji"]
                    if task.status in self.status_info
                    else ""
                )
                task_line = f"<li>{checkbox} {task.content} {status_emoji}</li>"
                task_lines.append(task_line)

            if task_lines:
                sections.append(
                    f"{project_header}\n<ul>\n" + "\n".join(task_lines) + "\n</ul>"
                )

        # Wrap in HTML
        content = "\n\n".join(sections)
        return f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
{content}
</body>
</html>
"""

    def _format_header(self, date_str: str, is_report: bool) -> str:
        """Format message header for email.

        Args:
            date_str: Date string
            is_report: Whether this is an EOD report

        Returns:
            Formatted header string
        """
        header_text = "EOD REPORT" if is_report else "DAILY PLAN"
        return f"<h2>{header_text} - {date_str}</h2>"
