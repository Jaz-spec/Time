from rich.console import Console
from typing import List

from ..data.models import TimeEntry, ReportSummary
from ..core.duration import format_duration
from .tables import TableFormatters

class ReportRenderer:
    """Renders formatted reports using Rich."""
    
    def __init__(self):
        self.console = Console()
    
    def render_report(self, entries: List[TimeEntry], summary: ReportSummary, show_details: bool = True):
        """Render complete time tracking report."""
        # Header
        self.console.print("\n[bold blue]Time Tracking Report[/bold blue]", style="bold")
        self.console.print("=" * 50, style="dim")
        
        # Summary
        self.console.print(f"\n[green]Total entries:[/green] {summary.total_entries}")
        self.console.print(f"[green]Total time:[/green] [bold]{format_duration(summary.total_duration)}[/bold]")
        
        # Project breakdown
        if summary.projects:
            self.console.print("\n[bold cyan]Project Breakdown:[/bold cyan]")
            project_table = TableFormatters.create_project_breakdown_table(summary)
            self.console.print(project_table)
        
        # Daily breakdown
        if TableFormatters.should_show_daily_breakdown(summary):
            self.console.print("\n[bold cyan]Daily Breakdown:[/bold cyan]")
            daily_table = TableFormatters.create_daily_breakdown_table(summary)
            self.console.print(daily_table)
        
        # Detailed entries (optional)
        if show_details and entries:
            self.console.print("\n[bold cyan]Detailed Entries:[/bold cyan]")
            entries_table = TableFormatters.create_detailed_entries_table(entries)
            self.console.print(entries_table)
    
    def render_no_entries_message(self):
        """Render message when no entries found."""
        self.console.print("No time entries found matching the specified criteria.")