@echo off
REM Book Buzz Web App Launcher for Windows

echo.
echo ============================================================
echo   Book Buzz - Web Version
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install/upgrade Flask if needed
echo Installing dependencies...
pip install -r requirements-web.txt --quiet

REM Extract assets
echo.
echo Extracting assets...
python extract_assets.py

REM Start the web app
echo.
echo ============================================================
echo   Starting Book Buzz Web Server...
echo ============================================================
echo.
echo   Open your browser to: http://localhost:5000
echo.
echo   Press Ctrl+C to stop the server
echo ============================================================
echo.

python web_app.py
