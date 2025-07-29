#!/bin/bash
# Chrome Custom Devices Manager - Demo Script

echo "🎯 Chrome Custom Devices Manager - Demo"
echo "========================================"
echo ""

echo "📋 Available installation methods:"
echo ""

echo "1️⃣  One-Command Remote Installation (Easiest):"
echo "   curl -sSL https://raw.githubusercontent.com/user/repo/main/quick-install.sh | bash"
echo ""

echo "2️⃣  Local Installation - All Profiles:"
echo "   python chrome_devices_manager.py --install-all"
echo ""

echo "3️⃣  Local Installation - Single Profile:"
echo "   python chrome_devices_manager.py --install"
echo ""

echo "4️⃣  List Chrome Profiles:"
echo "   python chrome_devices_manager.py --list-profiles"
echo ""

echo "5️⃣  Generate for Vibranium CLI:"
echo "   python chrome_devices_manager.py --output vibranium"
echo ""

echo "🔧 Quick test - List your Chrome profiles:"
python3 chrome_devices_manager.py --list-profiles

echo ""
echo "✨ Ready to install? Run one of the commands above!"
echo "   The easiest is method 1 (remote installation)"
echo ""
echo "📱 This will install 22 custom device presets including:"
echo "   • MacBook models (12\", 13\", 15\", 16\") from 2014-2021"
echo "   • iMac 24\" - 2021"
echo "   • MacBook Air models"
echo "   • Notebooks with touch and HiDPI screens" 
echo "   • Dell Latitude 3420"
echo "   • Microsoft Surface Duo"
echo "   • Generic notebook"
echo ""
echo "🎉 After installation, restart Chrome and check DevTools > Settings > Devices"
