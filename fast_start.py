#!/usr/bin/env python3
"""
Fast Start Script for S3 On-Premise AI Assistant
Pre-warms system components for optimal performance
"""

import time
import sys
import os
from pathlib import Path

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "success": "\033[92m✅",
        "warning": "\033[93m⚠️ ",
        "error": "\033[91m❌",
        "info": "\033[94mℹ️ "
    }
    print(f"{colors.get(status, '')} {message}\033[0m")

def pre_warm_system():
    """Pre-warm system components for faster response"""
    print("🔥 Pre-warming system components...")
    
    try:
        # Pre-load model cache
        print_status("Loading model cache...", "info")
        start = time.time()
        from model_cache import ModelCache
        
        # Pre-load LLM
        llm = ModelCache.get_llm()
        llm_time = time.time() - start
        print_status(f"LLM loaded in {llm_time:.2f}s", "success")
        
        # Pre-load response cache
        start = time.time()
        from response_cache import response_cache
        cache_time = time.time() - start
        print_status(f"Response cache loaded in {cache_time:.3f}s", "success")
        
        # Pre-load bucket index
        start = time.time()
        from bucket_index import bucket_index
        bucket_time = time.time() - start
        print_status(f"Bucket index loaded in {bucket_time:.3f}s", "success")
        
        # Try to pre-load vector store (if available)
        try:
            start = time.time()
            vector_store = ModelCache.get_vector_store()
            vs_time = time.time() - start
            print_status(f"Vector store loaded in {vs_time:.2f}s", "success")
        except Exception:
            print_status("Vector store not available (build index first)", "warning")
        
        return True
        
    except Exception as e:
        print_status(f"Pre-warming failed: {e}", "error")
        return False

def check_performance_setup():
    """Check if system is optimized for performance"""
    print("\n🔍 Checking performance setup...")
    
    checks = []
    
    # Check if Ollama is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            print_status("Ollama server is running", "success")
            checks.append(True)
            
            # Check if phi3:mini is available
            models = response.json().get('models', [])
            if any('phi3' in model.get('name', '') for model in models):
                print_status("phi3:mini model is available", "success")
                checks.append(True)
            else:
                print_status("phi3:mini model not found", "warning")
                print("         Run: ollama pull phi3:mini")
                checks.append(False)
        else:
            print_status("Ollama server not responding", "error")
            checks.append(False)
    except Exception:
        print_status("Ollama not running", "error")
        print("         Start with: ollama serve")
        checks.append(False)
    
    # Check docs directory
    docs_path = Path("docs")
    if docs_path.exists() and any(docs_path.iterdir()):
        doc_count = len(list(docs_path.glob("*")))
        print_status(f"Documents available: {doc_count} files", "success")
        checks.append(True)
    else:
        print_status("No documents in docs/ directory", "warning")
        print("         Upload documents for better search results")
        checks.append(False)
    
    # Check if vector index exists
    if Path("s3_all_docs").exists():
        print_status("Vector index exists", "success")
        checks.append(True)
    else:
        print_status("Vector index not found", "warning")
        print("         Build index for faster vector search")
        checks.append(False)
    
    return all(checks)

def start_desktop_app():
    """Start the optimized desktop application"""
    print("\n🖥️  Starting Desktop Application...")
    
    if not Path("ultra_modern_app.py").exists():
        print_status("ultra_modern_app.py not found", "error")
        return False
    
    try:
        # Check if pywebview is available
        import webview
        print_status("PyWebView available", "success")
        
        # Start the application
        print_status("Launching desktop application...", "info")
        from ultra_modern_app import main
        main()
        
        return True
        
    except ImportError:
        print_status("PyWebView not installed", "error")
        print("         Install with: pip install pywebview")
        return False
    except Exception as e:
        print_status(f"Failed to start desktop app: {e}", "error")
        return False

def start_streamlit_app():
    """Start the Streamlit web application"""
    print("\n🌐 Starting Streamlit Web Interface...")
    
    if not Path("streamlit_ui.py").exists():
        print_status("streamlit_ui.py not found", "error")
        return False
    
    try:
        import streamlit
        print_status("Streamlit available", "success")
        
        # Start streamlit
        print_status("Launching Streamlit web interface...", "info")
        print("         Opening in browser at: http://localhost:8501")
        
        import subprocess
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_ui.py',
            '--server.port', '8501'
        ])
        
        return True
        
    except ImportError:
        print_status("Streamlit not installed", "error")
        print("         Install with: pip install streamlit")
        return False
    except Exception as e:
        print_status(f"Failed to start Streamlit: {e}", "error")
        return False

def show_quick_tips():
    """Show quick performance tips"""
    print("\n⚡ Quick Performance Tips:")
    print("=" * 30)
    print("🏆 FASTEST: Use cached queries (<0.1s)")
    print("🥇 FAST: Use bucket search queries (0.1-1s)")
    print("🥈 GOOD: Use vector search after building index (1-5s)")
    print("🥉 SLOW: First-time complex queries (5-30s)")
    print("\n💡 Pro tip: Build the index once, then enjoy fast queries!")

def main():
    print("🚀 S3 On-Premise AI Assistant - Fast Start")
    print("=" * 45)
    
    # Pre-warm system
    if pre_warm_system():
        print_status("System pre-warming complete", "success")
    else:
        print_status("Some components failed to pre-warm", "warning")
    
    # Check performance setup
    performance_ready = check_performance_setup()
    
    if performance_ready:
        print_status("System optimized for high performance", "success")
    else:
        print_status("System needs optimization", "warning")
    
    show_quick_tips()
    
    print("\n" + "=" * 45)
    print("🎯 Choose your interface:")
    print("1. Desktop App (Recommended for best performance)")
    print("2. Web Interface (Browser-based)")
    print("3. Performance Test")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                if start_desktop_app():
                    break
            elif choice == "2":
                if start_streamlit_app():
                    break
            elif choice == "3":
                os.system("python performance_test.py")
                break
            elif choice == "4":
                print_status("Goodbye!", "info")
                break
            else:
                print_status("Invalid choice. Please enter 1-4.", "warning")
                
        except KeyboardInterrupt:
            print_status("\nGoodbye!", "info")
            break
        except Exception as e:
            print_status(f"Error: {e}", "error")

if __name__ == "__main__":
    main()