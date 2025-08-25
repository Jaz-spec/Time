import os
import sys
import time
import signal
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ...core.notifications import NotificationService
from ...data.database import Database
from ...data.repositories.time_entries import TimeEntryRepository
from ...config.paths import Paths

class AlertDaemon:
    """Background daemon that monitors active timers and sends alerts."""
    
    def __init__(self, entry_id: int, expected_duration: int):
        self.entry_id = entry_id
        self.expected_duration = expected_duration  # in seconds
        self.notification_service = NotificationService()
        self.pid_file = Paths.get_alert_pid_file(entry_id)
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.running = False
    
    def start_daemon(self):
        """Start the daemon process in the background."""
        # Fork to background
        if os.fork() > 0:
            return  # Parent process returns
        
        # Child process continues
        os.setsid()  # Create new session
        
        # Fork again to ensure we're not session leader
        if os.fork() > 0:
            sys.exit(0)
        
        # Redirect standard file descriptors
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()
        
        # Write PID file
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Start monitoring
        self._monitor_timer()
    
    def _monitor_timer(self):
        """Monitor the timer and send alert when expected duration is reached."""
        start_time = datetime.now()
        alert_sent = False
        
        while self.running:
            try:
                # Check if timer is still active
                db = Database()
                repo = TimeEntryRepository(db)
                entry = repo.get_by_id(self.entry_id)
                
                if not entry or not entry.is_active:
                    # Timer stopped, exit daemon
                    break
                
                # Calculate elapsed time
                current_time = datetime.now()
                elapsed_seconds = int((current_time - entry.start_time).total_seconds())
                
                # Check if expected duration reached and alert not sent
                if elapsed_seconds >= self.expected_duration and not alert_sent:
                    self.notification_service.send_alert(
                        title="Time Tracker Alert",
                        message=f"Expected time reached for {entry.project_display}",
                        duration_str=self._format_duration(self.expected_duration)
                    )
                    alert_sent = True
                
                # Sleep for 30 seconds before next check
                time.sleep(30)
                
            except Exception as e:
                # Log error and continue (in production, use proper logging)
                time.sleep(60)  # Wait longer on error
        
        # Clean up
        self._cleanup()
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to human readable format."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _cleanup(self):
        """Clean up daemon resources."""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
        except:
            pass
    
    @classmethod
    def stop_daemon(cls, entry_id: int):
        """Stop the daemon for a specific entry."""
        pid_file = Paths.get_alert_pid_file(entry_id)
        
        if not pid_file.exists():
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to terminate
            for _ in range(10):  # Wait up to 10 seconds
                try:
                    os.kill(pid, 0)  # Check if process exists
                    time.sleep(1)
                except OSError:
                    break  # Process terminated
            
            # Force kill if still running
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
            
            # Remove PID file
            try:
                pid_file.unlink()
            except:
                pass
            
            return True
            
        except (ValueError, OSError):
            # Clean up stale PID file
            try:
                pid_file.unlink()
            except:
                pass
            return False

def start_alert_daemon(entry_id: int, expected_duration: int):
    """Start an alert daemon for the given entry."""
    daemon = AlertDaemon(entry_id, expected_duration)
    daemon.start_daemon()

def stop_alert_daemon(entry_id: int):
    """Stop the alert daemon for the given entry."""
    return AlertDaemon.stop_daemon(entry_id)