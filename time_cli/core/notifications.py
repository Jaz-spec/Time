import platform
import subprocess
from typing import Optional

class NotificationService:
    """Cross-platform notification service."""
    
    def __init__(self):
        self.system = platform.system().lower()
    
    def send_alert(self, title: str, message: str, duration_str: str):
        """Send a cross-platform notification alert."""
        full_message = f"{message}\nDuration: {duration_str}"
        
        try:
            if self.system == "darwin":  # macOS
                self._send_macos_notification(title, full_message)
            elif self.system == "linux":
                self._send_linux_notification(title, full_message)
            elif self.system == "windows":
                self._send_windows_notification(title, full_message)
            else:
                # Fallback: print to console (for development/testing)
                print(f"ALERT: {title}")
                print(f"Message: {full_message}")
        
        except Exception as e:
            # Fallback to console output on error
            print(f"ALERT: {title}")
            print(f"Message: {full_message}")
            print(f"Notification error: {e}")
    
    def _send_macos_notification(self, title: str, message: str):
        """Send notification on macOS using AppleScript."""
        apple_script = f'''
        display notification "{message}" \\
        with title "{title}" \\
        sound name "default"
        '''
        
        subprocess.run([
            "osascript", "-e", apple_script
        ], check=True, capture_output=True)
    
    def _send_linux_notification(self, title: str, message: str):
        """Send notification on Linux using notify-send."""
        subprocess.run([
            "notify-send",
            "--urgency=normal",
            "--app-name=Time Tracker",
            "--icon=clock",
            title,
            message
        ], check=True, capture_output=True)
    
    def _send_windows_notification(self, title: str, message: str):
        """Send notification on Windows using PowerShell."""
        ps_script = f'''
        [reflection.assembly]::loadwithpartialname("System.Windows.Forms")
        [reflection.assembly]::loadwithpartialname("System.Drawing")
        $notify = new-object system.windows.forms.notifyicon
        $notify.icon = [System.Drawing.SystemIcons]::Information
        $notify.visible = $true
        $notify.showballoontip(10,"{title}","{message}",[system.windows.forms.tooltipicon]::Info)
        '''
        
        subprocess.run([
            "powershell", "-Command", ps_script
        ], check=True, capture_output=True)
    
    def test_notification(self):
        """Send a test notification to verify the system works."""
        self.send_alert(
            title="Time Tracker Test",
            message="Notification system is working!",
            duration_str="Test"
        )