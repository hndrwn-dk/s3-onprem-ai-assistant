#!/usr/bin/env python3
"""
Ultra Modern Desktop App using WebView
Provides a web-app-like experience with modern UI/UX
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
        """Create the webview window with modern HTML interface"""
        html_content = self.get_html_content()
        
        window = webview.create_window(
            'S3 AI Assistant',
            html=html_content,
            js_api=self.api,
            width=1200,
            height=800,
            min_size=(900, 600),
            resizable=True,
            shadow=True,
            on_top=False,
            text_select=True
        )
        
        return window
    
    def get_html_content(self):
        """Generate modern HTML interface"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>S3 AI Assistant</title>
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --dark: #0f172a;
            --dark-light: #1e293b;
            --gray: #64748b;
            --gray-light: #f1f5f9;
            --white: #ffffff;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            --border-radius: 0.75rem;
            --transition: all 0.3s ease;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: var(--dark);
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            min-height: 100vh;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
            color: var(--white);
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.25rem;
            opacity: 0.9;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 2rem;
            height: calc(100vh - 200px);
        }
        
        .sidebar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: var(--border-radius);
            padding: 2rem;
            box-shadow: var(--shadow-lg);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .sidebar h3 {
            margin-bottom: 1.5rem;
            color: var(--dark);
            font-size: 1.25rem;
        }
        
        .btn {
            width: 100%;
            padding: 1rem;
            margin-bottom: 1rem;
            border: none;
            border-radius: var(--border-radius);
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 0.75rem;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: var(--white);
            box-shadow: var(--shadow);
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, var(--secondary), #7c3aed);
            color: var(--white);
            box-shadow: var(--shadow);
        }
        
        .btn-secondary:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--success), #059669);
            color: var(--white);
        }
        
        .btn-warning {
            background: linear-gradient(135deg, var(--warning), #d97706);
            color: var(--white);
        }
        
        .main-content {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: var(--border-radius);
            padding: 2rem;
            box-shadow: var(--shadow-lg);
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            flex-direction: column;
        }
        
        .query-section {
            margin-bottom: 2rem;
        }
        
        .query-input {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e2e8f0;
            border-radius: var(--border-radius);
            font-size: 1.1rem;
            transition: var(--transition);
            background: var(--white);
        }
        
        .query-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }
        
        .query-controls {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .ask-btn {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: var(--white);
            padding: 1rem 2rem;
            border: none;
            border-radius: var(--border-radius);
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            box-shadow: var(--shadow);
        }
        
        .ask-btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .ask-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .results-section {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .results-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .results-content {
            flex: 1;
            background: #f8fafc;
            border-radius: var(--border-radius);
            padding: 2rem;
            overflow-y: auto;
            border: 1px solid #e2e8f0;
            font-size: 1rem;
            line-height: 1.6;
        }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            background: rgba(0, 0, 0, 0.05);
            border-radius: var(--border-radius);
            margin-top: 1rem;
        }
        
        .progress-bar {
            width: 200px;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .welcome-content {
            text-align: center;
            color: var(--gray);
            padding: 4rem 2rem;
        }
        
        .welcome-content h2 {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: var(--dark);
        }
        
        .welcome-content p {
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        
        .feature-card {
            background: var(--white);
            padding: 1.5rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            border: 1px solid #e2e8f0;
            text-align: center;
        }
        
        .feature-card h4 {
            margin-bottom: 0.5rem;
            color: var(--primary);
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: var(--success);
            color: var(--white);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-lg);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification.error {
            background: var(--error);
        }
        
        .notification.warning {
            background: var(--warning);
        }
        
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
                height: auto;
            }
            
            .container {
                padding: 1rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 S3 AI Assistant</h1>
            <p>Ultra-Modern AI-Powered Documentation Assistant</p>
        </div>
        
        <div class="main-grid">
            <div class="sidebar">
                <h3>🛠️ Actions</h3>
                <button class="btn btn-primary" onclick="addDocuments()">
                    📁 Add Documents
                </button>
                <button class="btn btn-secondary" onclick="buildIndex()">
                    🏗️ Build Index
                </button>
                <button class="btn btn-success" onclick="openWebUI()">
                    🌐 Web Interface
                </button>
                <button class="btn btn-warning" onclick="startAPI()">
                    🔗 Start API
                </button>
                
                <h3 style="margin-top: 2rem;">⚙️ Settings</h3>
                <select class="btn" style="background: #f1f5f9; color: var(--dark);" onchange="changeTheme(this.value)">
                    <option value="modern">Modern Theme</option>
                    <option value="dark">Dark Theme</option>
                    <option value="light">Light Theme</option>
                </select>
            </div>
            
            <div class="main-content">
                <div class="query-section">
                    <input 
                        type="text" 
                        class="query-input" 
                        id="queryInput"
                        placeholder="Ask a question about your S3 documentation..."
                        onkeypress="if(event.key==='Enter') askQuestion()"
                    >
                    <div class="query-controls">
                        <button class="ask-btn" id="askBtn" onclick="askQuestion()">
                            Ask Question
                        </button>
                    </div>
                </div>
                
                <div class="results-section">
                    <div class="results-header">
                        <h3>💬 AI Response</h3>
                    </div>
                    <div class="results-content" id="resultsContent">
                        <div class="welcome-content">
                            <h2>Welcome to S3 AI Assistant! 🎉</h2>
                            <p>Your intelligent companion for S3 storage documentation</p>
                            
                            <div class="feature-grid">
                                <div class="feature-card">
                                    <h4>🤖 AI-Powered</h4>
                                    <p>Natural language queries with intelligent responses</p>
                                </div>
                                <div class="feature-card">
                                    <h4>📚 Multi-Format</h4>
                                    <p>PDF, TXT, MD, JSON document support</p>
                                </div>
                                <div class="feature-card">
                                    <h4>⚡ Fast Search</h4>
                                    <p>Vector-based semantic search technology</p>
                                </div>
                                <div class="feature-card">
                                    <h4>🎨 Modern UI</h4>
                                    <p>Beautiful, responsive interface</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="status-bar">
                    <div id="statusText">Ready</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="notification" id="notification"></div>
    
    <script>
        let isProcessing = false;
        
        function updateStatus(message, progress = 0) {
            document.getElementById('statusText').textContent = message;
            document.getElementById('progressFill').style.width = progress + '%';
        }
        
        function showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification ${type} show`;
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }
        
        async function askQuestion() {
            if (isProcessing) return;
            
            const input = document.getElementById('queryInput');
            const question = input.value.trim();
            
            if (!question) {
                showNotification('Please enter a question', 'warning');
                return;
            }
            
            isProcessing = true;
            const askBtn = document.getElementById('askBtn');
            const resultsContent = document.getElementById('resultsContent');
            
            askBtn.disabled = true;
            askBtn.innerHTML = '<span class="loading"></span> Processing...';
            
            updateStatus('🤔 Processing your question...', 10);
            resultsContent.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--gray);">🤔 Thinking about your question...<br><br>This may take 30-60 seconds for complex queries.</div>';
            
            try {
                updateStatus('🔍 Searching documents...', 30);
                const response = await pywebview.api.ask_question(question);
                
                updateStatus('✅ Answer ready!', 100);
                
                if (response.success) {
                    resultsContent.innerHTML = `<div style="white-space: pre-wrap; line-height: 1.6;">${response.answer}</div>`;
                    showNotification('Answer generated successfully!');
                } else {
                    resultsContent.innerHTML = `<div style="color: var(--error); padding: 2rem;">❌ Error: ${response.error}<br><br><strong>Troubleshooting:</strong><br>• Make sure you've built the vector index<br>• Check that Ollama is running<br>• Verify your documents are in the docs/ folder</div>`;
                    showNotification('Failed to get answer', 'error');
                }
            } catch (error) {
                resultsContent.innerHTML = `<div style="color: var(--error); padding: 2rem;">❌ Error: ${error.message}</div>`;
                showNotification('Request failed', 'error');
                updateStatus('❌ Error occurred', 0);
            }
            
            isProcessing = false;
            askBtn.disabled = false;
            askBtn.innerHTML = 'Ask Question';
        }
        
        async function addDocuments() {
            updateStatus('📁 Opening file dialog...', 20);
            try {
                const result = await pywebview.api.add_documents();
                if (result.success) {
                    showNotification(`Added ${result.count} documents successfully!`);
                    updateStatus(`📁 Added ${result.count} documents`, 100);
                } else {
                    showNotification(result.error, 'error');
                    updateStatus('❌ Failed to add documents', 0);
                }
            } catch (error) {
                showNotification('Failed to add documents', 'error');
                updateStatus('❌ Error occurred', 0);
            }
        }
        
        async function buildIndex() {
            if (isProcessing) return;
            
            if (!confirm('This will rebuild the vector index for all documents. This may take several minutes. Continue?')) {
                return;
            }
            
            isProcessing = true;
            updateStatus('🏗️ Building vector index...', 10);
            document.getElementById('resultsContent').innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--gray);">🏗️ Building vector index...<br><br>This process:<br>• Reads all documents in docs/ folder<br>• Splits them into chunks<br>• Creates embeddings<br>• Builds searchable index<br><br>Please wait...</div>';
            
            try {
                updateStatus('📚 Processing documents...', 30);
                const result = await pywebview.api.build_index();
                
                if (result.success) {
                    document.getElementById('resultsContent').innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--success);">✅ Vector index built successfully!<br><br>🎉 Your documents are now ready for AI-powered search.<br><br>You can now ask questions about your S3 documentation and get intelligent answers.<br><br>💡 Try asking a question above!</div>';
                    updateStatus('✅ Index built successfully!', 100);
                    showNotification('Index built successfully!');
                } else {
                    document.getElementById('resultsContent').innerHTML = `<div style="color: var(--error); padding: 2rem;">❌ Build failed:<br><br>${result.error}<br><br><strong>Troubleshooting:</strong><br>• Make sure you have documents in docs/ folder<br>• Check Python dependencies are installed<br>• Verify Ollama is running</div>`;
                    updateStatus('❌ Build failed', 0);
                    showNotification('Build failed', 'error');
                }
            } catch (error) {
                showNotification('Build process failed', 'error');
                updateStatus('❌ Error occurred', 0);
            }
            
            isProcessing = false;
        }
        
        async function openWebUI() {
            updateStatus('🌐 Starting web interface...', 50);
            try {
                const result = await pywebview.api.open_web_ui();
                if (result.success) {
                    showNotification('Web UI opened in browser!');
                    updateStatus('🌐 Web UI opened in browser', 100);
                } else {
                    showNotification('Failed to start web UI', 'error');
                    updateStatus('❌ Failed to start web UI', 0);
                }
            } catch (error) {
                showNotification('Failed to start web UI', 'error');
                updateStatus('❌ Error occurred', 0);
            }
        }
        
        async function startAPI() {
            updateStatus('🔗 Starting API server...', 50);
            try {
                const result = await pywebview.api.start_api();
                if (result.success) {
                    showNotification('API server started on http://localhost:8000');
                    updateStatus('🔗 API running on http://localhost:8000', 100);
                } else {
                    showNotification('Failed to start API', 'error');
                    updateStatus('❌ Failed to start API', 0);
                }
            } catch (error) {
                showNotification('Failed to start API', 'error');
                updateStatus('❌ Error occurred', 0);
            }
        }
        
        function changeTheme(theme) {
            // Theme switching logic would go here
            showNotification(`Switched to ${theme} theme`);
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            updateStatus('Ready', 0);
        });
    </script>
</body>
</html>
        """
    
    def run(self):
        """Start the application"""
        window = self.create_window()
        webview.start(debug=False)

class S3AIWebAPI:
    """API class for handling JavaScript calls from the web interface"""
    
    def ask_question(self, question):
        """Handle question asking"""
        try:
            # Check if running as executable or from source
            if getattr(sys, 'frozen', False):
                app_dir = sys._MEIPASS
                s3ai_script = os.path.join(app_dir, 's3ai_query.py')
                cmd = [sys.executable, s3ai_script, question]
                cwd = app_dir
            else:
                cmd = [sys.executable, 's3ai_query.py', question]
                cwd = os.getcwd()
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=cwd
            )
            
            if result.returncode == 0 and result.stdout:
                # Extract clean answer
                lines = result.stdout.split('\\n')
                answer_started = False
                answer_lines = []
                
                for line in lines:
                    if '🤖 AI-PROCESSED ANSWER' in line or 'Answer:' in line:
                        answer_started = True
                        continue
                    elif answer_started and ('=' * 50 in line or line.startswith('INFO:')):
                        break
                    elif answer_started:
                        answer_lines.append(line)
                
                if answer_lines:
                    clean_answer = '\\n'.join(answer_lines).strip()
                    return {"success": True, "answer": clean_answer}
                else:
                    return {"success": True, "answer": result.stdout}
            else:
                error_msg = result.stderr if result.stderr else "No response received"
                return {"success": False, "error": error_msg}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Query timed out after 5 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_documents(self):
        """Handle document addition"""
        try:
            # Create hidden tkinter root for file dialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            files = filedialog.askopenfilenames(
                title="Select Documents to Add",
                filetypes=[
                    ("PDF files", "*.pdf"),
                    ("Text files", "*.txt"),
                    ("Markdown files", "*.md"),
                    ("JSON files", "*.json"),
                    ("All files", "*.*")
                ]
            )
            
            root.destroy()
            
            if files:
                docs_dir = Path("docs")
                docs_dir.mkdir(exist_ok=True)
                
                copied_files = []
                for file_path in files:
                    try:
                        import shutil
                        dest_path = docs_dir / Path(file_path).name
                        shutil.copy2(file_path, dest_path)
                        copied_files.append(Path(file_path).name)
                    except Exception as e:
                        return {"success": False, "error": f"Failed to copy {file_path}: {e}"}
                
                return {"success": True, "count": len(copied_files), "files": copied_files}
            else:
                return {"success": False, "error": "No files selected"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def build_index(self):
        """Handle index building"""
        try:
            # Check if running as executable or from source
            if getattr(sys, 'frozen', False):
                app_dir = sys._MEIPASS
                build_script = os.path.join(app_dir, 'build_embeddings_all.py')
                cmd = [sys.executable, build_script]
                cwd = app_dir
            else:
                cmd = [sys.executable, 'build_embeddings_all.py']
                cwd = os.getcwd()
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minutes
                cwd=cwd
            )
            
            if result.returncode == 0:
                return {"success": True, "message": "Index built successfully"}
            else:
                return {"success": False, "error": result.stderr or "Build failed"}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Build timed out after 30 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_web_ui(self):
        """Handle web UI opening"""
        try:
            subprocess.Popen([
                sys.executable, '-m', 'streamlit', 'run', 'streamlit_ui.py',
                '--server.headless', 'true',
                '--server.port', '8501'
            ])
            
            # Wait a moment then open browser
            import webbrowser
            threading.Timer(3.0, lambda: webbrowser.open('http://localhost:8501')).start()
            
            return {"success": True, "message": "Web UI started"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_api(self):
        """Handle API starting"""
        try:
            subprocess.Popen([
                sys.executable, '-m', 'uvicorn', 'api:app',
                '--host', '0.0.0.0',
                '--port', '8000',
                '--reload'
            ])
            
            return {"success": True, "message": "API started on http://localhost:8000"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    # Check if webview is available
    try:
        import webview
    except ImportError:
        print("Installing pywebview for ultra-modern interface...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywebview'])
        import webview
    
    app = S3AIWebApp()
    app.run()

if __name__ == "__main__":
    main()