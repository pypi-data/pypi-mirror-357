# Chrome Custom Devices Manager

[![PyPI version](https://badge.fury.io/py/chrome-custom-devices.svg)](https://badge.fury.io/py/chrome-custom-devices)
[![npm version](https://badge.fury.io/js/chrome-custom-devices.svg)](https://badge.fury.io/js/chrome-custom-devices)
[![GitHub release](https://img.shields.io/github/release/hatimmakki/chrome-custom-devices.svg)](https://github.com/hatimmakki/chrome-custom-devices/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-blue)](https://github.com/hatimmakki/chrome-custom-devices)

Add 22+ desktop device presets to Chrome DevTools with one command. Perfect for testing responsive designs on MacBooks, iMacs, and other desktop resolutions.

## Features

- ✅ Safe modification of Chrome Preferences (no core file changes)
- ✅ Multiple installation methods (direct, Vibranium CLI, manual)
- ✅ Cross-platform support (Windows, macOS, Linux)
- ✅ Automatic backup and rollback functionality
- ✅ Proper user agent generation for different device types
- ✅ Support for both portrait and landscape orientations
- ✅ Chrome process detection and safety warnings

## Quick Start

### Method 1: One-Command Remote Installation (Easiest)
```bash
# Install to ALL Chrome profiles with one command
curl -sSL https://raw.githubusercontent.com/hatimmakki/chrome-custom-devices/main/quick-install.sh | bash
```

### Method 2: Python Package (PyPI)
```bash
# Install via pip
pip install chrome-custom-devices

# Run installation
chrome-devices --install-all
```

### Method 3: Node.js Package (npm)
```bash
# Install globally via npm
npm install -g chrome-custom-devices

# Run installation
chrome-devices
```

### Method 4: Homebrew (macOS)
```bash
# Add tap and install
brew tap hatimmakki/tap
brew install chrome-custom-devices

# Run installation
chrome-devices --install-all
```

### Method 5: Local Development
```bash
# Clone and install locally
git clone https://github.com/hatimmakki/chrome-custom-devices.git
cd chrome-custom-devices
pip install -e .
chrome-devices --install-all
```

### Method 6: Using Vibranium CLI
```bash
# Install Vibranium globally
npm install -g @pittankopta/vibranium

# Generate and install devices
chrome-devices --output vibranium
npx @pittankopta/vibranium add devices.json
```

## Device List

The script includes the following devices:

| Device Name | Width | Height | DPR | Type |
|-------------|-------|--------|-----|------|
| Apple MacBook 12-inch | 2304 | 1310 | 2 | Desktop |
| Apple MacBook Pro 13-inch | 2560 | 1470 | 2 | Desktop |
| Apple MacBook Pro 15-inch | 2880 | 1670 | 2 | Desktop |
| iMac 24 - 2021 | 2048 | 1152 | 2 | Desktop |
| MacBook PRO 16 - 2021 | 1728 | 1117 | 2 | Desktop |
| MacBook Air 13 - 2020 | 1280 | 800 | 2 | Desktop |
| MacBook Pro 16 - 2019 | 1536 | 960 | 2 | Desktop |
| MacBook Pro 13 - 2018 | 1280 | 800 | 2 | Desktop |
| MacBook Air 13 - 2018 | 1280 | 800 | 2 | Desktop |
| MacBook Pro 15 - 2018 | 1440 | 900 | 2 | Desktop |
| MacBook Pro 13 Pro - 2017 | 1440 | 900 | 2 | Desktop |
| MacBook Pro 15 Pro - 2017 | 1280 | 800 | 2 | Desktop |
| MacBook Pro 13 Pro - 2016 | 1280 | 800 | 2 | Desktop |
| MacBook Pro 15 Pro - 2016 | 1440 | 900 | 2 | Desktop |
| MacBook Pro 13 Pro - 2015 | 1280 | 800 | 2 | Desktop |
| MacBook Pro 15 Pro - 2015 | 1440 | 900 | 2 | Desktop |
| MacBook Pro 15 Pro - 2014 | 1440 | 900 | 2 | Desktop |
| Notebook with touch | 1280 | 950 | 1 | Desktop |
| Notebook with HiDPI screen | 1440 | 900 | 2 | Desktop |
| Dell Latitude 3420 14 | 1440 | 809 | 1 | Desktop |
| Microsoft Surface Duo | 1114 | 705 | 2.5 | Mobile |
| Generic notebook | 1280 | 800 | 1 | Desktop |

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/chrome-custom-devices.git
cd chrome-custom-devices
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the script:
```bash
python chrome_devices_manager.py --help
```

## Usage

### One-Command Remote Installation
```bash
# The easiest way - installs to ALL Chrome profiles automatically
curl -sSL https://raw.githubusercontent.com/user/repo/main/quick-install.sh | bash
```

### Python Script Commands
```bash
# Show help
python chrome_devices_manager.py --help

# Install to ALL Chrome profiles automatically (NEW!)
python chrome_devices_manager.py --install-all

# Install to a single Chrome profile (with selection)
python chrome_devices_manager.py --install

# List all found Chrome profiles
python chrome_devices_manager.py --list-profiles

# Generate Vibranium-compatible JSON
python chrome_devices_manager.py --output vibranium

# Generate manual installation files
python chrome_devices_manager.py --output manual

# Backup current Chrome settings
python chrome_devices_manager.py --backup

# Restore from backup
python chrome_devices_manager.py --restore backup_20231215_143022.json
```

### Advanced Examples
```bash
# Install to a specific profile
python chrome_devices_manager.py --install --profile "/path/to/Chrome/Profile/Preferences"

# Backup a specific profile
python chrome_devices_manager.py --backup --profile "/path/to/Chrome/Profile/Preferences"

# Generate devices JSON in different formats
python chrome_devices_manager.py --output preferences  # For direct modification
python chrome_devices_manager.py --output manual       # For manual installation
python chrome_devices_manager.py --output vibranium    # For Vibranium CLI
```

## Safety Features

- **Automatic Backup**: Creates timestamped backups before any modifications
- **Chrome Detection**: Warns if Chrome is running during installation
- **Profile Detection**: Automatically finds Chrome profiles on your system
- **Rollback Support**: Easy restoration from backups
- **Validation**: Verifies JSON structure before installation

## Supported Platforms

- **Windows**: Chrome, Chrome Beta, Chrome Dev, Chrome Canary
- **macOS**: Chrome, Chrome Beta, Chrome Dev, Chrome Canary
- **Linux**: Chrome, Chromium, Chrome Beta, Chrome Dev

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your devices to the `devices.py` file
4. Test your changes
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

### v1.1.0 (2025-06-22)
- Added one-command remote installation script (`quick-install.sh`)
- Added `--install-all` flag to install to ALL Chrome profiles automatically
- Enhanced cross-platform support for Chrome variants (Beta, Dev, Canary, Arc, Chromium)
- Improved user experience with colored output and progress indicators
- Added comprehensive profile detection and display
- Self-contained bash script with embedded device data

### v1.0.0 (2025-06-22)
- Initial release
- Support for 22 custom devices
- Multiple installation methods
- Cross-platform compatibility
- Automatic backup and restore functionality

## Troubleshooting

### Chrome settings are overridden
- Make sure Chrome is completely closed before running the script
- Check that you're modifying the correct profile

### Devices don't appear in DevTools
- Restart Chrome after installation
- Check DevTools > Settings > Devices
- Verify the JSON structure in your Preferences file

### Permission errors
- Run with administrator/sudo privileges if needed
- Check file permissions on Chrome profile directory

## Credits

- Inspired by [mfehrenbach's Chrome device dimensions gist](https://gist.github.com/mfehrenbach/aaf646bee2e8880b5142d92e20b633d4)
- Uses [Vibranium CLI tool](https://github.com/Pittan/vibranium) for automated installation
- Based on Chrome DevTools device emulation API
