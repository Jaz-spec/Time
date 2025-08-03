import re
from typing import List

from ..config.settings import Settings

def validate_project_name(project_name: str) -> bool:
    """Validate project name length and format."""
    if not project_name or not project_name.strip():
        return False
    return len(project_name.strip()) <= Settings.MAX_PROJECT_NAME_LENGTH

def validate_tags(tags: List[str]) -> bool:
    """Validate tag list."""
    if not tags:
        return True
    
    for tag in tags:
        if not tag or not tag.strip():
            return False
        if len(tag.strip()) > Settings.MAX_TAG_LENGTH:
            return False
    
    return True

def sanitize_project_name(project_name: str) -> str:
    """Sanitize project name by trimming whitespace."""
    return project_name.strip()

def sanitize_tags(tags: List[str]) -> List[str]:
    """Sanitize tag list by trimming and filtering empty tags."""
    return [tag.strip() for tag in tags if tag and tag.strip()]