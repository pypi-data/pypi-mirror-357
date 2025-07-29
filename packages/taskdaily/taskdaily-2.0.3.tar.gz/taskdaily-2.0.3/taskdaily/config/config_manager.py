import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class ConfigManager:
    """Manages configuration loading and saving."""

    DEFAULT_CONFIG = {
        "storage": {
            "type": "file",
            "base_dir": ".",  # Use current directory by default
        },
        "default_format": "slack",
        "default_sections": [
            {"emoji": "🏠", "name": "Personal"},
            {"emoji": "💼", "name": "Work"},
            {"emoji": "📚", "name": "Learning"},
        ],
        "status": {
            "planned": {
                "name": "Planned",
                "emoji": "📝",
                "show_in_report": False,
                "carry_forward": True,
            },
            "in_progress": {
                "name": "In Progress",
                "emoji": "⚡",
                "show_in_report": True,
                "carry_forward": True,
            },
            "blocked": {
                "name": "Blocked",
                "emoji": "🚧",
                "show_in_report": True,
                "carry_forward": True,
            },
            "completed": {
                "name": "Completed",
                "emoji": "✅",
                "show_in_report": True,
                "carry_forward": False,
            },
            "cancelled": {
                "name": "Cancelled",
                "emoji": "🚫",
                "show_in_report": True,
                "carry_forward": False,
            },
            "carried_forward": {
                "name": "Carried Forward",
                "emoji": "➡️",
                "show_in_report": True,
                "carry_forward": True,
            },
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize config manager.

        Args:
            config_path: Path to config file
        """
        self.config_path = (
            Path(config_path)
            if config_path
            else Path.home() / ".taskdaily" / "config.yaml"
        )
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            self.config = self.DEFAULT_CONFIG
            return

        try:
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f)

            # Ensure all required sections exist
            for key, value in self.DEFAULT_CONFIG.items():
                if key not in self.config:
                    self.config[key] = value
        except Exception as e:
            raise ValueError(f"Failed to load config from {self.config_path}: {e}")

    def save_config(self) -> None:
        """Save current configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)

    def get_value(self, key: str, default: Optional[str] = None) -> str:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set_value(self, key: str, value: str) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self.save_config()

    def add_status(
        self,
        name: str,
        emoji: str,
        show_in_report: bool = True,
        carry_forward: bool = True,
    ) -> None:
        """Add a new status to configuration.

        Args:
            name: Status name
            emoji: Status emoji
            show_in_report: Whether to show in reports
            carry_forward: Whether to carry forward tasks with this status
        """
        key = name.lower().replace(" ", "_")
        self.config["status"][key] = {
            "name": name,
            "emoji": emoji,
            "show_in_report": show_in_report,
            "carry_forward": carry_forward,
        }
        self.save_config()

    def remove_status(self, name: str) -> bool:
        """Remove a status from configuration.

        Args:
            name: Status name to remove

        Returns:
            True if status was found and removed, False otherwise
        """
        key = name.lower().replace(" ", "_")
        if key in self.config["status"]:
            del self.config["status"][key]
            self.save_config()
            return True
        return False

    @property
    def storage_type(self) -> str:
        """Get storage type from config."""
        return self.config.get("storage", {}).get("type", "file")

    @property
    def storage_base_dir(self) -> str:
        """Get storage base directory from config."""
        base_dir = self.config.get("storage", {}).get("base_dir", ".")
        if base_dir == ".":
            return str(Path.cwd())
        return os.path.expanduser(base_dir)

    @property
    def default_format(self) -> str:
        """Get default format from config."""
        return self.config.get("default_format", "slack")

    @property
    def default_sections(self) -> List[Dict[str, str]]:
        """Get default sections from config."""
        return self.config.get("default_sections", [])

    @property
    def status_info(self) -> Dict[str, Dict[str, str]]:
        """Get status information from config."""
        return self.config.get("status", {})
