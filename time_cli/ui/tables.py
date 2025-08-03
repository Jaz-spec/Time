from rich.table import Table
from rich import box
from typing import List

from ..data.models import TimeEntry, ReportSummary
from ..core.duration import format_duration
from ..config.settings import Settings

class TableFormatters:
    """Rich table formatting for reports."""
    
    @staticmethod
    def create_project_breakdown_table(summary: ReportSummary) -> Table:
        """Create project breakdown table."""
        table = Table(box=box.SIMPLE_HEAD)
        table.add_column("Project", style="cyan", no_wrap=True)
        table.add_column("Duration", style="green", justify="right")
        table.add_column("Entries", style="yellow", justify="center")
        
        # Sort projects by duration (descending)
        sorted_projects = sorted(
            summary.projects.items(),
            key=lambda x: x[1]['duration'],
            reverse=True
        )
        
        for project, data in sorted_projects:
            duration_str = format_duration(data['duration'])
            table.add_row(project, duration_str, str(data['entries']))
            
            # Sub-projects
            if data['sub_projects']:
                for sub_project, sub_duration in data['sub_projects'].items():
                    sub_duration_str = format_duration(sub_duration)
                    table.add_row(f"  └─ {sub_project}", sub_duration_str, "", style="dim")
        
        return table
    
    @staticmethod
    def create_daily_breakdown_table(summary: ReportSummary) -> Table:
        """Create daily breakdown table."""
        table = Table(box=box.SIMPLE_HEAD)
        table.add_column("Date", style="cyan")
        table.add_column("Duration", style="green", justify="right")
        
        sorted_days = sorted(summary.daily_totals.items())
        for date, duration in sorted_days:
            duration_str = format_duration(duration)
            table.add_row(date, duration_str)
        
        return table
    
    @staticmethod
    def create_detailed_entries_table(entries: List[TimeEntry]) -> Table:
        """Create detailed entries table."""
        table = Table(box=box.SIMPLE_HEAD)
        table.add_column("ID", style="cyan")
        table.add_column("Date & Time", style="cyan")
        table.add_column("Project", style="magenta")
        table.add_column("Tags", style="yellow")
        table.add_column("Duration", style="green", justify="right")
        
        for entry in entries:
            project_display = entry.project_display
            tags_display = ', '.join(entry.tags) if entry.tags else ""
            duration_str = format_duration(entry.duration or 0)
            date_str = entry.start_time.strftime('%Y-%m-%d %H:%M')
            
            table.add_row(str(entry.id), date_str, project_display, tags_display, duration_str)
        
        return table
    
    @staticmethod
    def should_show_daily_breakdown(summary: ReportSummary) -> bool:
        """Determine if daily breakdown should be shown."""
        return (summary.daily_totals and 
                len(summary.daily_totals) <= Settings.MAX_DAILY_ENTRIES_FOR_BREAKDOWN)