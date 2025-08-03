from rich.text import Text
from rich.panel import Panel
from typing import List

from ..data.models import TimeEntry
from ..core.duration import format_duration

class Formatters:
    """Rich formatting utilities for UI components."""
    
    @staticmethod
    def format_timer_started(session_id: int, project: str, sub_project: str = None, tags: List[str] = None) -> Panel:
        """Format timer started message."""
        project_display = f"{project}:{sub_project}" if sub_project else project
        tags_display = ", ".join(tags) if tags else "No tags"
        
        start_text = Text()
        start_text.append("▶️  Timer started for ", style="green")
        start_text.append(f"{project_display}\n", style="bold magenta")
        start_text.append("Tags: ", style="cyan")
        start_text.append(f"{tags_display}\n", style="yellow")
        start_text.append("Session ID: ", style="cyan")
        start_text.append(f"{session_id}", style="dim")
        
        return Panel(start_text, title="Timer Started", border_style="green")
    
    @staticmethod
    def format_timer_stopped(entry: TimeEntry, duration: int) -> Panel:
        """Format timer stopped message."""
        project_display = entry.project_display
        tags_display = ", ".join(entry.tags) if entry.tags else "No tags"
        
        stop_text = Text()
        stop_text.append("⏹️  Timer stopped for ", style="red")
        stop_text.append(f"{project_display}\n", style="bold magenta")
        stop_text.append("Tags: ", style="cyan")
        stop_text.append(f"{tags_display}\n", style="yellow")
        stop_text.append("Duration: ", style="cyan")
        stop_text.append(f"{format_duration(duration)}", style="bold green")
        
        return Panel(stop_text, title="Timer Stopped", border_style="red")
    
    @staticmethod
    def format_active_session(entry: TimeEntry) -> Panel:
        """Format active session status."""
        project_display = entry.project_display
        tags_display = ", ".join(entry.tags) if entry.tags else "No tags"
        
        status_text = Text()
        status_text.append("Project: ", style="cyan")
        status_text.append(f"{project_display}\n", style="bold magenta")
        status_text.append("Tags: ", style="cyan")
        status_text.append(f"{tags_display}\n", style="yellow")
        status_text.append("Started: ", style="cyan")
        status_text.append(f"{entry.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n", style="white")
        status_text.append("Elapsed: ", style="cyan")
        status_text.append(f"{format_duration(entry.duration)}\n", style="bold green")
        status_text.append("Directory: ", style="cyan")
        status_text.append(f"{entry.directory}", style="dim")
        
        return Panel(status_text, title="⏱️  Active Timer Session", border_style="green")
    
    @staticmethod
    def format_directory_linked(directory: str, project_name: str) -> Panel:
        """Format directory linked message."""
        link_text = Text()
        link_text.append("🔗 Linked directory\n", style="green")
        link_text.append(f"'{directory}'\n", style="cyan")
        link_text.append("to project\n", style="white")
        link_text.append(f"'{project_name}'", style="bold magenta")
        
        return Panel(link_text, title="Directory Linked", border_style="green")
    
    @staticmethod
    def format_entry_details(entry: TimeEntry) -> Panel:
        """Format entry details for editing."""
        return Panel(
            f"[cyan]Editing Entry ID:[/cyan] [bold]{entry.id}[/bold]\n"
            f"[cyan]Project:[/cyan] {entry.project}\n"
            f"[cyan]Sub-project:[/cyan] {entry.sub_project or 'N/A'}\n"
            f"[cyan]Tags:[/cyan] {', '.join(entry.tags) if entry.tags else 'N/A'}",
            title="Current Entry Details",
            border_style="yellow"
        )
    
    @staticmethod
    def format_error(message: str) -> str:
        """Format error message."""
        return f"[red]Error: {message}[/red]"
    
    @staticmethod
    def format_success(message: str) -> str:
        """Format success message."""
        return f"[green]{message}[/green]"
    
    @staticmethod
    def format_warning(message: str) -> Panel:
        """Format warning message."""
        return Panel(f"[yellow]{message}[/yellow]", border_style="yellow")