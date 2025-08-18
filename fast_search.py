#!/usr/bin/env python
"""
Fast Search Module - Bypasses slow vector loading
Provides instant search capabilities for enterprise use
"""

import os
import time
import re
from pathlib import Path
from typing import List, Dict, Optional

class FastSearch:
    """Fast text-based search that bypasses slow vector loading"""
    
    def __init__(self):
        self.documents = {}
        self.loaded = False
        
    def load_documents(self):
        """Load documents into memory for fast searching"""
        if self.loaded:
            return
            
        print("🔍 Loading documents for fast search...")
        start_time = time.time()
        
        docs_path = Path("docs")
        if not docs_path.exists():
            print("❌ No docs directory found")
            return
            
        # Load text files quickly
        for file_path in docs_path.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents[str(file_path)] = {
                        'content': content,
                        'filename': file_path.name,
                        'type': 'txt'
                    }
            except Exception as e:
                print(f"⚠️ Failed to load {file_path}: {e}")
        
        # Load markdown files
        for file_path in docs_path.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents[str(file_path)] = {
                        'content': content,
                        'filename': file_path.name,
                        'type': 'md'
                    }
            except Exception as e:
                print(f"⚠️ Failed to load {file_path}: {e}")
        
        self.loaded = True
        load_time = time.time() - start_time
        print(f"✅ Fast search loaded {len(self.documents)} documents in {load_time:.2f}s")
        
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Fast text-based search"""
        if not self.loaded:
            self.load_documents()
            
        if not self.documents:
            return []
            
        query_lower = query.lower()
        query_words = re.findall(r'\w+', query_lower)
        
        results = []
        
        for doc_path, doc_info in self.documents.items():
            content_lower = doc_info['content'].lower()
            
            # Calculate relevance score
            score = 0
            matches = []
            
            for word in query_words:
                word_count = content_lower.count(word)
                if word_count > 0:
                    score += word_count
                    matches.append(word)
            
            if score > 0:
                # Find relevant snippet
                snippet = self._get_relevant_snippet(doc_info['content'], query_words)
                
                results.append({
                    'filename': doc_info['filename'],
                    'score': score,
                    'matches': matches,
                    'snippet': snippet,
                    'type': doc_info['type']
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
    
    def _get_relevant_snippet(self, content: str, query_words: List[str], snippet_length: int = 500) -> str:
        """Extract relevant snippet around query words"""
        content_lower = content.lower()
        
        # Find first occurrence of any query word
        best_pos = -1
        for word in query_words:
            pos = content_lower.find(word)
            if pos != -1 and (best_pos == -1 or pos < best_pos):
                best_pos = pos
        
        if best_pos == -1:
            return content[:snippet_length] + "..."
        
        # Extract snippet around the found word
        start = max(0, best_pos - snippet_length // 2)
        end = min(len(content), start + snippet_length)
        
        snippet = content[start:end]
        
        # Clean up snippet
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
            
        return snippet

# Global instance
fast_search = FastSearch()

def quick_answer(query: str) -> str:
    """Generate quick answer using fast search"""
    start_time = time.time()
    
    # Load documents if not loaded
    if not fast_search.loaded:
        fast_search.load_documents()
    
    # Search for relevant content
    results = fast_search.search(query, max_results=3)
    
    if not results:
        return "No relevant information found in the documents. Try uploading more S3 documentation or using different keywords."
    
    # Format response
    response_parts = [f"Based on your S3 documentation (found in {len(results)} files):"]
    
    for i, result in enumerate(results, 1):
        response_parts.append(f"\n{i}. From {result['filename']}:")
        response_parts.append(f"   {result['snippet']}")
        
    response_parts.append(f"\nSearch completed in {time.time() - start_time:.2f} seconds")
    response_parts.append(f"Matched keywords: {', '.join(set(word for r in results for word in r['matches']))}")
    
    return "\n".join(response_parts)

if __name__ == "__main__":
    # Test the fast search
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Query: {query}")
        print("-" * 50)
        print(quick_answer(query))
    else:
        print("Usage: python fast_search.py 'your query'")
        print("Example: python fast_search.py 'how to purge bucket'")