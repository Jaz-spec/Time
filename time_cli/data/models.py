from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class TimeEntry:
    """Represents a time tracking entry."""
    id: Optional[int]
    project: str
    sub_project: Optional[str]
    tags: List[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[int]  # seconds
    directory: str
    created_at: Optional[datetime] = None
    
    @property
    def is_active(self) -> bool:
        """Check if this entry is currently active (no end time)."""
        return self.end_time is None
    
    @property
    def project_display(self) -> str:
        """Get formatted project display string."""
        if self.sub_project:
            return f"{self.project}:{self.sub_project}"
        return self.project

@dataclass
class DirectoryMapping:
    """Represents a directory-to-project mapping."""
    id: Optional[int]
    directory_path: str
    project_name: str
    auto_detected: bool
    detection_method: str
    created_at: Optional[datetime] = None

@dataclass
class ReportSummary:
    """Summary statistics for time reports."""
    total_entries: int
    total_duration: int
    projects: dict
    daily_totals: dict