import click

from ..data.database import Database
from ..data.repositories.time_entries import TimeEntryRepository
from ..core.filters import FilterService
from ..ui.reports import ReportRenderer

@click.command()
@click.option('--today', is_flag=True, help='Show today\'s entries')
@click.option('--week', is_flag=True, help='Show this week\'s entries')
@click.option('--month', is_flag=True, help='Show this month\'s entries')
@click.option('--from', 'from_date', help='Start date (YYYY-MM-DD)')
@click.option('--to', 'to_date', help='End date (YYYY-MM-DD)')
@click.option('--project', multiple=True, help='Filter by project(s)')
@click.option('--tag', multiple=True, help='Filter by tag/label(s)')
@click.option('--label', multiple=True, help='Alias for --tag')
@click.option('--summary', is_flag=True, help='Show only summary without detailed entries')
def report(today, week, month, from_date, to_date, project, tag, label, summary):
    """Generate time reports with flexible filtering."""
    # Initialize services
    db = Database()
    time_repo = TimeEntryRepository(db)
    renderer = ReportRenderer()
    
    try:
        # Build filters
        all_tags = list(tag) + list(label)
        filters = FilterService.build_filters(
            today=today, week=week, month=month,
            from_date=from_date, to_date=to_date,
            projects=list(project) if project else None,
            tags=all_tags if all_tags else None
        )
        
        # Get entries
        entries = time_repo.find_with_filters(filters)
        
        if not entries:
            renderer.render_no_entries_message()
            return
        
        # Generate summary and render report
        report_summary = FilterService.generate_summary(entries)
        show_details = not summary
        renderer.render_report(entries, report_summary, show_details)
        
    except Exception as e:
        from ..ui.formatters import Formatters
        from rich.console import Console
        console = Console()
        console.print(Formatters.format_error(f"Failed to generate report: {e}"))