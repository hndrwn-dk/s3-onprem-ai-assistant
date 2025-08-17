#!/usr/bin/env python
"""
Simple Web Interface Startup - Reliable Fallback
Starts the Streamlit web interface with the same enterprise design
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "success": "✅",
        "warning": "⚠️ ",
        "error": "❌",
        "info": "ℹ️ "
    }
    print(f"{colors.get(status, '')} {message}")

def check_streamlit():
    """Check if Streamlit is available"""
    try:
        import streamlit
        print_status("Streamlit available", "success")
        return True
    except ImportError:
        print_status("Streamlit not installed", "error")
        print("Installing Streamlit...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'streamlit'])
            print_status("Streamlit installed successfully", "success")
            return True
        except Exception as e:
            print_status(f"Failed to install Streamlit: {e}", "error")
            return False

def start_web_interface():
    """Start the Streamlit web interface"""
    if not Path("streamlit_ui.py").exists():
        print_status("streamlit_ui.py not found", "error")
        return False
    
    try:
        print_status("Starting S3 On-Premise AI Assistant Web Interface...", "info")
        print("🌐 Opening at: http://localhost:8501")
        print("❌ To stop: Press Ctrl+C in this terminal")
        print("-" * 50)
        
        # Start Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_ui.py',
            '--server.port', '8501',
            '--server.headless', 'false'
        ])
        
        return True
        
    except KeyboardInterrupt:
        print_status("Web interface stopped by user", "info")
        return True
    except Exception as e:
        print_status(f"Failed to start web interface: {e}", "error")
        return False

def main():
    print("🏢 S3 On-Premise AI Assistant - Web Interface")
    print("=" * 50)
    print("🌐 Reliable web-based interface with enterprise design")
    print("✅ Same features as desktop app")
    print("✅ Same professional appearance")
    print("✅ Works when desktop app has issues")
    print()
    
    # Check Streamlit
    if not check_streamlit():
        print("❌ Cannot start web interface without Streamlit")
        return
    
    # Start web interface
    if start_web_interface():
        print_status("Web interface session completed", "success")
    else:
        print_status("Web interface failed to start", "error")
        print("💡 Try installing dependencies: pip install streamlit")

if __name__ == "__main__":
    main()