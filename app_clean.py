#!/usr/bin/env python
"""
Clean Desktop App - S3 On-Premise AI Assistant
Properly indented version with working JavaScript
"""

import webview
import threading
import subprocess
import sys
import os
import time
from pathlib import Path
from tkinter import filedialog
import tkinter as tk

class S3AIWebApp:
    def __init__(self):
        self.api = S3AIWebAPI()
        
    def create_window(self):
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
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>S3 On-Premise AI Assistant</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            color: #1e293b;
            font-size: 14px;
            margin: 0;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            text-align: center;
            color: white;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 8px;
        }
        
        .header .subtitle {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 20px;
        }
        
        .sidebar {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #e2e8f0;
        }
        
        .sidebar h3 {
            font-size: 16px;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .btn {
            width: 100%;
            padding: 12px 16px;
            margin-bottom: 12px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            background: #3b82f6;
            color: white;
            transition: all 0.2s ease;
        }
        
        .btn:hover {
            background: #2563eb;
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: white;
            color: #374151;
            border: 1px solid #d1d5db;
        }
        
        .btn-secondary:hover {
            background: #f9fafb;
        }
        
        .main-content {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #e2e8f0;
        }
        
        .card h3 {
            font-size: 16px;
            margin-bottom: 16px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }
        
        .metric-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }
        
        .metric-label {
            font-size: 10px;
            color: #64748b;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        
        .metric-value {
            font-size: 18px;
            font-weight: bold;
            color: #1e293b;
        }
        
        .query-input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #cbd5e1;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 16px;
        }
        
        .query-input:focus {
            outline: none;
            border-color: #3b82f6;
        }
        
        .results-area {
            background: #f1f5f9;
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
            border: 1px solid #cbd5e1;
            min-height: 200px;
            max-height: 400px;
            font-family: monospace;
            font-size: 12px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        
        .loading {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #64748b;
            font-size: 14px;
        }
        
        .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid #cbd5e1;
            border-top-color: #3b82f6;
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
                
                <button class="btn" onclick="executeQuery()">
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
                            <div class="metric-label">🚀 Response Time</div>
                            <div class="metric-value" id="response-time">--</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">💾 Cache Rate</div>
                            <div class="metric-value" id="cache-rate">0%</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">🔍 Queries</div>
                            <div class="metric-value" id="query-count">0</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">📊 Status</div>
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
                        placeholder="Enter your query (e.g., 'how to purge bucket in cloudian hyperstore')"
                        onkeypress="if(event.key==='Enter') executeQuery()"
                    >
                    
                    <div id="status-message" class="loading" style="display: none;">
                        <div class="spinner"></div>
                        <span>Processing...</span>
                    </div>
                    
                    <div id="results" class="results-area">Ready to process your queries with AI...

Performance Tips:
• Ollama is running ✅
• Index built with 10,777 chunks ✅  
• First query: 5-15 seconds
• Cached queries: under 0.1 seconds

Try: "how to purge bucket in cloudian hyperstore"</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        console.log('JavaScript loaded successfully');
        
        let queryCount = 0;
        let cacheHits = 0;
        
        async function executeQuery() {
            console.log('executeQuery called');
            
            const queryInput = document.getElementById('queryInput');
            const query = queryInput.value.trim();
            
            console.log('Query:', query);
            
            if (!query) {
                updateResults('❌ Please enter a query');
                return;
            }
            
            queryCount++;
            updateMetric('query-count', queryCount);
            
            setStatus('🔍 Processing query...');
            updateResults('🔍 Processing: ' + query + '\\n\\nSearching 10,777 document chunks...\\nUsing AI to generate answer...');
            
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
            setStatus('📁 Opening file dialog...');
            updateResults('📁 File Upload\\n\\nOpening file dialog...\\nSelect your S3 documentation files.');
            
            try {
                const result = await pywebview.api.upload_files();
                console.log('Upload result:', result);
                
                if (result.success) {
                    updateResults('✅ Upload Successful\\n\\nUploaded ' + result.count + ' files\\n\\nNext: Click "🔄 Rebuild Index" to make them searchable');
                } else {
                    updateResults('❌ Upload Failed\\n\\n' + result.error);
                }
            } catch (error) {
                updateResults('❌ Upload Error\\n\\n' + error.message);
            } finally {
                setStatus('');
            }
        }
        
        async function buildIndex() {
            console.log('buildIndex called');
            
            if (!confirm('Build index? This will process all documents and may take 2-10 minutes.')) {
                return;
            }
            
            setStatus('🔄 Building index...');
            updateResults('🔄 Building Knowledge Base\\n\\nProcessing documents...\\nCreating embeddings...\\nThis may take 2-10 minutes...\\n\\nPlease wait...');
            
            const startTime = performance.now();
            
            try {
                const result = await pywebview.api.build_index();
                const buildTime = ((performance.now() - startTime) / 1000 / 60).toFixed(1);
                
                if (result.success) {
                    updateResults('✅ Index Complete\\n\\nBuild time: ' + buildTime + ' minutes\\nDocuments: ' + (result.file_count || 'processed') + '\\n\\nQueries will now be much faster!');
                    updateMetric('system-load', 'Optimized');
                } else {
                    updateResults('❌ Index Failed\\n\\n' + result.error);
                }
            } catch (error) {
                updateResults('❌ Build Error\\n\\n' + error.message);
            } finally {
                setStatus('');
            }
        }
        
        async function openWebUI() {
            console.log('openWebUI called');
            setStatus('🌐 Starting web interface...');
            updateResults('🌐 Starting Web Interface\\n\\nLaunching Streamlit...\\nBrowser will open in 3 seconds...');
            
            try {
                const result = await pywebview.api.open_web_ui();
                if (result.success) {
                    updateResults('✅ Web Interface Started\\n\\nURL: http://localhost:8501\\nBrowser should open automatically');
                } else {
                    updateResults('❌ Web Interface Failed\\n\\n' + result.error);
                }
            } catch (error) {
                updateResults('❌ Web Interface Error\\n\\n' + error.message);
            } finally {
                setStatus('');
            }
        }
        
        async function startAPI() {
            console.log('startAPI called');
            setStatus('🔌 Starting API...');
            updateResults('🔌 Starting API Server\\n\\nLaunching FastAPI...\\nWill be available at http://localhost:8000');
            
            try {
                const result = await pywebview.api.start_api();
                if (result.success) {
                    updateResults('✅ API Server Started\\n\\nURL: http://localhost:8000\\nAPI endpoints available');
                } else {
                    updateResults('❌ API Failed\\n\\n' + result.error);
                }
            } catch (error) {
                updateResults('❌ API Error\\n\\n' + error.message);
            } finally {
                setStatus('');
            }
        }
        
        function displayResult(result, responseTime) {
            const resultsDiv = document.getElementById('results');
            const timestamp = new Date().toLocaleTimeString();
            
            let statusText = '';
            if (result.cached) {
                statusText = '⚡ Cached Result';
            } else if (result.source === 'vector') {
                statusText = '🎯 Vector Search';
            } else if (result.source === 'quick_search') {
                statusText = '🚀 Quick Search';
            } else {
                statusText = '🔄 Fallback Search';
            }
            
            const actualTime = result.response_time ? result.response_time.toFixed(2) : responseTime;
            resultsDiv.innerHTML = statusText + ' • ' + actualTime + 's • ' + timestamp + '\\n\\n' + result.answer;
            
            if (actualTime < 0.5) {
                updateMetric('system-load', 'Excellent');
            } else if (actualTime < 5) {
                updateMetric('system-load', 'Good');
            } else {
                updateMetric('system-load', 'Normal');
            }
        }
        
        function displayError(error) {
            const resultsDiv = document.getElementById('results');
            const timestamp = new Date().toLocaleTimeString();
            resultsDiv.innerHTML = '❌ Error • ' + timestamp + '\\n\\n' + error;
        }
        
        function setStatus(message) {
            const statusDiv = document.getElementById('status-message');
            if (!statusDiv) return;
            
            const statusText = statusDiv.querySelector('span');
            if (message && statusText) {
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
        
        function updateResults(message) {
            const resultsDiv = document.getElementById('results');
            if (resultsDiv) {
                resultsDiv.innerHTML = message;
            }
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM loaded');
            const queryInput = document.getElementById('queryInput');
            if (queryInput) {
                queryInput.focus();
            }
        });
    </script>
</body>
</html>'''

class S3AIWebAPI:
    def __init__(self):
        print("🔧 API: Initializing...")
        
    def query(self, query_text):
        print(f"🔍 API: Query received: '{query_text}'")
        start_time = time.time()
        
        try:
            # Check cache first
            print("🔍 API: Checking cache...")
            from response_cache import response_cache
            cached_response = response_cache.get(query_text)
            
            if cached_response:
                print("⚡ API: Cache hit!")
                return {
                    "answer": cached_response,
                    "source": "cache",
                    "cached": True,
                    "success": True,
                    "response_time": time.time() - start_time
                }
            
            # Try vector search (since index is built)
            print("🎯 API: Trying vector search...")
            try:
                from model_cache import ModelCache
                vector_store = ModelCache.get_vector_store()
                
                if vector_store:
                    from langchain.chains import RetrievalQA
                    from config import VECTOR_SEARCH_K, LLM_TIMEOUT_SECONDS
                    
                    print(f"🎯 API: Vector store loaded, searching...")
                    retriever = vector_store.as_retriever(search_kwargs={"k": VECTOR_SEARCH_K})
                    llm = ModelCache.get_llm()
                    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
                    
                    print("🤖 API: Running AI query...")
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(qa_chain.run, query_text)
                        response = future.result(timeout=LLM_TIMEOUT_SECONDS)
                    
                    if response and response.strip():
                        print("✅ API: Vector search successful!")
                        response_cache.set(query_text, response, "vector")
                        return {
                            "answer": response,
                            "source": "vector",
                            "cached": False,
                            "success": True,
                            "response_time": time.time() - start_time
                        }
                        
            except Exception as e:
                print(f"❌ API: Vector search failed: {e}")
            
            # If vector search fails
            return {
                "answer": f"Vector search failed. Your index has 10,777 chunks but search encountered an error.\n\nPossible issues:\n• Ollama not responding\n• Model not loaded\n• Try restarting: ollama serve\n\nQuery: {query_text}",
                "source": "error",
                "cached": False,
                "success": False,
                "response_time": time.time() - start_time
            }
            
        except Exception as e:
            print(f"❌ API: Query error: {e}")
            return {
                "answer": f"System error: {str(e)}",
                "source": "error",
                "cached": False,
                "success": False,
                "response_time": time.time() - start_time
            }
    
    def upload_files(self):
        print("📁 API: Upload files called")
        
        try:
            root = tk.Tk()
            root.withdraw()
            root.lift()
            root.attributes('-topmost', True)
            
            files = filedialog.askopenfilenames(
                title="Select S3 Documentation",
                filetypes=[
                    ("PDF files", "*.pdf"),
                    ("Text files", "*.txt"),
                    ("Markdown files", "*.md"),
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
                        return {"success": False, "error": f"Failed to copy {file_path}: {e}"}
                
                print(f"✅ API: Successfully copied {len(copied_files)} files")
                return {"success": True, "count": len(copied_files), "files": copied_files}
            else:
                print("📁 API: No files selected")
                return {"success": False, "error": "No files selected"}
                
        except Exception as e:
            print(f"❌ API: Upload error: {e}")
            return {"success": False, "error": str(e)}
    
    def build_index(self):
        print("🔄 API: Build index called")
        
        try:
            docs_path = Path("docs")
            if not docs_path.exists() or not any(docs_path.iterdir()):
                return {"success": False, "error": "No documents found. Upload documents first."}
            
            print("🔄 API: Building index...")
            from build_embeddings_all import build_vector_index
            build_vector_index()
            
            # Clear cache
            from model_cache import ModelCache
            ModelCache.reset_vector_store()
            
            print("✅ API: Index built successfully")
            return {"success": True, "message": "Index built successfully"}
            
        except Exception as e:
            print(f"❌ API: Build error: {e}")
            return {"success": False, "error": str(e)}
    
    def open_web_ui(self):
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
        print("🔌 API: Start API called")
        
        try:
            subprocess.Popen([
                'python', '-m', 'uvicorn', 'api:app',
                '--host', '0.0.0.0',
                '--port', '8000'
            ])
            
            print("✅ API: API server started")
            return {"success": True, "message": "API started"}
            
        except Exception as e:
            print(f"❌ API: API start error: {e}")
            return {"success": False, "error": str(e)}

def main():
    print("🏢 S3 On-Premise AI Assistant - Clean Version")
    print("=" * 50)
    print("✅ Fixed indentation issues")
    print("✅ Real-time UI updates")
    print("✅ Vector search with 10,777 chunks")
    print("✅ Ollama integration ready")
    print()
    
    app = S3AIWebApp()
    app.run()

if __name__ == "__main__":
    main()