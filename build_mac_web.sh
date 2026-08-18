#!/bin/bash
set -e

echo "🍎 Building Book Buzz Web App for macOS..."
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

PYTHON=$(which python3)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BUILD_DIR="$SCRIPT_DIR/build_mac_web"
APP_DIR="$BUILD_DIR/BookBuzz.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

echo "📦 Setting up Python virtual environment..."
"$PYTHON" -m venv "$RESOURCES_DIR/venv"
source "$RESOURCES_DIR/venv/bin/activate"

echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

echo "📋 Copying application files..."
cp "$SCRIPT_DIR/web_app.py" "$RESOURCES_DIR/"
cp -r "$SCRIPT_DIR/templates" "$RESOURCES_DIR/"
cp -r "$SCRIPT_DIR/static" "$RESOURCES_DIR/"
cp -r "$SCRIPT_DIR/engine" "$RESOURCES_DIR/"

echo "🔧 Creating launcher script..."
cat > "$MACOS_DIR/BookBuzz" << 'EOF'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES_DIR="$DIR/../Resources"
source "$RESOURCES_DIR/venv/bin/activate"
cd "$RESOURCES_DIR"
python web_app.py &
PID=$!
sleep 3
open "http://localhost:5000"
wait $PID
EOF
chmod +x "$MACOS_DIR/BookBuzz"

echo "📄 Creating Info.plist..."
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>BookBuzz</string>
    <key>CFBundleIdentifier</key>
    <string>com.bookbuzz.app</string>
    <key>CFBundleName</key>
    <string>Book Buzz</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
EOF

echo ""
echo "=================================================="
echo "✅ Build complete!"
echo "=================================================="
echo ""
echo "📦 Location: $APP_DIR"
echo ""
echo "To use the app:"
echo "  1. Find 'BookBuzz.app' in Finder (build_mac_web folder)"
echo "  2. Double-click to run"
echo "  3. A browser window will open automatically"
echo "  4. If not, go to: http://localhost:5000"
echo ""
echo "Note: The first run may take 10-15 seconds to start."
echo ""
