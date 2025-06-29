import os
import json
from pathlib import Path
from subprocess import run, PIPE

def detect_project_from_directory(db=None):
    """Detect project name from current directory"""
    current_dir = Path.cwd()
    
    # Priority 1: Check stored directory mappings
    if db:
        mapping = db.get_directory_mapping(current_dir)
        if mapping:
            return mapping['project_name'], 'stored_mapping'
    
    # Priority 2: Check for .timetrack config file
    timetrack_config = current_dir / '.timetrack'
    if timetrack_config.exists():
        with open(timetrack_config, 'r') as f:
            config = json.load(f)
            project_name = config.get('project_name')
            if project_name:
                return project_name, 'config_file'
    
    # Priority 3: Check if git repository
    try:
        result = run(['git', 'rev-parse', '--show-toplevel'], 
                    capture_output=True, text=True, cwd=current_dir)
        if result.returncode == 0:
            git_root = Path(result.stdout.strip())
            return git_root.name, 'git_repo'
    except FileNotFoundError:
        pass
    
    # Priority 4: Fallback to directory name
    return current_dir.name, 'directory_name'

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"