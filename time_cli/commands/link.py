import click
from pathlib import Path
from rich.console import Console

from ..core.timer import TimerService
from ..data.database import Database
from ..data.repositories.time_entries import TimeEntryRepository
from ..data.repositories.directory_mappings import DirectoryMappingRepository
from ..ui.formatters import Formatters

@click.command()
@click.argument('project_name')
def link(project_name):
    """Link current directory to a project name."""
    console = Console()
    current_dir = Path.cwd()
    
    # Initialize services
    db = Database()
    time_repo = TimeEntryRepository(db)
    directory_repo = DirectoryMappingRepository(db)
    timer_service = TimerService(time_repo, directory_repo)
    
    try:
        # Link the directory
        success = timer_service.link_directory(project_name)
        
        if success:
            panel = Formatters.format_directory_linked(str(current_dir), project_name)
            console.print(panel)
        else:
            console.print(Formatters.format_error("Failed to link directory"))
            
    except Exception as e:
        console.print(Formatters.format_error(f"Failed to link directory: {e}"))