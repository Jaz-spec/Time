import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from ..config.paths import Paths
from ..config.settings import Settings

class Database:
    """Database connection and initialization."""
    
    def __init__(self):
        self.db_path = Paths.get_db_path()
        self.init_db()
    
    def init_db(self):
        """Initialize database with required tables."""
        with self.get_connection() as conn:
            # Time entries table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS time_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project TEXT NOT NULL,
                    sub_project TEXT,
                    tags TEXT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    duration INTEGER,
                    directory TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    paused_duration INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Add status and paused_duration columns if they don't exist (for existing databases)
            try:
                conn.execute('ALTER TABLE time_entries ADD COLUMN status TEXT DEFAULT "active"')
                conn.execute('ALTER TABLE time_entries ADD COLUMN paused_duration INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                # Columns already exist
                pass
            
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
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        conn = sqlite3.connect(self.db_path, timeout=Settings.DB_TIMEOUT)
        try:
            yield conn
        finally:
            conn.close()