"""Application settings and defaults."""

class Settings:
    """Application-wide settings and defaults."""

    # Default tags
    DEFAULT_WORK_TAG = "in-work"
    OUT_WORK_TAG = "out-work"

    # Database settings
    DB_TIMEOUT = 30.0  # seconds

    # UI settings
    MAX_PROJECT_NAME_LENGTH = 50
    MAX_TAG_LENGTH = 30

    # Report settings
    MAX_DAILY_ENTRIES_FOR_BREAKDOWN = 31

    # Duration formats
    SUPPORTED_DURATION_FORMATS = [
        "1h30m (hours and minutes)",
        "90m (minutes only)",
        "5400s (seconds only)",
        "5400 (plain number as seconds)"
    ]
