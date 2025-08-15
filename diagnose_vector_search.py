#!/usr/bin/env python3
"""
Diagnostic script for troubleshooting vector search issues
Usage: python diagnose_vector_search.py
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if we're in the right environment"""
    print("=== Environment Check ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.executable}")
    
    # Check for required files
    required_files = [
        "config.py", "utils.py", "build_embeddings_all.py", 
        "model_cache.py", "api.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
    
    print()

def check_documents():
    """Check what documents are available"""
    print("=== Document Check ===")
    
    docs_path = "docs"
    if not os.path.exists(docs_path):
        print(f"✗ {docs_path} directory does not exist")
        return False
    
    print(f"✓ {docs_path} directory exists")
    
    # List all files in docs
    files = list(Path(docs_path).rglob("*"))
    if not files:
        print("✗ No files found in docs directory")
        return False
    
    print(f"Files in {docs_path}:")
    document_files = []
    for file in files:
        if file.is_file():
            size = file.stat().st_size
            print(f"  - {file.relative_to(docs_path)} ({size} bytes)")
            if file.suffix.lower() in ['.pdf', '.txt', '.md', '.json']:
                if not file.name.endswith('sample_bucket_metadata_converted.txt'):
                    document_files.append(file)
    
    if document_files:
        print(f"✓ Found {len(document_files)} uploadable documents")
        return True
    else:
        print("✗ Only sample file found - no real documents for embedding")
        return False

def check_vector_index():
    """Check vector index status"""
    print("=== Vector Index Check ===")
    
    index_path = "s3_all_docs"
    chunks_path = "s3_all_chunks.pkl"
    
    if os.path.exists(index_path):
        print(f"✓ {index_path} directory exists")
        
        # Check for FAISS files
        faiss_files = ["index.faiss", "index.pkl"]
        all_exist = True
        for file in faiss_files:
            file_path = os.path.join(index_path, file)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"  ✓ {file} ({size} bytes)")
            else:
                print(f"  ✗ {file} missing")
                all_exist = False
        
        if all_exist:
            print("✓ Vector index appears complete")
        else:
            print("✗ Vector index incomplete")
    else:
        print(f"✗ {index_path} directory does not exist")
    
    if os.path.exists(chunks_path):
        size = os.path.getsize(chunks_path)
        print(f"✓ {chunks_path} exists ({size} bytes)")
    else:
        print(f"✗ {chunks_path} does not exist")
    
    print()

def check_config():
    """Check configuration"""
    print("=== Configuration Check ===")
    
    try:
        from config import (
            DOCS_PATH, VECTOR_INDEX_PATH, EMBED_MODEL, 
            EMBED_DEVICE, VECTOR_SEARCH_K
        )
        
        print(f"✓ Config loaded successfully")
        print(f"  - DOCS_PATH: {DOCS_PATH}")
        print(f"  - VECTOR_INDEX_PATH: {VECTOR_INDEX_PATH}")
        print(f"  - EMBED_MODEL: {EMBED_MODEL}")
        print(f"  - EMBED_DEVICE: {EMBED_DEVICE}")
        print(f"  - VECTOR_SEARCH_K: {VECTOR_SEARCH_K}")
        
    except Exception as e:
        print(f"✗ Config load failed: {e}")
        return False
    
    print()
    return True

def test_imports():
    """Test if required packages can be imported"""
    print("=== Package Import Check ===")
    
    packages = [
        ("langchain_community.embeddings", "HuggingFaceEmbeddings"),
        ("langchain_community.vectorstores", "FAISS"),
        ("langchain.text_splitter", "RecursiveCharacterTextSplitter"),
    ]
    
    all_good = True
    for module, class_name in packages:
        try:
            __import__(module)
            print(f"✓ {module} imported successfully")
        except ImportError as e:
            print(f"✗ {module} import failed: {e}")
            all_good = False
    
    print()
    return all_good

def provide_recommendations():
    """Provide recommendations based on findings"""
    print("=== Recommendations ===")
    
    # Check if vector index exists
    if not os.path.exists("s3_all_docs"):
        print("1. REBUILD VECTOR INDEX: Run 'python build_embeddings_all.py'")
    
    # Check if documents exist
    docs_exist = check_documents_silent()
    if not docs_exist:
        print("2. UPLOAD DOCUMENTS: Add PDF/TXT/MD/JSON files to the 'docs' folder")
    
    # Check if in air-gapped environment
    print("3. AIR-GAPPED SETUP:")
    print("   - Ensure HuggingFace model is pre-downloaded")
    print("   - Check Ollama is running locally")
    print("   - Verify no internet dependencies")
    
    print("4. DEBUGGING:")
    print("   - Check logs during vector search attempts")
    print("   - Verify FAISS index integrity")
    print("   - Test with simple queries first")

def check_documents_silent():
    """Silent version of document check"""
    docs_path = "docs"
    if not os.path.exists(docs_path):
        return False
    
    files = list(Path(docs_path).rglob("*"))
    document_files = []
    for file in files:
        if file.is_file() and file.suffix.lower() in ['.pdf', '.txt', '.md', '.json']:
            if not file.name.endswith('sample_bucket_metadata_converted.txt'):
                document_files.append(file)
    
    return len(document_files) > 0

def main():
    print("Vector Search Diagnostic Tool")
    print("=" * 50)
    
    check_environment()
    check_config()
    test_imports()
    check_documents()
    check_vector_index()
    provide_recommendations()
    
    print("Diagnostic complete!")

if __name__ == "__main__":
    main()