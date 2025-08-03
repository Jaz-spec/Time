import click
from typing import List, Optional

from ..data.models import TimeEntry
from ..core.duration import format_duration

class Prompts:
    """Interactive prompts for user input."""
    
    @staticmethod
    def prompt_for_project_edit(entry: TimeEntry) -> str:
        """Prompt for new project name."""
        return click.prompt(
            "New project (leave blank to keep)",
            default=entry.project,
            show_default=False
        )
    
    @staticmethod
    def prompt_for_sub_project_edit(entry: TimeEntry) -> str:
        """Prompt for new sub-project name."""
        return click.prompt(
            "New sub-project (leave blank to keep, 'none' to remove)",
            default=entry.sub_project or '',
            show_default=False
        )
    
    @staticmethod
    def prompt_for_tags_edit(entry: TimeEntry) -> str:
        """Prompt for new tags."""
        return click.prompt(
            "New tags (comma-separated, leave blank to keep)",
            default=', '.join(entry.tags),
            show_default=False
        )
    
    @staticmethod
    def prompt_for_duration_edit(entry: TimeEntry) -> str:
        """Prompt for new duration."""
        current_duration_display = format_duration(entry.duration) if entry.duration else 'N/A'
        return click.prompt(
            "New duration (format: 1h30m or 90m or 5400s, leave blank to keep)",
            default=current_duration_display,
            show_default=False
        )
    
    @staticmethod
    def parse_tags_input(tags_str: str) -> List[str]:
        """Parse comma-separated tags input."""
        return [tag.strip() for tag in tags_str.split(',') if tag.strip()]