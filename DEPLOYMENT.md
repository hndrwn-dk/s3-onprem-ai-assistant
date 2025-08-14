# S3 On-Premises AI Assistant - Deployment Guide v2.2.7

Complete deployment guide for the secure, production-ready S3 AI Assistant.

## Prerequisites

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

## Docker Deployment (Recommended)

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

# Start with both production and monitoring
docker-compose --profile production --profile monitoring up -d
```

## Manual Installation

### 1. Environment Setup

```bash
# Clone and setup
git clone https://github.com/hndrwn-dk/s3-onprem-ai-assistant.git
cd s3-onprem-ai-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Ollama

**Linux/macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
- Download from https://ollama.com/download
- Run the installer

### 3. Download Models

```bash
# Pull the PHI3 mini model
ollama pull phi3:mini

# Verify model installation
ollama list
```

### 4. Prepare Documents

```bash
# Create docs directory
mkdir -p docs

# Copy your documents
cp /path/to/your/documents/* docs/

# Build embeddings
python build_embeddings_all.py
```

### 5. Configuration

Create a `.env` file:

```env
# S3 AI Assistant Configuration
S3AI_LOG_LEVEL=INFO
S3AI_LLM_MODEL=phi3:mini
S3AI_OLLAMA_BASE_URL=http://localhost:11434
S3AI_MAX_QUERY_LENGTH=2000
S3AI_RATE_LIMIT_PER_MINUTE=30
S3AI_API_HOST=0.0.0.0
S3AI_API_PORT=8000
S3AI_DEBUG_MODE=false
```

### 6. Start Services

```bash
# Start API server
python api.py

# In another terminal, start Streamlit UI
streamlit run streamlit_ui.py --server.port 8501

# Or use the CLI
python s3ai_query.py "show all buckets under dept: engineering"
```

## Configuration Management

### Environment Variables

All configuration can be set via environment variables prefixed with `S3AI_`:

```bash
export S3AI_LOG_LEVEL=DEBUG
export S3AI_LLM_MODEL=phi3:mini
export S3AI_OLLAMA_BASE_URL=http://localhost:11434
export S3AI_MAX_QUERY_LENGTH=2000
export S3AI_MAX_FILE_SIZE_MB=100
export S3AI_ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
export S3AI_TRUSTED_HOSTS="localhost,127.0.0.1,*.local"
export S3AI_RATE_LIMIT_PER_MINUTE=30
export S3AI_API_HOST=0.0.0.0
export S3AI_API_PORT=8000
export S3AI_DEBUG_MODE=false
```

### Configuration File

Alternatively, modify `config.py` directly:

```python
from dataclasses import dataclass
from config import AppConfig

# Override default settings
config = AppConfig()
config.llm_model = "llama2:7b"  # Use different model
config.max_query_length = 5000  # Longer queries
config.rate_limit_per_minute = 60  # Higher rate limit
```

## Security Configuration

### 1. TLS/SSL Setup

```bash
# Generate self-signed certificates (development only)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Update docker-compose.yml to use HTTPS
# Add volume mounts for certificates
volumes:
  - ./cert.pem:/app/cert.pem:ro
  - ./key.pem:/app/key.pem:ro
```

### 2. Reverse Proxy (Nginx)

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ui {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. Security Checklist

- [ ] Change default ports
- [ ] Set up TLS/SSL certificates
- [ ] Configure firewall rules
- [ ] Set strong rate limits
- [ ] Validate input file types
- [ ] Enable access logging
- [ ] Set up monitoring alerts
- [ ] Regular security updates

## Monitoring and Logging

### Built-in Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Performance metrics
curl http://localhost:8000/metrics

# Cache statistics
curl http://localhost:8000/cache/stats
```

### Prometheus Integration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 's3ai-assistant'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Log Management

```bash
# View application logs
tail -f app.log

# Docker logs
docker-compose logs -f s3ai-api

# Structured logging format
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Query processed",
  "query_id": "query_1705314600123",
  "response_time": 0.45,
  "source": "vector_search"
}
```

## Troubleshooting

### Common Issues

**1. Ollama Connection Failed**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve

# Check firewall
sudo ufw allow 11434
```

**2. Model Loading Errors**
```bash
# Check available models
ollama list

# Re-download model
ollama pull phi3:mini

# Check disk space
df -h
```

**3. Vector Store Issues**
```bash
# Rebuild embeddings
python build_embeddings_all.py

# Check embeddings directory
ls -la s3_all_docs/

# Clear and rebuild
rm -rf s3_all_docs/
python build_embeddings_all.py
```

**4. Permission Errors**
```bash
# Fix file permissions
sudo chown -R $USER:$USER docs/
chmod -R 755 docs/

# Docker permission issues
sudo usermod -aG docker $USER
newgrp docker
```

### Performance Tuning

**1. Memory Optimization**
```python
# Reduce vector search results
VECTOR_SEARCH_K = 3  # Default: 5

# Limit chunk size
CHUNK_SIZE = 500  # Default: 1000
CHUNK_OVERLAP = 50  # Default: 100
```

**2. Model Optimization**
```bash
# Use smaller model for faster responses
ollama pull phi3:mini  # 2.3GB
# ollama pull llama2:7b  # 3.8GB (more accurate)
```

**3. Caching Configuration**
```python
# Increase cache size
CACHE_MAX_SIZE = 1000  # Default: 500

# Extend cache TTL
CACHE_TTL = 3600  # 1 hour (default: 1800)
```

## Scaling and High Availability

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  s3ai-api:
    deploy:
      replicas: 3
    depends_on:
      - redis
      - ollama
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - s3ai-api
```

### Load Balancer Configuration

```nginx
upstream s3ai_backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://s3ai_backend;
    }
}
```

## CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy S3 AI Assistant

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Run Tests
        run: |
          pip install -r requirements.txt
          python run_tests.py
      
      - name: Build Docker Image
        run: |
          docker build -t s3ai:${{ github.sha }} .
          docker tag s3ai:${{ github.sha }} s3ai:latest
      
      - name: Deploy to Production
        run: |
          docker-compose down
          docker-compose up -d
```

## Backup and Recovery

### Data Backup

```bash
# Backup documents
tar -czf docs-backup-$(date +%Y%m%d).tar.gz docs/

# Backup vector store
tar -czf vectors-backup-$(date +%Y%m%d).tar.gz s3_all_docs/

# Backup cache
docker exec redis redis-cli BGSAVE
cp /var/lib/redis/dump.rdb redis-backup-$(date +%Y%m%d).rdb
```

### Recovery Procedures

```bash
# Restore documents
tar -xzf docs-backup-20240115.tar.gz

# Rebuild embeddings
python build_embeddings_all.py

# Restart services
docker-compose restart
```

## Production Checklist

### Before Deployment

- [ ] Security configuration completed
- [ ] TLS/SSL certificates installed
- [ ] Firewall rules configured
- [ ] Monitoring setup verified
- [ ] Backup procedures tested
- [ ] Performance tuning applied
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Team training completed

### Post-Deployment

- [ ] Health checks passing
- [ ] Monitoring alerts configured
- [ ] Log aggregation working
- [ ] Backup automation verified
- [ ] Performance baselines established
- [ ] User access confirmed
- [ ] Documentation distributed
- [ ] Support procedures activated

## Support and Maintenance

### Regular Maintenance Tasks

```bash
# Weekly tasks
docker system prune -f
python run_tests.py
curl http://localhost:8000/health

# Monthly tasks
ollama pull phi3:mini  # Update model
pip install -r requirements.txt --upgrade
docker-compose pull
```

### Monitoring Checklist

- [ ] Response times < 3s for 95% of queries
- [ ] Cache hit rate > 60%
- [ ] System memory usage < 80%
- [ ] Disk space usage < 80%
- [ ] Error rate < 1%
- [ ] API availability > 99.5%

For additional support, check the [GitHub repository](https://github.com/hndrwn-dk/s3-onprem-ai-assistant) or create an issue.