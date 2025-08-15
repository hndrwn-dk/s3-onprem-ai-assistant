# S3 On-Premise AI Assistant

🚀 **Ultra-fast AI assistant for S3 storage systems** (Cloudian, IBM, MinIO, etc.)

## Quick Start

### 1. Modern Desktop App (Easiest) 🖥️
```bash
python modern_desktop_app.py
```
*Beautiful, modern GUI with dark theme and all features built-in*

### 2. CLI Interface
```bash
python s3ai_query.py "how to purge bucket in Cloudian Hyperstore"
```

### 3. Web Interface  
```bash
python -m streamlit run streamlit_ui.py
# Open: http://localhost:8501
```

### 4. REST API
```bash
python -m uvicorn api:app --reload
# Test: curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d '{"question": "your question"}'
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your documents:**
   ```bash
   # Copy your PDF/TXT files to the docs/ folder
   cp your-s3-docs.pdf docs/
   ```

3. **Build vector index:**
   ```bash
   python build_embeddings_all.py
   ```

4. **Start using:**
   ```bash
   python s3ai_query.py "your question"
   ```

## Features

✅ **Vector Search** - Fast semantic search through your documents  
✅ **LLM Processing** - Clean, human-readable answers  
✅ **Multiple Interfaces** - CLI, Web UI, REST API  
✅ **Caching** - Instant responses for repeated queries  
✅ **Air-gap Ready** - Works offline once configured  

## File Structure

```
📁 S3 AI Assistant/
├── 🖥️ modern_desktop_app.py   # Modern Desktop GUI (Recommended)
├── 📱 desktop_app.py         # Classic Desktop GUI
├── 🚀 s3ai_query.py          # CLI interface
├── 🌐 streamlit_ui.py        # Web interface  
├── 🔗 api.py                 # REST API
├── ⚙️ config.py              # Configuration
├── 🧠 model_cache.py         # LLM & vector caching
├── 🔍 bucket_index.py        # Quick bucket search
├── 💾 response_cache.py      # Query caching
├── 🛠️ utils.py               # Utilities
├── 🏗️ build_embeddings_all.py # Vector index builder
├── ✅ validation.py          # System validation
├── 📦 build_package.py       # Desktop packaging tool
├── 📄 requirements.txt       # Dependencies
├── 📁 docs/                  # Your PDF documents
├── 📁 s3_all_docs/           # Vector index files
├── 📁 cache/                 # Response cache
├── 📁 deployment/            # Docker & deployment files
└── 📁 documentation/         # Detailed documentation
```

## Documentation

- **Setup Guide**: `documentation/DEPLOYMENT.md`
- **Testing Guide**: `documentation/TESTING.md`  
- **Contributing**: `documentation/CONTRIBUTING.md`

---

**🎯 Perfect for:** DevOps teams, storage administrators, and anyone working with S3-compatible storage systems who needs instant access to technical documentation.