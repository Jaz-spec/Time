import click
from rich.console import Console

from ..core.timer import TimerService
from ..data.database import Database
from ..data.repositories.time_entries import TimeEntryRepository
from ..data.repositories.directory_mappings import DirectoryMappingRepository
from ..ui.formatters import Formatters

@click.command()
def resume():
    """Resume paused timer."""
    console = Console()
    
    # Initialize services
    db = Database()
    time_repo = TimeEntryRepository(db)
    directory_repo = DirectoryMappingRepository(db)
    timer_service = TimerService(time_repo, directory_repo)
    
    try:
        # Check if there's a paused session
        paused_session = timer_service.get_paused_session()
        if not paused_session:
            console.print(Formatters.format_warning("No paused timer session found"))
            return
        
        # Resume the timer
        entry_id = timer_service.resume_timer()
        
        if entry_id:
            # Get the resumed entry for display
            resumed_entry = time_repo.get_by_id(entry_id)
            if resumed_entry:
                panel = Formatters.format_timer_resumed(resumed_entry)
                console.print(panel)
            else:
                console.print(Formatters.format_success(f"Timer resumed with session ID: {entry_id}"))
        else:
            console.print(Formatters.format_error("Failed to resume timer"))
            
    except Exception as e:
        console.print(Formatters.format_error(f"Failed to resume timer: {e}"))