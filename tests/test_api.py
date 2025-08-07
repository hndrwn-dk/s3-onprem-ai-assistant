# tests/test_api.py - Tests for FastAPI endpoints

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

from api import app
from validation import ValidationError

class TestAPI:
    """Test cases for FastAPI endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "cache_stats" in data
        assert "system_info" in data
        assert "uptime" in data
        assert data["version"] == "2.2.7"
    
    def test_health_check_rate_limit(self):
        """Test health check rate limiting"""
        # Make multiple requests to test rate limiting
        for i in range(12):  # Exceeds 10/minute limit
            response = self.client.get("/health")
            if i < 10:
                assert response.status_code == 200
            else:
                assert response.status_code == 429  # Rate limited
    
    @patch('api.response_cache')
    @patch('api.ModelCache')
    def test_ask_question_valid(self, mock_model_cache, mock_response_cache):
        """Test valid question submission"""
        # Mock cache miss
        mock_response_cache.get.return_value = None
        
        # Mock successful LLM response
        mock_llm = Mock()
        mock_llm.return_value = "This is a test answer"
        mock_model_cache.get_llm.return_value = mock_llm
        
        # Mock bucket search
        with patch('api.bucket_index') as mock_bucket_index:
            mock_bucket_index.quick_search.return_value = "Test bucket data"
            
            response = self.client.post(
                "/ask",
                json={"question": "show all buckets under dept: engineering"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "source" in data
            assert "response_time" in data
            assert "query_id" in data
            assert "confidence" in data
    
    def test_ask_question_empty(self):
        """Test empty question validation"""
        response = self.client.post(
            "/ask",
            json={"question": ""}
        )
        assert response.status_code == 422  # Validation error
    
    def test_ask_question_too_long(self):
        """Test query length validation"""
        long_question = "a" * 2001
        response = self.client.post(
            "/ask",
            json={"question": long_question}
        )
        assert response.status_code == 422  # Validation error
    
    def test_ask_question_suspicious(self):
        """Test suspicious content detection"""
        suspicious_question = "../../../etc/passwd"
        response = self.client.post(
            "/ask",
            json={"question": suspicious_question}
        )
        assert response.status_code == 422  # Validation error
    
    @patch('api.response_cache')
    def test_ask_question_cached(self, mock_response_cache):
        """Test cached response"""
        # Mock cache hit
        mock_response_cache.get.return_value = "Cached answer"
        
        response = self.client.post(
            "/ask",
            json={"question": "test question"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Cached answer"
        assert data["source"] == "cache"
        assert data["confidence"] == 1.0
    
    def test_ask_question_rate_limit(self):
        """Test rate limiting on ask endpoint"""
        # Mock all dependencies to avoid actual processing
        with patch('api.response_cache') as mock_cache:
            mock_cache.get.return_value = "Test answer"
            
            # Make multiple requests
            for i in range(32):  # Exceeds 30/minute limit
                response = self.client.post(
                    "/ask",
                    json={"question": f"test question {i}"}
                )
                if i < 30:
                    assert response.status_code == 200
                else:
                    assert response.status_code == 429  # Rate limited
    
    @patch('api.response_cache')
    def test_clear_cache(self, mock_response_cache):
        """Test cache clearing endpoint"""
        response = self.client.post("/cache/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "timestamp" in data
        mock_response_cache.clear_expired.assert_called_once()
    
    def test_cache_stats(self):
        """Test cache statistics endpoint"""
        response = self.client.get("/cache/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "cache_enabled" in data
        assert "timestamp" in data
    
    @patch('api.performance_monitor')
    @patch('api.ModelCache')
    def test_metrics(self, mock_model_cache, mock_performance_monitor):
        """Test metrics endpoint"""
        # Mock performance monitor
        mock_performance_monitor.get_all_stats.return_value = {
            "test_operation": {
                "count": 5,
                "average": 1.2,
                "min": 0.5,
                "max": 2.0
            }
        }
        
        # Mock model cache health
        mock_model_cache.health_check.return_value = {
            "llm": True,
            "embeddings": True,
            "vector_store": True
        }
        
        response = self.client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "performance" in data
        assert "health" in data
        assert "uptime" in data
        assert "timestamp" in data
    
    def test_nonexistent_endpoint(self):
        """Test non-existent endpoint returns 404"""
        response = self.client.get("/nonexistent")
        assert response.status_code == 404

class TestAPIValidation:
    """Test API input validation"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_request_validation_missing_question(self):
        """Test request validation with missing question field"""
        response = self.client.post("/ask", json={})
        assert response.status_code == 422
    
    def test_request_validation_wrong_type(self):
        """Test request validation with wrong data type"""
        response = self.client.post("/ask", json={"question": 123})
        assert response.status_code == 422
    
    def test_request_validation_invalid_json(self):
        """Test request validation with invalid JSON"""
        response = self.client.post(
            "/ask",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

class TestAPIErrors:
    """Test API error handling"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    @patch('api.ModelCache')
    def test_llm_error_handling(self, mock_model_cache):
        """Test LLM error handling"""
        # Mock cache miss
        with patch('api.response_cache') as mock_cache:
            mock_cache.get.return_value = None
            
            # Mock bucket search success but LLM failure
            with patch('api.bucket_index') as mock_bucket_index:
                mock_bucket_index.quick_search.return_value = "Test data"
                
                # Mock LLM to raise exception
                mock_llm = Mock()
                mock_llm.side_effect = Exception("LLM connection failed")
                mock_model_cache.get_llm.return_value = mock_llm
                
                response = self.client.post(
                    "/ask",
                    json={"question": "test question"}
                )
                
                # Should still return 200 with raw results
                assert response.status_code == 200
                data = response.json()
                assert data["source"] == "quick_search_raw"
    
    @patch('api.ModelCache')
    @patch('api.bucket_index')
    @patch('api.response_cache')
    def test_vector_search_fallback(self, mock_cache, mock_bucket_index, mock_model_cache):
        """Test vector search fallback"""
        # Mock cache miss
        mock_cache.get.return_value = None
        
        # Mock bucket search miss
        mock_bucket_index.quick_search.return_value = None
        
        # Mock vector store success
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_retriever.return_value = mock_retriever
        mock_vector_store.as_retriever.return_value = mock_retriever
        mock_model_cache.get_vector_store.return_value = mock_vector_store
        
        mock_llm = Mock()
        mock_model_cache.get_llm.return_value = mock_llm
        
        # Mock RetrievalQA
        with patch('api.RetrievalQA') as mock_qa:
            mock_chain = Mock()
            mock_chain.run.return_value = "Vector search result"
            mock_qa.from_chain_type.return_value = mock_chain
            
            response = self.client.post(
                "/ask",
                json={"question": "test question"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "vector"

class TestAPIMiddleware:
    """Test API middleware functionality"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.options("/health")
        # CORS headers should be present
        assert "access-control-allow-origin" in [
            h.lower() for h in response.headers.keys()
        ]
    
    def test_trusted_host_middleware(self):
        """Test trusted host middleware"""
        # This should work with localhost
        response = self.client.get("/health")
        assert response.status_code == 200

class TestAsyncOperations:
    """Test async endpoint operations"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            with patch('api.response_cache') as mock_cache:
                mock_cache.get.return_value = "Test answer"
                response = self.client.post(
                    "/ask",
                    json={"question": "test concurrent request"}
                )
                results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)

if __name__ == "__main__":
    pytest.main([__file__])