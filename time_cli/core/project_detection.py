import json
from pathlib import Path
from subprocess import run, PIPE
from typing import Tuple

from ..data.repositories.directory_mappings import DirectoryMappingRepository
from ..config.paths import Paths

def detect_project_from_directory(directory_repo: DirectoryMappingRepository) -> Tuple[str, str]:
    """Detect project name from current directory."""
    current_dir = Path.cwd()
    
    # Priority 1: Check stored directory mappings
    mapping = directory_repo.get_by_path(current_dir)
    if mapping:
        return mapping.project_name, 'stored_mapping'
    
    # Priority 2: Check for .timetrack config file
    timetrack_config = Paths.get_config_file_path()
    if timetrack_config.exists():
        try:
            with open(timetrack_config, 'r') as f:
                config = json.load(f)
                project_name = config.get('project_name')
                if project_name:
                    return project_name, 'config_file'
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
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