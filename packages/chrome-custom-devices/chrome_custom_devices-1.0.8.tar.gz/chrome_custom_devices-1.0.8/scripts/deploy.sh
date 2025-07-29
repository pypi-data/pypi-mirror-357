#!/bin/bash
# Deployment script for Chrome Custom Devices

set -e

VERSION="1.0.0"
REPO_URL="https://github.com/hatimmakki/chrome-custom-devices"

echo "🚀 Chrome Custom Devices - Deployment Script"
echo "=============================================="
echo "Version: $VERSION"
echo ""

# Check if we're in the right directory
if [ ! -f "chrome_devices_manager.py" ]; then
    echo "❌ Must be run from the project root directory"
    exit 1
fi

# Check if git is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Git working directory is not clean. Please commit your changes first."
    exit 1
fi

echo "✅ Git working directory is clean"

# Build and test Python package
echo "📦 Building Python package..."
python -m pip install --upgrade build twine
python -m build

echo "🧪 Testing Python package..."
python -m twine check dist/*

# Test npm package
echo "📦 Testing npm package..."
npm pack --dry-run

echo ""
echo "🎯 Ready for deployment!"
echo ""
echo "Next steps:"
echo "1. Push to GitHub:"
echo "   git push origin main"
echo ""
echo "2. Create and push tag:"
echo "   git tag v$VERSION"
echo "   git push origin v$VERSION"
echo ""
echo "3. The GitHub Action will automatically:"
echo "   ✅ Run tests on multiple platforms"
echo "   ✅ Deploy to PyPI"
echo "   ✅ Deploy to npm"
echo "   ✅ Create GitHub release"
echo ""
echo "4. Manual steps:"
echo "   📝 Submit Homebrew formula to homebrew-tap"
echo "   📢 Announce on social media"
echo "   🎉 Celebrate!"
echo ""
echo "🔗 Repository: $REPO_URL"
