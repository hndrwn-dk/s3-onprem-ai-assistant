#!/bin/bash

# Setup script for air-gapped S3 AI Assistant
# This script helps diagnose and fix vector search issues

echo "=== S3 AI Assistant - Air-Gapped Setup ==="
echo

# Check if we're in the right directory
if [ ! -f "build_embeddings_all.py" ]; then
    echo "❌ Error: build_embeddings_all.py not found!"
    echo "   Please run this script from the project root directory"
    exit 1
fi

echo "✅ Found build_embeddings_all.py in current directory"

# Check docs folder
if [ ! -d "docs" ]; then
    echo "📁 Creating docs directory..."
    mkdir -p docs
fi

echo "📁 Checking docs folder contents:"
doc_count=$(find docs -name "*.pdf" -o -name "*.txt" -o -name "*.json" -o -name "*.md" | grep -v sample_bucket_metadata_converted.txt | wc -l)

if [ $doc_count -eq 0 ]; then
    echo "❌ No uploaded documents found in docs folder"
    echo "   Please upload your S3 vendor PDFs/documents to the 'docs' folder before proceeding"
    echo "   Supported formats: PDF, TXT, MD, JSON"
    exit 1
else
    echo "✅ Found $doc_count uploadable documents in docs folder"
fi

# Check if vector index exists
echo
echo "🔍 Checking vector index status:"
if [ -d "s3_all_docs" ] && [ -f "s3_all_docs/index.faiss" ] && [ -f "s3_all_docs/index.pkl" ]; then
    echo "✅ Vector index exists and appears complete"
    index_size=$(du -sh s3_all_docs | cut -f1)
    echo "   Index size: $index_size"
else
    echo "❌ Vector index missing or incomplete"
    echo "   Will need to rebuild vector index"
    NEED_REBUILD=1
fi

if [ -f "s3_all_chunks.pkl" ]; then
    chunk_size=$(du -sh s3_all_chunks.pkl | cut -f1)
    echo "✅ Chunks file exists ($chunk_size)"
else
    echo "❌ Chunks file missing"
    NEED_REBUILD=1
fi

# Check Python environment
echo
echo "🐍 Checking Python environment:"
if command -v python3 &> /dev/null; then
    echo "✅ Python3 found: $(python3 --version)"
else
    echo "❌ Python3 not found!"
    exit 1
fi

# Check if we need to rebuild
if [ "$NEED_REBUILD" = "1" ]; then
    echo
    echo "🔧 Vector index needs to be rebuilt"
    echo "   This will process all documents in the docs folder"
    echo
    read -p "   Do you want to rebuild the vector index now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Building vector index..."
        if python3 build_embeddings_all.py; then
            echo "✅ Vector index built successfully!"
        else
            echo "❌ Vector index build failed!"
            echo "   Check the error messages above"
            echo "   Common issues:"
            echo "   - Missing Python dependencies (langchain, faiss, etc.)"
            echo "   - Insufficient memory for large documents"
            echo "   - No internet access for downloading embedding models"
            exit 1
        fi
    else
        echo "⏭️  Skipping rebuild - you can run 'python3 build_embeddings_all.py' later"
    fi
fi

# Final status check
echo
echo "📊 Final Status:"
if [ -d "s3_all_docs" ] && [ -f "s3_all_chunks.pkl" ]; then
    echo "✅ Vector search should now work properly"
    echo "✅ Uploaded documents will be searchable"
    echo "✅ System will not fall back to sample file"
else
    echo "❌ Vector search will still fall back to sample file"
    echo "   Please rebuild the vector index with uploaded documents"
fi

echo
echo "🔧 Troubleshooting tips:"
echo "   - Ensure all PDFs are in the 'docs' folder"
echo "   - Run 'python3 diagnose_vector_search.py' for detailed diagnostics"
echo "   - Check logs during API startup for vector loading errors"
echo "   - For air-gapped setups, pre-download HuggingFace models"

echo
echo "=== Setup Complete ==="