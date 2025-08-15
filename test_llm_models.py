#!/usr/bin/env python3
"""
Test different LLM models to find the fastest working one
"""

import time
import os
import sys
from langchain_community.llms import Ollama

def test_llm_model(model_name: str, test_prompt: str = "Hello, how are you?"):
    """Test a specific LLM model"""
    print(f"\n🧪 Testing {model_name}...")
    try:
        start_time = time.time()
        
        # Create LLM with minimal settings for speed
        llm = Ollama(
            model=model_name,
            temperature=0.1,  # Lower for faster response
            top_k=5,          # Reduced for speed
            top_p=0.5,        # Reduced for speed
        )
        
        print(f"  ⏳ Sending test prompt...")
        result = llm.invoke(test_prompt)
        
        response_time = time.time() - start_time
        
        if result and result.strip():
            print(f"  ✅ SUCCESS in {response_time:.2f}s")
            print(f"  📝 Response: {result[:100]}...")
            return True, response_time
        else:
            print(f"  ❌ Empty response after {response_time:.2f}s")
            return False, response_time
            
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False, 0

def main():
    print("🔍 LLM Model Testing Tool")
    print("=" * 50)
    
    # Test prompt
    test_prompt = "Explain what bucket purging means in 1 sentence."
    
    # Models to test (based on what you have installed)
    models_to_test = [
        "phi3:mini",      # Current default
        "qwen:latest",    # Alternative you have
        "mistral:latest"  # Alternative you have
    ]
    
    results = []
    
    for model in models_to_test:
        success, response_time = test_llm_model(model, test_prompt)
        results.append((model, success, response_time))
    
    print("\n📊 RESULTS SUMMARY")
    print("=" * 50)
    
    working_models = [(m, t) for m, s, t in results if s]
    
    if working_models:
        # Sort by response time
        working_models.sort(key=lambda x: x[1])
        
        print("✅ Working models (fastest first):")
        for model, response_time in working_models:
            print(f"  {model}: {response_time:.2f}s")
        
        fastest_model = working_models[0][0]
        print(f"\n🚀 RECOMMENDATION: Use {fastest_model}")
        print(f"   Set environment variable: MODEL={fastest_model}")
        
    else:
        print("❌ No models are working properly!")
        print("   Check if Ollama is running: ollama ps")
    
    print("\n🔧 To switch models:")
    for model, success, _ in results:
        if success:
            print(f"   $env:MODEL=\"{model}\" (PowerShell)")

if __name__ == "__main__":
    main()