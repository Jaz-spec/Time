import click
import os
from pathlib import Path
from .database import TimeTrackDB
from .utils import detect_project_from_directory, format_duration, get_date_range, generate_report_summary, format_report
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

@click.group()
def cli():
    """CLI-based timekeeping tool"""
    pass

@cli.command()
@click.argument('args', nargs=-1)
def start(args):
    """Start timer with optional project and tags"""
    db = TimeTrackDB()
    current_dir = str(Path.cwd())
    
    # Parse arguments
    project = None
    sub_project = None
    tags = []
    
    tags.append("in-work")
    
    if args:
        # First argument might be project or project:sub_project
        first_arg = args[0]
        if ':' in first_arg:
            project, sub_project = first_arg.split(':', 1)
        else:
            project = first_arg
        
        # Remaining arguments are tags
        tags = list(args[1:])
        if "out-work" not in tags:
            tags.append("in-work")

    
    # If no project specified, auto-detect from directory
    if not project:
        project, detection_method = detect_project_from_directory(db)
        
        # Save auto-detected mapping if it's not already stored
        if detection_method != 'stored_mapping':
            db.save_directory_mapping(
                directory_path=current_dir,
                project_name=project,
                auto_detected=True,
                detection_method=detection_method
            )
    
    # Start the timer
    session_id = db.start_timer(project, sub_project, tags, current_dir)
    
    # Build Rich output message
    console = Console()
    project_display = f"{project}:{sub_project}" if sub_project else project
    tags_display = ", ".join(tags) if tags else "No tags"
    
    start_text = Text()
    start_text.append("▶️  Timer started for ", style="green")
    start_text.append(f"{project_display}\n", style="bold magenta")
    start_text.append("Tags: ", style="cyan")
    start_text.append(f"{tags_display}\n", style="yellow")
    start_text.append("Session ID: ", style="cyan")
    start_text.append(f"{session_id}", style="dim")
    
    console.print(Panel(start_text, title="Timer Started", border_style="green"))

@cli.command()
def stop():
    """Stop current timer"""
    console = Console()
    db = TimeTrackDB()
    
    # Check if there's an active session
    active_session = db.get_active_session()
    if not active_session:
        console.print(Panel("[yellow]No active timer session found[/yellow]", title="Stop Timer", border_style="yellow"))
        return
    
    # Stop the timer
    duration = db.stop_timer()
    
    if duration:
        project_display = f"{active_session['project']}:{active_session['sub_project']}" if active_session['sub_project'] else active_session['project']
        tags_display = ", ".join(active_session['tags']) if active_session['tags'] else "No tags"
        
        stop_text = Text()
        stop_text.append("⏹️  Timer stopped for ", style="red")
        stop_text.append(f"{project_display}\n", style="bold magenta")
        stop_text.append("Tags: ", style="cyan")
        stop_text.append(f"{tags_display}\n", style="yellow")
        stop_text.append("Duration: ", style="cyan")
        stop_text.append(f"{format_duration(duration)}", style="bold green")
        
        console.print(Panel(stop_text, title="Timer Stopped", border_style="red"))
    else:
        console.print(Panel("[red]Failed to stop timer[/red]", title="Error", border_style="red"))

@cli.command()
def status():
    """Show current session and elapsed time"""
    console = Console()
    db = TimeTrackDB()
    
    active_session = db.get_active_session()
    
    if not active_session:
        console.print(Panel("[yellow]No active timer session[/yellow]", title="Status", border_style="yellow"))
        return
    
    project_display = f"{active_session['project']}:{active_session['sub_project']}" if active_session['sub_project'] else active_session['project']
    tags_display = ", ".join(active_session['tags']) if active_session['tags'] else "No tags"
    
    status_text = Text()
    status_text.append("Project: ", style="cyan")
    status_text.append(f"{project_display}\n", style="bold magenta")
    status_text.append("Tags: ", style="cyan")
    status_text.append(f"{tags_display}\n", style="yellow")
    status_text.append("Started: ", style="cyan")
    status_text.append(f"{active_session['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n", style="white")
    status_text.append("Elapsed: ", style="cyan")
    status_text.append(f"{format_duration(active_session['elapsed'])}\n", style="bold green")
    status_text.append("Directory: ", style="cyan")
    status_text.append(f"{active_session['directory']}", style="dim")
    
    console.print(Panel(status_text, title="⏱️  Active Timer Session", border_style="green"))

@cli.command()
@click.argument('project_name')
def link(project_name):
    """Link current directory to a project name"""
    console = Console()
    db = TimeTrackDB()
    current_dir = Path.cwd()
    
    # Save the manual mapping
    db.save_directory_mapping(
        directory_path=current_dir,
        project_name=project_name,
        auto_detected=False,
        detection_method='manual'
    )
    
    link_text = Text()
    link_text.append("🔗 Linked directory\n", style="green")
    link_text.append(f"'{current_dir}'\n", style="cyan")
    link_text.append("to project\n", style="white")
    link_text.append(f"'{project_name}'", style="bold magenta")
    
    console.print(Panel(link_text, title="Directory Linked", border_style="green"))

@cli.command()
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
    """Generate time reports with flexible filtering"""
    db = TimeTrackDB()
    
    # Build filters
    filters = {}
    
    # Date filtering
    if today:
        filters['from_date'], filters['to_date'] = get_date_range('today')
    elif week:
        filters['from_date'], filters['to_date'] = get_date_range('week')
    elif month:
        filters['from_date'], filters['to_date'] = get_date_range('month')
    elif from_date or to_date:
        if from_date:
            filters['from_date'] = from_date
        if to_date:
            filters['to_date'] = to_date
    
    # Project filtering
    if project:
        filters['projects'] = list(project)
    
    # Tag filtering (combine --tag and --label)
    all_tags = list(tag) + list(label)
    if all_tags:
        filters['tags'] = all_tags
    
    # Get entries
    entries = db.get_time_entries(filters)
    
    if not entries:
        click.echo("No time entries found matching the specified criteria.")
        return
    
    # Generate summary and format report
    report_summary = generate_report_summary(entries)
    show_details = not summary
    format_report(entries, report_summary, show_details)

@cli.command()
@click.argument('entry_id', type=int)
def edit(entry_id):
    """Edit a specific time entry by its ID."""
    db = TimeTrackDB()
    console = Console()

    # Fetch the entry to be edited
    entry = db.get_entry_by_id(entry_id)
    if not entry:
        console.print(f"[red]Error: No time entry found with ID {entry_id}[/red]")
        return

    # Display current entry details
    console.print(Panel(
        f"[cyan]Editing Entry ID:[/cyan] [bold]{entry['id']}[/bold]\n"
        f"[cyan]Project:[/cyan] {entry['project']}\n"
        f"[cyan]Sub-project:[/cyan] {entry['sub_project'] or 'N/A'}\n"
        f"[cyan]Tags:[/cyan] {', '.join(entry['tags']) if entry['tags'] else 'N/A'}",
        title="Current Entry Details",
        border_style="yellow"
    ))

    # Prompt for new values
    new_project = click.prompt(
        "New project (leave blank to keep)",
        default=entry['project'],
        show_default=False
    )
    new_sub_project = click.prompt(
        "New sub-project (leave blank to keep, 'none' to remove)",
        default=entry['sub_project'] or '',
        show_default=False
    )
    new_tags_str = click.prompt(
        "New tags (comma-separated, leave blank to keep)",
        default=', '.join(entry['tags']),
        show_default=False
    )

    # Prepare updates
    updates = {}
    if new_project != entry['project']:
        updates['project'] = new_project
    
    if new_sub_project != (entry['sub_project'] or ''):
        updates['sub_project'] = new_sub_project if new_sub_project.lower() != 'none' else None

    new_tags = [tag.strip() for tag in new_tags_str.split(',') if tag.strip()]
    if set(new_tags) != set(entry['tags']):
        updates['tags'] = new_tags

    if not updates:
        console.print("[yellow]No changes made.[/yellow]")
        return

    # Update the database
    if db.update_time_entry(entry_id, updates):
        console.print(f"[green]Successfully updated time entry {entry_id}.[/green]")
    else:
        console.print(f"[red]Error: Failed to update time entry {entry_id}.[/red]")

if __name__ == '__main__':
    cli()