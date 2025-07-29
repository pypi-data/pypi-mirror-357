from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .task import Task


@dataclass
class Project:
    """Represents a project with its tasks."""

    name: str
    emoji: str
    tasks: List[Task] = field(default_factory=list)

    def get_tasks_for_report(
        self, status_info: Dict[str, Dict[str, str]]
    ) -> List[Task]:
        """Get tasks that should be shown in reports.

        Args:
            status_info: Status configuration from config manager

        Returns:
            List of tasks to show in reports
        """
        return [task for task in self.tasks if task.should_show_in_report(status_info)]

    @property
    def incomplete_tasks(self) -> List[Task]:
        """Get incomplete tasks."""
        return [
            task
            for task in self.tasks
            if not task.is_completed and not task.is_cancelled
        ]

    @property
    def completed_tasks(self) -> List[Task]:
        """Get completed tasks."""
        return [task for task in self.tasks if task.is_completed]

    @property
    def planned_tasks(self) -> List[Task]:
        """Get planned tasks."""
        return [task for task in self.tasks if task.is_planned]

    @property
    def has_active_tasks(self) -> bool:
        """Check if project has any active tasks."""
        return bool(self.incomplete_tasks)

    @classmethod
    def from_markdown(cls, header: str, task_lines: List[str]) -> "Project":
        """Create a Project instance from markdown format."""
        # First character should be the emoji
        emoji = header[0]
        name = header[1:].strip()

        project = cls(name=name, emoji=emoji)

        # Add tasks
        for line in task_lines:
            if line.strip() and line.startswith("- "):
                task = Task.from_markdown(line, name)
                project.add_task(task)

        return project

    def to_markdown(self) -> List[str]:
        """Convert project and tasks to markdown format."""
        if not self.tasks:
            return []

        lines = [f"{self.emoji} {self.name}"]
        for task in self.tasks:
            lines.append(task.to_markdown())
        return lines

    def add_task(self, task: Task) -> None:
        """Add a task to the project.

        Args:
            task: Task to add
        """
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the project.

        Args:
            task: Task to remove
        """
        self.tasks.remove(task)

    def get_task_by_content(self, content: str) -> Optional[Task]:
        """Find a task by its content."""
        for task in self.tasks:
            if task.content.strip() == content.strip():
                return task
        return None

    def carry_forward_tasks(self, status_info: Dict[str, Dict[str, str]]) -> List[Task]:
        """Get tasks that should be carried forward.

        Args:
            status_info: Status configuration from config manager

        Returns:
            List of tasks to carry forward
        """
        carried_tasks = []
        for task in self.tasks:
            carried_task = task.carry_forward(status_info)
            if carried_task:
                carried_tasks.append(carried_task)
        return carried_tasks

    def clear_tasks(self) -> None:
        """Remove all tasks from the project."""
        self.tasks.clear()
