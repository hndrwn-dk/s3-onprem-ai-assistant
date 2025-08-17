#!/usr/bin/env python3
"""
Quick diagnostic script to check what's working
"""

import sys
import os
from pathlib import Path

def check_python():
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Python executable: {sys.executable}")

def check_basic_imports():
    """Test basic imports"""
    print("\n🔍 Testing basic imports...")
    
    imports_to_test = [
        ("time", "time"),
        ("pathlib", "Path"),
        ("os", "os"),
        ("sys", "sys")
    ]
    
    for module_name, import_name in imports_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}")
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")

def check_project_imports():
    """Test project-specific imports"""
    print("\n🔍 Testing project imports...")
    
    project_imports = [
        "model_cache",
        "response_cache", 
        "bucket_index",
        "config"
    ]
    
    for module in project_imports:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {e}")

def check_optional_imports():
    """Test optional dependencies"""
    print("\n🔍 Testing optional dependencies...")
    
    optional_imports = [
        ("webview", "pywebview"),
        ("streamlit", "streamlit"),
        ("requests", "requests")
    ]
    
    for module_name, package_name in optional_imports:
        try:
            __import__(module_name)
            print(f"  ✅ {package_name}")
        except Exception as e:
            print(f"  ❌ {package_name}: {e}")

def check_files():
    """Check if required files exist"""
    print("\n📁 Checking required files...")
    
    required_files = [
        "ultra_modern_app.py",
        "fast_start.py", 
        "performance_test.py",
        "model_cache.py",
        "response_cache.py",
        "bucket_index.py",
        "config.py"
    ]
    
    for filename in required_files:
        if Path(filename).exists():
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename} (missing)")

def check_directories():
    """Check directories"""
    print("\n📂 Checking directories...")
    
    dirs_to_check = [
        ("docs", "Document storage"),
        ("cache", "Cache storage"),
        ("s3_all_docs", "Vector index")
    ]
    
    for dirname, description in dirs_to_check:
        path = Path(dirname)
        if path.exists():
            if path.is_dir():
                file_count = len(list(path.glob("*")))
                print(f"  ✅ {dirname}/ ({file_count} files) - {description}")
            else:
                print(f"  ⚠️  {dirname} exists but is not a directory")
        else:
            print(f"  ❌ {dirname}/ (missing) - {description}")

def test_simple_app():
    """Test a simple version of the app"""
    print("\n🧪 Testing simple app functionality...")
    
    try:
        # Test basic webview import
        import webview
        print("  ✅ PyWebView import successful")
        
        # Test simple window creation (don't start)
        window = webview.create_window(
            'Test Window',
            html='<h1>Test</h1>',
            width=400,
            height=300
        )
        print("  ✅ Window creation successful")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ PyWebView not available: {e}")
        print("     Install with: pip3 install pywebview")
        return False
    except Exception as e:
        print(f"  ❌ Window creation failed: {e}")
        return False

def show_solutions():
    """Show common solutions"""
    print("\n🔧 Common Solutions:")
    print("=" * 40)
    print("1. Install missing dependencies:")
    print("   pip3 install pywebview streamlit requests")
    print()
    print("2. Use python3 instead of python:")
    print("   python3 ultra_modern_app.py")
    print("   python3 fast_start.py")
    print()
    print("3. Check if Ollama is running:")
    print("   curl http://localhost:11434/api/tags")
    print("   ollama serve  # if not running")
    print()
    print("4. Create missing directories:")
    print("   mkdir -p docs cache")
    print()
    print("5. Add test documents:")
    print("   echo 'Test S3 documentation' > docs/test.txt")

def main():
    print("🏢 S3 On-Premise AI Assistant - Diagnostic Check")
    print("=" * 50)
    
    check_python()
    check_basic_imports()
    check_project_imports()
    check_optional_imports()
    check_files()
    check_directories()
    
    app_works = test_simple_app()
    
    print("\n" + "=" * 50)
    if app_works:
        print("🎉 Basic functionality works!")
        print("Try: python3 ultra_modern_app.py")
    else:
        print("⚠️  Issues detected. See solutions below.")
    
    show_solutions()

if __name__ == "__main__":
    main()