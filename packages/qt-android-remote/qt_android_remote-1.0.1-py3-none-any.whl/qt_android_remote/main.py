#!/usr/bin/env python3
"""
QT Android Remote Control

Main entry point for the QT Android Remote Control application.
A desktop application for controlling Android TV devices using direct connection.
"""

import sys
import signal
import atexit
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon

from .remote_window import RemoteWindow
from . import __version__


def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("QT Android Remote Control")
    app.setApplicationDisplayName("QT Android Remote Control")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("David Markey")
    app.setOrganizationDomain("dmarkey.com")
    
    # Set application icon if available
    try:
        # Try to find the logo in various locations
        possible_icon_paths = [
            Path(__file__).parent / "logo.png",  # Package directory (preferred)
            Path(__file__).parent.parent / "images" / "logo.png",  # Development directory
            Path("images") / "logo.png",
            Path("logo.png")
        ]
        
        for icon_path in possible_icon_paths:
            if icon_path.exists():
                app.setWindowIcon(QIcon(str(icon_path)))
                break
    except Exception:
        pass  # Continue without icon if not found
    
    # Enable automatic detection of system theme changes
    app.setStyle('Fusion')  # Use Fusion style which respects system themes better
    
    # Set application to follow system color scheme
    app.setStyleSheet("")  # Clear any default styling to use system theme

    # Create the main window
    window = RemoteWindow()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        window.disconnect_from_remote()
        app.quit()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Register cleanup function to run on exit
    def cleanup_on_exit():
        """Cleanup function to run when the application exits"""
        if window:
            window.disconnect_from_remote()
    
    atexit.register(cleanup_on_exit)

    # Create a QTimer to periodically process Python signals
    # This is crucial for Ctrl+C to work in a Qt application
    timer = QTimer()
    timer.start(500) # Check every 500ms
    timer.timeout.connect(lambda: None) # Dummy function to keep the event loop alive

    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())