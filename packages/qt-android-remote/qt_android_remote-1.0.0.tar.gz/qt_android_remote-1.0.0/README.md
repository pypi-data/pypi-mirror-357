# QT Android Remote

<div align="center">
  <img src="images/logo.png" alt="QT Android Remote Logo" width="128" height="128">
</div>

A desktop remote control application for Android TV devices using direct connection via the androidtvremote2 protocol.

## Screenshot

<div align="center">
  <img src="images/screenshot.png" alt="QT Android Remote Application Screenshot" width="400">
</div>

## Features

- **Direct Connection**: Connect directly to Android TV devices without requiring Home Assistant
- **Device Discovery**: Automatically discover Android TV devices on your network using Zeroconf
- **Pairing Wizard**: Easy step-by-step pairing process with Android TV devices
- **Full Remote Control**: Complete remote control functionality including:
  - D-pad navigation (arrow keys, OK button)
  - Power control
  - Volume control and mute
  - Media controls (play/pause, stop, rewind, fast forward)
  - Home and back buttons
  - App launching (YouTube, Netflix, and custom apps)
  - Text input support
- **Keyboard Shortcuts**: Control your Android TV using keyboard shortcuts
- **Multiple Remotes**: Manage multiple Android TV devices
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **System Theme Support**: Automatically adapts to your system's light/dark theme

## Installation

### From PyPI (Recommended)

```bash
pip install qt-android-remote
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/dmarkey/qt-android-remote.git
cd qt-android-remote
```

2. Install dependencies:
```bash
pip install -e .
```

## Usage

### Starting the Application

```bash
qt-android-remote
```

Or if installed from source:
```bash
python -m qt_android_remote.main
```

### Setting Up Your First Remote

1. **Launch the application** and click the "+" button to add a new remote
2. **Device Discovery**: 
   - Click "Scan Network" to automatically discover Android TV devices
   - Or manually enter your Android TV's IP address
3. **Connection Details**: Configure the client name that will appear on your Android TV
4. **Pairing**: 
   - The app will connect to your Android TV and start the pairing process
   - A pairing dialog will appear on your Android TV screen
   - Enter the 6-digit pairing code shown on your TV
5. **Name Your Remote**: Give your remote a descriptive name
6. **Done**: Your remote is now ready to use!

### Keyboard Shortcuts

- **Arrow Keys**: Navigate (D-pad)
- **Enter/Space**: OK/Select
- **Escape/Backspace**: Back
- **Home**: Home button
- **M**: Menu
- **P**: Power
- **+/-**: Volume up/down

### Supported Android TV Devices

This application works with any Android TV device that supports the Android TV Remote protocol v2, including:

- NVIDIA SHIELD TV
- Google Chromecast with Google TV
- Sony Android TVs
- Philips Android TVs
- TCL Android TVs
- And many more Android TV devices

## Requirements

- Python 3.10 or higher
- PySide6
- androidtvremote2
- zeroconf
- cryptography
- protobuf

## Configuration

Configuration files are stored in platform-specific locations:

- **Windows**: `%APPDATA%\QTAndroidRemote\`
- **macOS**: `~/Library/Application Support/QTAndroidRemote/`
- **Linux**: `~/.config/qt-android-remote/`

The configuration includes:
- `remotes.json`: Remote configurations
- `certs/`: SSL certificates for each paired device

## Troubleshooting

### Cannot Discover Devices

1. Ensure your Android TV and computer are on the same network
2. Check that your Android TV has "Network remote control" enabled:
   - Go to Settings > Device Preferences > About > Android TV OS build
   - Click 7 times to enable Developer options
   - Go to Settings > Device Preferences > Developer options
   - Enable "Network debugging"

### Pairing Issues

1. Make sure your Android TV is turned on and connected to the network
2. Try restarting the Android TV Remote Service:
   - Go to Settings > Apps > See all apps > Show system apps
   - Find "Android TV Remote Service"
   - Force stop and restart it
3. Clear the Android TV Remote Service data if pairing continues to fail

### Connection Problems

1. Verify the IP address is correct
2. Check firewall settings on both devices
3. Ensure the Android TV Remote Service is running
4. Try re-pairing the device

## Development

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/dmarkey/qt-android-remote.git
cd qt-android-remote
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black qt_android_remote/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [androidtvremote2](https://github.com/tronikos/androidtvremote2) - The underlying Android TV remote protocol implementation
- [ha-desktop-remote](https://github.com/dmarkey/ha-desktop-remote) - UI inspiration and design patterns
- Google's Android TV Remote protocol documentation

## Related Projects

- [androidtvremote2](https://github.com/tronikos/androidtvremote2) - Python library for Android TV remote protocol
- [ha-desktop-remote](https://github.com/dmarkey/ha-desktop-remote) - Home Assistant desktop remote control

## Support

If you encounter any issues or have questions, please:

1. Check the [troubleshooting section](#troubleshooting)
2. Search existing [GitHub issues](https://github.com/dmarkey/qt-android-remote/issues)
3. Create a new issue with detailed information about your problem

## Changelog

### v1.0.0
- Initial release
- Direct Android TV connection support
- Device discovery via Zeroconf
- Complete pairing wizard
- Full remote control functionality
- Keyboard shortcuts
- Multi-device support
- Cross-platform compatibility