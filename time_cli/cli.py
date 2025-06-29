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
    """Start timer with optional project and tasks"""
    db = TimeTrackDB()
    current_dir = str(Path.cwd())
    
    # Parse arguments
    project = None
    sub_project = None
    tasks = []
    
    if args:
        # First argument might be project or project:sub_project
        first_arg = args[0]
        if ':' in first_arg:
            project, sub_project = first_arg.split(':', 1)
        else:
            project = first_arg
        
        # Remaining arguments are tasks
        tasks = list(args[1:])
    
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
    session_id = db.start_timer(project, sub_project, tasks, current_dir)
    
    # Build Rich output message
    console = Console()
    project_display = f"{project}:{sub_project}" if sub_project else project
    tasks_display = ", ".join(tasks) if tasks else "No tasks"
    
    start_text = Text()
    start_text.append("▶️  Timer started for ", style="green")
    start_text.append(f"{project_display}\n", style="bold magenta")
    start_text.append("Tasks: ", style="cyan")
    start_text.append(f"{tasks_display}\n", style="yellow")
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
        tasks_display = ", ".join(active_session['tasks']) if active_session['tasks'] else "No tasks"
        
        stop_text = Text()
        stop_text.append("⏹️  Timer stopped for ", style="red")
        stop_text.append(f"{project_display}\n", style="bold magenta")
        stop_text.append("Tasks: ", style="cyan")
        stop_text.append(f"{tasks_display}\n", style="yellow")
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
    tasks_display = ", ".join(active_session['tasks']) if active_session['tasks'] else "No tasks"
    
    status_text = Text()
    status_text.append("Project: ", style="cyan")
    status_text.append(f"{project_display}\n", style="bold magenta")
    status_text.append("Tasks: ", style="cyan")
    status_text.append(f"{tasks_display}\n", style="yellow")
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
@click.option('--task', multiple=True, help='Filter by task/label(s)')
@click.option('--label', multiple=True, help='Alias for --task')
@click.option('--summary', is_flag=True, help='Show only summary without detailed entries')
def report(today, week, month, from_date, to_date, project, task, label, summary):
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
    
    # Task filtering (combine --task and --label)
    all_tasks = list(task) + list(label)
    if all_tasks:
        filters['tasks'] = all_tasks
    
    # Get entries
    entries = db.get_time_entries(filters)
    
    if not entries:
        click.echo("No time entries found matching the specified criteria.")
        return
    
    # Generate summary and format report
    report_summary = generate_report_summary(entries)
    show_details = not summary
    format_report(entries, report_summary, show_details)

if __name__ == '__main__':
    cli()