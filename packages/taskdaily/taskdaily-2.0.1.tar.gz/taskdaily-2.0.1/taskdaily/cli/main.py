"""Command-line interface for TaskDaily."""

import sys
from datetime import datetime
from typing import Optional

import click
from rich.console import Console

from ..config.config_manager import ConfigManager
from ..task_manager import TaskManager
from ..utils import parse_date
from ..version import __version__

console = Console()


@click.group()
@click.version_option(version=__version__)
def main():
    """TaskDaily - A flexible daily task management system."""
    pass


@main.command()
@click.option(
    "--format", "-f", default="slack", help="Output format (slack/teams/whatsapp/email)"
)
@click.option("--report/--no-report", default=False, help="Generate EOD report")
@click.option("--date", "-d", default=None, type=str, help="Date in YYYY-MM-DD format")
def share(format, report, date):
    """Share your daily tasks in various formats."""
    try:
        task_manager = TaskManager()
        date_obj = datetime.strptime(date, "%Y-%m-%d") if date else None
        content = task_manager.format_tasks(
            format_type=format, is_report=report, date_obj=date_obj
        )
        console.print(content)
        console.print("[green]✓ Message copied to clipboard![/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@main.command()
@click.option("--date", "-d", default=None, help="Date in YYYY-MM-DD format")
def create(date):
    """Create a new daily task file."""
    try:
        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        task_manager = TaskManager()
        task_manager.create_daily_file(date)
        console.print("[green]✓ Daily task file created successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@main.command()
@click.option("--date", "-d", default=None, help="Date in YYYY-MM-DD format")
def share_today(date):
    """Share today's tasks."""
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d") if date else None
        task_mgr = TaskManager()
        content = task_mgr.format_tasks(
            date_obj=date_obj, format_type=task_mgr.config.default_format
        )
        console.print(content)
        console.print("[green]✓ Message copied to clipboard![/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@main.command()
@click.option("--start-date", "-s", help="Start date in YYYY-MM-DD format")
@click.option("--end-date", "-e", help="End date in YYYY-MM-DD format")
def stats(start_date: Optional[str], end_date: Optional[str]):
    """Show statistics for the specified date range."""
    console.print("[yellow]Stats functionality to be implemented[/yellow]")


@main.group()
def config():
    """Configuration commands group."""
    pass


@config.command(name="init")
def config_init():
    """Initialize configuration with default settings."""
    try:
        config_mgr = ConfigManager()
        config_mgr.save_config()
        console.print("[green]✓ Configuration initialized successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@config.command(name="path")
def config_path():
    """Show configuration paths."""
    try:
        config_mgr = ConfigManager()
        console.print(f"[green]Config file location:[/green] {config_mgr.config_path}")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
