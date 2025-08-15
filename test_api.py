#!/usr/bin/env python3
"""
Test script for the API endpoint
"""

import requests
import json
import time

def test_api(question: str, base_url: str = "http://localhost:8000"):
    """Test the API with a question"""
    print(f"🧪 Testing API with question: {question}")
    print("-" * 60)
    
    url = f"{base_url}/ask"
    payload = {"question": question}
    
    try:
        print(f"📤 Sending POST request to: {url}")
        start_time = time.time()
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes timeout
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS ({response.status_code}) in {response_time:.2f}s")
            print("-" * 60)
            print("📋 Response:")
            print(f"Answer: {result.get('answer', 'No answer')}")
            print(f"Source: {result.get('source', 'Unknown')}")
            print(f"Response Time: {result.get('response_time', 0):.2f}s")
        else:
            print(f"❌ FAILED ({response.status_code}) in {response_time:.2f}s")
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 2 minutes")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection failed - is the API server running?")
        print("Start with: python -m uvicorn api:app --reload")
    except Exception as e:
        print(f"💥 Error: {e}")

def test_health(base_url: str = "http://localhost:8000"):
    """Test the health endpoint"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"🟢 API Health: {result.get('status', 'unknown')}")
            return True
        else:
            print(f"🔴 Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"🔴 Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 API Testing Tool")
    print("=" * 60)
    
    # First check health
    if test_health():
        print()
        # Test the main question
        test_api("how to purge bucket in Cloudian Hyperstore")
        
        print("\n" + "=" * 60)
        print("💡 You can also test manually:")
        print('curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d "{\\"question\\": \\"your question here\\"}"')
    else:
        print("\n❌ API server is not running or not responding")
        print("Start the API server with: python -m uvicorn api:app --reload")