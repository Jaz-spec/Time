import click
import os
from pathlib import Path
from .database import TimeTrackDB
from .utils import detect_project_from_directory, format_duration

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
    
    # Build output message
    project_display = f"{project}:{sub_project}" if sub_project else project
    if tasks:
        tasks_display = " [" + ", ".join(tasks) + "]"
    else:
        tasks_display = ""
    
    click.echo(f"Timer started for {project_display}{tasks_display}")
    click.echo(f"Session ID: {session_id}")

@cli.command()
def stop():
    """Stop current timer"""
    db = TimeTrackDB()
    
    # Check if there's an active session
    active_session = db.get_active_session()
    if not active_session:
        click.echo("No active timer session found")
        return
    
    # Stop the timer
    duration = db.stop_timer()
    
    if duration:
        project_display = f"{active_session['project']}:{active_session['sub_project']}" if active_session['sub_project'] else active_session['project']
        tasks_display = " [" + ", ".join(active_session['tasks']) + "]" if active_session['tasks'] else ""
        
        click.echo(f"Timer stopped for {project_display}{tasks_display}")
        click.echo(f"Duration: {format_duration(duration)}")
    else:
        click.echo("Failed to stop timer")

@cli.command()
def status():
    """Show current session and elapsed time"""
    db = TimeTrackDB()
    
    active_session = db.get_active_session()
    
    if not active_session:
        click.echo("No active timer session")
        return
    
    project_display = f"{active_session['project']}:{active_session['sub_project']}" if active_session['sub_project'] else active_session['project']
    tasks_display = " [" + ", ".join(active_session['tasks']) + "]" if active_session['tasks'] else ""
    
    click.echo(f"Active session: {project_display}{tasks_display}")
    click.echo(f"Started: {active_session['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo(f"Elapsed: {format_duration(active_session['elapsed'])}")
    click.echo(f"Directory: {active_session['directory']}")

@cli.command()
@click.argument('project_name')
def link(project_name):
    """Link current directory to a project name"""
    db = TimeTrackDB()
    current_dir = Path.cwd()
    
    # Save the manual mapping
    db.save_directory_mapping(
        directory_path=current_dir,
        project_name=project_name,
        auto_detected=False,
        detection_method='manual'
    )
    
    click.echo(f"Linked directory '{current_dir}' to project '{project_name}'")

@cli.command()
@click.option('--today', is_flag=True, help='Show today\'s entries')
@click.option('--week', is_flag=True, help='Show this week\'s entries')
@click.option('--month', is_flag=True, help='Show this month\'s entries')
@click.option('--from', 'from_date', help='Start date (YYYY-MM-DD)')
@click.option('--to', 'to_date', help='End date (YYYY-MM-DD)')
@click.option('--project', multiple=True, help='Filter by project(s)')
@click.option('--task', multiple=True, help='Filter by task/label(s)')
@click.option('--label', multiple=True, help='Alias for --task')
def report(today, week, month, from_date, to_date, project, task, label):
    """Generate time reports with flexible filtering"""
    click.echo("Report (placeholder)")

if __name__ == '__main__':
    cli()