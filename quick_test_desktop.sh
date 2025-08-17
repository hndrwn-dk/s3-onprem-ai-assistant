#!/bin/bash

# 🖥️ Quick Test Setup Script for Enterprise Desktop AI Assistant
# This script prepares your environment for testing the improved desktop application

echo "🏢 Enterprise Desktop AI Assistant - Quick Test Setup"
echo "===================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python --version 2>&1)
if [[ $? -eq 0 ]]; then
    print_status "Python found: $python_version"
else
    print_error "Python not found. Please install Python 3.8+"
    exit 1
fi

# Check GUI availability
echo "🖥️  Checking GUI availability..."
if python -c "import tkinter" 2>/dev/null; then
    print_status "GUI backend available"
else
    print_warning "GUI backend not available"
    print_info "On Linux, install with: sudo apt-get install python3-tk python3-dev"
    print_info "On macOS, GUI should be available by default"
    print_info "On Windows, GUI should be available by default"
fi

# Install pywebview
echo "📦 Installing pywebview for desktop app..."
if pip install pywebview; then
    print_status "pywebview installed successfully"
else
    print_error "Failed to install pywebview"
    echo "Try: pip install --upgrade pip"
    echo "Then: pip install pywebview"
fi

# Install other dependencies
echo "📦 Installing other dependencies..."
if pip install -r requirements.txt; then
    print_status "Dependencies installed successfully"
else
    print_error "Failed to install some dependencies"
    print_info "This might be okay if core dependencies are already installed"
fi

# Check if Ollama is installed
echo "🤖 Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    ollama_version=$(ollama --version)
    print_status "Ollama found: $ollama_version"
else
    print_warning "Ollama not found. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p docs cache
print_status "Created docs and cache directories"

# Pull Ollama model
echo "🧠 Checking/pulling phi3:mini model..."
if ollama list | grep -q "phi3:mini"; then
    print_status "phi3:mini model already available"
else
    print_warning "Pulling phi3:mini model (this may take a few minutes)..."
    if ollama pull phi3:mini; then
        print_status "phi3:mini model downloaded successfully"
    else
        print_error "Failed to download phi3:mini model"
        exit 1
    fi
fi

# Create test documents
echo "📝 Creating test documents for desktop app..."
cat > docs/desktop_test_guide.txt << 'EOF'
# Enterprise Desktop AI Assistant Test Guide

## S3 Storage Systems Supported
- Cloudian HyperStore: Enterprise object storage
- IBM Cloud Object Storage: Scalable cloud storage
- MinIO: High-performance object storage
- Dell ECS: Software-defined storage
- NetApp StorageGRID: Hybrid cloud storage

## Desktop App Features
- Native desktop interface
- Professional enterprise design
- Real-time performance metrics
- Integrated file management
- Web interface launcher
- API server management

## Test Queries
Try these queries in the desktop app:
- "Show me MinIO configuration best practices"
- "How to troubleshoot Cloudian storage issues"
- "What are the IBM Cloud Object Storage limits"
- "Dell ECS backup and recovery procedures"
EOF

cat > docs/professional_features.md << 'EOF'
# Professional Features Guide

## Enterprise Dashboard
The desktop application includes:
- Performance metrics tracking
- Query response time monitoring
- Cache hit rate statistics
- System load indicators

## Professional Interface Elements
- Inter font typography
- Glass-morphism design
- Professional color scheme
- Status indicators
- Progress animations
- Native file dialogs

## Business Integration
- Web interface integration
- REST API server
- Document management
- Index building automation
EOF

print_status "Created test documents for desktop app testing"

# Test Ollama connection
echo "🔗 Testing Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    print_status "Ollama server is running and accessible"
else
    print_warning "Starting Ollama server..."
    ollama serve &
    sleep 3
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        print_status "Ollama server started successfully"
    else
        print_error "Failed to start Ollama server"
    fi
fi

# Check current branch
echo "🌿 Checking current branch..."
current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
if [[ "$current_branch" == "cursor/diagnose-vector-search-index-read-issue-efab" ]]; then
    print_status "On correct branch: $current_branch"
else
    print_warning "Current branch: $current_branch"
    print_info "ultra_modern_app.py is available on branch: cursor/diagnose-vector-search-index-read-issue-efab"
fi

echo ""
echo "🎉 Desktop App Setup Complete!"
echo "==============================="
echo ""
echo "🖥️  To test the Enterprise Desktop AI Assistant:"
echo "1. Run: python ultra_modern_app.py"
echo "2. A native desktop window will open"
echo "3. Test these features:"
echo "   • 🔍 Execute Query: 'show MinIO configuration'"
echo "   • 📁 Upload Documents: Add your S3 documentation"
echo "   • 🔄 Rebuild Index: Build searchable knowledge base"
echo "   • 🌐 Web Interface: Launch Streamlit web UI"
echo "   • 🔌 API Server: Start REST API server"
echo ""
echo "📖 For detailed testing guide, see: TESTING_DESKTOP_APP.md"
echo ""
echo "🚀 Starting Desktop Application now..."
echo ""

# Check if ultra_modern_app.py exists
if [[ -f "ultra_modern_app.py" ]]; then
    print_status "ultra_modern_app.py found - launching desktop application"
    python ultra_modern_app.py
else
    print_error "ultra_modern_app.py not found in current directory"
    print_info "Make sure you're on the correct branch: cursor/diagnose-vector-search-index-read-issue-efab"
    print_info "Run: git checkout cursor/diagnose-vector-search-index-read-issue-efab"
fi