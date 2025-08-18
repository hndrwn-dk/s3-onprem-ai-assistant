#!/usr/bin/env python
"""
Test script to verify what documents are in the vector index
"""

import sys
from pathlib import Path

def test_vector_search(query="bucketops"):
    """Test what documents are retrieved for a specific query"""
    print(f"🔍 Testing vector search for: '{query}'")
    print("-" * 50)
    
    try:
        # Load vector store
        print("📚 Loading vector store...")
        from model_cache import ModelCache
        vector_store = ModelCache.get_vector_store()
        
        if not vector_store:
            print("❌ Vector store not available")
            return
        
        print("✅ Vector store loaded")
        
        # Search for documents
        print(f"🔍 Searching for documents related to '{query}'...")
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        docs = retriever.get_relevant_documents(query)
        
        print(f"📋 Found {len(docs)} documents:")
        print()
        
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'unknown')
            content_preview = doc.page_content[:200].replace('\n', ' ')
            
            print(f"{i+1}. SOURCE: {source}")
            print(f"   LENGTH: {len(doc.page_content)} characters")
            print(f"   PREVIEW: {content_preview}...")
            print(f"   CONTAINS 'bucketops': {'bucketops' in doc.page_content.lower()}")
            print(f"   CONTAINS 'cloudian': {'cloudian' in doc.page_content.lower()}")
            print("-" * 40)
        
        if not docs:
            print("❌ No documents found for this query")
            print("💡 This means either:")
            print("   • The term doesn't exist in your documents")
            print("   • The vector search isn't working properly")
            print("   • The index doesn't contain the expected content")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def check_docs_folder():
    """Check what's actually in the docs folder"""
    print("\n📁 Checking docs folder contents:")
    print("-" * 50)
    
    docs_path = Path("docs")
    if not docs_path.exists():
        print("❌ docs/ folder doesn't exist")
        return
    
    files = list(docs_path.glob("*"))
    print(f"📄 Found {len(files)} files:")
    
    for file_path in files:
        if file_path.is_file():
            size_kb = file_path.stat().st_size / 1024
            print(f"  • {file_path.name} ({size_kb:.1f} KB)")
            
            # Check if it's a text file we can preview
            if file_path.suffix.lower() in ['.txt', '.md']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(500)
                        print(f"    Preview: {content[:100]}...")
                        print(f"    Contains 'bucketops': {'bucketops' in content.lower()}")
                        print(f"    Contains 'cloudian': {'cloudian' in content.lower()}")
                except:
                    print("    (Could not read file)")

def test_text_search(query="bucketops"):
    """Test text-based search in documents"""
    print(f"\n🔍 Testing text search for: '{query}'")
    print("-" * 50)
    
    try:
        from utils import load_txt_documents, search_in_fallback_text
        
        print("📚 Loading text documents...")
        fallback_text = load_txt_documents()
        
        if not fallback_text:
            print("❌ No text documents loaded")
            return
        
        print(f"✅ Loaded text documents ({len(fallback_text)} characters)")
        
        print(f"🔍 Searching for '{query}'...")
        relevant_context = search_in_fallback_text(query, fallback_text)
        
        if relevant_context:
            print("✅ Found relevant context:")
            print(relevant_context[:500] + "..." if len(relevant_context) > 500 else relevant_context)
        else:
            print("❌ No relevant context found in text search")
            
    except Exception as e:
        print(f"❌ Text search failed: {e}")

def main():
    print("🏢 S3 On-Premise AI Assistant - Document Search Test")
    print("=" * 60)
    
    query = sys.argv[1] if len(sys.argv) > 1 else "bucketops"
    
    # Check what's in docs folder
    check_docs_folder()
    
    # Test text search
    test_text_search(query)
    
    # Test vector search
    test_vector_search(query)
    
    print("\n" + "=" * 60)
    print("🎯 Analysis Complete")
    print("💡 If documents contain the term but search doesn't find it:")
    print("   • Vector index may not be properly built")
    print("   • Search algorithm may need tuning")
    print("   • Document processing may have issues")

if __name__ == "__main__":
    main()