#!/usr/bin/env python
"""
s3ai_query.py - S3 AI Query Interface
Fast PDF search + AI formatting for vendor documentation
Searches actual vendor docs + makes them human readable
"""

import sys
import time
from pathlib import Path

def main_query(query):
    """Fast PDF search + AI formatting for human readability"""
    print(f"🔍 Smart Search for: '{query}'")
    print("-" * 50)
    
    start_time = time.time()
    
    # Step 1: Fast PDF search to get actual vendor content
    try:
        from fast_pdf_search import search_pdfs_directly
        pdf_results = search_pdfs_directly(query, max_results=3)
        
        if "No matches found" in pdf_results:
            return pdf_results
        
        print("✅ Found vendor documentation content")
        search_time = time.time() - start_time
        
        # Step 2: Use AI to make it human readable (but ONLY from retrieved content)
        print("🤖 Formatting with AI (using ONLY retrieved vendor docs)...")
        
        try:
            from model_cache import ModelCache
            llm = ModelCache.get_llm()
            
            # Strict prompt that forces AI to use only the provided content
            prompt = f"""CRITICAL: You are a technical documentation formatter. You must ONLY use the content provided below from vendor documentation. Do NOT add any information from your training data.

USER QUERY: "{query}"

VENDOR DOCUMENTATION CONTENT (from PDF extraction):
{pdf_results}

TASK: 
1. Format the above vendor documentation content to be human-readable
2. Extract and organize the relevant API endpoints and information
3. Present it in a clear, structured way
4. ONLY use information from the provided vendor documentation above
5. If the documentation doesn't fully answer the query, say so explicitly

FORMATTED RESPONSE BASED ONLY ON PROVIDED VENDOR DOCS:"""

            # Get AI response
            ai_start = time.time()
            response = llm.invoke(prompt)
            ai_time = time.time() - ai_start
            
            if response and str(response).strip():
                total_time = time.time() - start_time
                
                formatted_response = f"""🎯 Smart Search Results for '{query}'
📚 Source: Your actual vendor documentation
🕒 Total time: {total_time:.2f}s (Search: {search_time:.2f}s + AI formatting: {ai_time:.2f}s)

{str(response).strip()}

---
📋 Raw vendor documentation sources:
{pdf_results}"""
                
                return formatted_response
            else:
                return f"❌ AI formatting failed. Raw results:\n\n{pdf_results}"
        
        except Exception as ai_error:
            print(f"⚠️ AI formatting failed: {ai_error}")
            return f"⚠️ AI formatting failed, showing raw results:\n\n{pdf_results}"
    
    except Exception as e:
        return f"❌ Smart search failed: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python s3ai_query.py <your-question>")
        print("Example: python s3ai_query.py \"bucketops\"")
        print("Example: python s3ai_query.py \"how to purge bucket in cloudian\"")
        return
    
    query = " ".join(sys.argv[1:])
    
    print("🏢 S3 On-Premise AI Assistant")
    print("=" * 50)
    print("🎯 Searching your actual vendor documentation")
    print("✅ Fast PDF search + AI formatting")
    print()
    
    result = main_query(query)
    print(result)

if __name__ == "__main__":
    main()