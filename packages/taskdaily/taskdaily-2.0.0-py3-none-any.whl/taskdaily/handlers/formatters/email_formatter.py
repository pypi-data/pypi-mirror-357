from datetime import datetime
from typing import Dict, List

from .base_formatter import BaseFormatter


class EmailFormatter(BaseFormatter):
    """Formats tasks for email messages."""

    def format_message(
        self, tasks: Dict[str, List[str]], date: datetime, is_report: bool = False
    ) -> str:
        """Format tasks into an email message."""
        date_str = date.strftime("%Y-%m-%d")
        sections = []

        # Add header
        sections.append(
            f"<h2>{'EOD REPORT' if is_report else 'DAILY PLAN'} - {date_str}</h2>"
        )
        sections.append("<hr>")

        # Process each project
        for project_name, project_tasks in tasks.items():
            if not project_tasks:
                continue

            filtered_tasks = self._filter_tasks(project_tasks, is_report)

            if filtered_tasks:
                sections.append(f"<h3>{project_name}</h3>")
                sections.append("<ul>")
                for task in filtered_tasks:
                    task_text = self._convert_to_email_format(task)
                    sections.append(f"<li>{task_text}</li>")
                sections.append("</ul>")
                sections.append("<hr>")

        return "\n".join(sections)

    def _convert_to_email_format(self, task: str) -> str:
        """Convert markdown task format to HTML format."""
        # Convert checkboxes to HTML-friendly format
        task = task.replace("- [ ]", "☐").replace("- [x]", "☑")
        return task
