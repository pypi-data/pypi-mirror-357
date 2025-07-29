"""Task model for TaskDaily."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class Task:
    """Represents a single task with its properties."""

    content: str
    project_name: str
    status_emoji: str = "📝"  # Default to planned
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status_emoji == "✅"

    @property
    def is_planned(self) -> bool:
        """Check if task is in planned state."""
        return self.status_emoji == "📝"

    @property
    def is_cancelled(self) -> bool:
        """Check if task is cancelled."""
        return self.status_emoji == "🚫"

    def should_carry_forward(self, status_info: Dict[str, Dict[str, str]]) -> bool:
        """Check if task should be carried forward based on its status.

        Args:
            status_info: Status configuration from config manager

        Returns:
            True if task should be carried forward, False otherwise
        """
        # Find status by emoji
        for status in status_info.values():
            if status["emoji"] == self.status_emoji:
                return bool(status.get("carry_forward", True))
        return True  # Default to carrying forward if status not found

    def should_show_in_report(self, status_info: Dict[str, Dict[str, str]]) -> bool:
        """Check if task should be shown in reports based on its status.

        Args:
            status_info: Status configuration from config manager

        Returns:
            True if task should be shown in reports, False otherwise
        """
        # Find status by emoji
        for status in status_info.values():
            if status["emoji"] == self.status_emoji:
                return bool(status.get("show_in_report", True))
        return True  # Default to showing if status not found

    def carry_forward(self, status_info: Dict[str, Dict[str, str]]) -> Optional["Task"]:
        """Create a new task for carrying forward.

        Args:
            status_info: Status configuration from config manager

        Returns:
            New task if should be carried forward, None otherwise
        """
        if not self.should_carry_forward(status_info):
            return None

        return Task(
            content=self.content,
            project_name=self.project_name,
            status_emoji=self.status_emoji,  # Keep original status emoji
        )

    def to_markdown(self) -> str:
        """Convert task to markdown format.

        Returns:
            Markdown formatted string
        """
        return f"- [ ] {self.content} {self.status_emoji}"

    @classmethod
    def from_markdown(cls, line: str, project_name: str) -> "Task":
        """Create task from markdown line.

        Args:
            line: Markdown line to parse
            project_name: Name of the project this task belongs to

        Returns:
            Task instance
        """
        # Remove leading "- [ ]" or "- [x]"
        content = line[6:].strip()

        # Extract status emoji if present
        status_emoji = "📝"  # Default to planned
        if content and content[-1] in "📝✅🚫⚡🚧➡️":
            status_emoji = content[-1]
            content = content[:-2].strip()

        return cls(
            content=content, project_name=project_name, status_emoji=status_emoji
        )
