# 🚀 S3 On-Premises AI Assistant - Deployment Guide v2.2.7

Complete deployment guide for the secure, production-ready S3 AI Assistant.

## 📋 Prerequisites

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 16GB+ recommended (8GB minimum)
- **Storage**: 10GB+ available space
- **OS**: Linux, macOS, or Windows with Docker support
- **Network**: Internet access for initial model download

### Required Software
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Python** 3.8+ (for local development)
- **Git** for cloning the repository

## 🐳 Docker Deployment (Recommended)

### Quick Start with Docker Compose

```bash
# Clone repository
git clone https://github.com/hndrwn-dk/s3-onprem-ai-assistant.git
cd s3-onprem-ai-assistant

# Place your documents in the docs/ directory
cp your-documents/* docs/

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f s3ai-api
```

### Service URLs
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501
- **Ollama**: http://localhost:11434

### Production Deployment with Monitoring

```bash
# Start with production profile (includes Redis caching)
docker-compose --profile production up -d

# Start with monitoring (includes Prometheus)
docker-compose --profile monitoring up -d

# Start with both
docker-compose --profile production --profile monitoring up -d
```

### Environment Configuration

Create a `.env` file for custom configuration:

```bash
# API Configuration
S3AI_API_HOST=0.0.0.0
S3AI_API_PORT=8000
S3AI_LOG_LEVEL=INFO
S3AI_DEBUG=false

# Model Configuration
S3AI_LLM_MODEL=phi3:mini
OLLAMA_BASE_URL=http://ollama:11434
S3AI_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Performance Settings
S3AI_VECTOR_SEARCH_K=3
S3AI_CHUNK_SIZE=800
S3AI_CHUNK_OVERLAP=100
S3AI_CACHE_TTL_HOURS=24

# Security Settings
S3AI_RATE_LIMIT=30
S3AI_MAX_QUERY_LENGTH=2000
S3AI_MAX_FILE_SIZE_MB=100

# Allowed origins (comma-separated)
S3AI_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Trusted hosts (comma-separated)
S3AI_TRUSTED_HOSTS=localhost,127.0.0.1,0.0.0.0,*.local
```

## 🛠️ Manual Installation

### 1. System Setup

```bash
# Clone repository
git clone https://github.com/hndrwn-dk/s3-onprem-ai-assistant.git
cd s3-onprem-ai-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install and Configure Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &

# Pull the model
ollama pull phi3:mini
```

### 3. Prepare Documents

```bash
# Place your documents in docs/
mkdir -p docs
cp your-s3-documentation/* docs/

# Build vector embeddings
python build_embeddings_all.py
```

### 4. Start Services

```bash
# Start API server
python api.py

# In another terminal, start Streamlit UI
streamlit run streamlit_ui.py

# Or use CLI directly
python s3ai_query.py "show all buckets under dept: engineering"
```

## 🔧 Configuration Management

### Environment Variables

The application supports comprehensive configuration via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `S3AI_DOCS_PATH` | `docs` | Path to document directory |
| `S3AI_CACHE_DIR` | `cache` | Cache directory path |
| `S3AI_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `S3AI_API_HOST` | `0.0.0.0` | API host address |
| `S3AI_API_PORT` | `8000` | API port number |
| `S3AI_DEBUG` | `false` | Enable debug mode |
| `S3AI_LLM_MODEL` | `phi3:mini` | LLM model name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama service URL |
| `S3AI_RATE_LIMIT` | `30` | Rate limit per minute |
| `S3AI_CACHE_TTL_HOURS` | `24` | Cache TTL in hours |

### Configuration File

You can also use a configuration file for complex setups:

```python
# config_override.py
from config import config

# Override default settings
config.llm_temperature = 0.5
config.vector_search_k = 5
config.debug_mode = True
```

## 🔐 Security Configuration

### Production Security Checklist

- [ ] Change default API keys (if using authentication)
- [ ] Configure CORS origins for your domain
- [ ] Set up TLS/SSL certificates
- [ ] Configure firewall rules
- [ ] Set appropriate rate limits
- [ ] Review allowed file extensions
- [ ] Configure log retention policies
- [ ] Set up security monitoring

### TLS/SSL Setup

For production deployment with HTTPS:

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - s3ai-api
```

### Reverse Proxy Configuration

Example Nginx configuration:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/certs/key.pem;

    location / {
        proxy_pass http://s3ai-api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring and Observability

### Health Checks

The application provides comprehensive health checks:

```bash
# API health check
curl http://localhost:8000/health

# Get performance metrics
curl http://localhost:8000/metrics

# Check cache statistics
curl http://localhost:8000/cache/stats
```

### Log Management

Logs are written to multiple locations:

- **Console output**: Real-time logging
- **File logging**: `app.log` (configurable path)
- **Structured logs**: JSON format for parsing

### Prometheus Metrics

When using the monitoring profile:

- **Prometheus**: http://localhost:9090
- **Metrics endpoint**: http://localhost:8000/metrics

Example queries:
```promql
# Average response time
rate(s3ai_request_duration_seconds_sum[5m]) / rate(s3ai_request_duration_seconds_count[5m])

# Request rate by endpoint
rate(s3ai_requests_total[5m])

# Cache hit rate
rate(s3ai_cache_hits_total[5m]) / rate(s3ai_cache_requests_total[5m])
```

## 🔧 Troubleshooting

### Common Issues

**1. Ollama Connection Failed**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama
docker-compose restart ollama
```

**2. Model Not Found**
```bash
# Pull required model
docker-compose exec ollama ollama pull phi3:mini
```

**3. Permission Denied Errors**
```bash
# Fix file permissions
sudo chown -R $(id -u):$(id -g) docs/ cache/ s3_all_docs/
```

**4. Out of Memory**
```bash
# Reduce chunk size in configuration
export S3AI_CHUNK_SIZE=400
export S3AI_VECTOR_SEARCH_K=2
```

**5. Slow Performance**
```bash
# Clear cache
curl -X POST http://localhost:8000/cache/clear

# Rebuild embeddings
python build_embeddings_all.py
```

### Debug Mode

Enable debug logging:

```bash
export S3AI_DEBUG=true
export S3AI_LOG_LEVEL=DEBUG

# Or in Docker
docker-compose up -d -e S3AI_DEBUG=true -e S3AI_LOG_LEVEL=DEBUG
```

### Performance Tuning

**Memory Optimization:**
```bash
# Reduce memory usage
export S3AI_CHUNK_SIZE=400
export S3AI_CHUNK_OVERLAP=50
export S3AI_VECTOR_SEARCH_K=2
```

**Speed Optimization:**
```bash
# Increase cache TTL
export S3AI_CACHE_TTL_HOURS=48

# Use faster model (if available)
export S3AI_LLM_MODEL=phi3:mini-q4
```

## 📈 Scaling and High Availability

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  s3ai-api:
    deploy:
      replicas: 3
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
    depends_on:
      - s3ai-api
```

### Load Balancer Configuration

```nginx
upstream s3ai_backend {
    server s3ai-api-1:8000;
    server s3ai-api-2:8000;
    server s3ai-api-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://s3ai_backend;
    }
}
```

## 🚀 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy S3 AI Assistant

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to staging
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
          
      - name: Run health checks
        run: |
          sleep 30
          curl -f http://localhost:8000/health
          
      - name: Run tests
        run: |
          docker-compose exec -T s3ai-api pytest tests/
```

## 📚 Backup and Recovery

### Data Backup

```bash
# Backup vector store
tar -czf backup-$(date +%Y%m%d).tar.gz s3_all_docs/ cache/ docs/

# Backup using Docker volumes
docker run --rm -v s3ai_vectors:/data -v $(pwd):/backup alpine tar czf /backup/vectors-backup.tar.gz /data
```

### Recovery

```bash
# Restore from backup
tar -xzf backup-20240115.tar.gz

# Rebuild if needed
python build_embeddings_all.py
```

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] TLS/SSL certificates installed
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] Log rotation configured
- [ ] Health checks working
- [ ] Documentation deployed
- [ ] Security scan completed

---

## 📞 Support

For deployment issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review logs: `docker-compose logs -f`
3. Verify configuration: `curl http://localhost:8000/health`
4. Open an issue on GitHub with detailed logs

**Remember**: This is a production-ready deployment with comprehensive security and monitoring features!