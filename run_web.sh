#!/bin/bash
# Book Buzz Web App Launcher for macOS and Linux

echo ""
echo "============================================================"
echo "  Book Buzz - Web Version"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Install via: brew install python3"
    exit 1
fi

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements-web.txt --quiet

# Extract assets
echo ""
echo "Extracting assets..."
python3 extract_assets.py

# Start the web app
echo ""
echo "============================================================"
echo "  Starting Book Buzz Web Server..."
echo "============================================================"
echo ""
echo "  Open your browser to: http://localhost:5000"
echo ""
echo "  Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

python3 web_app.py
