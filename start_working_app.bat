@echo off
echo.
echo 🏢 S3 On-Premise AI Assistant - Working Version
echo ===============================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found
    pause
    exit /b 1
)

echo ✅ Python available
python --version
echo.

REM Check if file exists
if not exist "working_app.py" (
    echo ❌ working_app.py not found
    pause
    exit /b 1
)

echo ✅ Starting working version...
echo 🔍 This version has simplified JavaScript that should work
echo 💡 Check console for debug output
echo.

REM Start the working app
python working_app.py

echo.
echo ✅ App closed
pause