from datetime import datetime
from typing import List, Optional

import pyperclip
from rich.console import Console

from .config.config_manager import ConfigManager
from .core.models.project import Project
from .core.models.task import Task
from .formatters.factory import FormatterFactory
from .storage.factory import StorageFactory
from .utils.text import clean_section_header, split_into_sections

console = Console()


class TaskManager:
    """Manages task operations and file handling."""

    def __init__(self):
        """Initialize task manager with config and storage."""
        self.config = ConfigManager()
        self.storage = StorageFactory.create_storage(
            storage_type=self.config.storage_type, base_dir=self.config.storage_base_dir
        )

    def create_daily_file(self, date_obj: Optional[datetime] = None) -> None:
        """Create a new daily task file.

        Args:
            date_obj: Date to create file for, defaults to today
        """
        if date_obj is None:
            date_obj = datetime.now()
        elif isinstance(date_obj, datetime):
            pass
        else:  # It's a date object
            date_obj = datetime.combine(date_obj, datetime.min.time())

        # Get last log to carry forward tasks
        last_log = self._get_last_log(date_obj)
        if last_log:
            content = self._generate_content_from_log(last_log)
        else:
            content = self._generate_empty_content()

        # Save new log
        self.storage.save_daily_log(content, date_obj.date())

    def format_tasks(
        self,
        format_type: str = "slack",
        is_report: bool = False,
        date_obj: Optional[datetime] = None,
        copy_to_clipboard: bool = True,
    ) -> str:
        """Format tasks for output.

        Args:
            format_type: Output format (slack/teams/whatsapp/email)
            is_report: Whether this is an EOD report
            date_obj: Date to format tasks for, defaults to today
            copy_to_clipboard: Whether to copy output to clipboard

        Returns:
            Formatted task string
        """
        if date_obj is None:
            date_obj = datetime.now()

        # Get daily log
        content = self.storage.load_daily_log(date_obj.date())
        if not content:
            return "No tasks found for the specified date."

        # Parse content into projects
        projects = self._parse_content_to_projects(content)

        # Format tasks
        formatter = FormatterFactory.create_formatter(
            format_type, self.config.status_info
        )
        formatted_content = formatter.format_tasks(projects, date_obj.date(), is_report)

        # Copy to clipboard if requested
        if copy_to_clipboard:
            pyperclip.copy(formatted_content)

        return formatted_content

    def _get_last_log(self, date_obj: datetime) -> Optional[str]:
        """Get the last log before the given date.

        Args:
            date_obj: Date to look before

        Returns:
            Last log content if found, None otherwise
        """
        last_date = self.storage.find_last_log_date(date_obj.date())
        if last_date:
            return self.storage.load_daily_log(last_date)
        return None

    def _parse_content_to_projects(self, content: str) -> List[Project]:
        """Parse markdown content into projects.

        Args:
            content: Markdown content to parse

        Returns:
            List of Project objects
        """
        projects = []
        sections = split_into_sections(content)

        for header, tasks in sections.items():
            if not tasks:
                continue

            # Extract emoji and name
            emoji, name = clean_section_header(header)
            project = Project(name=name, emoji=emoji)

            # Parse tasks
            for task_line in tasks:
                if task_line.strip():
                    task = Task.from_markdown(task_line, name)
                    project.add_task(task)

            projects.append(project)

        return projects

    def _generate_content_from_projects(self, projects: List[Project]) -> str:
        """Generate markdown content from projects.

        Args:
            projects: List of projects to format

        Returns:
            Markdown formatted string
        """
        lines = []
        for project in projects:
            if not project.tasks:
                continue

            # Add project header
            lines.append(f"{project.emoji} {project.name}")
            lines.append("")  # Empty line after header

            # Add tasks
            for task in project.tasks:
                lines.append(task.to_markdown())

            lines.append("")  # Empty line after tasks

        return "\n".join(lines).strip()

    def _generate_empty_content(self) -> str:
        """Generate empty content with default sections.

        Returns:
            Markdown formatted string with empty sections
        """
        lines = []
        for section in self.config.default_sections:
            lines.extend(
                [
                    f"{section['emoji']} {section['name']}",
                    "",  # Empty line after header
                    "",  # Empty line after section
                ]
            )
        return "\n".join(lines).strip()

    def _generate_content_from_log(self, content: str) -> str:
        """Generate new content from previous log.

        Args:
            content: Previous log content

        Returns:
            New markdown formatted string
        """
        projects = self._parse_content_to_projects(content)
        new_projects = []

        for project in projects:
            new_project = Project(name=project.name, emoji=project.emoji)

            # Carry forward incomplete tasks
            carried_tasks = project.carry_forward_tasks(self.config.status_info)
            for task in carried_tasks:
                new_project.add_task(task)

            if new_project.tasks:
                new_projects.append(new_project)

        return self._generate_content_from_projects(new_projects)
