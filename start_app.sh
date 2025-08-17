#!/bin/bash

# 🏢 S3 On-Premise AI Assistant - Smart Startup Script
# Automatically detects python version and starts the app

echo "🏢 S3 On-Premise AI Assistant - Starting..."
echo "============================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Detect Python
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
    print_status "Using python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    print_status "Using python3"
else
    print_error "Python not found. Please install Python 3.8+"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
print_status "Python version: $PYTHON_VERSION"

# Quick dependency check
echo "🔍 Checking dependencies..."
if $PYTHON_CMD -c "import webview" 2>/dev/null; then
    print_status "PyWebView available"
else
    print_error "PyWebView missing. Install with: pip install pywebview"
    echo "Installing PyWebView..."
    pip install pywebview
fi

# Check if ultra_modern_app.py exists
if [ ! -f "ultra_modern_app.py" ]; then
    print_error "ultra_modern_app.py not found in current directory"
    exit 1
fi

# Start the desktop app
echo ""
print_status "Starting Enterprise Desktop AI Assistant..."
echo "Window will open in a few seconds..."
echo ""

# Run the app
$PYTHON_CMD ultra_modern_app.py

# If app exits, show message
echo ""
print_status "Desktop app closed. Thank you for using S3 On-Premise AI Assistant!"