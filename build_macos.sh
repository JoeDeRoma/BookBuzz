#!/bin/bash
# Build standalone macOS .app bundle for Book Buzz
# Run this on a Mac: bash build_macos.sh

set -e

echo "📦 Building Book Buzz for macOS..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "Install via: brew install python3"
    exit 1
fi

PYTHON_VER=$(python3 --version | awk '{print $2}')
echo "✅ Using Python $PYTHON_VER"

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install PyInstaller PySide6 pandas numpy pillow

# Extract assets
echo "Extracting asset packs..."
python3 extract_assets.py

# Generate icon
echo "Generating app icon..."
python3 create_icon.py

# Build the .app bundle
echo "Building macOS .app bundle..."
python3 -m PyInstaller \
  --noconfirm \
  --onedir \
  --windowed \
  --name=BookBuzz \
  --icon=bookclub.ico \
  --add-data=assets:assets \
  --add-data=bookclub.ico:. \
  --hidden-import=PySide6 \
  --hidden-import=pandas \
  --hidden-import=numpy \
  --hidden-import=PIL \
  --osx-bundle-identifier=com.bookbuzz.app \
  --codesign-identity=- \
  app.py

# Get app size
APP_PATH="dist/BookBuzz.app"
APP_SIZE=$(du -sh "$APP_PATH" | awk '{print $1}')

# Remove quarantine attribute
xattr -d com.apple.quarantine "$APP_PATH" 2>/dev/null || true

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ SUCCESS! macOS app bundle created!"
echo "════════════════════════════════════════════════════════════"
echo "Location: $APP_PATH"
echo "Size: $APP_SIZE"
echo ""
echo "To run the app:"
echo "  open dist/BookBuzz.app"
echo ""
echo "To install system-wide:"
echo "  mv dist/BookBuzz.app /Applications/"
echo ""
echo "You can now share dist/BookBuzz.app with others!"
echo "════════════════════════════════════════════════════════════"

# Deactivate venv
deactivate
