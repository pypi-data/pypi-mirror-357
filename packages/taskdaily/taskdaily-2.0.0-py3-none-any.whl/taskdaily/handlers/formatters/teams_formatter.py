from datetime import datetime
from typing import Dict, List

from .base_formatter import BaseFormatter


class TeamsFormatter(BaseFormatter):
    """Formats tasks for Microsoft Teams messages."""

    def format_message(
        self, tasks: Dict[str, List[str]], date: datetime, is_report: bool = False
    ) -> str:
        """Format tasks into a Teams message."""
        date_str = date.strftime("%Y-%m-%d")
        sections = []

        # Add header
        sections.append(
            f"## {'EOD REPORT' if is_report else 'DAILY PLAN'} - {date_str}"
        )
        sections.append("")  # Empty line after header

        # Process each project
        for project_name, project_tasks in tasks.items():
            if not project_tasks:
                continue

            filtered_tasks = self._filter_tasks(project_tasks, is_report)

            if filtered_tasks:
                sections.append(f"### {project_name}")
                for task in filtered_tasks:
                    task_text = self._convert_to_teams_format(task)
                    sections.append(f"* {task_text}")
                sections.append("")  # Empty line between projects

        return "\n".join(sections)

    def _convert_to_teams_format(self, task: str) -> str:
        """Convert markdown task format to Teams format."""
        # Convert checkboxes to Teams-friendly format
        task = task.replace("- [ ]", "☐").replace("- [x]", "☑")
        return task
