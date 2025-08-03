import click
from rich.console import Console

from ..core.timer import TimerService
from ..data.database import Database
from ..data.repositories.time_entries import TimeEntryRepository
from ..data.repositories.directory_mappings import DirectoryMappingRepository
from ..ui.formatters import Formatters
from ..ui.prompts import Prompts

@click.command()
@click.argument('entry_id', type=int)
def edit(entry_id):
    """Edit a specific time entry by its ID."""
    console = Console()
    
    # Initialize services
    db = Database()
    time_repo = TimeEntryRepository(db)
    directory_repo = DirectoryMappingRepository(db)
    timer_service = TimerService(time_repo, directory_repo)
    
    try:
        # Fetch the entry to be edited
        entry = time_repo.get_by_id(entry_id)
        if not entry:
            console.print(Formatters.format_error(f"No time entry found with ID {entry_id}"))
            return

        # Display current entry details
        details_panel = Formatters.format_entry_details(entry)
        console.print(details_panel)

        # Prompt for new values
        new_project = Prompts.prompt_for_project_edit(entry)
        new_sub_project = Prompts.prompt_for_sub_project_edit(entry)
        new_tags_str = Prompts.prompt_for_tags_edit(entry)
        new_duration_str = Prompts.prompt_for_duration_edit(entry)

        # Prepare updates
        updates = {}
        if new_project != entry.project:
            updates['project'] = new_project
        
        if new_sub_project != (entry.sub_project or ''):
            updates['sub_project'] = new_sub_project if new_sub_project.lower() != 'none' else None

        new_tags = Prompts.parse_tags_input(new_tags_str)
        if set(new_tags) != set(entry.tags):
            updates['tags'] = new_tags

        # Handle duration edit separately through timer service
        duration_updated = False
        current_duration_display = timer_service.time_repo.get_by_id(entry_id)
        if current_duration_display:
            from ..core.duration import format_duration
            current_display = format_duration(current_duration_display.duration) if current_duration_display.duration else 'N/A'
            if new_duration_str.strip() and new_duration_str != current_display:
                duration_updated = timer_service.edit_entry_duration(entry_id, new_duration_str)
                if not duration_updated:
                    console.print(Formatters.format_error("Invalid duration format"))
                    return

        # Apply other updates
        other_updates_applied = False
        if updates:
            other_updates_applied = time_repo.update(entry_id, updates)

        if duration_updated or other_updates_applied or not updates:
            if duration_updated or other_updates_applied:
                console.print(Formatters.format_success(f"Successfully updated time entry {entry_id}"))
            else:
                console.print("[yellow]No changes made.[/yellow]")
        else:
            console.print(Formatters.format_error(f"Failed to update time entry {entry_id}"))
            
    except Exception as e:
        console.print(Formatters.format_error(f"Failed to edit entry: {e}"))