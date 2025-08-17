#!/usr/bin/env python
"""
Simple Debug Version - S3 On-Premise AI Assistant
Minimal version to test what's working
"""

import sys
import time

def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    
    try:
        import webview
        print("✅ PyWebView imported successfully")
        
        import tkinter as tk
        print("✅ Tkinter imported successfully")
        
        from model_cache import ModelCache
        print("✅ ModelCache imported successfully")
        
        from response_cache import response_cache
        print("✅ ResponseCache imported successfully")
        
        from bucket_index import bucket_index
        print("✅ BucketIndex imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_simple_window():
    """Test simple webview window"""
    print("\n🖥️  Testing simple window...")
    
    try:
        import webview
        
        # Simple HTML for testing
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Window</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    background: #f0f0f0; 
                }
                .test-btn {
                    background: #007bff;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 10px;
                }
            </style>
        </head>
        <body>
            <h1>🏢 S3 On-Premise AI Assistant - Debug Mode</h1>
            <p>If you can see this window, PyWebView is working!</p>
            
            <button class="test-btn" onclick="testAPI()">Test API Call</button>
            <button class="test-btn" onclick="testQuery()">Test Query</button>
            
            <div id="output" style="margin-top: 20px; padding: 10px; background: white; border-radius: 5px;">
                Ready for testing...
            </div>
            
            <script>
                async function testAPI() {
                    document.getElementById('output').innerHTML = 'Testing API...';
                    try {
                        const result = await pywebview.api.test_function();
                        document.getElementById('output').innerHTML = 'API Test Result: ' + JSON.stringify(result);
                    } catch (error) {
                        document.getElementById('output').innerHTML = 'API Error: ' + error.message;
                    }
                }
                
                async function testQuery() {
                    document.getElementById('output').innerHTML = 'Testing query...';
                    try {
                        const result = await pywebview.api.test_query('test query');
                        document.getElementById('output').innerHTML = 'Query Result: ' + JSON.stringify(result);
                    } catch (error) {
                        document.getElementById('output').innerHTML = 'Query Error: ' + error.message;
                    }
                }
            </script>
        </body>
        </html>
        """
        
        # Simple API for testing
        class TestAPI:
            def test_function(self):
                print("🧪 API: test_function called")
                return {"status": "success", "message": "API is working!"}
            
            def test_query(self, query):
                print(f"🔍 API: test_query called with: {query}")
                return {"query": query, "answer": "Test response", "time": time.time()}
        
        # Create window
        window = webview.create_window(
            'S3 AI Assistant - Debug Mode',
            html=html,
            js_api=TestAPI(),
            width=800,
            height=600,
            resizable=True
        )
        
        print("✅ Window created successfully")
        print("🚀 Starting webview (debug mode)...")
        print("💡 If window opens, test the buttons to check API communication")
        print("-" * 60)
        
        webview.start(debug=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Window test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🏢 S3 On-Premise AI Assistant - Simple Debug Mode")
    print("=" * 55)
    print("🔍 This will help identify what's not working")
    print()
    
    # Test imports first
    if not test_imports():
        print("❌ Import test failed. Install dependencies:")
        print("   pip install pywebview streamlit langchain-community")
        return
    
    print("✅ All imports successful!")
    
    # Test simple window
    if test_simple_window():
        print("✅ Desktop window test completed")
    else:
        print("❌ Desktop window test failed")
        print("🌐 Try web interface instead: python start_web.py")

if __name__ == "__main__":
    main()