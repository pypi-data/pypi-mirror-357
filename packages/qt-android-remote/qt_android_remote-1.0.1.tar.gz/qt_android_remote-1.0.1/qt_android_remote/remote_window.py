"""
Remote Window for QT Android Remote Control

Main window interface for the QT Android Remote Control application.
"""

import sys
import logging
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QGridLayout,
                               QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox, QMessageBox, QLineEdit)
from PySide6.QtGui import QKeyEvent, QIcon
from PySide6.QtCore import Qt, QTimer

from .remote_manager import load_remotes, save_remotes
from .remote_wizard import RemoteWizard
from .android_tv_connection import AndroidTVConnectionThread
from . import __version__

_LOGGER = logging.getLogger(__name__)


class RemoteWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"QT Android Remote Control v{__version__}")
        self.setFixedSize(350, 600)  # Increased width and height for dropdown
        
        # Set window icon if available
        try:
            icon_path = "images/logo.png"
            if not QIcon(icon_path).isNull():
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass  # Icon not found, continue without it
        
        # Load remotes and initialize connection variables
        self.remotes = load_remotes()
        self.current_remote: Optional[Dict[str, Any]] = None
        self.connection_thread: Optional[AndroidTVConnectionThread] = None
        
        # Dictionary to store button references for visual feedback
        self.command_buttons = {}
        
        # Initialize feedback state
        self._showing_feedback = False
        
        # Track held keys for long press functionality
        self._held_keys = set()
        self._key_timers = {}
        self._long_press_threshold = 300  # milliseconds
        
        self.init_ui()
        self.apply_styles()
        # Enable keyboard focus so the widget can receive key events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # Ensure the window gets focus when shown
        self.setFocus()
        
        # Install event filter to ensure keyboard events always reach the main window
        self.installEventFilter(self)

    def closeEvent(self, event):
        """Handle application close event"""
        # Properly disconnect from remote before closing
        self.disconnect_from_remote()
        super().closeEvent(event)

    def showEvent(self, event):
        """Override showEvent to ensure keyboard focus when window is shown"""
        super().showEvent(event)
        # Use a timer to ensure focus is set after the window is fully shown
        QTimer.singleShot(100, self.ensure_keyboard_focus)

    def changeEvent(self, event):
        """Override changeEvent to handle window activation"""
        super().changeEvent(event)
        if event.type() == event.Type.ActivationChange and self.isActiveWindow():
            self.ensure_keyboard_focus()

    def send_remote_command(self, command):
        """Send command to Android TV"""
        if self.connection_thread and self.connection_thread.isRunning():
            self.connection_thread.send_key_command(command)
            print(f"Sent: {command}")
        else:
            print(f"Not connected - cannot send: {command}")

    def send_remote_command_with_direction(self, command, direction="SHORT"):
        """Send command to Android TV with specific direction (SHORT, START_LONG, END_LONG)"""
        if self.connection_thread and self.connection_thread.isRunning():
            self.connection_thread.send_key_command_with_direction(command, direction)
            print(f"Sent: {command} ({direction})")
        else:
            print(f"Not connected - cannot send: {command} ({direction})")

    def send_command_and_refocus(self, command):
        """Send command and return focus to main window for keyboard input"""
        self.send_remote_command(command)
        self.ensure_keyboard_focus()

    def ensure_keyboard_focus(self):
        """Ensure the main window has keyboard focus for remote control"""
        self.setFocus()
        self.activateWindow()
        self.raise_()

    def animate_button_press(self, button):
        """Add visual feedback when button is pressed"""
        # Prevent multiple animations on the same button
        if hasattr(button, '_animating') and button._animating:
            return
            
        button._animating = True
        original_style = button.styleSheet()
        
        # Get button class for appropriate feedback color
        button_class = button.property("class")
        feedback_color = "#66BB6A"  # Default green
        
        # Use different colors based on button type for better visual distinction
        if button_class == "power":
            feedback_color = "#FF5722"  # Bright orange for power
        elif button_class == "dpad" or button_class == "dpad-center":
            feedback_color = "#2196F3"  # Bright blue for navigation
        elif button_class == "volume":
            feedback_color = "#FF9800"  # Orange for volume
        elif button_class == "media":
            feedback_color = "#9C27B0"  # Purple for media
        elif button_class == "app":
            feedback_color = "#E91E63"  # Pink for apps
        elif button_class == "youtube":
            feedback_color = "#66BB6A"  # Bright green for YouTube
        
        # Change button appearance temporarily - no layout-affecting properties
        button.setStyleSheet(original_style + f"""
            QPushButton {{
                background-color: {feedback_color};
                border-color: {feedback_color};
            }}
        """)
        
        # Reset after 150ms and clear animation flag
        def reset_button():
            button.setStyleSheet(original_style)
            button._animating = False
            
        QTimer.singleShot(150, reset_button)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input for remote control"""
        key = event.key()
        
        # Prevent auto-repeat for held keys
        if event.isAutoRepeat():
            return
        
        # Extended key mappings including Android TV specific keys
        key_mappings = {
            # D-Pad navigation
            int(Qt.Key.Key_Up): "DPAD_UP",
            int(Qt.Key.Key_Down): "DPAD_DOWN",
            int(Qt.Key.Key_Left): "DPAD_LEFT",
            int(Qt.Key.Key_Right): "DPAD_RIGHT",
            int(Qt.Key.Key_Return): "DPAD_CENTER",
            int(Qt.Key.Key_Enter): "DPAD_CENTER",
            int(Qt.Key.Key_Space): "DPAD_CENTER",
            
            # Navigation
            int(Qt.Key.Key_Backspace): "BACK",
            int(Qt.Key.Key_Escape): "BACK",
            int(Qt.Key.Key_Home): "HOME",
            int(Qt.Key.Key_M): "MENU",
            int(Qt.Key.Key_P): "POWER",
            
            # Volume controls
            int(Qt.Key.Key_Plus): "VOLUME_UP",
            int(Qt.Key.Key_Minus): "VOLUME_DOWN",
            int(Qt.Key.Key_Equal): "VOLUME_UP",  # For + without shift
            int(Qt.Key.Key_Underscore): "VOLUME_DOWN",  # For -
            int(Qt.Key.Key_0): "MUTE",
            
            # Media controls
            int(Qt.Key.Key_MediaPlay): "MEDIA_PLAY_PAUSE",
            int(Qt.Key.Key_MediaPause): "MEDIA_PLAY_PAUSE",
            int(Qt.Key.Key_MediaStop): "MEDIA_STOP",
            int(Qt.Key.Key_MediaNext): "MEDIA_NEXT",
            int(Qt.Key.Key_MediaPrevious): "MEDIA_PREVIOUS",
            int(Qt.Key.Key_MediaRecord): "MEDIA_RECORD",
            
            # Number keys
            int(Qt.Key.Key_1): "1",
            int(Qt.Key.Key_2): "2",
            int(Qt.Key.Key_3): "3",
            int(Qt.Key.Key_4): "4",
            int(Qt.Key.Key_5): "5",
            int(Qt.Key.Key_6): "6",
            int(Qt.Key.Key_7): "7",
            int(Qt.Key.Key_8): "8",
            int(Qt.Key.Key_9): "9",
            
            # Additional Android TV keys
            int(Qt.Key.Key_I): "INFO",
            int(Qt.Key.Key_G): "GUIDE",
            int(Qt.Key.Key_S): "SEARCH",
            int(Qt.Key.Key_Delete): "DEL",
            int(Qt.Key.Key_PageUp): "CHANNEL_UP",
            int(Qt.Key.Key_PageDown): "CHANNEL_DOWN",
            
            # Function keys for colored buttons
            int(Qt.Key.Key_F1): "PROG_RED",
            int(Qt.Key.Key_F2): "PROG_GREEN",
            int(Qt.Key.Key_F3): "PROG_YELLOW",
            int(Qt.Key.Key_F4): "PROG_BLUE",
            
            # Gamepad buttons (for those with game controllers)
            int(Qt.Key.Key_A): "BUTTON_A",
            int(Qt.Key.Key_B): "BUTTON_B",
            int(Qt.Key.Key_X): "BUTTON_X",
            
            # App shortcuts
            int(Qt.Key.Key_Y): "YOUTUBE",
        }
        
        # Check if this key supports long press (D-Pad and media keys)
        long_press_keys = {
            int(Qt.Key.Key_Up), int(Qt.Key.Key_Down), int(Qt.Key.Key_Left), int(Qt.Key.Key_Right),
            int(Qt.Key.Key_Return), int(Qt.Key.Key_Enter), int(Qt.Key.Key_Space),
            int(Qt.Key.Key_Plus), int(Qt.Key.Key_Minus), int(Qt.Key.Key_Equal), int(Qt.Key.Key_Underscore),
            int(Qt.Key.Key_MediaNext), int(Qt.Key.Key_MediaPrevious)
        }
        
        # Send the command if the key is mapped
        if key in key_mappings:
            command = key_mappings[key]
            
            # Handle long press for supported keys
            if key in long_press_keys:
                if key not in self._held_keys:
                    self._held_keys.add(key)
                    
                    # Don't send anything immediately - wait to see if it's a long press
                    # Set up timer for long press
                    timer = QTimer()
                    timer.setSingleShot(True)
                    timer.timeout.connect(lambda k=key, c=command: self.start_long_press(k, c))
                    timer.start(self._long_press_threshold)
                    self._key_timers[key] = timer
                # If key is already held, ignore repeated events
            else:
                # Regular key press for non-long-press keys
                if command == "YOUTUBE":
                    self.launch_app("com.google.android.youtube.tv")
                else:
                    self.send_remote_command(command)
            
            # Update status label with current command
            self.update_status_label(command)
            
            # Trigger visual feedback for the corresponding button
            button = self.get_button_for_command(command)
            if button:
                self.animate_button_press(button)
            else:
                # Show visual feedback even if no button exists
                self.show_keyboard_feedback(command)
            
            print(f"Keyboard shortcut: {event.text()} -> {command}")
        else:
            # Call parent implementation for unhandled keys
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle keyboard release for long press functionality"""
        key = event.key()
        
        # Prevent auto-repeat handling
        if event.isAutoRepeat():
            return
        
        # Handle key release for long press keys
        if key in self._held_keys:
            self._held_keys.remove(key)
            
            # Check if timer is still active (short press) or if we're in long press mode
            if key in self._key_timers:
                timer = self._key_timers[key]
                if timer.isActive():
                    # Short press - timer didn't fire yet
                    timer.stop()
                    key_mappings = {
                        int(Qt.Key.Key_Up): "DPAD_UP",
                        int(Qt.Key.Key_Down): "DPAD_DOWN",
                        int(Qt.Key.Key_Left): "DPAD_LEFT",
                        int(Qt.Key.Key_Right): "DPAD_RIGHT",
                        int(Qt.Key.Key_Return): "DPAD_CENTER",
                        int(Qt.Key.Key_Enter): "DPAD_CENTER",
                        int(Qt.Key.Key_Space): "DPAD_CENTER",
                        int(Qt.Key.Key_Plus): "VOLUME_UP",
                        int(Qt.Key.Key_Minus): "VOLUME_DOWN",
                        int(Qt.Key.Key_Equal): "VOLUME_UP",
                        int(Qt.Key.Key_Underscore): "VOLUME_DOWN",
                        int(Qt.Key.Key_MediaNext): "MEDIA_NEXT",
                        int(Qt.Key.Key_MediaPrevious): "MEDIA_PREVIOUS"
                    }
                    
                    if key in key_mappings:
                        command = key_mappings[key]
                        self.send_remote_command_with_direction(command, "SHORT")
                        print(f"Short press: {command}")
                del self._key_timers[key]
            else:
                # Long press mode - send END_LONG
                key_mappings = {
                    int(Qt.Key.Key_Up): "DPAD_UP",
                    int(Qt.Key.Key_Down): "DPAD_DOWN",
                    int(Qt.Key.Key_Left): "DPAD_LEFT",
                    int(Qt.Key.Key_Right): "DPAD_RIGHT",
                    int(Qt.Key.Key_Return): "DPAD_CENTER",
                    int(Qt.Key.Key_Enter): "DPAD_CENTER",
                    int(Qt.Key.Key_Space): "DPAD_CENTER",
                    int(Qt.Key.Key_Plus): "VOLUME_UP",
                    int(Qt.Key.Key_Minus): "VOLUME_DOWN",
                    int(Qt.Key.Key_Equal): "VOLUME_UP",
                    int(Qt.Key.Key_Underscore): "VOLUME_DOWN",
                    int(Qt.Key.Key_MediaNext): "MEDIA_NEXT",
                    int(Qt.Key.Key_MediaPrevious): "MEDIA_PREVIOUS"
                }
                
                if key in key_mappings:
                    command = key_mappings[key]
                    self.send_remote_command_with_direction(command, "END_LONG")
                    print(f"Long press ended: {command}")
        
        super().keyReleaseEvent(event)

    def start_long_press(self, key: int, command: str):
        """Start long press for a key"""
        if key in self._held_keys:
            # Remove timer since we're now in long press mode
            if key in self._key_timers:
                del self._key_timers[key]
            
            # Send START_LONG command
            self.send_remote_command_with_direction(command, "START_LONG")
            print(f"Long press started: {command}")
            
            # Update status to show long press
            self.update_status_label(f"{command} (LONG)")

    def eventFilter(self, obj, event):
        """Event filter to ensure keyboard events are handled by the main window"""
        if event.type() == event.Type.KeyPress or event.type() == event.Type.KeyRelease:
            # Check if this is a key we want to handle for remote control
            key = event.key()
            remote_keys = {
                # D-Pad and navigation
                int(Qt.Key.Key_Up), int(Qt.Key.Key_Down), int(Qt.Key.Key_Left), int(Qt.Key.Key_Right),
                int(Qt.Key.Key_Return), int(Qt.Key.Key_Enter), int(Qt.Key.Key_Space),
                int(Qt.Key.Key_Backspace), int(Qt.Key.Key_Escape), int(Qt.Key.Key_Home),
                int(Qt.Key.Key_M), int(Qt.Key.Key_P),
                # Volume
                int(Qt.Key.Key_Plus), int(Qt.Key.Key_Minus), int(Qt.Key.Key_Equal), int(Qt.Key.Key_Underscore),
                int(Qt.Key.Key_0),
                # Media keys
                int(Qt.Key.Key_MediaPlay), int(Qt.Key.Key_MediaPause), int(Qt.Key.Key_MediaStop),
                int(Qt.Key.Key_MediaNext), int(Qt.Key.Key_MediaPrevious), int(Qt.Key.Key_MediaRecord),
                # Numbers
                int(Qt.Key.Key_1), int(Qt.Key.Key_2), int(Qt.Key.Key_3), int(Qt.Key.Key_4), int(Qt.Key.Key_5),
                int(Qt.Key.Key_6), int(Qt.Key.Key_7), int(Qt.Key.Key_8), int(Qt.Key.Key_9),
                # Additional keys
                int(Qt.Key.Key_I), int(Qt.Key.Key_G), int(Qt.Key.Key_S), int(Qt.Key.Key_Delete),
                int(Qt.Key.Key_PageUp), int(Qt.Key.Key_PageDown),
                # Function keys
                int(Qt.Key.Key_F1), int(Qt.Key.Key_F2), int(Qt.Key.Key_F3), int(Qt.Key.Key_F4),
                # Gamepad
                int(Qt.Key.Key_A), int(Qt.Key.Key_B), int(Qt.Key.Key_X),
                # App shortcuts
                int(Qt.Key.Key_Y)
            }
            
            if key in remote_keys:
                # Handle the key event directly in the main window
                if event.type() == event.Type.KeyPress:
                    self.keyPressEvent(event)
                else:  # KeyRelease
                    self.keyReleaseEvent(event)
                return True  # Event handled, don't pass to other widgets
        
        # For all other events, use default handling
        return super().eventFilter(obj, event)

    def get_button_for_command(self, command):
        """Get the button widget associated with a command for visual feedback"""
        return self.command_buttons.get(command)

    def update_status_label(self, command):
        """Update status label to show the current command"""
        if hasattr(self, 'status_label'):
            # Show the command briefly, then return to help text
            self.status_label.setText(f"Command: {command}")
            self.status_label.setStyleSheet("""
                QLabel[class="status"] {
                    background-color: #4CAF50;
                    border: 1px solid #66BB6A;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 9px;
                    color: #ffffff;
                    margin: 10px 0;
                }
            """)
            
            # Reset after 500ms
            def reset_status():
                self.status_label.setText("Keyboard: ↑↓←→ Enter Esc Home M P +/- Y | Hold for long press")
                self.status_label.setStyleSheet("")  # Reset to default styling
                
            QTimer.singleShot(500, reset_status)

    def show_keyboard_feedback(self, command):
        """Show visual feedback for keyboard commands without corresponding buttons"""
        # Prevent multiple feedback animations
        if hasattr(self, '_showing_feedback') and self._showing_feedback:
            return
            
        self._showing_feedback = True
        
        # Create a temporary visual indicator in the window title
        original_title = f"QT Android Remote Control v{__version__}"
        self.setWindowTitle(f"QT Android Remote Control v{__version__} - {command}")
        
        # Reset title and clear flag after 250ms
        def reset_feedback():
            self.setWindowTitle(original_title)
            self._showing_feedback = False
            
        QTimer.singleShot(250, reset_feedback)

    def create_button(self, text, command, style_class="normal", supports_long_press=False):
        """Create a styled button with command binding"""
        button = QPushButton(text)
        
        if supports_long_press:
            # For D-Pad buttons, implement mouse press/release for long press
            button.pressed.connect(lambda: self.button_press_started(button, command))
            button.released.connect(lambda: self.button_press_ended(button, command))
            button.setProperty("supports_long_press", True)
        else:
            button.clicked.connect(lambda: self.button_pressed(button, command))
        
        button.setProperty("class", style_class)
        
        # Prevent buttons from stealing keyboard focus
        button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        
        # Store button reference for keyboard visual feedback
        self.command_buttons[command] = button
        
        return button

    def button_pressed(self, button, command):
        """Handle button press with animation and command"""
        self.animate_button_press(button)
        
        # Handle special commands
        if command == "YOUTUBE":
            self.launch_app("com.google.android.youtube.tv")
        else:
            self.send_command_and_refocus(command)

    def button_press_started(self, button, command):
        """Handle button press start for long press functionality"""
        self.animate_button_press(button)
        
        # Don't send anything immediately - wait to see if it's a long press
        # Set up timer for long press
        if not hasattr(button, '_long_press_timer'):
            button._long_press_timer = QTimer()
            button._long_press_timer.setSingleShot(True)
        
        # Use lambda with default arguments to capture current values
        try:
            button._long_press_timer.timeout.disconnect()  # Clear any existing connections
        except RuntimeError:
            pass  # No connections to disconnect
        button._long_press_timer.timeout.connect(lambda b=button, c=command: self.button_long_press_started(b, c))
        button._long_press_timer.start(self._long_press_threshold)
        button._is_long_pressing = False
        
        print(f"Button press started: {command}")
        self.ensure_keyboard_focus()

    def button_press_ended(self, button, command):
        """Handle button press end for long press functionality"""
        print(f"Button press ended: {command}")
        
        # Check if timer is still active (short press) or if we're in long press mode
        if hasattr(button, '_long_press_timer') and button._long_press_timer.isActive():
            # Short press - timer didn't fire yet
            button._long_press_timer.stop()
            self.send_remote_command_with_direction(command, "SHORT")
            print(f"Button short press: {command}")
        elif hasattr(button, '_is_long_pressing') and button._is_long_pressing:
            # Long press mode - send END_LONG
            self.send_remote_command_with_direction(command, "END_LONG")
            button._is_long_pressing = False
            print(f"Button long press ended: {command}")
        
        self.ensure_keyboard_focus()

    def button_long_press_started(self, button, command):
        """Handle when button long press threshold is reached"""
        print(f"Long press threshold reached for: {command}")
        button._is_long_pressing = True
        self.send_remote_command_with_direction(command, "START_LONG")
        print(f"Button long press started: {command}")
        
        # Update status to show long press
        self.update_status_label(f"{command} (LONG)")

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Remote selection dropdown at the top
        remote_selection_layout = QVBoxLayout()
        remote_selection_layout.setSpacing(5)
        
        # Dropdown and buttons row
        dropdown_layout = QHBoxLayout()
        dropdown_layout.setSpacing(8)
        
        # Connection status circle
        self.connection_circle = QLabel("●")
        self.connection_circle.setProperty("class", "connection-circle")
        self.connection_circle.setFixedSize(20, 20)
        self.connection_circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connection_circle.setStyleSheet("""
            QLabel[class="connection-circle"] {
                color: #757575;
                font-size: 16px;
                background-color: transparent;
                border: none;
            }
        """)
        dropdown_layout.addWidget(self.connection_circle)
        
        self.remote_dropdown = QComboBox()
        self.remote_dropdown.currentIndexChanged.connect(self.on_remote_selected)
        self.remote_dropdown.setMinimumHeight(30)
        self.remote_dropdown.setMinimumWidth(200)
        # Prevent dropdown from stealing focus for keyboard navigation
        self.remote_dropdown.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        dropdown_layout.addWidget(self.remote_dropdown, 1)  # Give it stretch factor
        
        self.add_remote_button = QPushButton("+")
        self.add_remote_button.setObjectName("add_remote_button")
        self.add_remote_button.clicked.connect(self.add_remote_with_focus_restore)
        self.add_remote_button.setFixedSize(30, 30)
        self.add_remote_button.setToolTip("Add Remote")
        self.add_remote_button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        dropdown_layout.addWidget(self.add_remote_button)
        
        self.edit_remote_button = QPushButton("✎")
        self.edit_remote_button.setObjectName("edit_remote_button")
        self.edit_remote_button.clicked.connect(self.edit_remote_with_focus_restore)
        self.edit_remote_button.setEnabled(False)
        self.edit_remote_button.setFixedSize(30, 30)
        self.edit_remote_button.setToolTip("Edit Remote")
        self.edit_remote_button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        dropdown_layout.addWidget(self.edit_remote_button)

        self.delete_remote_button = QPushButton("🗑️")
        self.delete_remote_button.setObjectName("delete_remote_button")
        self.delete_remote_button.clicked.connect(self.delete_remote_with_focus_restore)
        self.delete_remote_button.setEnabled(False)
        self.delete_remote_button.setFixedSize(30, 30)
        self.delete_remote_button.setToolTip("Delete Selected Remote")
        self.delete_remote_button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        dropdown_layout.addWidget(self.delete_remote_button)
        
        remote_selection_layout.addLayout(dropdown_layout)
        main_layout.addLayout(remote_selection_layout)


        # Top row with Power, Volume and Menu controls
        from PySide6.QtWidgets import QSizePolicy

        top_controls_layout = QHBoxLayout()
        top_controls_layout.setSpacing(10)
        top_controls_layout.setContentsMargins(0, 0, 0, 0)

        power_button = self.create_button("⏻", "POWER", "power")
        vol_down = self.create_button("VOL-", "VOLUME_DOWN", "volume", supports_long_press=True)
        mute = self.create_button("MUTE", "MUTE", "volume")
        vol_up = self.create_button("VOL+", "VOLUME_UP", "volume", supports_long_press=True)
        menu_button = self.create_button("MENU", "MENU", "menu")

        # Set all top row buttons to expanding horizontally and preferred vertically
        for btn in [power_button, vol_down, mute, vol_up, menu_button]:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            btn.setMinimumHeight(35)  # Match nav/media button height

        top_controls_layout.addWidget(power_button)
        top_controls_layout.addWidget(vol_down)
        top_controls_layout.addWidget(mute)
        top_controls_layout.addWidget(vol_up)
        top_controls_layout.addWidget(menu_button)
        main_layout.addLayout(top_controls_layout)

        # D-Pad section - using simple grid layout
        dpad_frame = QFrame()
        dpad_frame.setProperty("class", "dpad-frame")
        dpad_grid = QGridLayout(dpad_frame)
        dpad_grid.setHorizontalSpacing(10)  # Horizontal spacing between columns
        dpad_grid.setVerticalSpacing(15)    # Consistent vertical spacing
        dpad_grid.setContentsMargins(20, 20, 20, 20)  # Consistent padding around the frame
        
        # Create D-pad buttons with long press support
        up_button = self.create_button("▲", "DPAD_UP", "dpad", supports_long_press=True)
        left_button = self.create_button("◀", "DPAD_LEFT", "dpad", supports_long_press=True)
        center_button = self.create_button("OK", "DPAD_CENTER", "dpad-center", supports_long_press=True)
        right_button = self.create_button("▶", "DPAD_RIGHT", "dpad", supports_long_press=True)
        down_button = self.create_button("▼", "DPAD_DOWN", "dpad", supports_long_press=True)
        
        # Add to grid - simple 3x3 layout
        dpad_grid.addWidget(up_button, 0, 1)
        dpad_grid.addWidget(left_button, 1, 0)
        dpad_grid.addWidget(center_button, 1, 1)
        dpad_grid.addWidget(right_button, 1, 2)
        dpad_grid.addWidget(down_button, 2, 1)
        
        # Set equal column widths and row heights
        dpad_grid.setColumnStretch(0, 1)
        dpad_grid.setColumnStretch(1, 1)
        dpad_grid.setColumnStretch(2, 1)
        dpad_grid.setRowStretch(0, 1)
        dpad_grid.setRowStretch(1, 1)
        dpad_grid.setRowStretch(2, 1)
        
        main_layout.addWidget(dpad_frame)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        back_button = self.create_button("BACK", "BACK", "nav")
        home_button = self.create_button("HOME", "HOME", "nav")
        nav_layout.addWidget(back_button)
        nav_layout.addWidget(home_button)
        main_layout.addLayout(nav_layout)

        # Media controls
        media_layout = QHBoxLayout()
        media_layout.setSpacing(10)
        rewind = self.create_button("⏪", "MEDIA_REWIND", "media")
        play_pause = self.create_button("⏯", "MEDIA_PLAY_PAUSE", "media")
        stop = self.create_button("⏹", "MEDIA_STOP", "media")
        fast_forward = self.create_button("⏩", "MEDIA_FAST_FORWARD", "media")
        youtube_button = self.create_button("📺", "YOUTUBE", "media")
        
        # Set all media row buttons to expanding horizontally and preferred vertically (like top row)
        for btn in [rewind, play_pause, stop, fast_forward, youtube_button]:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            btn.setMinimumHeight(35)  # Match nav/media button height
        
        media_layout.addWidget(rewind)
        media_layout.addWidget(play_pause)
        media_layout.addWidget(stop)
        media_layout.addWidget(fast_forward)
        media_layout.addWidget(youtube_button)
        main_layout.addLayout(media_layout)

        # Text input section
        text_input_layout = QHBoxLayout()
        text_input_layout.setSpacing(10)
        
        # Text input field
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter text to send to Android TV (press Enter)...")
        self.text_input.setProperty("class", "text-input")
        self.text_input.setMinimumHeight(28)
        self.text_input.setMaximumHeight(28)
        # Prevent text input from stealing focus for keyboard navigation
        self.text_input.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        # Connect Enter key to send text
        self.text_input.returnPressed.connect(self.send_text_input)
        text_input_layout.addWidget(self.text_input, 1)  # Give it stretch factor
        
        main_layout.addLayout(text_input_layout)

        # Add keyboard status label at the bottom
        self.status_label = QLabel("Keyboard: ↑↓←→ Enter Esc Home M P +/- Y | Hold for long press")
        self.status_label.setProperty("class", "status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)
        
        # Populate the dropdown after all UI elements are created
        self.populate_remote_dropdown()

    def launch_app(self, app_link):
        """Launch an app on the Android TV"""
        if self.connection_thread and self.connection_thread.isRunning():
            self.connection_thread.send_launch_app_command(app_link)
            print(f"Launching app: {app_link}")
        else:
            print(f"Not connected - cannot launch app: {app_link}")

    def send_text_input(self):
        """Send the text from the input field to Android TV"""
        if hasattr(self, 'text_input'):
            text = self.text_input.text().strip()
            if text:
                if self.connection_thread and self.connection_thread.isRunning():
                    self.connection_thread.send_text(text)
                    print(f"Sent text: {text}")
                    # Clear the input field after sending
                    self.text_input.clear()
                    # Restore keyboard focus
                    self.ensure_keyboard_focus()
                else:
                    print(f"Not connected - cannot send text: {text}")
            else:
                print("No text to send")

    def apply_styles(self):
        """Apply styling that respects the system theme"""
        # Base styling that uses system palette colors
        base_styles = """
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: palette(window);
                color: palette(window-text);
            }
            
            QComboBox {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 4px 8px;
                color: palette(text);
                font-size: 10px;
                min-height: 20px;
            }
            
            QComboBox::drop-down {
                border-left: 1px solid palette(mid);
                width: 20px;
            }
            
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            
            QComboBox QAbstractItemView {
                background-color: palette(base);
                border: 1px solid palette(mid);
                selection-background-color: palette(highlight);
                color: palette(text);
            }
            
            QPushButton {
                border: 1px solid palette(mid);
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
                font-weight: 500;
                background-color: palette(button);
                color: palette(button-text);
                min-height: 32px;
            }
            
            QPushButton:hover {
                background-color: palette(light);
                border-color: palette(dark);
            }
            
            QPushButton:pressed {
                background-color: palette(mid);
            }
            
            QPushButton[class="power"] {
                background-color: #d32f2f;
                border-color: #d32f2f;
                font-size: 24px;
                font-weight: bold;
                min-height: 30px;
                color: #ffffff;
            }
            
            QPushButton[class="power"]:hover {
                background-color: #c62828;
            }
            
            QPushButton[class="volume"] {
                background-color: palette(dark);
                border-color: palette(dark);
                font-size: 10px;
                min-height: 30px;
                color: #ffffff;
            }
            
            QPushButton[class="volume"]:hover {
                background-color: palette(shadow);
                color: #ffffff;
            }
            
            QPushButton[class="menu"] {
                background-color: #1976d2;
                border-color: #1976d2;
                font-size: 10px;
                min-height: 30px;
                color: #ffffff;
            }
            
            QPushButton[class="menu"]:hover {
                background-color: #1565c0;
            }
            
            QPushButton[class="dpad"] {
                background-color: palette(dark);
                border-color: palette(dark);
                font-size: 30px;
                min-width: 45px;
                min-height: 45px;
                border-radius: 4px;
                color: #ffffff;
            }
            
            QPushButton[class="dpad"]:hover {
                background-color: palette(shadow);
                color: #ffffff;
            }
            
            QPushButton[class="dpad-center"] {
                background-color: #388e3c;
                border-color: #388e3c;
                font-size: 11px;
                font-weight: bold;
                min-width: 45px;
                min-height: 45px;
                border-radius: 4px;
                color: #ffffff;
            }
            
            QPushButton[class="dpad-center"]:hover {
                background-color: #2e7d32;
            }
            
            QFrame[class="dpad-frame"] {
                background-color: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 8px;
                margin: 10px 0;
            }
            
            QPushButton[class="nav"] {
                background-color: palette(dark);
                border-color: palette(dark);
                min-width: 100px;
                font-size: 10px;
                min-height: 30px;
                color: #ffffff;
            }
            
            QPushButton[class="nav"]:hover {
                background-color: palette(shadow);
                color: #ffffff;
            }
            
            QPushButton[class="media"] {
                background-color: palette(button);
                border-color: palette(mid);
                font-size: 28px;
                min-width: 50px;
                min-height: 35px;
                color: palette(button-text);
            }
            
            QPushButton[class="media"]:hover {
                background-color: palette(light);
                border-color: palette(dark);
            }
            
            QPushButton[class="app"] {
                background-color: #7b1fa2;
                border-color: #7b1fa2;
                min-width: 100px;
                font-weight: bold;
                font-size: 11px;
                min-height: 35px;
                color: #ffffff;
            }
            
            QPushButton[class="app"]:hover {
                background-color: #8e24aa;
            }
            
            QPushButton[class="youtube"] {
                background-color: #388e3c;
                border-color: #388e3c;
                font-size: 10px;
                min-height: 30px;
                color: #ffffff;
            }
            
            QPushButton[class="youtube"]:hover {
                background-color: #2e7d32;
            }
            
            QLabel[class="status"] {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 6px;
                font-size: 9px;
                color: palette(text);
                margin: 10px 0;
            }
            
            
            /* Specific styling for management buttons */
            QPushButton#add_remote_button,
            QPushButton#edit_remote_button,
            QPushButton#delete_remote_button {
                background-color: palette(button);
                border: 1px solid palette(mid);
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                min-height: 20px;
                max-height: 30px;
                min-width: 30px;
                max-width: 30px;
                padding: 0px;
                color: palette(button-text);
            }
            
            QPushButton#add_remote_button:hover,
            QPushButton#edit_remote_button:hover,
            QPushButton#delete_remote_button:hover {
                background-color: palette(light);
            }
            
            QPushButton#add_remote_button:disabled,
            QPushButton#edit_remote_button:disabled,
            QPushButton#delete_remote_button:disabled {
                background-color: palette(mid);
                color: palette(dark);
            }
            
            /* Text input styling */
            QLineEdit[class="text-input"] {
                background-color: palette(base);
                border: 2px solid palette(mid);
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                color: palette(text);
                min-height: 16px;
            }
            
            QLineEdit[class="text-input"]:focus {
                border-color: #2196F3;
                background-color: palette(base);
            }
            
        """
        
        self.setStyleSheet(base_styles)

    def populate_remote_dropdown(self):
        """Populate the dropdown with available remotes"""
        self.remote_dropdown.clear()
        
        if not self.remotes:
            self.remote_dropdown.addItem("No remotes configured")
            self.edit_remote_button.setEnabled(False)
            self.delete_remote_button.setEnabled(False)
        else:
            for remote in self.remotes:
                self.remote_dropdown.addItem(remote["name"], remote)
            self.edit_remote_button.setEnabled(True)
            self.delete_remote_button.setEnabled(True)
            # Auto-select first remote if available
            if len(self.remotes) > 0:
                self.remote_dropdown.setCurrentIndex(0)
                self.on_remote_selected(0)

    def on_remote_selected(self, index):
        """Handle remote selection from dropdown"""
        if index >= 0 and self.remotes:
            selected_remote = self.remote_dropdown.currentData()
            if selected_remote:
                self.current_remote = selected_remote
                self.connect_to_remote(selected_remote)
                print(f"Selected remote: {selected_remote['name']}")
        else:
            self.current_remote = None
            self.disconnect_from_remote()
        
        # Restore keyboard focus after dropdown selection
        self.ensure_keyboard_focus()

    def connect_to_remote(self, remote_config):
        """Connect to the selected Android TV remote"""
        # Disconnect any existing connection
        self.disconnect_from_remote()
        
        # Set circle to orange for connecting
        self.connection_circle.setStyleSheet("""
            QLabel[class="connection-circle"] {
                color: #FF9800;
                font-size: 16px;
                background-color: transparent;
                border: none;
            }
        """)
        
        # Start connection thread
        self.connection_thread = AndroidTVConnectionThread()
        self.connection_thread.setup_remote(
            remote_config["host"],
            remote_config["client_name"],
            remote_config["cert_file"],
            remote_config["key_file"]
        )
        
        # Connect signals
        self.connection_thread.connection_established.connect(self.on_connection_established)
        self.connection_thread.connection_lost.connect(self.on_connection_lost)
        self.connection_thread.device_info_updated.connect(self.on_device_info_updated)
        self.connection_thread.is_on_updated.connect(self.on_is_on_updated)
        self.connection_thread.current_app_updated.connect(self.on_current_app_updated)
        self.connection_thread.volume_info_updated.connect(self.on_volume_info_updated)
        self.connection_thread.is_available_updated.connect(self.on_is_available_updated)
        
        self.connection_thread.start()

    def disconnect_from_remote(self):
        """Disconnect from the current Android TV remote"""
        if self.connection_thread and self.connection_thread.isRunning():
            self.connection_thread.stop()
            # Wait for the thread to finish with a timeout to prevent hanging
            if not self.connection_thread.wait(5000):  # 5 second timeout
                _LOGGER.warning("Connection thread did not stop within timeout, terminating")
                self.connection_thread.terminate()
                self.connection_thread.wait(1000)  # Wait 1 more second for termination
            self.connection_thread = None
        
        # Set circle to gray for disconnected
        self.connection_circle.setStyleSheet("""
            QLabel[class="connection-circle"] {
                color: #757575;
                font-size: 16px;
                background-color: transparent;
                border: none;
            }
        """)

    def on_connection_established(self):
        """Handle successful connection"""
        # Set circle to green for connected
        self.connection_circle.setStyleSheet("""
            QLabel[class="connection-circle"] {
                color: #4CAF50;
                font-size: 16px;
                background-color: transparent;
                border: none;
            }
        """)

    def on_connection_lost(self, error: str):
        """Handle connection lost"""
        # Set circle to red for connection lost
        self.connection_circle.setStyleSheet("""
            QLabel[class="connection-circle"] {
                color: #F44336;
                font-size: 16px;
                background-color: transparent;
                border: none;
            }
        """)

    def on_device_info_updated(self, device_info: Dict[str, Any]):
        """Handle device info update"""
        print(f"Device info: {device_info}")

    def on_is_on_updated(self, is_on: bool):
        """Handle is_on update"""
        print(f"Device is on: {is_on}")

    def on_current_app_updated(self, current_app: str):
        """Handle current app update"""
        print(f"Current app: {current_app}")

    def on_volume_info_updated(self, volume_info: Dict[str, Any]):
        """Handle volume info update"""
        print(f"Volume info: {volume_info}")

    def on_is_available_updated(self, is_available: bool):
        """Handle availability update"""
        if is_available:
            # Set circle to green for available
            self.connection_circle.setStyleSheet("""
                QLabel[class="connection-circle"] {
                    color: #4CAF50;
                    font-size: 16px;
                    background-color: transparent;
                    border: none;
                }
            """)
        else:
            # Set circle to orange for unavailable
            self.connection_circle.setStyleSheet("""
                QLabel[class="connection-circle"] {
                    color: #FF9800;
                    font-size: 16px;
                    background-color: transparent;
                    border: none;
                }
            """)

    def add_remote_with_focus_restore(self):
        """Open wizard to add a new remote and restore focus"""
        self.add_remote()
        self.ensure_keyboard_focus()

    def edit_remote_with_focus_restore(self):
        """Open wizard to edit the selected remote and restore focus"""
        self.edit_remote()
        self.ensure_keyboard_focus()

    def delete_remote_with_focus_restore(self):
        """Delete the currently selected remote and restore focus"""
        self.delete_remote()
        self.ensure_keyboard_focus()

    def add_remote(self):
        """Open wizard to add a new remote"""
        wizard = RemoteWizard(parent=self)
        wizard.remote_saved.connect(self.handle_remote_saved, Qt.ConnectionType.UniqueConnection)
        wizard.exec()
        # Explicitly disconnect to prevent multiple connections
        wizard.remote_saved.disconnect(self.handle_remote_saved)

    def edit_remote(self):
        """Open wizard to edit the selected remote"""
        current_index = self.remote_dropdown.currentIndex()
        if current_index >= 0 and self.remotes:
            remote_to_edit = self.remotes[current_index]
            wizard = RemoteWizard(remote_data=remote_to_edit, remote_index=current_index, parent=self)
            wizard.remote_saved.connect(self.handle_remote_saved, Qt.ConnectionType.UniqueConnection)
            wizard.exec()
            # Explicitly disconnect to prevent multiple connections
            wizard.remote_saved.disconnect(self.handle_remote_saved)

    def handle_remote_saved(self, saved_remote, remote_index):
        """Handle when a remote is saved from the wizard"""
        # Prevent multiple dialogs by checking if we're already processing
        if hasattr(self, '_processing_remote_save') and self._processing_remote_save:
            return
        
        self._processing_remote_save = True
        
        try:
            if remote_index == -1:  # New remote
                self.remotes.append(saved_remote)
                message = f"Remote '{saved_remote['name']}' added successfully!"
            else:  # Existing remote edited
                self.remotes[remote_index] = saved_remote
                message = f"Remote '{saved_remote['name']}' updated successfully!"
            
            save_remotes(self.remotes)
            self.populate_remote_dropdown()
            
            # Select the newly added/edited remote
            if remote_index == -1:
                self.remote_dropdown.setCurrentIndex(len(self.remotes) - 1)
            else:
                self.remote_dropdown.setCurrentIndex(remote_index)
            
            # Restore keyboard focus after wizard closes
            self.ensure_keyboard_focus()
        finally:
            # Always reset the flag
            self._processing_remote_save = False

    def delete_remote(self):
        """Delete the currently selected remote"""
        current_index = self.remote_dropdown.currentIndex()
        if current_index >= 0 and self.remotes:
            remote_to_delete = self.remotes[current_index]
            
            reply = QMessageBox.question(self, "Delete Remote",
                                        f"Are you sure you want to delete '{remote_to_delete['name']}'?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                del self.remotes[current_index]
                save_remotes(self.remotes)
                self.populate_remote_dropdown()
                
                # If there are still remotes, select the first one, otherwise show "No remotes"
                if self.remotes:
                    self.remote_dropdown.setCurrentIndex(0)
                    self.on_remote_selected(0)
                else:
                    self.on_remote_selected(-1) # Clear current selection
                
                QMessageBox.information(self, "Success", f"Remote '{remote_to_delete['name']}' deleted successfully!")
                
                # Restore keyboard focus after dialog closes
                self.ensure_keyboard_focus()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RemoteWindow()
    window.show()
    sys.exit(app.exec())