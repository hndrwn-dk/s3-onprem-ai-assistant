#!/usr/bin/env python3
"""
Enterprise-Grade Desktop AI Assistant
Professional S3 Analytics Platform with Modern UI/UX
Version 3.0.0 - Enterprise Edition
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
        """Create the webview window with enterprise-grade interface"""
        html_content = self.get_html_content()
        
        window = webview.create_window(
            'Enterprise AI Assistant | S3 Analytics Platform',
            html=html_content,
            js_api=self.api,
            width=1400,
            height=900,
            min_size=(1200, 700),
            resizable=True,
            shadow=True,
            on_top=False,
            text_select=True
        )
        
        return window
    
    def run(self):
        """Start the application"""
        window = self.create_window()
        webview.start(debug=False)
    
    def get_html_content(self):
        """Generate enterprise-grade HTML interface"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise AI Assistant | S3 Analytics Platform</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            /* Enterprise Color Palette */
            --primary: #3b82f6;
            --primary-dark: #2563eb;
            --primary-light: #60a5fa;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --info: #06b6d4;
            
            /* Professional Grays */
            --slate-50: #f8fafc;
            --slate-100: #f1f5f9;
            --slate-200: #e2e8f0;
            --slate-300: #cbd5e1;
            --slate-400: #94a3b8;
            --slate-500: #64748b;
            --slate-600: #475569;
            --slate-700: #334155;
            --slate-800: #1e293b;
            --slate-900: #0f172a;
            
            /* Enterprise Design System */
            --white: #ffffff;
            --background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            --card-background: rgba(255, 255, 255, 0.95);
            --glass-background: rgba(255, 255, 255, 0.8);
            
            /* Professional Shadows */
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
            
            /* Typography Scale */
            --text-xs: 0.75rem;
            --text-sm: 0.875rem;
            --text-base: 1rem;
            --text-lg: 1.125rem;
            --text-xl: 1.25rem;
            --text-2xl: 1.5rem;
            --text-3xl: 1.875rem;
            --text-4xl: 2.25rem;
            
            /* Spacing */
            --space-1: 0.25rem;
            --space-2: 0.5rem;
            --space-3: 0.75rem;
            --space-4: 1rem;
            --space-5: 1.25rem;
            --space-6: 1.5rem;
            --space-8: 2rem;
            --space-10: 2.5rem;
            --space-12: 3rem;
            
            /* Border Radius */
            --radius-sm: 0.375rem;
            --radius: 0.5rem;
            --radius-lg: 0.75rem;
            --radius-xl: 1rem;
            
            /* Transitions */
            --transition: all 0.2s ease;
            --transition-slow: all 0.3s ease;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: var(--background);
            color: var(--slate-800);
            overflow-x: hidden;
            font-size: var(--text-sm);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: var(--space-6);
            min-height: 100vh;
        }
        
        /* Enterprise Header */
        .header {
            background: linear-gradient(135deg, var(--slate-800) 0%, var(--slate-700) 100%);
            padding: var(--space-8) var(--space-10);
            border-radius: var(--radius-xl);
            margin-bottom: var(--space-8);
            box-shadow: var(--shadow-xl);
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
        }
        
        .header h1 {
            font-size: var(--text-4xl);
            font-weight: 700;
            color: var(--white);
            margin-bottom: var(--space-2);
            letter-spacing: -0.025em;
        }
        
        .header .subtitle {
            font-size: var(--text-lg);
            color: var(--slate-300);
            font-weight: 400;
            opacity: 0.9;
        }
        
        .header .enterprise-badge {
            display: inline-flex;
            align-items: center;
            gap: var(--space-2);
            background: rgba(59, 130, 246, 0.2);
            color: var(--slate-100);
            padding: var(--space-2) var(--space-4);
            border-radius: var(--radius-lg);
            font-size: var(--text-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: var(--space-4);
            border: 1px solid rgba(59, 130, 246, 0.3);
        }
        
        /* Main Layout */
        .main-grid {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: var(--space-8);
            min-height: calc(100vh - 300px);
        }
        
        /* Professional Sidebar */
        .sidebar {
            background: var(--card-background);
            backdrop-filter: blur(10px);
            border-radius: var(--radius-xl);
            padding: var(--space-6);
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--slate-200);
            height: fit-content;
            position: sticky;
            top: var(--space-6);
        }
        
        .sidebar h3 {
            font-size: var(--text-lg);
            font-weight: 600;
            color: var(--slate-800);
            margin-bottom: var(--space-6);
            padding-bottom: var(--space-3);
            border-bottom: 2px solid var(--slate-200);
            display: flex;
            align-items: center;
            gap: var(--space-2);
        }
        
        /* Professional Buttons */
        .btn {
            width: 100%;
            padding: var(--space-4) var(--space-5);
            margin-bottom: var(--space-3);
            border: none;
            border-radius: var(--radius-lg);
            font-size: var(--text-sm);
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition);
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: var(--space-3);
            font-family: 'Inter', sans-serif;
            text-align: left;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: var(--white);
            box-shadow: var(--shadow);
            border: 1px solid transparent;
        }
        
        .btn-primary:hover {
            background: linear-gradient(135deg, var(--primary-dark), #1d4ed8);
            transform: translateY(-1px);
            box-shadow: var(--shadow-lg);
        }
        
        .btn-secondary {
            background: var(--white);
            color: var(--slate-700);
            border: 1px solid var(--slate-300);
            box-shadow: var(--shadow-sm);
        }
        
        .btn-secondary:hover {
            background: var(--slate-50);
            border-color: var(--slate-400);
            transform: translateY(-1px);
            box-shadow: var(--shadow);
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--success), #059669);
            color: var(--white);
            box-shadow: var(--shadow);
        }
        
        .btn-success:hover {
            background: linear-gradient(135deg, #059669, #047857);
            transform: translateY(-1px);
            box-shadow: var(--shadow-lg);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        
        .btn-icon {
            font-size: var(--text-lg);
            min-width: 20px;
            text-align: center;
        }
        
        /* Main Content Area */
        .main-content {
            display: flex;
            flex-direction: column;
            gap: var(--space-6);
        }
        
        /* Enterprise Cards */
        .card {
            background: var(--card-background);
            backdrop-filter: blur(10px);
            border-radius: var(--radius-xl);
            padding: var(--space-6);
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--slate-200);
            transition: var(--transition);
        }
        
        .card:hover {
            box-shadow: var(--shadow-xl);
            transform: translateY(-2px);
        }
        
        .card h3 {
            font-size: var(--text-xl);
            font-weight: 600;
            color: var(--slate-800);
            margin-bottom: var(--space-4);
            display: flex;
            align-items: center;
            gap: var(--space-2);
        }
        
        /* Performance Dashboard */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--space-4);
            margin-bottom: var(--space-6);
        }
        
        .metric-card {
            background: linear-gradient(135deg, var(--white) 0%, var(--slate-50) 100%);
            border: 1px solid var(--slate-200);
            border-radius: var(--radius-lg);
            padding: var(--space-5);
            text-align: center;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .metric-label {
            font-size: var(--text-xs);
            font-weight: 600;
            color: var(--slate-500);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: var(--space-2);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: var(--space-1);
        }
        
        .metric-value {
            font-size: var(--text-2xl);
            font-weight: 700;
            color: var(--slate-800);
            font-family: 'JetBrains Mono', monospace;
        }
        
        /* Query Interface */
        .query-section {
            background: var(--card-background);
            border-radius: var(--radius-xl);
            padding: var(--space-8);
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--slate-200);
        }
        
        .query-input {
            width: 100%;
            padding: var(--space-4) var(--space-5);
            border: 2px solid var(--slate-300);
            border-radius: var(--radius-lg);
            font-size: var(--text-base);
            font-family: 'Inter', sans-serif;
            background: var(--white);
            color: var(--slate-800);
            transition: var(--transition);
            margin-bottom: var(--space-4);
        }
        
        .query-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .query-input::placeholder {
            color: var(--slate-400);
        }
        
        /* Status Indicators */
        .status-indicator {
            display: inline-flex;
            align-items: center;
            padding: var(--space-1) var(--space-3);
            border-radius: var(--radius-lg);
            font-size: var(--text-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            gap: var(--space-1);
        }
        
        .status-online {
            background: #dcfce7;
            color: #166534;
            border: 1px solid #bbf7d0;
        }
        
        .status-processing {
            background: #dbeafe;
            color: #1e40af;
            border: 1px solid #bfdbfe;
        }
        
        .status-warning {
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
        }
        
        .status-error {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }
        
        /* Results Area */
        .results-area {
            background: var(--slate-50);
            border-radius: var(--radius-lg);
            padding: var(--space-6);
            margin-top: var(--space-4);
            border: 1px solid var(--slate-200);
            min-height: 200px;
            font-family: 'JetBrains Mono', monospace;
            font-size: var(--text-sm);
            line-height: 1.7;
            white-space: pre-wrap;
            overflow-y: auto;
        }
        
        /* Progress Bar */
        .progress-container {
            width: 100%;
            background: var(--slate-200);
            border-radius: var(--radius);
            overflow: hidden;
            margin: var(--space-4) 0;
        }
        
        .progress-bar {
            height: 8px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: var(--radius);
            transition: width 0.3s ease;
            width: 0%;
        }
        
        /* Loading States */
        .loading {
            display: inline-flex;
            align-items: center;
            gap: var(--space-2);
            color: var(--slate-600);
            font-size: var(--text-sm);
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
        
        /* File Upload Area */
        .upload-area {
            border: 2px dashed var(--slate-300);
            border-radius: var(--radius-lg);
            padding: var(--space-8);
            text-align: center;
            background: var(--slate-50);
            margin: var(--space-4) 0;
            transition: var(--transition);
            cursor: pointer;
        }
        
        .upload-area:hover {
            border-color: var(--primary);
            background: rgba(59, 130, 246, 0.05);
        }
        
        .upload-area.dragover {
            border-color: var(--primary);
            background: rgba(59, 130, 246, 0.1);
        }
        
        /* Responsive Design */
        @media (max-width: 1200px) {
            .main-grid {
                grid-template-columns: 280px 1fr;
                gap: var(--space-6);
            }
            
            .container {
                padding: var(--space-4);
            }
        }
        
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
                gap: var(--space-4);
            }
            
            .sidebar {
                position: static;
                order: 2;
            }
            
            .header h1 {
                font-size: var(--text-3xl);
            }
            
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        /* Hide scrollbars but keep functionality */
        .results-area::-webkit-scrollbar {
            width: 6px;
        }
        
        .results-area::-webkit-scrollbar-track {
            background: var(--slate-100);
            border-radius: var(--radius);
        }
        
        .results-area::-webkit-scrollbar-thumb {
            background: var(--slate-400);
            border-radius: var(--radius);
        }
        
        .results-area::-webkit-scrollbar-thumb:hover {
            background: var(--slate-500);
        }
        
        /* Professional Animations */
        .fade-in {
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Enterprise Form Elements */
        .form-group {
            margin-bottom: var(--space-4);
        }
        
        .form-label {
            display: block;
            font-size: var(--text-sm);
            font-weight: 500;
            color: var(--slate-700);
            margin-bottom: var(--space-2);
        }
        
        .form-input {
            width: 100%;
            padding: var(--space-3) var(--space-4);
            border: 1px solid var(--slate-300);
            border-radius: var(--radius);
            font-size: var(--text-sm);
            transition: var(--transition);
        }
        
        .form-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        /* Success/Error Messages */
        .alert {
            padding: var(--space-4);
            border-radius: var(--radius-lg);
            margin: var(--space-4) 0;
            font-size: var(--text-sm);
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: var(--space-2);
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
    </style>
</head>
<body>
    <div class="container">
        <!-- Enterprise Header -->
        <div class="header">
            <h1>🏢 Enterprise AI Assistant</h1>
            <p class="subtitle">Advanced S3 Analytics Platform • Cloudian • IBM • MinIO • Metadata Intelligence</p>
            <div class="enterprise-badge">
                <span>🚀</span>
                Professional Edition v3.0
            </div>
        </div>
        
        <div class="main-grid">
            <!-- Professional Sidebar -->
            <div class="sidebar">
                <h3><span class="btn-icon">⚡</span>Quick Actions</h3>
                
                <button class="btn btn-primary" onclick="executeQuery()">
                    <span class="btn-icon">🔍</span>
                    Execute Query
                </button>
                
                <button class="btn btn-secondary" onclick="uploadFiles()">
                    <span class="btn-icon">📁</span>
                    Upload Documents
                </button>
                
                <button class="btn btn-success" onclick="buildIndex()">
                    <span class="btn-icon">🔄</span>
                    Rebuild Index
                </button>
                
                <button class="btn btn-secondary" onclick="openWebUI()">
                    <span class="btn-icon">🌐</span>
                    Web Interface
                </button>
                
                <button class="btn btn-secondary" onclick="startAPI()">
                    <span class="btn-icon">🔌</span>
                    API Server
                </button>
                
                <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--slate-200);">
                    <h3><span class="btn-icon">📊</span>System Status</h3>
                    <div class="status-indicator status-online">
                        <span>●</span>
                        Online
                    </div>
                </div>
            </div>
            
            <!-- Main Content -->
            <div class="main-content">
                <!-- Performance Metrics -->
                <div class="card">
                    <h3><span class="btn-icon">📈</span>Performance Dashboard</h3>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-label">
                                <span>🚀</span>
                                Query Response
                            </div>
                            <div class="metric-value" id="response-time">--</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">
                                <span>💾</span>
                                Cache Hit Rate
                            </div>
                            <div class="metric-value" id="cache-rate">0%</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">
                                <span>🔍</span>
                                Total Queries
                            </div>
                            <div class="metric-value" id="query-count">0</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">
                                <span>📊</span>
                                System Load
                            </div>
                            <div class="metric-value" id="system-load">Low</div>
                        </div>
                    </div>
                </div>
                
                <!-- Query Interface -->
                <div class="query-section">
                    <h3><span class="btn-icon">💬</span>Enterprise Query Interface</h3>
                    <input 
                        type="text" 
                        class="query-input" 
                        id="queryInput" 
                        placeholder="🔍 Enter your enterprise query (e.g., 'Show all buckets for engineering department')"
                        onkeypress="if(event.key==='Enter') executeQuery()"
                    >
                    
                    <div id="progress-container" class="progress-container" style="display: none;">
                        <div class="progress-bar" id="progress-bar"></div>
                    </div>
                    
                    <div id="status-message" class="loading" style="display: none;">
                        <div class="spinner"></div>
                        <span>Processing your query...</span>
                    </div>
                    
                    <div id="results" class="results-area">
                        <div style="color: var(--slate-500); font-style: italic; text-align: center; padding: 2rem;">
                            Ready to process your enterprise queries...
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let queryCount = 0;
        let cacheHits = 0;
        
        async function executeQuery() {
            const queryInput = document.getElementById('queryInput');
            const query = queryInput.value.trim();
            
            if (!query) {
                showAlert('Please enter a query', 'error');
                return;
            }
            
            queryCount++;
            updateMetric('query-count', queryCount);
            
            showProgress(true);
            setStatus('🔍 Processing query...');
            
            const startTime = performance.now();
            
            try {
                const result = await pywebview.api.query(query);
                const endTime = performance.now();
                const responseTime = ((endTime - startTime) / 1000).toFixed(2);
                
                updateMetric('response-time', responseTime + 's');
                
                if (result.cached) {
                    cacheHits++;
                    updateMetric('cache-rate', Math.round((cacheHits / queryCount) * 100) + '%');
                }
                
                displayResult(result, responseTime);
                
            } catch (error) {
                displayError(error.message);
            } finally {
                showProgress(false);
                setStatus('');
            }
        }
        
        async function uploadFiles() {
            setStatus('📁 Opening file dialog...');
            
            try {
                const result = await pywebview.api.upload_files();
                
                if (result.success) {
                    showAlert(`✅ Successfully uploaded ${result.count} file(s): ${result.files.join(', ')}`, 'success');
                } else {
                    showAlert(`❌ Upload failed: ${result.error}`, 'error');
                }
            } catch (error) {
                showAlert(`❌ Upload error: ${error.message}`, 'error');
            } finally {
                setStatus('');
            }
        }
        
        async function buildIndex() {
            setStatus('🔄 Building knowledge base index...');
            showProgress(true);
            
            try {
                const result = await pywebview.api.build_index();
                
                if (result.success) {
                    showAlert('✅ Knowledge base index built successfully', 'success');
                } else {
                    showAlert(`❌ Index build failed: ${result.error}`, 'error');
                }
            } catch (error) {
                showAlert(`❌ Build error: ${error.message}`, 'error');
            } finally {
                showProgress(false);
                setStatus('');
            }
        }
        
        async function openWebUI() {
            try {
                const result = await pywebview.api.open_web_ui();
                
                if (result.success) {
                    showAlert('🌐 Web interface starting... Opening browser in 3 seconds', 'info');
                } else {
                    showAlert(`❌ Failed to start web UI: ${result.error}`, 'error');
                }
            } catch (error) {
                showAlert(`❌ Web UI error: ${error.message}`, 'error');
            }
        }
        
        async function startAPI() {
            try {
                const result = await pywebview.api.start_api();
                
                if (result.success) {
                    showAlert('🔌 API server started successfully at http://localhost:8000', 'success');
                } else {
                    showAlert(`❌ Failed to start API: ${result.error}`, 'error');
                }
            } catch (error) {
                showAlert(`❌ API error: ${error.message}`, 'error');
            }
        }
        
        function displayResult(result, responseTime) {
            const resultsDiv = document.getElementById('results');
            const timestamp = new Date().toLocaleTimeString();
            
            let statusBadge = '';
            if (result.cached) {
                statusBadge = '<span class="status-indicator status-online">⚡ Cached Result</span>';
            } else if (result.source === 'quick_search') {
                statusBadge = '<span class="status-indicator status-processing">🚀 Quick Search</span>';
            } else if (result.source === 'vector') {
                statusBadge = '<span class="status-indicator status-processing">🎯 Vector Search</span>';
            } else {
                statusBadge = '<span class="status-indicator status-processing">🔄 Fallback Search</span>';
            }
            
            resultsDiv.innerHTML = `
                <div style="margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--slate-200); display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        ${statusBadge}
                        <span style="color: var(--slate-500); font-size: var(--text-xs); margin-left: 1rem;">
                            ${responseTime}s • ${timestamp}
                        </span>
                    </div>
                </div>
                <div style="color: var(--slate-800); line-height: 1.6;">
                    ${result.answer || result.response || 'No response received'}
                </div>
            `;
            
            resultsDiv.classList.add('fade-in');
        }
        
        function displayError(error) {
            const resultsDiv = document.getElementById('results');
            const timestamp = new Date().toLocaleTimeString();
            
            resultsDiv.innerHTML = `
                <div style="margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--slate-200);">
                    <span class="status-indicator status-error">❌ Error</span>
                    <span style="color: var(--slate-500); font-size: var(--text-xs); margin-left: 1rem;">
                        ${timestamp}
                    </span>
                </div>
                <div style="color: var(--error);">
                    ${error}
                </div>
            `;
        }
        
        function showProgress(show) {
            const progressContainer = document.getElementById('progress-container');
            const progressBar = document.getElementById('progress-bar');
            
            if (show) {
                progressContainer.style.display = 'block';
                progressBar.style.width = '0%';
                
                // Simulate progress
                let progress = 0;
                const interval = setInterval(() => {
                    progress += Math.random() * 30;
                    if (progress > 90) progress = 90;
                    progressBar.style.width = progress + '%';
                }, 200);
                
                progressContainer.dataset.interval = interval;
            } else {
                progressContainer.style.display = 'none';
                if (progressContainer.dataset.interval) {
                    clearInterval(progressContainer.dataset.interval);
                }
                progressBar.style.width = '100%';
            }
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
        
        function showAlert(message, type = 'info') {
            // Create alert element
            const alert = document.createElement('div');
            alert.className = `alert alert-${type} fade-in`;
            alert.innerHTML = message;
            
            // Insert at top of main content
            const mainContent = document.querySelector('.main-content');
            mainContent.insertBefore(alert, mainContent.firstChild);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }
        
        // Initialize metrics
        updateMetric('system-load', 'Low');
        updateMetric('response-time', '--');
        updateMetric('cache-rate', '0%');
        updateMetric('query-count', '0');
        
        // Focus on query input when page loads
        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('queryInput').focus();
        });
    </script>
</body>
</html>
        """

class S3AIWebAPI:
    """API class for handling web interface interactions"""
    
    def query(self, query_text):
        """Handle query execution"""
        try:
            # Import here to avoid circular imports
            from s3ai_query import main as query_main
            import sys
            from io import StringIO
            
            # Capture output
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            try:
                # Execute query
                result = query_main([query_text])
                output = captured_output.getvalue()
                
                return {
                    "answer": output or "No response generated",
                    "source": "s3ai_query",
                    "cached": False,
                    "success": True
                }
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "source": "error",
                "cached": False,
                "success": False
            }
    
    def upload_files(self):
        """Handle file upload dialog"""
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.lift()
            root.attributes('-topmost', True)
            
            files = filedialog.askopenfilenames(
                title="Select Documents to Upload",
                filetypes=[
                    ("PDF files", "*.pdf"),
                    ("Text files", "*.txt"),
                    ("Markdown files", "*.md"),
                    ("JSON files", "*.json"),
                    ("Word documents", "*.docx"),
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