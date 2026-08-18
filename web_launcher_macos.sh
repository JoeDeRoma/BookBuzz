#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES_DIR="$DIR/../Resources"

# Activate virtual environment
source "$RESOURCES_DIR/venv/bin/activate"

# Change to resources directory
cd "$RESOURCES_DIR"

# Start the Flask app in the background
python web_app.py &
PID=$!

# Wait for server to start (give it 3 seconds)
sleep 3

# Open browser
open "http://localhost:5000"

# Wait for the app to finish
wait $PID
