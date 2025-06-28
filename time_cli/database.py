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
    
    def start_timer(self, project, tasks, directory):
        """Start a new timer session"""
        pass
    
    def stop_timer(self):
        """Stop current timer session"""
        pass
    
    def get_active_session(self):
        """Get currently active timer session"""
        pass
    
    def get_time_entries(self, filters=None):
        """Retrieve time entries with optional filtering"""
        pass