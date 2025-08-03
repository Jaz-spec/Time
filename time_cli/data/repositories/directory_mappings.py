from typing import List, Optional
from pathlib import Path

from ..database import Database
from ..models import DirectoryMapping

class DirectoryMappingRepository:
    """Repository for directory mapping operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, directory_path: Path, project_name: str, 
               auto_detected: bool = True, detection_method: str = None) -> int:
        """Create a new directory mapping."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO directory_mappings 
                (directory_path, project_name, auto_detected, detection_method)
                VALUES (?, ?, ?, ?)
            ''', (str(directory_path), project_name, auto_detected, detection_method))
            conn.commit()
            return cursor.lastrowid
    
    def get_by_path(self, directory_path: Path) -> Optional[DirectoryMapping]:
        """Get directory mapping by path."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, directory_path, project_name, auto_detected, detection_method, created_at
                FROM directory_mappings
                WHERE directory_path = ?
            ''', (str(directory_path),))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_model(row)
        return None
    
    def list_all(self) -> List[DirectoryMapping]:
        """List all directory mappings."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, directory_path, project_name, auto_detected, detection_method, created_at
                FROM directory_mappings
                ORDER BY created_at DESC
            ''')
            rows = cursor.fetchall()
            
            return [self._row_to_model(row) for row in rows]
    
    def _row_to_model(self, row) -> DirectoryMapping:
        """Convert database row to DirectoryMapping model."""
        mapping_id, directory_path, project_name, auto_detected, detection_method, created_at = row
        
        return DirectoryMapping(
            id=mapping_id,
            directory_path=directory_path,
            project_name=project_name,
            auto_detected=bool(auto_detected),
            detection_method=detection_method,
            created_at=created_at
        )