# S3 On-Prem AI Assistant - Speed Optimized

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1%2B-green.svg)](https://python.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29%2B-red)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.108%2B-teal)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Offline AI](https://img.shields.io/badge/Offline-AI-important.svg)](https://ollama.com/)
[![PHI3 Powered](https://img.shields.io/badge/LLM-PHI3_Mini-ff69b4.svg)](https://ollama.com/library/phi3)
[![Performance](https://img.shields.io/badge/Performance-15--60x_Faster-brightgreen.svg)](#performance-improvements)

A **lightning-fast**, fully offline-capable AI assistant for answering operational, admin, and troubleshooting questions for on-premises S3-compatible platforms. **15-60x faster** than typical implementations with advanced caching and optimization.

## Support Me

If you find this project helpful, you can support me here:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-yellow?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://buymeacoffee.com/hendrawan)


## Supported Platforms

- **Cloudian HyperStore**
- **Huawei OceanStor** 
- **Pure FlashBlade**
- **IBM Cloud Object Storage**
- **MinIO**
- **Dell ECS**
- **NetApp StorageGRID**
- And more S3-compatible storage systems

## Key Features

- **Lightning Fast**: Subsecond responses with multi-tier caching
- **Smart Search**: Vector + pre-indexed + fallback search
- **Multi-Interface**: CLI, Web UI, and REST API
- **Fully Offline**: No cloud dependency, runs entirely on-premises
- **Performance Monitoring**: Built-in timing and metrics
- **Intelligent Fallbacks**: Progressive search strategy
- **Response Caching**: Instant answers for repeated queries
- **Document Types**: PDF, TXT, JSON, MD support

## Performance Improvements

| Query Type | Before | After | Improvement |
|-----------|--------|--------|-------------|
| **Cached queries** | 3-5s | 0.01s | **300-500x faster** |
| **Bucket dept queries** | 5-10s | 0.1-0.5s | **20-100x faster** |
| **Vector search** | 5-15s | 1-3s | **5-10x faster** |
| **Model loading** | 5-10s | 2-5s | **2-3x faster** |

## Architecture Overview

```
Query Input
    |
[Input Validation & Security]
    |
[1. Cache Layer] <-> Redis (Optional)
    | (miss)
[2. Quick Bucket Search] <-> Pre-indexed Metadata
    | (miss)
[3. Vector Search] <-> FAISS + HuggingFace Embeddings
    | (miss)
[4. Text Fallback] <-> Raw Text Search
    |
[AI Response Generation] <-> Ollama (PHI3:mini)
    |
[Response Caching]
    |
JSON Response
```

### Multi-Tier Search Strategy

1. **Cache Layer** (0.01s): Instant responses for repeated queries
2. **Quick Bucket Search** (0.1-0.5s): Pre-indexed department/label searches
3. **Vector Search** (1-3s): Semantic similarity with FAISS
4. **Text Fallback** (2-4s): Keyword matching in raw documents

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/hndrwn-dk/s3-onprem-ai-assistant.git
cd s3-onprem-ai-assistant

# Place your documents in docs/
cp your-s3-docs/* docs/

# Start all services
docker-compose up -d

# Access interfaces
# Web UI: http://localhost:8501
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull phi3:mini

# Place documents and build embeddings
mkdir docs && cp your-documents/* docs/
python build_embeddings_all.py

# Start services
python api.py &
streamlit run streamlit_ui.py
```

## Project Structure

```
s3-onprem-ai-assistant/
|-- api.py                 # FastAPI REST API server
|-- streamlit_ui.py        # Streamlit web interface
|-- s3ai_query.py         # Command-line interface
|-- model_cache.py        # LLM and vector store caching
|-- response_cache.py     # Response caching system
|-- bucket_index.py       # Quick bucket search index
|-- utils.py              # Document loading and utilities
|-- config.py            # Configuration management
|-- validation.py        # Input validation and security
|-- build_embeddings_all.py # Embedding generation script
|-- requirements.txt     # Python dependencies
|-- Dockerfile          # Container image definition
|-- docker-compose.yml  # Multi-service deployment
|-- docs/               # Your documents go here
|-- s3_all_docs/        # Generated vector embeddings
|-- cache/              # Response cache storage
|-- tests/              # Test suite
`-- logs/               # Application logs
```

## Usage Examples

### Web Interface
- Upload documents via the sidebar
- Ask questions in natural language
- View performance metrics and cache stats
- Browse query history

### API Interface

```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "show all buckets under dept: engineering"}'

# Get performance metrics
curl http://localhost:8000/metrics
```

### CLI Interface

```bash
# Direct query
python s3ai_query.py "show buckets with label: production"

# Interactive mode
python s3ai_query.py
> Enter your question: how to configure S3 access policies?
```

## Sample Queries

### Bucket Management
```
"show all buckets under dept: engineering"
"find buckets with label: production"
"list buckets created by user: admin"
"show buckets with size > 100GB"
```

### Operational Queries
```
"how to configure S3 access policies?"
"what are the backup procedures for critical buckets?"
"how to set up replication between sites?"
"troubleshoot slow S3 performance"
```

### Administrative Tasks
```
"how to add new users to S3?"
"what are the monitoring best practices?"
"how to upgrade Cloudian software?"
"configure SSL certificates for S3"
```

## Configuration

### Environment Variables

```bash
# Core Configuration
export S3AI_LOG_LEVEL=INFO
export S3AI_LLM_MODEL=phi3:mini
export S3AI_OLLAMA_BASE_URL=http://localhost:11434

# Performance Tuning
export S3AI_VECTOR_SEARCH_K=5
export S3AI_CHUNK_SIZE=1000
export S3AI_CHUNK_OVERLAP=100

# Security Settings
export S3AI_RATE_LIMIT_PER_MINUTE=30
export S3AI_MAX_QUERY_LENGTH=2000
export S3AI_MAX_FILE_SIZE_MB=100

# API Configuration
export S3AI_API_HOST=0.0.0.0
export S3AI_API_PORT=8000
export S3AI_DEBUG_MODE=false
```

### Advanced Configuration

See [config.py](config.py) for the complete configuration dataclass with validation.

## Security Features

### Input Validation
- Query sanitization and length limits
- File path validation to prevent directory traversal
- File type and size restrictions
- XSS and code injection prevention

### API Security
- Rate limiting per IP address
- CORS configuration for trusted origins
- Input validation with Pydantic models
- Comprehensive error handling

### Infrastructure Security
- Non-root Docker containers
- Secure deserialization disabled
- Environment variable configuration
- Comprehensive logging and monitoring

## Performance Optimization

### Caching Strategy
- **Response Cache**: Stores AI-generated answers
- **Model Cache**: Pre-loads LLM and embeddings
- **Quick Index**: Pre-computed bucket searches
- **Vector Cache**: FAISS similarity search optimization

### Memory Management
- Lazy model loading
- Configurable chunk sizes
- Vector search result limits
- Automatic cache cleanup

### Speed Optimizations
- Concurrent document processing
- Streaming responses
- Background model preloading
- Progressive search fallbacks

## Testing

### Comprehensive Test Suite

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python -m pytest tests/test_validation.py -v
python -m pytest tests/test_api.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Test Categories
- **Security Tests**: Input validation, path traversal, XSS prevention
- **API Tests**: Endpoint functionality, rate limiting, error handling
- **Performance Tests**: Response times, caching, concurrent requests
- **Integration Tests**: End-to-end workflows

## Deployment

### Production Deployment

```bash
# Production with monitoring
docker-compose --profile production --profile monitoring up -d

# Manual deployment
pip install -r requirements.txt
python build_embeddings_all.py
gunicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Monitoring
- **Health endpoints**: `/health`, `/metrics`, `/cache/stats`
- **Prometheus integration**: Built-in metrics export
- **Structured logging**: JSON format with performance data
- **Performance tracking**: Response times and cache hit rates

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

## Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/hndrwn-dk/s3-onprem-ai-assistant.git
cd s3-onprem-ai-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest pytest-cov mypy black isort

# Setup pre-commit hooks
pre-commit install
```

### Code Quality
- **Type checking**: MyPy static analysis
- **Code formatting**: Black and isort
- **Testing**: Pytest with coverage
- **Security**: Bandit security linting
- **Documentation**: Comprehensive docstrings

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python run_tests.py`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Troubleshooting

### Common Issues

**Model Loading Errors**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Reinstall model
ollama pull phi3:mini
```

**Vector Store Issues**
```bash
# Rebuild embeddings
rm -rf s3_all_docs/
python build_embeddings_all.py
```

**Performance Issues**
```bash
# Clear cache
curl -X POST http://localhost:8000/cache/clear

# Check system resources
docker stats
```

### Debug Mode

```bash
export S3AI_LOG_LEVEL=DEBUG
export S3AI_DEBUG_MODE=true
python api.py
```

## Changelog

### v2.2.7 - Latest (Security & Performance Update)
- **SECURITY**: Fixed dangerous deserialization vulnerability
- **NEW**: Document upload via Streamlit UI
- **NEW**: Automatic embedding building
- **NEW**: Enhanced input validation and sanitization
- **NEW**: Comprehensive test suite
- **NEW**: Docker deployment with monitoring
- **IMPROVED**: Enhanced error handling and logging
- **IMPROVED**: Configuration management with validation
- **IMPROVED**: Performance monitoring and metrics

### v2.2.6 - Performance Optimization
- Multi-tier caching system (15-60x faster)
- Quick bucket search pre-indexing
- Response caching with TTL
- Model loading optimization
- Progressive search fallbacks

### v2.2.5 - Security Enhancement
- Input validation and sanitization
- Rate limiting implementation
- CORS configuration
- Error handling improvements

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Ollama** for local LLM inference
- **LangChain** for AI framework
- **FAISS** for vector similarity search
- **HuggingFace** for embeddings
- **FastAPI** for high-performance API
- **Streamlit** for rapid UI development

---

**Questions or issues?** Open an issue on GitHub or check the [troubleshooting guide](DEPLOYMENT.md#troubleshooting).

**Need help with deployment?** See the comprehensive [deployment guide](DEPLOYMENT.md).

**Want to contribute?** Read the [contributing guidelines](CONTRIBUTING.md).