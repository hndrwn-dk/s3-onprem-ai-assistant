#!/usr/bin/env python
"""
Working Desktop App - S3 On-Premise AI Assistant
Simplified version with proper JavaScript syntax
"""

import webview
import threading
import subprocess
import sys
import os
import json
import time
from pathlib import Path
from tkinter import filedialog
import tkinter as tk

class S3AIWebApp:
    def __init__(self):
        self.api = S3AIWebAPI()
        
    def create_window(self):
        """Create the webview window with working interface"""
        html_content = self.get_html_content()
        
        window = webview.create_window(
            'S3 On-Premise AI Assistant',
            html=html_content,
            js_api=self.api,
            width=1400,
            height=900,
            min_size=(1200, 700),
            resizable=True,
            shadow=True
        )
        
        return window
    
    def run(self):
        """Start the application with debugging"""
        try:
            window = self.create_window()
            print("✅ Desktop window created successfully")
            print("🔍 Debug mode enabled - check console for API calls")
            print("🌐 Window should open in a few seconds...")
            print("-" * 60)
            webview.start(debug=True)
        except Exception as e:
            print(f"❌ Desktop app failed: {e}")
            print("🌐 Try web interface: python start_web.py")
    
    def get_html_content(self):
        """Generate working HTML interface"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>S3 On-Premise AI Assistant</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #3b82f6;
            --primary-dark: #2563eb;
            --slate-50: #f8fafc;
            --slate-100: #f1f5f9;
            --slate-200: #e2e8f0;
            --slate-300: #cbd5e1;
            --slate-500: #64748b;
            --slate-700: #334155;
            --slate-800: #1e293b;
            --white: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            color: var(--slate-800);
            font-size: 0.85rem;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 1rem;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, var(--slate-800) 0%, var(--slate-700) 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            text-align: center;
            color: white;
        }
        
        .header h1 {
            font-size: 1.75rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .header .subtitle {
            font-size: 0.85rem;
            opacity: 0.9;
            line-height: 1.4;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 1.5rem;
        }
        
        .sidebar {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--slate-200);
            height: fit-content;
        }
        
        .sidebar h3 {
            font-size: 1rem;
            font-weight: 600;
            color: var(--slate-800);
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--slate-200);
        }
        
        .btn {
            width: 100%;
            padding: 0.75rem 1rem;
            margin-bottom: 0.75rem;
            border: none;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: 'Inter', sans-serif;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: var(--white);
            box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
        }
        
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
        }
        
        .btn-secondary {
            background: var(--white);
            color: var(--slate-700);
            border: 1px solid var(--slate-300);
        }
        
        .btn-secondary:hover {
            background: var(--slate-50);
            transform: translateY(-1px);
        }
        
        .main-content {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--slate-200);
        }
        
        .card h3 {
            font-size: 1rem;
            font-weight: 600;
            color: var(--slate-800);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.75rem;
        }
        
        .metric-card {
            background: linear-gradient(135deg, var(--white) 0%, var(--slate-50) 100%);
            border: 1px solid var(--slate-200);
            border-radius: 8px;
            padding: 0.75rem;
            text-align: center;
        }
        
        .metric-label {
            font-size: 0.6rem;
            font-weight: 600;
            color: var(--slate-500);
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }
        
        .metric-value {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--slate-800);
            font-family: 'JetBrains Mono', monospace;
        }
        
        .query-input {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid var(--slate-300);
            border-radius: 8px;
            font-size: 0.9rem;
            font-family: 'Inter', sans-serif;
            margin-bottom: 1rem;
        }
        
        .query-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .results-area {
            background: var(--slate-50);
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
            border: 1px solid var(--slate-200);
            min-height: 200px;
            max-height: 400px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            line-height: 1.5;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        
        .alert {
            padding: 0.75rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .alert-success {
            background: #dcfce7;
            color: #166534;
            border: 1px solid #bbf7d0;
        }
        
        .alert-error {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }
        
        .alert-info {
            background: #dbeafe;
            color: #1e40af;
            border: 1px solid #bfdbfe;
        }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.65rem;
            font-weight: 600;
            text-transform: uppercase;
            gap: 0.25rem;
        }
        
        .loading {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--slate-500);
            font-size: 0.8rem;
        }
        
        .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid var(--slate-300);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 S3 On-Premise AI Assistant</h1>
            <p class="subtitle">Fully offline-capable AI assistant for answering operational, admin, and troubleshooting questions for on-premises S3-compatible platforms</p>
        </div>
        
        <div class="main-grid">
            <div class="sidebar">
                <h3>⚡ Quick Actions</h3>
                
                <button class="btn btn-primary" onclick="executeQuery()">
                    🔍 Execute Query
                </button>
                
                <button class="btn btn-secondary" onclick="uploadFiles()">
                    📁 Upload Documents
                </button>
                
                <button class="btn btn-secondary" onclick="buildIndex()">
                    🔄 Rebuild Index
                </button>
                
                <button class="btn btn-secondary" onclick="openWebUI()">
                    🌐 Web Interface
                </button>
                
                <button class="btn btn-secondary" onclick="startAPI()">
                    🔌 API Server
                </button>
            </div>
            
            <div class="main-content">
                <div class="card">
                    <h3>📈 Performance Dashboard</h3>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-label">🚀 Query Response</div>
                            <div class="metric-value" id="response-time">--</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">💾 Cache Hit Rate</div>
                            <div class="metric-value" id="cache-rate">0%</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">🔍 Total Queries</div>
                            <div class="metric-value" id="query-count">0</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">📊 System Load</div>
                            <div class="metric-value" id="system-load">Ready</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>💬 Query Interface</h3>
                    <input 
                        type="text" 
                        class="query-input" 
                        id="queryInput" 
                        placeholder="Enter your query (e.g., 'Show all buckets for engineering department')"
                        onkeypress="handleKeyPress(event)"
                    >
                    
                    <div id="status-message" class="loading" style="display: none;">
                        <div class="spinner"></div>
                        <span>Processing...</span>
                    </div>
                    
                    <div id="results" class="results-area">
                        Ready to process your queries...
                        
                        Performance Tips:
                        • First-time queries: 1-5 seconds
                        • Repeated queries: under 0.1 seconds (cached)
                        • Upload docs then build index for best results
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        console.log('JavaScript loaded successfully');
        
        let queryCount = 0;
        let cacheHits = 0;
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                executeQuery();
            }
        }
        
        async function executeQuery() {
            console.log('executeQuery called');
            
            const queryInput = document.getElementById('queryInput');
            const query = queryInput.value.trim();
            
            console.log('Query:', query);
            
            if (!query) {
                alert('Please enter a query');
                return;
            }
            
            queryCount++;
            updateMetric('query-count', queryCount);
            
            setStatus('Processing query...');
            
            const startTime = performance.now();
            
            try {
                console.log('Calling API...');
                const result = await pywebview.api.query(query);
                console.log('API result:', result);
                
                const endTime = performance.now();
                const responseTime = ((endTime - startTime) / 1000).toFixed(2);
                
                updateMetric('response-time', responseTime + 's');
                
                if (result.cached) {
                    cacheHits++;
                    updateMetric('cache-rate', Math.round((cacheHits / queryCount) * 100) + '%');
                }
                
                displayResult(result, responseTime);
                
            } catch (error) {
                console.error('Query error:', error);
                displayError(error.message);
            } finally {
                setStatus('');
            }
        }
        
        async function uploadFiles() {
            console.log('uploadFiles called');
            
            try {
                console.log('Calling upload API...');
                const result = await pywebview.api.upload_files();
                console.log('Upload result:', result);
                
                if (result.success) {
                    alert('Successfully uploaded ' + result.count + ' files');
                } else {
                    alert('Upload failed: ' + result.error);
                }
            } catch (error) {
                console.error('Upload error:', error);
                alert('Upload error: ' + error.message);
            }
        }
        
        async function buildIndex() {
            console.log('buildIndex called');
            
            if (!confirm('Build index? This may take 30 seconds to 5 minutes.')) {
                return;
            }
            
            setStatus('Building index...');
            
            try {
                console.log('Calling build API...');
                const result = await pywebview.api.build_index();
                console.log('Build result:', result);
                
                if (result.success) {
                    alert('Index built successfully!');
                } else {
                    alert('Build failed: ' + result.error);
                }
            } catch (error) {
                console.error('Build error:', error);
                alert('Build error: ' + error.message);
            } finally {
                setStatus('');
            }
        }
        
        async function openWebUI() {
            console.log('openWebUI called');
            
            try {
                console.log('Calling web UI API...');
                const result = await pywebview.api.open_web_ui();
                console.log('Web UI result:', result);
                
                if (result.success) {
                    alert('Web interface starting... Browser will open in 3 seconds');
                } else {
                    alert('Failed to start web UI: ' + result.error);
                }
            } catch (error) {
                console.error('Web UI error:', error);
                alert('Web UI error: ' + error.message);
            }
        }
        
        async function startAPI() {
            console.log('startAPI called');
            
            try {
                console.log('Calling start API...');
                const result = await pywebview.api.start_api();
                console.log('API start result:', result);
                
                if (result.success) {
                    alert('API server started at http://localhost:8000');
                } else {
                    alert('Failed to start API: ' + result.error);
                }
            } catch (error) {
                console.error('API start error:', error);
                alert('API start error: ' + error.message);
            }
        }
        
        function displayResult(result, responseTime) {
            const resultsDiv = document.getElementById('results');
            const timestamp = new Date().toLocaleTimeString();
            
            let statusText = '';
            if (result.cached) {
                statusText = 'Cached Result';
            } else if (result.source === 'quick_search') {
                statusText = 'Quick Search';
            } else if (result.source === 'vector') {
                statusText = 'Vector Search';
            } else {
                statusText = 'Fallback Search';
            }
            
            resultsDiv.innerHTML = statusText + ' • ' + responseTime + 's • ' + timestamp + '\\n\\n' + result.answer;
        }
        
        function displayError(error) {
            const resultsDiv = document.getElementById('results');
            const timestamp = new Date().toLocaleTimeString();
            resultsDiv.innerHTML = 'Error • ' + timestamp + '\\n\\n' + error;
        }
        
        function setStatus(message) {
            const statusDiv = document.getElementById('status-message');
            const statusText = statusDiv.querySelector('span');
            
            if (message) {
                statusText.textContent = message;
                statusDiv.style.display = 'flex';
            } else {
                statusDiv.style.display = 'none';
            }
        }
        
        function updateMetric(metricId, value) {
            const element = document.getElementById(metricId);
            if (element) {
                element.textContent = value;
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM loaded');
            document.getElementById('queryInput').focus();
        });
        
        // Test API availability
        window.addEventListener('pywebviewready', function() {
            console.log('PyWebView ready');
        });
    </script>
</body>
</html>
        '''

class S3AIWebAPI:
    """Simplified API for testing"""
    
    def __init__(self):
        print("🔧 API: Initializing...")
        self._model_cache = None
        self._response_cache = None
        self._bucket_index = None
        
    def _get_model_cache(self):
        if self._model_cache is None:
            from model_cache import ModelCache
            self._model_cache = ModelCache
        return self._model_cache
    
    def _get_response_cache(self):
        if self._response_cache is None:
            from response_cache import response_cache
            self._response_cache = response_cache
        return self._response_cache
    
    def _get_bucket_index(self):
        if self._bucket_index is None:
            from bucket_index import bucket_index
            self._bucket_index = bucket_index
        return self._bucket_index
    
    def query(self, query_text):
        """Simple query handler with debug output"""
        print(f"🔍 API: Query received: '{query_text}'")
        start_time = time.time()
        
        try:
            # Check cache first
            print("🔍 API: Checking cache...")
            response_cache = self._get_response_cache()
            cached_response = response_cache.get(query_text)
            
            if cached_response:
                print(f"⚡ API: Cache hit!")
                return {
                    "answer": cached_response,
                    "source": "cache",
                    "cached": True,
                    "success": True,
                    "response_time": time.time() - start_time
                }
            
            # Try quick search
            print("🚀 API: Trying quick search...")
            bucket_index = self._get_bucket_index()
            quick_result = bucket_index.quick_search(query_text)
            
            if quick_result:
                print("🚀 API: Quick search found results!")
                response_cache.set(query_text, quick_result, "quick_search")
                return {
                    "answer": quick_result,
                    "source": "quick_search",
                    "cached": False,
                    "success": True,
                    "response_time": time.time() - start_time
                }
            
            print("⚠️ API: No quick results, returning default message")
            return {
                "answer": "No results found. Try uploading documents and building the index.",
                "source": "no_results",
                "cached": False,
                "success": False,
                "response_time": time.time() - start_time
            }
            
        except Exception as e:
            print(f"❌ API: Query error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "answer": f"Error: {str(e)}",
                "source": "error",
                "cached": False,
                "success": False,
                "response_time": time.time() - start_time
            }
    
    def upload_files(self):
        """Simple file upload with debug"""
        print("📁 API: Upload files called")
        
        try:
            root = tk.Tk()
            root.withdraw()
            root.lift()
            root.attributes('-topmost', True)
            
            files = filedialog.askopenfilenames(
                title="Select Documents to Upload",
                filetypes=[
                    ("All supported", "*.pdf;*.txt;*.md;*.json;*.docx"),
                    ("PDF files", "*.pdf"),
                    ("Text files", "*.txt"),
                    ("Markdown files", "*.md"),
                    ("JSON files", "*.json"),
                    ("All files", "*.*")
                ]
            )
            
            root.destroy()
            
            if files:
                print(f"📁 API: Selected {len(files)} files")
                docs_dir = Path("docs")
                docs_dir.mkdir(exist_ok=True)
                
                copied_files = []
                for file_path in files:
                    try:
                        import shutil
                        dest_path = docs_dir / Path(file_path).name
                        shutil.copy2(file_path, dest_path)
                        copied_files.append(Path(file_path).name)
                        print(f"📁 API: Copied {Path(file_path).name}")
                    except Exception as e:
                        print(f"❌ API: Failed to copy {file_path}: {e}")
                        return {"success": False, "error": f"Failed to copy {file_path}: {e}"}
                
                print(f"✅ API: Successfully copied {len(copied_files)} files")
                return {"success": True, "count": len(copied_files), "files": copied_files}
            else:
                print("📁 API: No files selected")
                return {"success": False, "error": "No files selected"}
                
        except Exception as e:
            print(f"❌ API: Upload error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def build_index(self):
        """Simple index building with debug"""
        print("🔄 API: Build index called")
        
        try:
            from pathlib import Path
            docs_path = Path("docs")
            
            if not docs_path.exists() or not any(docs_path.iterdir()):
                return {"success": False, "error": "No documents found. Upload documents first."}
            
            print("🔄 API: Building index...")
            from build_embeddings_all import build_vector_index
            build_vector_index()
            
            print("✅ API: Index built successfully")
            return {"success": True, "message": "Index built successfully"}
            
        except Exception as e:
            print(f"❌ API: Build error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def open_web_ui(self):
        """Simple web UI launcher with debug"""
        print("🌐 API: Open web UI called")
        
        try:
            subprocess.Popen([
                'python', '-m', 'streamlit', 'run', 'streamlit_ui.py',
                '--server.port', '8501'
            ])
            
            import webbrowser
            threading.Timer(3.0, lambda: webbrowser.open('http://localhost:8501')).start()
            
            print("✅ API: Web UI started")
            return {"success": True, "message": "Web UI started"}
            
        except Exception as e:
            print(f"❌ API: Web UI error: {e}")
            return {"success": False, "error": str(e)}
    
    def start_api(self):
        """Simple API starter with debug"""
        print("🔌 API: Start API called")
        
        try:
            subprocess.Popen([
                'python', '-m', 'uvicorn', 'api:app',
                '--host', '0.0.0.0',
                '--port', '8000'
            ])
            
            print("✅ API: API server started")
            return {"success": True, "message": "API started on http://localhost:8000"}
            
        except Exception as e:
            print(f"❌ API: API start error: {e}")
            return {"success": False, "error": str(e)}

def main():
    print("🏢 S3 On-Premise AI Assistant - Working Version")
    print("=" * 50)
    print("🔍 Simplified version with proper JavaScript")
    print("✅ All buttons should work")
    print("✅ Debug output in console")
    print()
    
    try:
        import webview
        print("✅ PyWebView available")
    except ImportError:
        print("❌ PyWebView not available. Install with: pip install pywebview")
        return
    
    app = S3AIWebApp()
    app.run()

if __name__ == "__main__":
    main()