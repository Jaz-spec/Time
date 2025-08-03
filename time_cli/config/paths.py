from pathlib import Path

class Paths:
    """Centralized path management for the application."""
    
    @staticmethod
    def get_app_dir() -> Path:
        """Get the application directory (~/.timetrack)."""
        app_dir = Path.home() / '.timetrack'
        app_dir.mkdir(exist_ok=True)
        return app_dir
    
    @staticmethod
    def get_db_path() -> Path:
        """Get the database file path."""
        return Paths.get_app_dir() / 'timetrack.db'
    
    @staticmethod
    def get_config_file_path() -> Path:
        """Get the path for .timetrack config file in current directory."""
        return Path.cwd() / '.timetrack'