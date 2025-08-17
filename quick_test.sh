#!/bin/bash

# 🧪 Quick Test Setup Script for Enterprise Streamlit UI
# This script prepares your environment for testing the improved interface

echo "🏢 Enterprise Streamlit UI - Quick Test Setup"
echo "============================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python --version 2>&1)
if [[ $? -eq 0 ]]; then
    print_status "Python found: $python_version"
else
    print_error "Python not found. Please install Python 3.8+"
    exit 1
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

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if pip install -r requirements.txt; then
    print_status "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    echo "Try: pip install --upgrade pip"
    echo "Then: pip install -r requirements.txt"
fi

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
echo "📝 Creating test documents..."
cat > docs/test_s3_guide.txt << 'EOF'
# S3 Bucket Management Guide

## Engineering Department Buckets
- eng-data-prod: Production data storage
- eng-backups: Daily backup storage  
- eng-logs: Application log storage

## Configuration
MinIO server configuration for production:
- Memory: 16GB minimum
- Storage: RAID10 recommended
- Network: 10Gb ethernet

## Policies
Default bucket policy allows read/write for department users.
EOF

cat > docs/minio_admin.md << 'EOF'
# MinIO Administration Guide

## Quick Start
1. Install MinIO server
2. Configure storage paths
3. Set up access keys
4. Configure bucket policies

## Troubleshooting
- Check server logs for errors
- Verify network connectivity
- Validate access credentials
EOF

print_status "Created test documents in docs/ directory"

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

echo ""
echo "🎉 Setup Complete! Ready to test the Enterprise UI"
echo "=================================================="
echo ""
echo "To start testing:"
echo "1. Run: streamlit run streamlit_ui.py"
echo "2. Open browser to: http://localhost:8501"
echo "3. Try these test queries:"
echo "   • 'show buckets for engineering'"
echo "   • 'MinIO configuration for production'"
echo "   • 'how to troubleshoot S3 issues'"
echo ""
echo "📖 For detailed testing guide, see: TESTING_STREAMLIT.md"
echo ""
echo "🚀 Starting Streamlit UI now..."
echo ""

# Start Streamlit
streamlit run streamlit_ui.py