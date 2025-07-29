from datetime import datetime
from typing import Any, Dict, List


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

    def _get_planned_emoji(self) -> str:
        """Get planned emoji from config."""
        return next(
            (
                info["emoji"]
                for info in self.status_info.values()
                if info.get("name", "").lower() == "planned"
            ),
            "📝",  # Fallback emoji
        )

    def _filter_tasks(self, tasks: List[str], is_report: bool) -> List[str]:
        """Filter tasks based on report type and remove template tasks."""
        planned_emoji = self._get_planned_emoji()
        filtered_tasks = []

        for task in tasks:
            # Skip template tasks
            if task.strip().endswith(f"New task {planned_emoji}"):
                continue

            # For reports, exclude planned tasks
            if is_report and planned_emoji in task:
                continue

            # For daily plan, remove planned emoji
            if not is_report:
                task = task.replace(planned_emoji, "").strip()
                # Clean up any double spaces from emoji removal
                while "  " in task:
                    task = task.replace("  ", " ")

            filtered_tasks.append(task)

        return filtered_tasks
