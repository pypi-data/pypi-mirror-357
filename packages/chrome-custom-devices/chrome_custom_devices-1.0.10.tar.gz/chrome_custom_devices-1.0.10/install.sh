#!/bin/bash
# Chrome Custom Devices Manager - Installation Script

set -e

echo "🚀 Chrome Custom Devices Manager - Installation Script"
echo "======================================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if we're in the right directory
if [ ! -f "chrome_devices_manager.py" ]; then
    echo "❌ chrome_devices_manager.py not found in current directory."
    echo "   Please run this script from the project root directory."
    exit 1
fi

# Make the script executable
chmod +x chrome_devices_manager.py

echo "✅ Made chrome_devices_manager.py executable"

# Test the script
echo "🧪 Testing the script..."
python3 chrome_devices_manager.py --help > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Script test passed!"
else
    echo "❌ Script test failed!"
    exit 1
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📖 Usage Examples:"
echo "   python3 chrome_devices_manager.py --output vibranium"
echo "   python3 chrome_devices_manager.py --install"
echo "   python3 chrome_devices_manager.py --list-profiles"
echo ""
echo "📚 For more information, see README.md"
