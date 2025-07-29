"""
Remote Wizard for QT Android Remote Control

Setup wizard for configuring new Android TV connections with pairing support.
"""

import asyncio
import logging
from typing import Optional, List, Tuple
from PySide6.QtWidgets import (QApplication, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QStackedWidget,
                                QPushButton, QLabel, QLineEdit, QListWidget,
                                QListWidgetItem, QMessageBox, QProgressBar, QTextEdit, QFrame,
                                QSpinBox)
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtGui import QPalette

from zeroconf import ServiceStateChange, Zeroconf
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

from .android_tv_connection import AndroidTVConnectionThread

_LOGGER = logging.getLogger(__name__)


class DeviceDiscoveryThread(QThread):
    """Thread for discovering Android TV devices via Zeroconf"""
    device_found = Signal(str, str, int)  # name, host, port
    discovery_finished = Signal()
    
    def __init__(self, timeout: float = 5.0):
        super().__init__()
        self.timeout = timeout
        self.devices = []
        
    def run(self):
        """Run device discovery"""
        try:
            asyncio.run(self._async_discover())
        except Exception as e:
            _LOGGER.error(f"Error during device discovery: {e}")
        finally:
            self.discovery_finished.emit()
    
    async def _async_discover(self):
        """Async device discovery"""
        def _async_on_service_state_change(
            zeroconf: Zeroconf,
            service_type: str,
            name: str,
            state_change: ServiceStateChange,
        ) -> None:
            if state_change is ServiceStateChange.Added:
                asyncio.ensure_future(
                    _async_display_service_info(zeroconf, service_type, name)
                )

        async def _async_display_service_info(
            zeroconf: Zeroconf, service_type: str, name: str
        ) -> None:
            try:
                info = AsyncServiceInfo(service_type, name)
                await info.async_request(zeroconf, 3000)
                if info and info.parsed_scoped_addresses():
                    host = info.parsed_scoped_addresses()[0]
                    port = info.port or 6467
                    device_name = name.split('.')[0]
                    self.device_found.emit(device_name, host, port)
            except Exception as e:
                _LOGGER.debug(f"Error getting service info for {name}: {e}")

        zc = AsyncZeroconf()
        services = ["_androidtvremote2._tcp.local."]
        
        browser = AsyncServiceBrowser(
            zc.zeroconf, services, handlers=[_async_on_service_state_change]
        )
        
        await asyncio.sleep(self.timeout)
        
        await browser.async_cancel()
        await zc.async_close()


class RemoteWizard(QDialog):
    remote_saved = Signal(dict, int)  # Signal to emit when a remote is saved (added or edited)

    def __init__(self, remote_data=None, remote_index=-1, parent=None):
        super().__init__(parent)
        self.remote_data = remote_data
        self.remote_index = remote_index
        self.discovery_thread: Optional[DeviceDiscoveryThread] = None
        self.connection_thread: Optional[AndroidTVConnectionThread] = None
        self.current_step = 0
        self.total_steps = 4
        self.discovered_devices: List[Tuple[str, str, int]] = []  # name, host, port
        self._pairing_in_progress = False

        if self.remote_data:
            self.setWindowTitle("Edit Android TV Remote - QT Android Remote")
            self.host = self.remote_data.get("host", "")
            self.client_name = self.remote_data.get("client_name", "QT Android Remote")
            self.remote_name = self.remote_data.get("name", "")
            self.cert_file = self.remote_data.get("cert_file", "")
            self.key_file = self.remote_data.get("key_file", "")
        else:
            self.setWindowTitle("Add New Android TV Remote - QT Android Remote")
            self.host = ""
            self.client_name = "QT Android Remote"
            self.remote_name = ""
            self.cert_file = ""
            self.key_file = ""
        
        # Set dialog properties for better UX
        self.setModal(True)
        self.setFixedSize(500, 650)
        
        self.stacked_widget = QStackedWidget()
        self.init_ui()
        self.apply_styles()
        self.setup_input_validation()
        
        # Set initial focus
        QTimer.singleShot(100, lambda: self.host_input.setFocus())

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Progress indicator at the top
        self.progress_frame = QFrame()
        self.progress_frame.setProperty("class", "progress-frame")
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setContentsMargins(15, 10, 15, 10)
        
        self.progress_label = QLabel("Step 1 of 4: Device Discovery")
        self.progress_label.setProperty("class", "progress-label")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.total_steps)
        self.progress_bar.setValue(1)
        self.progress_bar.setProperty("class", "progress-bar")
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(self.progress_frame)
        main_layout.addWidget(self.stacked_widget)

        # Page 1: Device Discovery
        self.create_page1()
        
        # Page 2: Connection Details
        self.create_page2()
        
        # Page 3: Pairing
        self.create_page3()
        
        # Page 4: Remote Name
        self.create_page4()

        self.setLayout(main_layout)

    def create_page1(self):
        """Create device discovery page"""
        self.page1 = QWidget()
        page1_layout = QVBoxLayout()
        page1_layout.setSpacing(15)
        page1_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and description
        title_label = QLabel("📺 Discover Android TV Devices")
        title_label.setProperty("class", "page-title")
        page1_layout.addWidget(title_label)
        
        desc_label = QLabel("Scan your network for Android TV devices or enter the IP address manually.")
        desc_label.setProperty("class", "page-description")
        desc_label.setWordWrap(True)
        page1_layout.addWidget(desc_label)
        
        # Discovery controls
        discovery_layout = QHBoxLayout()
        self.scan_button = QPushButton("🔍 Scan Network")
        self.scan_button.setProperty("class", "primary-button")
        self.scan_button.clicked.connect(self.start_device_discovery)
        discovery_layout.addWidget(self.scan_button)
        
        discovery_layout.addStretch()
        
        scan_timeout_label = QLabel("Timeout (s):")
        discovery_layout.addWidget(scan_timeout_label)
        
        self.scan_timeout = QSpinBox()
        self.scan_timeout.setRange(3, 30)
        self.scan_timeout.setValue(5)
        discovery_layout.addWidget(self.scan_timeout)
        
        page1_layout.addLayout(discovery_layout)
        
        # Discovered devices list with integrated status
        self.devices_label = QLabel("Discovered Devices:")
        self.devices_label.setProperty("class", "field-label")
        page1_layout.addWidget(self.devices_label)
        
        self.devices_list = QListWidget()
        self.devices_list.setProperty("class", "entity-list")
        self.devices_list.itemClicked.connect(self.select_device_from_list)
        self.devices_list.setMinimumHeight(150)
        page1_layout.addWidget(self.devices_list)
        
        # Add some spacing before manual input
        page1_layout.addSpacing(10)
        
        # Manual entry with integrated hint
        self.host_input = QLineEdit(self.host)
        self.host_input.setPlaceholderText("Or enter IP address manually (e.g., 192.168.1.100)")
        self.host_input.setProperty("class", "input-field")
        page1_layout.addWidget(self.host_input)
        
        page1_layout.addStretch()
        
        # Buttons
        page1_buttons_layout = QHBoxLayout()
        self.next_button_page1 = QPushButton("Continue →")
        self.next_button_page1.setProperty("class", "primary-button")
        self.next_button_page1.clicked.connect(self.validate_page1)
        page1_buttons_layout.addStretch()
        page1_buttons_layout.addWidget(self.next_button_page1)
        page1_layout.addLayout(page1_buttons_layout)
        
        self.page1.setLayout(page1_layout)
        self.stacked_widget.addWidget(self.page1)

    def create_page2(self):
        """Create connection details page"""
        self.page2 = QWidget()
        page2_layout = QVBoxLayout()
        page2_layout.setSpacing(15)
        page2_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and description
        title_label2 = QLabel("⚙️ Connection Details")
        title_label2.setProperty("class", "page-title")
        page2_layout.addWidget(title_label2)
        
        desc_label2 = QLabel("Configure the connection settings for your Android TV.")
        desc_label2.setProperty("class", "page-description")
        desc_label2.setWordWrap(True)
        page2_layout.addWidget(desc_label2)
        
        # Host display
        host_label = QLabel("Android TV IP Address:")
        host_label.setProperty("class", "field-label")
        page2_layout.addWidget(host_label)
        
        self.host_display = QLabel()
        self.host_display.setProperty("class", "host-display")
        page2_layout.addWidget(self.host_display)
        
        # Client name display (hardcoded)
        client_name_label = QLabel("Client Name (shown on Android TV):")
        client_name_label.setProperty("class", "field-label")
        page2_layout.addWidget(client_name_label)
        
        self.client_name_display = QLabel("QT Android Remote")
        self.client_name_display.setProperty("class", "host-display")
        page2_layout.addWidget(self.client_name_display)
        
        client_help = QLabel("💡 This name will appear on your Android TV during pairing")
        client_help.setProperty("class", "help-text")
        page2_layout.addWidget(client_help)
        
        page2_layout.addStretch()

        page2_buttons_layout = QHBoxLayout()
        self.back_button_page2 = QPushButton("← Back")
        self.back_button_page2.setProperty("class", "secondary-button")
        self.back_button_page2.clicked.connect(self.go_back_to_page1)
        self.next_button_page2 = QPushButton("Start Pairing →")
        self.next_button_page2.setProperty("class", "primary-button")
        self.next_button_page2.clicked.connect(self.validate_page2)
        page2_buttons_layout.addWidget(self.back_button_page2)
        page2_buttons_layout.addStretch()
        page2_buttons_layout.addWidget(self.next_button_page2)
        page2_layout.addLayout(page2_buttons_layout)
        self.page2.setLayout(page2_layout)
        self.stacked_widget.addWidget(self.page2)

    def create_page3(self):
        """Create pairing page"""
        self.page3 = QWidget()
        page3_layout = QVBoxLayout()
        page3_layout.setSpacing(15)
        page3_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and description
        title_label3 = QLabel("🔗 Pairing with Android TV")
        title_label3.setProperty("class", "page-title")
        page3_layout.addWidget(title_label3)
        
        self.pairing_desc = QLabel("Connecting to your Android TV...")
        self.pairing_desc.setProperty("class", "page-description")
        self.pairing_desc.setWordWrap(True)
        page3_layout.addWidget(self.pairing_desc)
        
        # Pairing progress
        self.pairing_progress = QProgressBar()
        self.pairing_progress.setRange(0, 0)  # Indeterminate
        page3_layout.addWidget(self.pairing_progress)
        
        # Pairing code input (initially hidden)
        self.pairing_code_frame = QFrame()
        pairing_code_layout = QVBoxLayout(self.pairing_code_frame)
        
        code_label = QLabel("Enter the 6-digit pairing code shown on your Android TV:")
        code_label.setProperty("class", "field-label")
        pairing_code_layout.addWidget(code_label)
        
        self.pairing_code_input = QLineEdit()
        self.pairing_code_input.setPlaceholderText("123ABC")
        self.pairing_code_input.setProperty("class", "input-field")
        self.pairing_code_input.setMaxLength(6)
        # Normalize pairing code to uppercase as user types
        self.pairing_code_input.textChanged.connect(self._normalize_pairing_code)
        pairing_code_layout.addWidget(self.pairing_code_input)
        
        code_help = QLabel("💡 Look for a pairing dialog on your Android TV screen")
        code_help.setProperty("class", "help-text")
        pairing_code_layout.addWidget(code_help)
        
        self.pairing_code_frame.hide()
        page3_layout.addWidget(self.pairing_code_frame)
        
        # Status message
        self.pairing_status = QLabel("")
        self.pairing_status.setProperty("class", "status-message")
        self.pairing_status.setWordWrap(True)
        self.pairing_status.hide()
        page3_layout.addWidget(self.pairing_status)
        
        page3_layout.addStretch()

        page3_buttons_layout = QHBoxLayout()
        self.back_button_page3 = QPushButton("← Back")
        self.back_button_page3.setProperty("class", "secondary-button")
        self.back_button_page3.clicked.connect(self.go_back_to_page2)
        
        self.submit_code_button = QPushButton("Submit Code")
        self.submit_code_button.setProperty("class", "primary-button")
        self.submit_code_button.clicked.connect(self.submit_pairing_code)
        self.submit_code_button.hide()
        
        self.retry_pairing_button = QPushButton("Retry Pairing")
        self.retry_pairing_button.setProperty("class", "primary-button")
        self.retry_pairing_button.clicked.connect(self.start_pairing)
        self.retry_pairing_button.hide()
        
        page3_buttons_layout.addWidget(self.back_button_page3)
        page3_buttons_layout.addStretch()
        page3_buttons_layout.addWidget(self.submit_code_button)
        page3_buttons_layout.addWidget(self.retry_pairing_button)
        page3_layout.addLayout(page3_buttons_layout)
        self.page3.setLayout(page3_layout)
        self.stacked_widget.addWidget(self.page3)

    def create_page4(self):
        """Create remote name page"""
        self.page4 = QWidget()
        page4_layout = QVBoxLayout()
        page4_layout.setSpacing(15)
        page4_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and description
        title_label4 = QLabel("🏷️ Name Your Remote")
        title_label4.setProperty("class", "page-title")
        page4_layout.addWidget(title_label4)
        
        desc_label4 = QLabel("Give your Android TV remote a friendly name to easily identify it.")
        desc_label4.setProperty("class", "page-description")
        desc_label4.setWordWrap(True)
        page4_layout.addWidget(desc_label4)
        
        # Name input
        name_label = QLabel("Remote Name:")
        name_label.setProperty("class", "field-label")
        page4_layout.addWidget(name_label)
        
        self.remote_name_input = QLineEdit(self.remote_name)
        self.remote_name_input.setPlaceholderText("e.g., Living Room Android TV, Bedroom TV")
        self.remote_name_input.setProperty("class", "input-field")
        page4_layout.addWidget(self.remote_name_input)
        
        name_help = QLabel("💡 Choose a descriptive name to distinguish this remote from others")
        name_help.setProperty("class", "help-text")
        page4_layout.addWidget(name_help)
        
        # Summary section
        summary_frame = QFrame()
        summary_frame.setProperty("class", "summary-frame")
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(15, 15, 15, 15)
        
        summary_title = QLabel("📋 Configuration Summary")
        summary_title.setProperty("class", "summary-title")
        summary_layout.addWidget(summary_title)
        
        self.summary_text = QTextEdit()
        self.summary_text.setProperty("class", "summary-text")
        self.summary_text.setMaximumHeight(120)
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)
        
        page4_layout.addWidget(summary_frame)
        page4_layout.addStretch()

        page4_buttons_layout = QHBoxLayout()
        self.back_button_page4 = QPushButton("← Back")
        self.back_button_page4.setProperty("class", "secondary-button")
        self.back_button_page4.clicked.connect(self.go_back_to_page3)
        
        finish_text = "Update Remote" if self.remote_data else "Create Remote"
        self.finish_button = QPushButton(f"✓ {finish_text}")
        self.finish_button.setProperty("class", "success-button")
        self.finish_button.clicked.connect(self.finish_wizard, Qt.ConnectionType.UniqueConnection)
        
        page4_buttons_layout.addWidget(self.back_button_page4)
        page4_buttons_layout.addStretch()
        page4_buttons_layout.addWidget(self.finish_button)
        page4_layout.addLayout(page4_buttons_layout)
        self.page4.setLayout(page4_layout)
        self.stacked_widget.addWidget(self.page4)

    def update_devices_label(self, status: str = ""):
        """Update the devices label with optional status"""
        if status:
            self.devices_label.setText(f"Discovered Devices: {status}")
        else:
            self.devices_label.setText("Discovered Devices:")

    def start_device_discovery(self):
        """Start discovering Android TV devices"""
        self.scan_button.setEnabled(False)
        self.scan_button.setText("Scanning...")
        self.update_devices_label("Scanning...")
        self.devices_list.clear()
        self.discovered_devices.clear()
        
        timeout = self.scan_timeout.value()
        self.discovery_thread = DeviceDiscoveryThread(timeout)
        self.discovery_thread.device_found.connect(self.on_device_found)
        self.discovery_thread.discovery_finished.connect(self.on_discovery_finished)
        self.discovery_thread.start()

    def on_device_found(self, name: str, host: str, port: int):
        """Handle discovered device"""
        self.discovered_devices.append((name, host, port))
        item_text = f"{name} - {host}:{port}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, (name, host, port))
        self.devices_list.addItem(item)
        
        # Update status to show progress
        device_count = len(self.discovered_devices)
        self.update_devices_label(f"Found {device_count}")

    def on_discovery_finished(self):
        """Handle discovery completion"""
        self.scan_button.setEnabled(True)
        self.scan_button.setText("🔍 Scan Network")
        
        if not self.discovered_devices:
            self.update_devices_label("None found")
            item = QListWidgetItem("No devices found. Try entering IP address manually.")
            self.devices_list.addItem(item)
        else:
            device_count = len(self.discovered_devices)
            self.update_devices_label(f"Found {device_count}")

    def select_device_from_list(self, item):
        """Handle device selection from list"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            name, host, port = data
            self.host_input.setText(host)

    def validate_page1(self):
        """Validate device discovery page"""
        self.host = self.host_input.text().strip()
        if not self.host:
            QMessageBox.warning(self, "Input Error", "Please enter an IP address or select a discovered device.")
            return
        
        self.current_step = 2
        self.update_progress()
        self.host_display.setText(self.host)
        self.stacked_widget.setCurrentWidget(self.page2)

    def go_back_to_page1(self):
        """Navigate back to page 1"""
        self.current_step = 1
        self.update_progress()
        self.stacked_widget.setCurrentWidget(self.page1)

    def validate_page2(self):
        """Validate connection details page"""
        # Client name is hardcoded to "QT Android Remote"
        self.client_name = "QT Android Remote"
        
        self.current_step = 3
        self.update_progress()
        self.stacked_widget.setCurrentWidget(self.page3)
        
        # Start pairing process
        QTimer.singleShot(500, self.start_pairing)

    def go_back_to_page2(self):
        """Navigate back to page 2"""
        # Cancel any ongoing pairing process
        if self.connection_thread and self.connection_thread.isRunning():
            # Cancel pairing first to unblock any waiting operations
            self.connection_thread.cancel_pairing()
            # Then stop the thread
            self.connection_thread.stop()
            # Wait for thread to finish with a timeout to prevent hanging
            if not self.connection_thread.wait(3000):  # 3 second timeout
                self.connection_thread.terminate()
                self.connection_thread.wait()
        
        # Reset pairing state
        self._pairing_in_progress = False
        
        self.current_step = 2
        self.update_progress()
        self.stacked_widget.setCurrentWidget(self.page2)

    def go_back_to_page3(self):
        """Navigate back to page 3"""
        self.current_step = 3
        self.update_progress()
        self.stacked_widget.setCurrentWidget(self.page3)

    def start_pairing(self):
        """Start the pairing process"""
        if self._pairing_in_progress:
            return
            
        self._pairing_in_progress = True
        self.pairing_desc.setText("Connecting to your Android TV...")
        self.pairing_progress.show()
        self.pairing_code_frame.hide()
        self.submit_code_button.hide()
        self.retry_pairing_button.hide()
        self.pairing_status.hide()
        
        # Generate certificate file names
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        self.cert_file = f"cert_{unique_id}.pem"
        self.key_file = f"key_{unique_id}.pem"
        
        # Start connection thread
        self.connection_thread = AndroidTVConnectionThread()
        self.connection_thread.setup_remote(self.host, self.client_name, self.cert_file, self.key_file)
        
        # Connect signals
        self.connection_thread.pairing_started.connect(self.on_pairing_started)
        self.connection_thread.pairing_code_required.connect(self.on_pairing_code_required)
        self.connection_thread.pairing_completed.connect(self.on_pairing_completed)
        self.connection_thread.pairing_failed.connect(self.on_pairing_failed)
        self.connection_thread.connection_established.connect(self.on_connection_established)
        self.connection_thread.connection_lost.connect(self.on_connection_lost)
        
        self.connection_thread.start()

    def on_pairing_started(self):
        """Handle pairing started"""
        self.pairing_desc.setText("Pairing started. Look for a pairing dialog on your Android TV.")

    def on_pairing_code_required(self):
        """Handle pairing code required"""
        self.pairing_desc.setText("Enter the pairing code shown on your Android TV:")
        self.pairing_progress.hide()
        self.pairing_code_frame.show()
        self.submit_code_button.show()
        self.pairing_code_input.setFocus()

    def _normalize_pairing_code(self, text):
        """Normalize pairing code input to uppercase"""
        # Get current cursor position
        cursor_pos = self.pairing_code_input.cursorPosition()
        
        # Convert to uppercase
        upper_text = text.upper()
        
        # Only update if the text actually changed to avoid infinite recursion
        if text != upper_text:
            # Temporarily disconnect the signal to avoid recursion
            self.pairing_code_input.textChanged.disconnect(self._normalize_pairing_code)
            self.pairing_code_input.setText(upper_text)
            # Restore cursor position
            self.pairing_code_input.setCursorPosition(cursor_pos)
            # Reconnect the signal
            self.pairing_code_input.textChanged.connect(self._normalize_pairing_code)

    def submit_pairing_code(self):
        """Submit the pairing code"""
        code = self.pairing_code_input.text().strip()
        if len(code) != 6:
            QMessageBox.warning(self, "Invalid Code", "Pairing code must be exactly 6 characters.")
            return
        
        self.submit_code_button.setEnabled(False)
        self.submit_code_button.setText("Submitting...")
        
        if self.connection_thread:
            self.connection_thread.submit_pairing_code(code)

    def on_pairing_completed(self):
        """Handle pairing completed"""
        self._pairing_in_progress = False
        self.pairing_desc.setText("✅ Pairing completed successfully!")
        self.pairing_progress.hide()
        self.pairing_code_frame.hide()
        self.submit_code_button.hide()
        
        # Move to next page
        QTimer.singleShot(1000, self.go_to_page4)

    def on_pairing_failed(self, error: str):
        """Handle pairing failed"""
        self._pairing_in_progress = False
        self.pairing_desc.setText("❌ Pairing failed")
        self.pairing_progress.hide()
        self.pairing_code_frame.hide()
        self.submit_code_button.hide()
        self.retry_pairing_button.show()
        
        self.pairing_status.setText(f"Error: {error}")
        self.pairing_status.setProperty("status_type", "error")
        self.pairing_status.style().unpolish(self.pairing_status)
        self.pairing_status.style().polish(self.pairing_status)
        self.pairing_status.show()

    def on_connection_established(self):
        """Handle connection established"""
        pass  # Pairing completed will be called

    def on_connection_lost(self, error: str):
        """Handle connection lost"""
        if self._pairing_in_progress:
            self.on_pairing_failed(error)

    def go_to_page4(self):
        """Navigate to page 4"""
        self.current_step = 4
        self.update_progress()
        self.update_summary()
        self.stacked_widget.setCurrentWidget(self.page4)

    def update_progress(self):
        """Update the progress indicator"""
        step_names = ["Device Discovery", "Connection Details", "Pairing", "Name & Finish"]
        self.progress_label.setText(f"Step {self.current_step} of {self.total_steps}: {step_names[self.current_step-1]}")
        self.progress_bar.setValue(self.current_step)

    def update_summary(self):
        """Update the configuration summary on page 4"""
        summary = f"""Android TV Host: {self.host}
Client Name: {self.client_name}
Certificate File: {self.cert_file}
Key File: {self.key_file}"""
        
        self.summary_text.setPlainText(summary)

    def finish_wizard(self):
        """Complete the wizard and save the remote configuration"""
        # Prevent multiple calls to finish_wizard
        if hasattr(self, '_wizard_finished') and self._wizard_finished:
            return
        
        self.remote_name = self.remote_name_input.text().strip()
        if not self.remote_name:
            QMessageBox.warning(self, "Input Error", "Remote name cannot be empty.")
            return

        # Disable the finish button to prevent multiple clicks
        self.finish_button.setEnabled(False)
        self.finish_button.setText("Creating...")
        
        self._wizard_finished = True
        
        saved_remote = {
            "name": self.remote_name,
            "host": self.host,
            "client_name": self.client_name,
            "cert_file": self.cert_file,
            "key_file": self.key_file
        }
        
        # Stop connection thread
        if self.connection_thread and self.connection_thread.isRunning():
            self.connection_thread.stop()
            self.connection_thread.wait()
        
        self.remote_saved.emit(saved_remote, self.remote_index)
        self.accept()

    def apply_styles(self):
        """Apply styling that respects the system theme"""
        # Get the current palette to detect theme
        palette = self.palette()
        is_dark_theme = palette.color(QPalette.ColorRole.Window).lightness() < 128
        
        # Base styling that uses system palette colors
        base_styles = """
            QDialog {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: palette(window);
                color: palette(window-text);
            }
            
            QFrame[class="progress-frame"] {
                background-color: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 8px;
                margin-bottom: 10px;
                padding: 5px;
            }
            
            QLabel[class="progress-label"] {
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 5px;
                color: palette(text);
            }
            
            QProgressBar[class="progress-bar"] {
                border-radius: 4px;
                text-align: center;
                height: 8px;
                background-color: palette(base);
                border: 1px solid palette(mid);
            }
            
            QProgressBar[class="progress-bar"]::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            
            QLabel[class="page-title"] {
                font-size: 18px;
                font-weight: 700;
                margin-bottom: 8px;
                color: palette(highlight);
            }
            
            QLabel[class="page-description"] {
                font-size: 13px;
                margin-bottom: 20px;
                line-height: 1.4;
                color: palette(text);
            }
            
            QLabel[class="field-label"] {
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 5px;
                margin-top: 10px;
                color: palette(text);
            }
            
            QLineEdit[class="input-field"] {
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                border: 2px solid palette(mid);
                background-color: palette(base);
                color: palette(text);
            }
            
            QLineEdit[class="input-field"]:focus {
                border-color: palette(highlight);
                outline: none;
            }
            
            QLabel[class="help-text"] {
                font-size: 11px;
                margin-bottom: 15px;
                font-style: italic;
                color: palette(dark);
            }
            
            QLabel[class="host-display"] {
                font-size: 14px;
                font-weight: bold;
                padding: 8px 12px;
                background-color: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 4px;
                color: palette(text);
            }
            
            QLabel[class="status-message"] {
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                margin: 10px 0;
                min-height: 20px;
            }
            
            QListWidget[class="entity-list"] {
                border-radius: 6px;
                font-size: 12px;
                padding: 5px;
                border: 2px solid palette(mid);
                background-color: palette(base);
                color: palette(text);
            }
            
            QListWidget[class="entity-list"]::item {
                padding: 8px 12px;
                border-radius: 3px;
                margin: 1px;
            }
            
            QListWidget[class="entity-list"]::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            
            QFrame[class="summary-frame"] {
                background-color: palette(alternate-base);
                border-radius: 8px;
                margin: 15px 0;
                border: 1px solid palette(mid);
            }
            
            QLabel[class="summary-title"] {
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 10px;
                color: palette(text);
            }
            
            QTextEdit[class="summary-text"] {
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 8px;
                border: 1px solid palette(mid);
                background-color: palette(base);
                color: palette(text);
            }
            
            QPushButton[class="primary-button"] {
                background-color: palette(highlight);
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
                min-width: 120px;
            }
            
            QPushButton[class="primary-button"]:hover {
                background-color: palette(dark);
                color: #ffffff;
            }
            
            QPushButton[class="primary-button"]:pressed {
                background-color: palette(shadow);
                color: #ffffff;
            }
            
            QPushButton[class="primary-button"]:disabled {
                background-color: palette(mid);
                color: palette(dark);
            }
            
            QPushButton[class="secondary-button"] {
                color: palette(text);
                border: 2px solid palette(mid);
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
                min-width: 100px;
                background-color: palette(base);
            }
            
            QPushButton[class="secondary-button"]:hover {
                border-color: palette(highlight);
                background-color: palette(alternate-base);
                color: palette(text);
            }
            
            QPushButton[class="success-button"] {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
                min-width: 140px;
            }
            
            QPushButton[class="success-button"]:hover {
                background-color: #45A049;
            }
            
            QPushButton[class="success-button"]:pressed {
                background-color: #3D8B40;
            }
            
            QLabel[class="scan-status-label"] {
                font-size: 11px;
                color: palette(dark);
                font-style: italic;
                margin: 2px 0;
            }
        """
        
        # Theme-specific status message colors
        if is_dark_theme:
            theme_specific = """
                QLabel[class="status-message"][status_type="success"] {
                    background-color: #1B5E20;
                    color: #A5D6A7;
                    border: 1px solid #2E7D32;
                    font-weight: 600;
                }
                
                QLabel[class="status-message"][status_type="error"] {
                    background-color: #B71C1C;
                    color: #FFCDD2;
                    border: 1px solid #D32F2F;
                    font-weight: 600;
                }
                
                QLabel[class="status-message"][status_type="info"] {
                    background-color: #0D47A1;
                    color: #BBDEFB;
                    border: 1px solid #1976D2;
                    font-weight: 600;
                }
            """
        else:
            theme_specific = """
                QLabel[class="status-message"][status_type="success"] {
                    background-color: #E8F5E8;
                    color: #2E7D32;
                    border: 1px solid #C8E6C9;
                    font-weight: 600;
                }
                
                QLabel[class="status-message"][status_type="error"] {
                    background-color: #FFEBEE;
                    color: #C62828;
                    border: 1px solid #FFCDD2;
                    font-weight: 600;
                }
                
                QLabel[class="status-message"][status_type="info"] {
                    background-color: #E3F2FD;
                    color: #1565C0;
                    border: 1px solid #BBDEFB;
                    font-weight: 600;
                }
            """
        
        self.setStyleSheet(base_styles + theme_specific)

    def setup_input_validation(self):
        """Setup input validation and keyboard shortcuts for better UX"""
        # Enable Enter key to proceed to next step
        self.host_input.returnPressed.connect(self.validate_page1)
        self.pairing_code_input.returnPressed.connect(self.submit_pairing_code)
        self.remote_name_input.returnPressed.connect(self.finish_wizard, Qt.ConnectionType.UniqueConnection)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for better navigation"""
        if event.key() == Qt.Key.Key_Escape:
            # Handle escape key properly by canceling any ongoing operations
            if self.connection_thread and self.connection_thread.isRunning():
                self.connection_thread.cancel_pairing()
            self.reject()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle dialog close event"""
        # Stop any running threads
        if self.discovery_thread and self.discovery_thread.isRunning():
            self.discovery_thread.terminate()
            self.discovery_thread.wait()
        
        if self.connection_thread and self.connection_thread.isRunning():
            # Cancel pairing first to unblock any waiting operations
            self.connection_thread.cancel_pairing()
            # Then stop the thread
            self.connection_thread.stop()
            # Wait for thread to finish with a timeout to prevent hanging
            if not self.connection_thread.wait(3000):  # 3 second timeout
                self.connection_thread.terminate()
                self.connection_thread.wait()
        
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    wizard = RemoteWizard()
    if wizard.exec() == QDialog.DialogCode.Accepted:
        print("Wizard finished. New remote added.")
    else:
        print("Wizard cancelled.")