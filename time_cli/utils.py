import os
import json
from pathlib import Path
from subprocess import run, PIPE
from datetime import datetime, timedelta
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

def detect_project_from_directory(db=None):
    """Detect project name from current directory"""
    current_dir = Path.cwd()
    
    # Priority 1: Check stored directory mappings
    if db:
        mapping = db.get_directory_mapping(current_dir)
        if mapping:
            return mapping['project_name'], 'stored_mapping'
    
    # Priority 2: Check for .timetrack config file
    timetrack_config = current_dir / '.timetrack'
    if timetrack_config.exists():
        with open(timetrack_config, 'r') as f:
            config = json.load(f)
            project_name = config.get('project_name')
            if project_name:
                return project_name, 'config_file'
    
    # Priority 3: Check if git repository
    try:
        result = run(['git', 'rev-parse', '--show-toplevel'], 
                    capture_output=True, text=True, cwd=current_dir)
        if result.returncode == 0:
            git_root = Path(result.stdout.strip())
            return git_root.name, 'git_repo'
    except FileNotFoundError:
        pass
    
    # Priority 4: Fallback to directory name
    return current_dir.name, 'directory_name'

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def get_date_range(period_type):
    """Get date range for different period types"""
    today = datetime.now().date()
    
    if period_type == 'today':
        return today.isoformat(), today.isoformat()
    elif period_type == 'week':
        # Get start of current week (Monday)
        start_of_week = today - timedelta(days=today.weekday())
        return start_of_week.isoformat(), today.isoformat()
    elif period_type == 'month':
        # Get start of current month
        start_of_month = today.replace(day=1)
        return start_of_month.isoformat(), today.isoformat()
    
    return None, None

def generate_report_summary(entries):
    """Generate summary statistics from time entries"""
    if not entries:
        return {
            'total_entries': 0,
            'total_duration': 0,
            'projects': {},
            'daily_totals': {}
        }
    
    total_duration = sum(entry['duration'] or 0 for entry in entries)
    projects = defaultdict(lambda: {'duration': 0, 'entries': 0, 'sub_projects': defaultdict(int)})
    daily_totals = defaultdict(int)
    
    for entry in entries:
        project = entry['project']
        sub_project = entry['sub_project']
        duration = entry['duration'] or 0
        date_key = entry['start_time'].date().isoformat()
        
        # Project totals
        projects[project]['duration'] += duration
        projects[project]['entries'] += 1
        
        if sub_project:
            projects[project]['sub_projects'][sub_project] += duration
        
        # Daily totals
        daily_totals[date_key] += duration
    
    return {
        'total_entries': len(entries),
        'total_duration': total_duration,
        'projects': dict(projects),
        'daily_totals': dict(daily_totals)
    }

def format_report(entries, summary, show_details=True):
    """Format report output using Rich formatting"""
    console = Console()
    
    # Header
    console.print("\n[bold blue]Time Tracking Report[/bold blue]", style="bold")
    console.print("=" * 50, style="dim")
    
    # Summary
    console.print(f"\n[green]Total entries:[/green] {summary['total_entries']}")
    console.print(f"[green]Total time:[/green] [bold]{format_duration(summary['total_duration'])}[/bold]")
    
    # Project breakdown
    if summary['projects']:
        console.print("\n[bold cyan]Project Breakdown:[/bold cyan]")
        
        project_table = Table(box=box.SIMPLE_HEAD)
        project_table.add_column("Project", style="cyan", no_wrap=True)
        project_table.add_column("Duration", style="green", justify="right")
        project_table.add_column("Entries", style="yellow", justify="center")
        
        # Sort projects by duration (descending)
        sorted_projects = sorted(
            summary['projects'].items(),
            key=lambda x: x[1]['duration'],
            reverse=True
        )
        
        for project, data in sorted_projects:
            duration_str = format_duration(data['duration'])
            project_table.add_row(project, duration_str, str(data['entries']))
            
            # Sub-projects
            if data['sub_projects']:
                for sub_project, sub_duration in data['sub_projects'].items():
                    sub_duration_str = format_duration(sub_duration)
                    project_table.add_row(f"  └─ {sub_project}", sub_duration_str, "", style="dim")
        
        console.print(project_table)
    
    # Daily breakdown
    if summary['daily_totals'] and len(summary['daily_totals']) <= 31:
        console.print("\n[bold cyan]Daily Breakdown:[/bold cyan]")
        
        daily_table = Table(box=box.SIMPLE_HEAD)
        daily_table.add_column("Date", style="cyan")
        daily_table.add_column("Duration", style="green", justify="right")
        
        sorted_days = sorted(summary['daily_totals'].items())
        for date, duration in sorted_days:
            duration_str = format_duration(duration)
            daily_table.add_row(date, duration_str)
        
        console.print(daily_table)
    
    # Detailed entries (optional)
    if show_details and entries:
        console.print("\n[bold cyan]Detailed Entries:[/bold cyan]")
        
        entries_table = Table(box=box.SIMPLE_HEAD)
        entries_table.add_column("Date & Time", style="cyan")
        entries_table.add_column("Project", style="magenta")
        entries_table.add_column("Tags", style="yellow")
        entries_table.add_column("Duration", style="green", justify="right")
        
        for entry in entries:
            project_display = f"{entry['project']}:{entry['sub_project']}" if entry['sub_project'] else entry['project']
            tags_display = ', '.join(entry['tags']) if entry['tags'] else ""
            duration_str = format_duration(entry['duration'] or 0)
            date_str = entry['start_time'].strftime('%Y-%m-%d %H:%M')
            
            entries_table.add_row(date_str, project_display, tags_display, duration_str)
        
        console.print(entries_table)
    
    # Return empty string since Rich handles the output directly
    return ""