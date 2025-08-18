#!/usr/bin/env python
"""
Check Cloudian PDF content to verify bucketops exists
"""

import sys
from pathlib import Path

def check_cloudian_pdfs():
    """Check if bucketops exists in Cloudian PDFs"""
    print("🔍 Checking Cloudian PDF files for 'bucketops'...")
    print("-" * 50)
    
    docs_path = Path("docs")
    cloudian_files = list(docs_path.glob("*Cloudian*"))
    
    if not cloudian_files:
        print("❌ No Cloudian files found in docs/")
        return
    
    print(f"📄 Found {len(cloudian_files)} Cloudian files:")
    for file_path in cloudian_files:
        print(f"  • {file_path.name}")
    
    # Try to extract text from PDFs
    print("\n🔍 Searching for 'bucketops' in Cloudian PDFs...")
    
    for file_path in cloudian_files:
        print(f"\n📖 Checking: {file_path.name}")
        try:
            # Try different PDF reading methods
            found_bucketops = False
            
            # Method 1: Try PyPDF2
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text_content = ""
                    for page_num, page in enumerate(reader.pages[:10]):  # Check first 10 pages
                        page_text = page.extract_text()
                        text_content += page_text
                        if 'bucketops' in page_text.lower():
                            print(f"  ✅ Found 'bucketops' on page {page_num + 1}")
                            print(f"     Context: {page_text[page_text.lower().find('bucketops')-50:page_text.lower().find('bucketops')+100]}")
                            found_bucketops = True
                    
                    if not found_bucketops:
                        print(f"  ❌ 'bucketops' not found in first 10 pages")
                        # Check if any S3-related terms exist
                        s3_terms = ['bucket', 'object', 'storage', 'hyperstore']
                        found_terms = [term for term in s3_terms if term in text_content.lower()]
                        print(f"  📋 Found S3 terms: {found_terms}")
            
            except ImportError:
                print("  ⚠️ PyPDF2 not available, trying alternative...")
                
                # Method 2: Try pypdf
                try:
                    import pypdf
                    with open(file_path, 'rb') as f:
                        reader = pypdf.PdfReader(f)
                        for page_num, page in enumerate(reader.pages[:5]):
                            page_text = page.extract_text()
                            if 'bucketops' in page_text.lower():
                                print(f"  ✅ Found 'bucketops' on page {page_num + 1}")
                                found_bucketops = True
                                break
                        
                        if not found_bucketops:
                            print("  ❌ 'bucketops' not found in first 5 pages")
                
                except ImportError:
                    print("  ❌ No PDF readers available")
            
        except Exception as e:
            print(f"  ❌ Error reading {file_path.name}: {e}")

def check_vector_index():
    """Check what's actually in the vector index"""
    print("\n🎯 Checking vector index content...")
    print("-" * 50)
    
    try:
        from pathlib import Path
        index_path = Path("s3_all_docs")
        
        if not index_path.exists():
            print("❌ Vector index (s3_all_docs) doesn't exist")
            return
        
        # Check index files
        index_files = list(index_path.glob("*"))
        print(f"📁 Vector index contains {len(index_files)} files:")
        for file_path in index_files:
            size_kb = file_path.stat().st_size / 1024
            print(f"  • {file_path.name} ({size_kb:.1f} KB)")
        
        # Try to load and check a sample
        print("\n🔍 Testing vector index search...")
        from model_cache import ModelCache
        
        # Quick test without full loading
        print("⚡ Testing quick retrieval...")
        vector_store = ModelCache.get_vector_store()
        
        if vector_store:
            # Test search
            retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            docs = retriever.get_relevant_documents("bucketops")
            
            print(f"📋 Vector search returned {len(docs)} documents for 'bucketops':")
            for i, doc in enumerate(docs):
                source = doc.metadata.get('source', 'unknown')
                contains_bucketops = 'bucketops' in doc.page_content.lower()
                print(f"  {i+1}. {source} - Contains 'bucketops': {contains_bucketops}")
        
    except Exception as e:
        print(f"❌ Vector index check failed: {e}")

def main():
    print("🏢 S3 On-Premise AI Assistant - Cloudian Document Check")
    print("=" * 60)
    
    # Check Cloudian PDFs
    check_cloudian_pdfs()
    
    # Check vector index
    check_vector_index()
    
    print("\n" + "=" * 60)
    print("🎯 Summary:")
    print("• If 'bucketops' exists in PDFs but not found by search:")
    print("  → Vector index may need rebuilding")
    print("  → PDF extraction may have issues")
    print("• If 'bucketops' doesn't exist in PDFs:")
    print("  → Term may not be in your documentation")
    print("  → Try different search terms")

if __name__ == "__main__":
    main()