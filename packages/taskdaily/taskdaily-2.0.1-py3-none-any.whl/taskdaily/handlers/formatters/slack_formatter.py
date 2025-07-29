from datetime import datetime
from typing import Any, Dict, List

from .base_formatter import BaseFormatter


class BaseFormatter:
    """Base class for message formatters."""

    def __init__(self, status_info: Dict[str, Dict[str, str]]):
        self.status_info = status_info
        self._init_emoji_map()

    def format_message(
        self, tasks: Dict[str, List[str]], date: datetime, is_report: bool = False
    ) -> str:
        """Format tasks into a message."""
        raise NotImplementedError("Subclasses must implement format_message")

    def _init_emoji_map(self) -> None:
        """Initialize emoji mapping."""
        self._emoji_map = {
            "📝": "memo",
            "⚡": "zap",
            "🚧": "construction",
            "📅": "calendar",
            "➡️": "arrow_right",
            "✅": "white_check_mark",
            "🚫": "no_entry",
            "🏠": "house",
            "💼": "briefcase",
            "📚": "books",
            # Add more mappings as needed
        }


class SlackFormatter(BaseFormatter):
    """Formats tasks for Slack messages."""

    def format_message(
        self, tasks: Dict[str, List[str]], date: datetime, is_report: bool = False
    ) -> str:
        """Format tasks into a Slack message."""
        date_str = date.strftime("%Y-%m-%d")
        sections = []

        # Add header with divider
        header = f"{'=' * 30}\n"
        header += f"{'EOD REPORT' if is_report else 'DAILY PLAN'} - {date_str}\n"
        header += f"{'=' * 30}"
        sections.append(header)

        # Process each project
        for project_name, project_tasks in tasks.items():
            if not project_tasks:
                continue

            filtered_tasks = self._filter_tasks(project_tasks, is_report)

            if filtered_tasks:
                # Add project header
                sections.append(f"\n{project_name}")

                # Add tasks with proper indentation
                for task in filtered_tasks:
                    task_text = self._convert_to_slack_format(task)
                    sections.append(f"  {task_text}")

                # Add divider after each project
                sections.append(f"{'-' * 45}")

        return "\n".join(sections)

    def _convert_to_slack_format(self, task: str) -> str:
        """Convert markdown task format to Slack format."""
        # Remove markdown checkbox and add better bullet points
        task = task.replace("- [ ]", "○").replace("- [x]", "●")

        # Convert status emojis
        for status in self.status_info.values():
            emoji = status["emoji"]
            if emoji in task:
                task = task.replace(emoji, f":{self._get_slack_emoji_name(emoji)}:")

        return task

    def _get_slack_emoji_name(self, emoji: str) -> str:
        """Convert Unicode emoji to Slack emoji name."""
        return self._emoji_map.get(
            emoji, "question"
        )  # Default to :question: if not found


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

        # Get planned emoji from config
        planned_emoji = next(
            (
                info["emoji"]
                for info in self.status_info.values()
                if info.get("name", "").lower() == "planned"
            ),
            "📝",
        )

        # Process each project
        for project_name, project_tasks in tasks.items():
            if not project_tasks:
                continue

            filtered_tasks = []
            for task in project_tasks:
                if task.strip().endswith(f"New task {planned_emoji}"):
                    continue
                if is_report and planned_emoji in task:
                    continue
                if not is_report:
                    task = task.replace(planned_emoji, "").strip()
                filtered_tasks.append(task)

            if filtered_tasks:
                sections.append(f"### {project_name}")
                for task in filtered_tasks:
                    task_text = task.replace("- [ ]", "☐").replace("- [x]", "☑")
                    sections.append(f"* {task_text}")
                sections.append("")  # Empty line between projects

        return "\n".join(sections)


class WhatsAppFormatter(BaseFormatter):
    """Formats tasks for WhatsApp messages."""

    def format_message(
        self, tasks: Dict[str, List[str]], date: datetime, is_report: bool = False
    ) -> str:
        """Format tasks into a WhatsApp message."""
        date_str = date.strftime("%Y-%m-%d")
        sections = []

        # Add header
        sections.append(f"*{'EOD REPORT' if is_report else 'DAILY PLAN'} - {date_str}*")
        sections.append("------------------------")

        # Get planned emoji from config
        planned_emoji = next(
            (
                info["emoji"]
                for info in self.status_info.values()
                if info.get("name", "").lower() == "planned"
            ),
            "📝",
        )

        # Process each project
        for project_name, project_tasks in tasks.items():
            if not project_tasks:
                continue

            filtered_tasks = []
            for task in project_tasks:
                if task.strip().endswith(f"New task {planned_emoji}"):
                    continue
                if is_report and planned_emoji in task:
                    continue
                if not is_report:
                    task = task.replace(planned_emoji, "").strip()
                filtered_tasks.append(task)

            if filtered_tasks:
                sections.append(f"\n*{project_name}*")
                for task in filtered_tasks:
                    task_text = task.replace("- [ ]", "○").replace("- [x]", "●")
                    sections.append(task_text)
                sections.append("------------------------")

        return "\n".join(sections)


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

        # Get planned emoji from config
        planned_emoji = next(
            (
                info["emoji"]
                for info in self.status_info.values()
                if info.get("name", "").lower() == "planned"
            ),
            "📝",
        )

        # Process each project
        for project_name, project_tasks in tasks.items():
            if not project_tasks:
                continue

            filtered_tasks = []
            for task in project_tasks:
                if task.strip().endswith(f"New task {planned_emoji}"):
                    continue
                if is_report and planned_emoji in task:
                    continue
                if not is_report:
                    task = task.replace(planned_emoji, "").strip()
                filtered_tasks.append(task)

            if filtered_tasks:
                sections.append(f"<h3>{project_name}</h3>")
                sections.append("<ul>")
                for task in filtered_tasks:
                    task_text = task.replace("- [ ]", "☐").replace("- [x]", "☑")
                    sections.append(f"<li>{task_text}</li>")
                sections.append("</ul>")
                sections.append("<hr>")

        return "\n".join(sections)
