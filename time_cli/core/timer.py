from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from ..data.repositories.time_entries import TimeEntryRepository
from ..data.repositories.directory_mappings import DirectoryMappingRepository
from ..data.models import TimeEntry
from ..config.settings import Settings
from .project_detection import detect_project_from_directory
from .duration import parse_duration_input
from ..utils.validation import sanitize_project_name, sanitize_tags

class TimerService:
    """Service for managing timer operations."""
    
    def __init__(self, time_repo: TimeEntryRepository, directory_repo: DirectoryMappingRepository):
        self.time_repo = time_repo
        self.directory_repo = directory_repo
    
    def start_timer(self, project: Optional[str] = None, sub_project: Optional[str] = None, 
                   tags: Optional[List[str]] = None) -> int:
        """Start a new timer session."""
        # Stop any existing active session
        self.stop_timer()
        
        # Prepare tags with default
        if tags is None:
            tags = []
        tags = sanitize_tags(tags)
        
        # Add default work tag if not explicitly overridden
        if Settings.OUT_WORK_TAG not in tags:
            tags.append(Settings.DEFAULT_WORK_TAG)
        
        # Auto-detect project if not specified
        if not project:
            project, detection_method = detect_project_from_directory(self.directory_repo)
            
            # Save auto-detected mapping if it's not already stored
            if detection_method != 'stored_mapping':
                self.directory_repo.create(
                    directory_path=Path.cwd(),
                    project_name=project,
                    auto_detected=True,
                    detection_method=detection_method
                )
        else:
            project = sanitize_project_name(project)
        
        # Create the timer entry
        return self.time_repo.create(
            project=project,
            sub_project=sub_project,
            tags=tags,
            directory=str(Path.cwd())
        )
    
    def stop_timer(self) -> Optional[int]:
        """Stop current timer session and return duration."""
        return self.time_repo.stop_active()
    
    def pause_timer(self) -> Optional[int]:
        """Pause current timer session and return elapsed duration."""
        return self.time_repo.pause_active()
    
    def resume_timer(self) -> Optional[int]:
        """Resume paused timer session and return entry ID."""
        return self.time_repo.resume_paused()
    
    def get_paused_session(self) -> Optional[TimeEntry]:
        """Get currently paused timer session."""
        return self.time_repo.get_paused()
    
    def get_active_session(self) -> Optional[TimeEntry]:
        """Get currently active timer session with elapsed time."""
        entry = self.time_repo.get_active()
        if not entry:
            return None
        
        # Calculate elapsed time for active sessions
        elapsed = int((datetime.now() - entry.start_time).total_seconds())
        entry.duration = elapsed
        
        return entry
    
    def edit_entry_duration(self, entry_id: int, new_duration_str: str) -> bool:
        """Edit the duration of a time entry."""
        entry = self.time_repo.get_by_id(entry_id)
        if not entry:
            return False
        
        try:
            new_duration = parse_duration_input(new_duration_str)
            # Calculate new end_time based on start_time and new duration
            new_end_time = entry.start_time + timedelta(seconds=new_duration)
            
            updates = {
                'duration': new_duration,
                'end_time': new_end_time.isoformat()
            }
            
            return self.time_repo.update(entry_id, updates)
        except ValueError:
            return False
    
    def link_directory(self, project_name: str) -> bool:
        """Link current directory to a project name."""
        try:
            project_name = sanitize_project_name(project_name)
            self.directory_repo.create(
                directory_path=Path.cwd(),
                project_name=project_name,
                auto_detected=False,
                detection_method='manual'
            )
            return True
        except Exception:
            return False