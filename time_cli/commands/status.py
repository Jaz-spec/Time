import click
from rich.console import Console

from ..core.timer import TimerService
from ..data.database import Database
from ..data.repositories.time_entries import TimeEntryRepository
from ..data.repositories.directory_mappings import DirectoryMappingRepository
from ..ui.formatters import Formatters

@click.command()
def status():
    """Show current session and elapsed time."""
    console = Console()
    
    # Initialize services
    db = Database()
    time_repo = TimeEntryRepository(db)
    directory_repo = DirectoryMappingRepository(db)
    timer_service = TimerService(time_repo, directory_repo)
    
    try:
        active_session = timer_service.get_active_session()
        
        if not active_session:
            console.print(Formatters.format_warning("No active timer session"))
            return
        
        panel = Formatters.format_active_session(active_session)
        console.print(panel)
        
    except Exception as e:
        console.print(Formatters.format_error(f"Failed to get status: {e}"))