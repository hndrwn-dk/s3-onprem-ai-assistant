# Vector Search Troubleshooting Guide

## Problem: Vector Search Falls Back to Sample File

If your vector search is always falling back to `docs/sample_bucket_metadata_converted.txt` instead of using uploaded PDFs, follow this guide.

## Root Cause Analysis

The issue occurs when:
1. ❌ **Vector index is missing** (`s3_all_docs/` directory doesn't exist)
2. ❌ **Chunks file is missing** (`s3_all_chunks.pkl` doesn't exist) 
3. ❌ **No real documents uploaded** (only sample file exists)
4. ❌ **Build process failed** (dependencies or memory issues)

## Quick Diagnosis

Run the diagnostic script:
```bash
python3 diagnose_vector_search.py
```

Or use the setup script:
```bash
./setup_airgapped.sh
```

## Step-by-Step Fix

### 1. Check Current Status
```bash
# Check if vector index exists
ls -la s3_all_docs/
ls -la s3_all_chunks.pkl

# Check documents in docs folder
ls -la docs/
```

### 2. Upload Your Documents
```bash
# Place your S3 vendor PDFs in the docs folder
cp /path/to/your/s3_vendor_docs/*.pdf docs/
cp /path/to/your/s3_vendor_docs/*.txt docs/
```

**Supported formats:** PDF, TXT, MD, JSON

### 3. Rebuild Vector Index
```bash
# This will process all documents in docs/ folder
python3 build_embeddings_all.py
```

**Expected output:**
```
=== Starting vector index build ===
✓ Found X real documents for embedding
Total documents loaded: X
Document sources:
  - docs/vendor_doc1.pdf: 1 documents
  - docs/vendor_doc2.pdf: 1 documents
...
✓ Vector store saved successfully
✓ Chunks saved successfully
=== Vector index build completed successfully ===
```

### 4. Verify Fix
After rebuilding, you should see:
```bash
s3_all_docs/
├── index.faiss
└── index.pkl
s3_all_chunks.pkl
```

## Air-Gapped Environment Setup

### Pre-download Required Models
```bash
# For air-gapped environments, pre-download the embedding model
python3 -c "
from langchain_community.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
print('Model downloaded successfully')
"
```

### Verify Ollama Setup
```bash
# Check if Ollama is running locally
curl http://localhost:11434/api/tags

# Test model availability
ollama list
```

## Common Issues & Solutions

### Issue 1: "No real documents found for embedding"
**Cause:** Only `sample_bucket_metadata_converted.txt` exists in docs folder  
**Solution:** Upload actual S3 vendor PDFs to docs folder

### Issue 2: "Vector store not available"
**Cause:** Vector index wasn't built or build failed  
**Solution:** Run `python3 build_embeddings_all.py` after uploading documents

### Issue 3: "ModuleNotFoundError: langchain_community"
**Cause:** Missing Python dependencies  
**Solution:** Install requirements in proper environment:
```bash
pip install -r requirements.txt
# or in Docker:
docker-compose build
```

### Issue 4: Build process hangs or fails
**Cause:** Insufficient memory or trying to download models  
**Solutions:**
- Reduce `CHUNK_SIZE` in config.py
- Pre-download embedding models
- Increase available memory

### Issue 5: Vector search returns empty results
**Cause:** Index built but query doesn't match document content  
**Solutions:**
- Check document content was extracted properly
- Verify chunks were created (`s3_all_chunks.pkl` size > 0)
- Test with simpler queries first

## Verification Steps

### 1. Check Vector Index Health
```python
python3 -c "
from model_cache import ModelCache
try:
    vs = ModelCache.get_vector_store()
    if vs:
        print('✅ Vector store loaded successfully')
        print(f'Index size: {vs.index.ntotal} vectors')
    else:
        print('❌ Vector store failed to load')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### 2. Test Document Loading
```python
python3 -c "
from utils import load_documents_from_path, ensure_documents_for_embedding
docs = load_documents_from_path()
print(f'Total documents: {len(docs)}')
print(f'Real documents available: {ensure_documents_for_embedding()}')
"
```

### 3. Test API Endpoint
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"question": "test query about your uploaded documents"}'
```

## File Structure After Fix

```
project_root/
├── build_embeddings_all.py          # ✅ Build script (in root)
├── docs/                             # ✅ Upload PDFs here
│   ├── vendor_doc1.pdf              # ✅ Your S3 vendor docs
│   ├── vendor_doc2.pdf              # ✅ Your S3 vendor docs
│   └── sample_bucket_metadata_converted.txt  # Sample file
├── s3_all_docs/                      # ✅ Generated vector index
│   ├── index.faiss                  # ✅ FAISS index
│   └── index.pkl                    # ✅ FAISS metadata
├── s3_all_chunks.pkl                 # ✅ Document chunks
└── ...other files
```

## Success Indicators

✅ **Vector search working correctly when:**
- `s3_all_docs/` directory exists with `index.faiss` and `index.pkl`
- `s3_all_chunks.pkl` file exists and has reasonable size
- API logs show "Vector store loaded successfully"
- Queries return relevant content from uploaded documents
- No fallback to `sample_bucket_metadata_converted.txt`

❌ **Still falling back to sample file when:**
- Missing vector index files
- Build process didn't complete successfully
- No uploaded documents in docs folder
- Dependencies missing or incompatible

## Contact & Support

If you continue to experience issues:
1. Run `python3 diagnose_vector_search.py` for detailed diagnostics
2. Check API logs during startup and query execution
3. Verify air-gapped environment has all required dependencies
4. Ensure sufficient memory for processing large PDF documents