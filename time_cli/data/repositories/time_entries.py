import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..database import Database
from ..models import TimeEntry

class TimeEntryRepository:
    """Repository for time entry operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, project: str, sub_project: Optional[str], tags: List[str], directory: str) -> int:
        """Create a new time entry and return its ID."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO time_entries (project, sub_project, tags, start_time, directory, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                project,
                sub_project,
                json.dumps(tags) if tags else None,
                datetime.now().isoformat(),
                directory,
                'active'
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_by_id(self, entry_id: int) -> Optional[TimeEntry]:
        """Get a time entry by ID."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, project, sub_project, tags, start_time, end_time, duration, directory, status, paused_duration FROM time_entries WHERE id = ?",
                (entry_id,),
            )
            row = cursor.fetchone()
            
            if row:
                return self._row_to_model(row)
        return None
    
    def get_active(self) -> Optional[TimeEntry]:
        """Get the currently active time entry."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, project, sub_project, tags, start_time, end_time, duration, directory, status, paused_duration
                FROM time_entries 
                WHERE end_time IS NULL AND status = 'active'
                ORDER BY start_time DESC 
                LIMIT 1
            ''')
            row = cursor.fetchone()
            
            if row:
                return self._row_to_model(row)
        return None
    
    def get_paused(self) -> Optional[TimeEntry]:
        """Get the currently paused time entry."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, project, sub_project, tags, start_time, end_time, duration, directory, status, paused_duration
                FROM time_entries 
                WHERE status = 'paused'
                ORDER BY start_time DESC 
                LIMIT 1
            ''')
            row = cursor.fetchone()
            
            if row:
                return self._row_to_model(row)
        return None
    
    def stop_active(self) -> Optional[int]:
        """Stop the active timer and return total duration in seconds."""
        active = self.get_active()
        if not active:
            return None
            
        end_time = datetime.now()
        # Calculate time since last start (or resume)
        current_session_duration = int((end_time - active.start_time).total_seconds())
        
        # Add any previous duration from before pauses (stored in duration field when paused)
        previous_duration = active.duration or 0
        total_duration = current_session_duration + previous_duration
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE time_entries 
                SET end_time = ?, duration = ?, status = 'completed'
                WHERE id = ?
            ''', (end_time.isoformat(), total_duration, active.id))
            conn.commit()
        
        return total_duration
    
    def pause_active(self) -> Optional[int]:
        """Pause the active timer and return elapsed duration in seconds."""
        active = self.get_active()
        if not active:
            return None
            
        pause_time = datetime.now()
        # Calculate time since last start (or resume)
        current_session_duration = int((pause_time - active.start_time).total_seconds())
        
        # Add to any previous duration from before pauses
        previous_duration = active.duration or 0
        total_elapsed = current_session_duration + previous_duration
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE time_entries 
                SET status = 'paused', duration = ? 
                WHERE id = ?
            ''', (total_elapsed, active.id))
            conn.commit()
        
        return total_elapsed
    
    def resume_paused(self) -> Optional[int]:
        """Resume the paused timer and return the entry ID."""
        paused = self.get_paused()
        if not paused:
            return None
        
        # Resume: reset start_time to now, keep accumulated duration, set status to active
        resume_time = datetime.now()
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE time_entries 
                SET status = 'active', start_time = ?
                WHERE id = ?
            ''', (resume_time.isoformat(), paused.id))
            conn.commit()
        
        return paused.id
    
    def update(self, entry_id: int, updates: Dict[str, Any]) -> bool:
        """Update a time entry with new values."""
        if not updates:
            return False

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            set_clauses = []
            params = []

            for key, value in updates.items():
                if key == "tags":
                    set_clauses.append("tags = ?")
                    params.append(json.dumps(value))
                else:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)

            if not set_clauses:
                return False

            query = f"UPDATE time_entries SET {', '.join(set_clauses)} WHERE id = ?"
            params.append(entry_id)

            cursor.execute(query, tuple(params))
            conn.commit()

            return cursor.rowcount > 0
    
    def find_with_filters(self, filters: Optional[Dict[str, Any]] = None) -> List[TimeEntry]:
        """Retrieve time entries with optional filtering."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT id, project, sub_project, tags, start_time, end_time, duration, directory, status, paused_duration
                FROM time_entries
                WHERE end_time IS NOT NULL
            '''
            params = []
            
            if filters:
                if filters.get('projects'):
                    project_placeholders = ','.join(['?' for _ in filters['projects']])
                    query += f' AND project IN ({project_placeholders})'
                    params.extend(filters['projects'])
                
                if filters.get('sub_projects'):
                    sub_project_placeholders = ','.join(['?' for _ in filters['sub_projects']])
                    query += f' AND sub_project IN ({sub_project_placeholders})'
                    params.extend(filters['sub_projects'])
                
                if filters.get('tags'):
                    for tag in filters['tags']:
                        query += ' AND (tags LIKE ? OR tags LIKE ? OR tags LIKE ?)'
                        params.extend([f'["{tag}"]', f'"{tag}",', f',"{tag}"'])
                
                if filters.get('from_date'):
                    query += ' AND DATE(start_time) >= ?'
                    params.append(filters['from_date'])
                
                if filters.get('to_date'):
                    query += ' AND DATE(start_time) <= ?'
                    params.append(filters['to_date'])
            
            query += ' ORDER BY start_time DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_model(row) for row in rows]
    
    def _row_to_model(self, row) -> TimeEntry:
        """Convert database row to TimeEntry model."""
        entry_id, project, sub_project, tags_json, start_time_str, end_time_str, duration, directory, status, paused_duration = row
        tags = json.loads(tags_json) if tags_json else []
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str) if end_time_str else None
        
        return TimeEntry(
            id=entry_id,
            project=project,
            sub_project=sub_project,
            tags=tags,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            directory=directory,
            status=status or 'active',
            paused_duration=paused_duration or 0
        )