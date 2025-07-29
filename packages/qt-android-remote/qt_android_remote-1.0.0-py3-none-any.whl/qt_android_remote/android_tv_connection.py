"""
Android TV Connection Handler

Manages the connection to Android TV devices using androidtvremote2.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from PySide6.QtCore import Signal, QThread

from androidtvremote2 import (
    AndroidTVRemote,
    CannotConnect,
    ConnectionClosed,
    InvalidAuth,
)

from .remote_manager import get_certs_dir

_LOGGER = logging.getLogger(__name__)


class AndroidTVConnectionThread(QThread):
    """Thread for handling Android TV connection operations"""
    
    # Signals
    connection_established = Signal()
    connection_lost = Signal(str)  # error message
    pairing_started = Signal()
    pairing_code_required = Signal()
    pairing_completed = Signal()
    pairing_failed = Signal(str)  # error message
    device_info_updated = Signal(dict)
    is_on_updated = Signal(bool)
    current_app_updated = Signal(str)
    volume_info_updated = Signal(dict)
    is_available_updated = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.remote: Optional[AndroidTVRemote] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._should_stop = False
        self._pairing_code: Optional[str] = None
        self._pairing_event: Optional[asyncio.Event] = None
        
    def setup_remote(self, host: str, client_name: str, cert_file: str, key_file: str):
        """Setup the Android TV remote configuration"""
        certs_dir = get_certs_dir()
        cert_path = certs_dir / cert_file
        key_path = certs_dir / key_file
        
        self.host = host
        self.client_name = client_name
        self.cert_file = str(cert_path)
        self.key_file = str(key_path)
        
    def run(self):
        """Main thread execution"""
        try:
            # Create new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Run the async main function
            self.loop.run_until_complete(self._async_main())
        except Exception as e:
            _LOGGER.error(f"Error in connection thread: {e}")
            self.connection_lost.emit(str(e))
        finally:
            if self.loop:
                # Properly cleanup any remaining tasks before closing the loop
                self._cleanup_tasks()
                self.loop.close()
    
    async def _async_main(self):
        """Main async function for the connection thread"""
        try:
            self.remote = AndroidTVRemote(
                self.client_name,
                self.cert_file,
                self.key_file,
                self.host
            )
            
            # Setup callbacks
            self.remote.add_is_on_updated_callback(self._on_is_on_updated)
            self.remote.add_current_app_updated_callback(self._on_current_app_updated)
            self.remote.add_volume_info_updated_callback(self._on_volume_info_updated)
            self.remote.add_is_available_updated_callback(self._on_is_available_updated)
            
            # Generate certificate if missing
            if await self.remote.async_generate_cert_if_missing():
                _LOGGER.info("Generated new certificate")
                await self._handle_pairing()
            
            # Try to connect
            while not self._should_stop:
                try:
                    await self.remote.async_connect()
                    self.connection_established.emit()
                    
                    # Emit device info
                    if self.remote.device_info:
                        self.device_info_updated.emit(self.remote.device_info)
                    
                    # Keep reconnecting
                    self.remote.keep_reconnecting(self._on_invalid_auth)
                    
                    # Wait for stop signal
                    while not self._should_stop:
                        await asyncio.sleep(0.1)
                    
                    break
                    
                except InvalidAuth:
                    _LOGGER.error("Need to pair again")
                    await self._handle_pairing()
                except (CannotConnect, ConnectionClosed) as exc:
                    _LOGGER.error(f"Cannot connect: {exc}")
                    self.connection_lost.emit(str(exc))
                    break
                    
        except Exception as e:
            _LOGGER.error(f"Error in async main: {e}")
            self.connection_lost.emit(str(e))
    
    async def _handle_pairing(self):
        """Handle the pairing process"""
        try:
            # Check if we should stop before starting
            if self._should_stop or not self.remote:
                return
                
            # Get device name and MAC
            name, mac = await self.remote.async_get_name_and_mac()
            _LOGGER.info(f"Found device: {name} ({mac})")
            
            # Check if we should stop before starting pairing
            if self._should_stop or not self.remote:
                return
            
            # Start pairing
            self.pairing_started.emit()
            await self.remote.async_start_pairing()
            
            # Wait for pairing code with timeout and cancellation support
            self.pairing_code_required.emit()
            self._pairing_event = asyncio.Event()
            
            # Wait for pairing code or cancellation with timeout
            try:
                await asyncio.wait_for(self._pairing_event.wait(), timeout=300.0)  # 5 minute timeout
            except asyncio.TimeoutError:
                self.pairing_failed.emit("Pairing timed out after 5 minutes")
                return
            
            # Check if pairing was cancelled
            if self._should_stop or not self.remote:
                return
            
            if self._pairing_code:
                await self.remote.async_finish_pairing(self._pairing_code)
                self.pairing_completed.emit()
            else:
                self.pairing_failed.emit("Pairing was cancelled")
                
        except InvalidAuth as exc:
            _LOGGER.error(f"Invalid pairing code: {exc}")
            self.pairing_failed.emit(str(exc))
        except ConnectionClosed as exc:
            _LOGGER.error(f"Pairing connection closed: {exc}")
            self.pairing_failed.emit(str(exc))
        except asyncio.CancelledError:
            _LOGGER.info("Pairing was cancelled")
            self.pairing_failed.emit("Pairing was cancelled")
        except Exception as exc:
            _LOGGER.error(f"Pairing error: {exc}")
            self.pairing_failed.emit(str(exc))
    
    def submit_pairing_code(self, code: str):
        """Submit the pairing code from the UI"""
        self._pairing_code = code
        if self._pairing_event and self.loop:
            self.loop.call_soon_threadsafe(self._pairing_event.set)
    
    def cancel_pairing(self):
        """Cancel the pairing process"""
        self._pairing_code = None
        if self._pairing_event and self.loop:
            self.loop.call_soon_threadsafe(self._pairing_event.set)
    
    def send_key_command(self, key_code: str):
        """Send a key command to the Android TV"""
        if self.remote and self.loop:
            self.loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._async_send_key_command(key_code))
            )
    
    def send_key_command_with_direction(self, key_code: str, direction: str = "SHORT"):
        """Send a key command to the Android TV with specific direction"""
        if self.remote and self.loop:
            self.loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._async_send_key_command_with_direction(key_code, direction))
            )
    
    async def _async_send_key_command(self, key_code: str):
        """Async version of send_key_command"""
        try:
            if self.remote:
                self.remote.send_key_command(key_code)
        except Exception as e:
            _LOGGER.error(f"Error sending key command {key_code}: {e}")
    
    async def _async_send_key_command_with_direction(self, key_code: str, direction: str):
        """Async version of send_key_command_with_direction"""
        try:
            if self.remote:
                self.remote.send_key_command(key_code, direction)
        except Exception as e:
            _LOGGER.error(f"Error sending key command {key_code} with direction {direction}: {e}")
    
    def send_text(self, text: str):
        """Send text to the Android TV"""
        if self.remote and self.loop:
            self.loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._async_send_text(text))
            )
    
    async def _async_send_text(self, text: str):
        """Async version of send_text"""
        try:
            if self.remote:
                self.remote.send_text(text)
        except Exception as e:
            _LOGGER.error(f"Error sending text: {e}")
    
    def send_launch_app_command(self, app_link: str):
        """Launch an app on the Android TV"""
        if self.remote and self.loop:
            self.loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._async_send_launch_app_command(app_link))
            )
    
    async def _async_send_launch_app_command(self, app_link: str):
        """Async version of send_launch_app_command"""
        try:
            if self.remote:
                self.remote.send_launch_app_command(app_link)
        except Exception as e:
            _LOGGER.error(f"Error launching app {app_link}: {e}")
    
    def stop(self):
        """Stop the connection thread"""
        self._should_stop = True
        if self.remote:
            if self.loop:
                self.loop.call_soon_threadsafe(self.remote.disconnect)
            else:
                self.remote.disconnect()
    
    def _on_is_on_updated(self, is_on: bool):
        """Callback for when is_on is updated"""
        self.is_on_updated.emit(is_on)
    
    def _on_current_app_updated(self, current_app: str):
        """Callback for when current_app is updated"""
        self.current_app_updated.emit(current_app)
    
    def _on_volume_info_updated(self, volume_info: Dict[str, Any]):
        """Callback for when volume_info is updated"""
        self.volume_info_updated.emit(volume_info)
    
    def _on_is_available_updated(self, is_available: bool):
        """Callback for when is_available is updated"""
        self.is_available_updated.emit(is_available)
    
    def _on_invalid_auth(self):
        """Callback for when authentication becomes invalid"""
        self.connection_lost.emit("Authentication invalid - need to pair again")
    
    async def _async_cleanup(self):
        """Async cleanup of the remote connection and tasks"""
        try:
            if self.remote:
                # Disconnect the remote
                self.remote.disconnect()
                
                # Wait a bit for any pending operations to complete
                await asyncio.sleep(0.1)
                
        except Exception as e:
            _LOGGER.error(f"Error during async cleanup: {e}")
    
    def _cleanup_tasks(self):
        """Cleanup any remaining asyncio tasks before closing the loop"""
        try:
            if not self.loop:
                return
                
            # Get all pending tasks
            pending_tasks = [task for task in asyncio.all_tasks(self.loop) if not task.done()]
            
            if pending_tasks:
                _LOGGER.info(f"Cleaning up {len(pending_tasks)} pending tasks")
                
                # Cancel all pending tasks
                for task in pending_tasks:
                    task.cancel()
                
                # Wait for all tasks to be cancelled
                if pending_tasks:
                    # Use run_until_complete to wait for cancellation
                    try:
                        self.loop.run_until_complete(
                            asyncio.gather(*pending_tasks, return_exceptions=True)
                        )
                    except Exception as e:
                        _LOGGER.debug(f"Expected exception during task cleanup: {e}")
                        
        except Exception as e:
            _LOGGER.error(f"Error during task cleanup: {e}")