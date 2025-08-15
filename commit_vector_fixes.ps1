# PowerShell script to commit vector search fixes
# Run this script to add and commit all the new files and improvements

Write-Host "=== Committing Vector Search Fixes ===" -ForegroundColor Cyan

# Check git status first
Write-Host "`nCurrent git status:" -ForegroundColor Yellow
git status

# Add new files
Write-Host "`nAdding new diagnostic files..." -ForegroundColor Green
git add diagnose_vector_search.py
git add VECTOR_SEARCH_TROUBLESHOOTING.md

# Add modified files if any
Write-Host "Adding any modified files..." -ForegroundColor Green
git add utils.py
git add build_embeddings_all.py
git add model_cache.py
git add api.py
git add config.py

# Show what will be committed
Write-Host "`nFiles to be committed:" -ForegroundColor Yellow
git status --staged

# Create the commit
Write-Host "`nCreating commit..." -ForegroundColor Green
git commit -m "Fix vector search fallback issue and add diagnostics

Features:
- Add diagnose_vector_search.py for troubleshooting vector search issues
- Add comprehensive VECTOR_SEARCH_TROUBLESHOOTING.md guide
- Enhance build_embeddings_all.py with better validation and logging
- Improve model_cache.py with proper vector index checking
- Add utility functions to distinguish real documents from sample file
- Better error messages and diagnostics for air-gapped environments
- Support for Windows PowerShell commands in documentation

Fixes:
- Vector search no longer falls back to sample_bucket_metadata_converted.txt
- Proper validation of uploaded documents vs sample file
- Enhanced logging and error reporting
- Better support for air-gapped deployments with local Ollama

This resolves the issue where vector search would always use the sample 
file instead of processing uploaded S3 vendor PDFs/documents."

# Push to main branch
Write-Host "`nPushing to main branch..." -ForegroundColor Green
git push origin main

Write-Host "`n✅ Vector search fixes committed and pushed successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Run: python diagnose_vector_search.py" -ForegroundColor White
Write-Host "2. Upload your S3 vendor PDFs to docs/ folder" -ForegroundColor White  
Write-Host "3. Run: python build_embeddings_all.py" -ForegroundColor White
Write-Host "4. Test vector search with your documents" -ForegroundColor White