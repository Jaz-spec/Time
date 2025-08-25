import click
from pathlib import Path
from rich.console import Console

from ..core.timer import TimerService
from ..core.duration import parse_duration_input
from ..data.database import Database
from ..data.repositories.time_entries import TimeEntryRepository
from ..data.repositories.directory_mappings import DirectoryMappingRepository
from ..ui.formatters import Formatters

@click.command()
@click.argument('args', nargs=-1)
@click.option('--alert', help='Alert after specified duration (e.g., "1h 20m")')
def start(args, alert):
    """Start timer with optional project and tags."""
    console = Console()
    
    # Initialize services
    db = Database()
    time_repo = TimeEntryRepository(db)
    directory_repo = DirectoryMappingRepository(db)
    timer_service = TimerService(time_repo, directory_repo)
    
    # Parse arguments
    project = None
    sub_project = None
    tags = []
    expected_duration = None
    
    if args:
        # First argument might be project or project:sub_project
        first_arg = args[0]
        if ':' in first_arg:
            project, sub_project = first_arg.split(':', 1)
        else:
            project = first_arg
        
        # Remaining arguments are tags
        tags = list(args[1:])
    
    # Parse alert duration if provided
    if alert:
        try:
            expected_duration = parse_duration_input(alert)
        except ValueError as e:
            console.print(Formatters.format_error(f"Invalid alert duration: {e}"))
            return
    
    try:
        # Start the timer
        session_id = timer_service.start_timer(project, sub_project, tags, expected_duration)
        
        # Get the created entry for display
        entry = time_repo.get_by_id(session_id)
        if entry:
            panel = Formatters.format_timer_started(
                session_id, entry.project, entry.sub_project, entry.tags
            )
            console.print(panel)
        else:
            console.print(Formatters.format_success(f"Timer started with session ID: {session_id}"))
            
    except Exception as e:
        console.print(Formatters.format_error(f"Failed to start timer: {e}"))