from datetime import datetime, timedelta
from typing import Tuple

def get_date_range(period_type: str) -> Tuple[str, str]:
    """Get date range for different period types."""
    today = datetime.now().date()
    
    if period_type == 'today':
        return today.isoformat(), today.isoformat()
    elif period_type == 'week':
        # Get start of current week (Monday)
        start_of_week = today - timedelta(days=today.weekday())
        return start_of_week.isoformat(), today.isoformat()
    elif period_type == 'month':
        # Get start of current month
        start_of_month = today.replace(day=1)
        return start_of_month.isoformat(), today.isoformat()
    
    return None, None