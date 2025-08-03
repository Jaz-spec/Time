from typing import Dict, Any, Optional, List
from collections import defaultdict

from ..data.models import TimeEntry, ReportSummary
from ..utils.date_utils import get_date_range

class FilterService:
    """Service for filtering and aggregating time entries."""
    
    @staticmethod
    def build_filters(today: bool = False, week: bool = False, month: bool = False,
                     from_date: Optional[str] = None, to_date: Optional[str] = None,
                     projects: Optional[List[str]] = None, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Build filters dictionary from command options."""
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
        if projects:
            filters['projects'] = projects
        
        # Tag filtering
        if tags:
            filters['tags'] = tags
        
        return filters
    
    @staticmethod
    def generate_summary(entries: List[TimeEntry]) -> ReportSummary:
        """Generate summary statistics from time entries."""
        if not entries:
            return ReportSummary(
                total_entries=0,
                total_duration=0,
                projects={},
                daily_totals={}
            )
        
        total_duration = sum(entry.duration or 0 for entry in entries)
        projects = defaultdict(lambda: {'duration': 0, 'entries': 0, 'sub_projects': defaultdict(int)})
        daily_totals = defaultdict(int)
        
        for entry in entries:
            project = entry.project
            sub_project = entry.sub_project
            duration = entry.duration or 0
            date_key = entry.start_time.date().isoformat()
            
            # Project totals
            projects[project]['duration'] += duration
            projects[project]['entries'] += 1
            
            if sub_project:
                projects[project]['sub_projects'][sub_project] += duration
            
            # Daily totals
            daily_totals[date_key] += duration
        
        return ReportSummary(
            total_entries=len(entries),
            total_duration=total_duration,
            projects=dict(projects),
            daily_totals=dict(daily_totals)
        )