import click
from ..data.database import Database
from ..data.repositories.time_entries import TimeEntryRepository

@click.command()
@click.argument('entry_id', type=int)
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
def delete(entry_id: int, force: bool):
    """Delete a time entry by ID."""
    db = Database()
    time_repo = TimeEntryRepository(db)
    
    # Check if entry exists
    entry = time_repo.get_by_id(entry_id)
    if not entry:
        click.echo(f"Error: Time entry with ID {entry_id} not found.")
        return
    
    # Show entry details and confirm deletion unless --force is used
    if not force:
        click.echo(f"Entry to delete:")
        click.echo(f"  ID: {entry.id}")
        click.echo(f"  Project: {entry.project_display}")
        if entry.tags:
            click.echo(f"  Tags: {', '.join(entry.tags)}")
        click.echo(f"  Start time: {entry.start_time}")
        if entry.end_time:
            click.echo(f"  End time: {entry.end_time}")
        click.echo(f"  Status: {entry.status}")
        
        if not click.confirm("Are you sure you want to delete this entry?"):
            click.echo("Deletion cancelled.")
            return
    
    # Delete the entry
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            click.echo(f"Successfully deleted time entry {entry_id}.")
        else:
            click.echo(f"Error: Failed to delete time entry {entry_id}.")