import click
from rich.console import Console

from ..core.timer import TimerService
from ..data.database import Database
from ..data.repositories.time_entries import TimeEntryRepository
from ..data.repositories.directory_mappings import DirectoryMappingRepository
from ..ui.formatters import Formatters

@click.command()
def stop():
    """Stop current timer."""
    console = Console()
    
    # Initialize services
    db = Database()
    time_repo = TimeEntryRepository(db)
    directory_repo = DirectoryMappingRepository(db)
    timer_service = TimerService(time_repo, directory_repo)
    
    try:
        # Check if there's an active session
        active_session = timer_service.get_active_session()
        if not active_session:
            console.print(Formatters.format_warning("No active timer session found"))
            return
        
        # Stop the timer
        duration = timer_service.stop_timer()
        
        if duration:
            panel = Formatters.format_timer_stopped(active_session, duration)
            console.print(panel)
        else:
            console.print(Formatters.format_error("Failed to stop timer"))
            
    except Exception as e:
        console.print(Formatters.format_error(f"Failed to stop timer: {e}"))