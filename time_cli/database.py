import sqlite3
import json
from pathlib import Path
from datetime import datetime

class TimeTrackDB:
    def __init__(self):
        self.db_dir = Path.home() / '.timetrack'
        self.db_dir.mkdir(exist_ok=True)
        self.db_path = self.db_dir / 'timetrack.db'
        self.init_db()
    
    def init_db(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            # Time entries table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS time_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project TEXT NOT NULL,
                    sub_project TEXT,
                    tasks TEXT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    duration INTEGER,
                    directory TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Directory mappings table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS directory_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    directory_path TEXT UNIQUE NOT NULL,
                    project_name TEXT NOT NULL,
                    auto_detected BOOLEAN DEFAULT TRUE,
                    detection_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def start_timer(self, project, sub_project, tasks, directory):
        """Start a new timer session"""
        # Stop any existing active session
        self.stop_timer()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO time_entries (project, sub_project, tasks, start_time, directory)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                project,
                sub_project,
                json.dumps(tasks) if tasks else None,
                datetime.now().isoformat(),
                directory
            ))
            conn.commit()
            return cursor.lastrowid
    
    def stop_timer(self):
        """Stop current timer session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Get active session
            cursor.execute('''
                SELECT id, start_time FROM time_entries 
                WHERE end_time IS NULL 
                ORDER BY start_time DESC 
                LIMIT 1
            ''')
            active_session = cursor.fetchone()
            
            if active_session:
                session_id, start_time_str = active_session
                start_time = datetime.fromisoformat(start_time_str)
                end_time = datetime.now()
                duration = int((end_time - start_time).total_seconds())
                
                cursor.execute('''
                    UPDATE time_entries 
                    SET end_time = ?, duration = ? 
                    WHERE id = ?
                ''', (end_time.isoformat(), duration, session_id))
                conn.commit()
                return duration
            return None
    
    def get_active_session(self):
        """Get currently active timer session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, project, sub_project, tasks, start_time, directory
                FROM time_entries 
                WHERE end_time IS NULL 
                ORDER BY start_time DESC 
                LIMIT 1
            ''')
            row = cursor.fetchone()
            
            if row:
                session_id, project, sub_project, tasks_json, start_time_str, directory = row
                tasks = json.loads(tasks_json) if tasks_json else []
                start_time = datetime.fromisoformat(start_time_str)
                elapsed = int((datetime.now() - start_time).total_seconds())
                
                return {
                    'id': session_id,
                    'project': project,
                    'sub_project': sub_project,
                    'tasks': tasks,
                    'start_time': start_time,
                    'elapsed': elapsed,
                    'directory': directory
                }
            return None
    
    def get_time_entries(self, filters=None):
        """Retrieve time entries with optional filtering"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT id, project, sub_project, tasks, start_time, end_time, duration, directory
                FROM time_entries
                WHERE 1=1
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
                
                if filters.get('from_date'):
                    query += ' AND start_time >= ?'
                    params.append(filters['from_date'])
                
                if filters.get('to_date'):
                    query += ' AND start_time <= ?'
                    params.append(filters['to_date'])
            
            query += ' ORDER BY start_time DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            entries = []
            for row in rows:
                entry_id, project, sub_project, tasks_json, start_time_str, end_time_str, duration, directory = row
                tasks = json.loads(tasks_json) if tasks_json else []
                start_time = datetime.fromisoformat(start_time_str)
                end_time = datetime.fromisoformat(end_time_str) if end_time_str else None
                
                entries.append({
                    'id': entry_id,
                    'project': project,
                    'sub_project': sub_project,
                    'tasks': tasks,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': duration,
                    'directory': directory
                })
            
            return entries
    
    def save_directory_mapping(self, directory_path, project_name, auto_detected=True, detection_method=None):
        """Save directory to project mapping"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO directory_mappings 
                (directory_path, project_name, auto_detected, detection_method)
                VALUES (?, ?, ?, ?)
            ''', (str(directory_path), project_name, auto_detected, detection_method))
            conn.commit()
            return cursor.lastrowid
    
    def get_directory_mapping(self, directory_path):
        """Get project mapping for a directory"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT project_name, auto_detected, detection_method
                FROM directory_mappings
                WHERE directory_path = ?
            ''', (str(directory_path),))
            row = cursor.fetchone()
            
            if row:
                project_name, auto_detected, detection_method = row
                return {
                    'project_name': project_name,
                    'auto_detected': bool(auto_detected),
                    'detection_method': detection_method
                }
            return None
    
    def list_directory_mappings(self):
        """List all directory mappings"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT directory_path, project_name, auto_detected, detection_method, created_at
                FROM directory_mappings
                ORDER BY created_at DESC
            ''')
            rows = cursor.fetchall()
            
            mappings = []
            for row in rows:
                directory_path, project_name, auto_detected, detection_method, created_at = row
                mappings.append({
                    'directory_path': directory_path,
                    'project_name': project_name,
                    'auto_detected': bool(auto_detected),
                    'detection_method': detection_method,
                    'created_at': created_at
                })
            
            return mappings