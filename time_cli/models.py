from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class TimeEntry:
    id: Optional[int]
    project: str
    tasks: List[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[int]
    directory: str
    created_at: datetime

@dataclass
class DirectoryMapping:
    directory_path: str
    project_name: str
    auto_detected: bool
    detection_method: str