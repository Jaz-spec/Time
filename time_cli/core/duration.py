import re

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format."""
    if seconds is None:
        return "N/A"
        
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def parse_duration_input(duration_str: str) -> int:
    """Parse duration input in various formats (1h30m, 90m, 5400s) to seconds."""
    duration_str = duration_str.strip().lower()
    
    if not duration_str:
        raise ValueError("Duration cannot be empty")
    
    total_seconds = 0
    
    # Handle pure seconds (e.g., "5400" or "5400s")
    if duration_str.isdigit():
        return int(duration_str)
    
    # Handle formats with units (e.g., "1h30m", "90m", "30s")
    
    # Extract hours
    hours_match = re.search(r'(\d+)h', duration_str)
    if hours_match:
        total_seconds += int(hours_match.group(1)) * 3600
    
    # Extract minutes
    minutes_match = re.search(r'(\d+)m', duration_str)
    if minutes_match:
        total_seconds += int(minutes_match.group(1)) * 60
    
    # Extract seconds
    seconds_match = re.search(r'(\d+)s', duration_str)
    if seconds_match:
        total_seconds += int(seconds_match.group(1))
    
    if total_seconds == 0:
        raise ValueError("Invalid duration format. Use formats like: 1h30m, 90m, 5400s, or 5400")
    
    return total_seconds