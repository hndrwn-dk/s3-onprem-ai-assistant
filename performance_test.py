#!/usr/bin/env python3
"""
Performance Testing Script for S3 On-Premise AI Assistant
Tests both desktop and web interfaces for speed optimization
"""

import time
import subprocess
import sys
import os
from pathlib import Path

def test_import_speed():
    """Test how fast key modules load"""
    print("🧪 Testing Import Performance...")
    
    modules_to_test = [
        'model_cache',
        'response_cache', 
        'bucket_index',
        'build_embeddings_all'
    ]
    
    for module in modules_to_test:
        start = time.time()
        try:
            __import__(module)
            load_time = time.time() - start
            print(f"  ✅ {module}: {load_time:.3f}s")
        except Exception as e:
            print(f"  ❌ {module}: Failed - {e}")

def test_cache_performance():
    """Test response cache speed"""
    print("\n💾 Testing Cache Performance...")
    
    try:
        from response_cache import response_cache
        
        # Test cache write
        start = time.time()
        response_cache.set("test_query", "test_response", "test_source")
        write_time = time.time() - start
        print(f"  ✅ Cache Write: {write_time:.4f}s")
        
        # Test cache read
        start = time.time()
        result = response_cache.get("test_query")
        read_time = time.time() - start
        print(f"  ✅ Cache Read: {read_time:.4f}s")
        
        if result:
            print(f"  ✅ Cache Hit: Success")
        else:
            print(f"  ❌ Cache Hit: Failed")
            
    except Exception as e:
        print(f"  ❌ Cache Test Failed: {e}")

def test_bucket_index_speed():
    """Test bucket index quick search speed"""
    print("\n🔍 Testing Bucket Index Performance...")
    
    try:
        from bucket_index import bucket_index
        
        test_queries = [
            "engineering",
            "production", 
            "backup",
            "logs"
        ]
        
        for query in test_queries:
            start = time.time()
            result = bucket_index.quick_search(query)
            search_time = time.time() - start
            
            if result:
                print(f"  ✅ '{query}': {search_time:.3f}s (Found)")
            else:
                print(f"  ⚠️  '{query}': {search_time:.3f}s (No results)")
                
    except Exception as e:
        print(f"  ❌ Bucket Index Test Failed: {e}")

def test_model_loading():
    """Test model loading performance"""
    print("\n🤖 Testing Model Loading Performance...")
    
    try:
        from model_cache import ModelCache
        
        # Test LLM loading
        start = time.time()
        llm = ModelCache.get_llm()
        llm_time = time.time() - start
        print(f"  ✅ LLM Loading: {llm_time:.3f}s")
        
        # Test vector store loading (if available)
        try:
            start = time.time()
            vector_store = ModelCache.get_vector_store()
            vs_time = time.time() - start
            print(f"  ✅ Vector Store Loading: {vs_time:.3f}s")
        except Exception as e:
            print(f"  ⚠️  Vector Store: Not available ({e})")
            
    except Exception as e:
        print(f"  ❌ Model Loading Test Failed: {e}")

def test_desktop_app_startup():
    """Test desktop app startup time"""
    print("\n🖥️  Testing Desktop App Startup...")
    
    if not Path("ultra_modern_app.py").exists():
        print("  ❌ ultra_modern_app.py not found")
        return
    
    try:
        # Test import time
        start = time.time()
        import webview
        webview_time = time.time() - start
        print(f"  ✅ WebView Import: {webview_time:.3f}s")
        
        print("  ℹ️  Desktop app startup test requires manual verification")
        print("     Run: python ultra_modern_app.py")
        
    except ImportError:
        print("  ⚠️  PyWebView not installed. Install with: pip install pywebview")
    except Exception as e:
        print(f"  ❌ Desktop App Test Failed: {e}")

def test_streamlit_startup():
    """Test Streamlit startup time"""
    print("\n🌐 Testing Streamlit Startup...")
    
    if not Path("streamlit_ui.py").exists():
        print("  ❌ streamlit_ui.py not found")
        return
    
    try:
        # Test streamlit import
        start = time.time()
        import streamlit
        st_time = time.time() - start
        print(f"  ✅ Streamlit Import: {st_time:.3f}s")
        
        print("  ℹ️  Streamlit startup test requires manual verification")
        print("     Run: streamlit run streamlit_ui.py")
        
    except ImportError:
        print("  ❌ Streamlit not installed")
    except Exception as e:
        print(f"  ❌ Streamlit Test Failed: {e}")

def check_ollama_performance():
    """Check Ollama performance"""
    print("\n🤖 Testing Ollama Performance...")
    
    try:
        import requests
        
        # Test Ollama connection
        start = time.time()
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        connection_time = time.time() - start
        
        if response.status_code == 200:
            print(f"  ✅ Ollama Connection: {connection_time:.3f}s")
            
            # Test model availability
            models = response.json().get('models', [])
            phi3_available = any('phi3' in model.get('name', '') for model in models)
            
            if phi3_available:
                print(f"  ✅ phi3:mini Model: Available")
            else:
                print(f"  ❌ phi3:mini Model: Not found. Run: ollama pull phi3:mini")
        else:
            print(f"  ❌ Ollama Connection: Failed")
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Ollama: Not running. Start with: ollama serve")
    except Exception as e:
        print(f"  ❌ Ollama Test Failed: {e}")

def show_performance_recommendations():
    """Show performance optimization recommendations"""
    print("\n🚀 Performance Optimization Recommendations:")
    print("=" * 50)
    
    recommendations = [
        ("📁 Document Management", [
            "Keep docs/ folder under 100 files for best performance",
            "Use TXT/MD files when possible (faster than PDF)",
            "Remove unused documents to reduce index size"
        ]),
        ("🧠 Model Optimization", [
            "Use phi3:mini model (fastest, good quality)",
            "Keep Ollama running in background",
            "Ensure sufficient RAM (4GB+ recommended)"
        ]),
        ("⚡ Query Optimization", [
            "Use specific keywords for faster bucket search",
            "Repeated queries use cache (sub-second response)",
            "Build index once, query many times"
        ]),
        ("🖥️  System Optimization", [
            "Use SSD storage for faster file access",
            "Close unnecessary applications",
            "Use desktop app for best performance"
        ])
    ]
    
    for category, tips in recommendations:
        print(f"\n{category}:")
        for tip in tips:
            print(f"  • {tip}")

def main():
    print("🏢 S3 On-Premise AI Assistant - Performance Test")
    print("=" * 50)
    
    # Run all performance tests
    test_import_speed()
    test_cache_performance()
    test_bucket_index_speed()
    test_model_loading()
    check_ollama_performance()
    test_desktop_app_startup()
    test_streamlit_startup()
    
    print("\n" + "=" * 50)
    print("🏁 Performance Test Complete")
    
    show_performance_recommendations()
    
    print("\n" + "=" * 50)
    print("🎯 Quick Performance Summary:")
    print("• Cache hits should be <0.1s")
    print("• Quick search should be <1s") 
    print("• Vector search should be <5s")
    print("• Index building: 30s-5min (one-time)")
    print("\n💡 For best experience: Upload docs → Build index → Query")

if __name__ == "__main__":
    main()