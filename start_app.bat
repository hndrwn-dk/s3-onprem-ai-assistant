@echo off
REM S3 On-Premise AI Assistant - Windows Startup Script
echo.
echo 🏢 S3 On-Premise AI Assistant - Starting...
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if ultra_modern_app.py exists
if not exist "ultra_modern_app.py" (
    echo ❌ ultra_modern_app.py not found in current directory
    pause
    exit /b 1
)

REM Quick dependency check
echo.
echo 🔍 Checking dependencies...
python -c "import webview" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PyWebView missing. Installing...
    pip install pywebview
    if %errorlevel% neq 0 (
        echo ❌ Failed to install PyWebView
        pause
        exit /b 1
    )
)

echo ✅ PyWebView available
echo.
echo ✅ Starting Enterprise Desktop AI Assistant...
echo Window will open in a few seconds...
echo.

REM Start the desktop app
python ultra_modern_app.py

REM If app exits, show message
echo.
echo ✅ Desktop app closed. Thank you for using S3 On-Premise AI Assistant!
pause