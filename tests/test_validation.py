# tests/test_validation.py - Tests for input validation

import pytest
import tempfile
import os
from pathlib import Path

from validation import (
    InputValidator, 
    ValidationError, 
    safe_query, 
    safe_file_path, 
    safe_filename
)

class TestInputValidator:
    """Test cases for InputValidator class"""
    
    def test_validate_query_normal(self):
        """Test normal query validation"""
        query = "show all buckets under dept: engineering"
        result = InputValidator.validate_query(query)
        assert result == query
    
    def test_validate_query_empty(self):
        """Test empty query validation"""
        with pytest.raises(ValidationError, match="Query cannot be empty"):
            InputValidator.validate_query("")
        
        with pytest.raises(ValidationError, match="Query cannot be empty"):
            InputValidator.validate_query("   ")
    
    def test_validate_query_too_long(self):
        """Test query length validation"""
        long_query = "a" * 2001
        with pytest.raises(ValidationError, match="Query too long"):
            InputValidator.validate_query(long_query)
    
    def test_validate_query_suspicious_patterns(self):
        """Test detection of suspicious patterns"""
        suspicious_queries = [
            "../../../etc/passwd",
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "eval(malicious_code)",
            "exec(dangerous_code)",
            "import os",
            "__file__",
            "file:///etc/passwd",
            "ftp://malicious.com"
        ]
        
        for query in suspicious_queries:
            with pytest.raises(ValidationError, match="potentially dangerous content"):
                InputValidator.validate_query(query)
    
    def test_validate_query_sanitization(self):
        """Test query sanitization"""
        query = "show buckets with special chars: ñ†∂∆"
        result = InputValidator.validate_query(query)
        # Should remove or replace special characters
        assert len(result) <= len(query)
    
    def test_validate_file_path_normal(self):
        """Test normal file path validation"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name
        
        try:
            result = InputValidator.validate_file_path(tmp_path)
            assert os.path.exists(result)
        finally:
            os.unlink(tmp_path)
    
    def test_validate_file_path_nonexistent(self):
        """Test validation of non-existent file"""
        with pytest.raises(ValidationError, match="File does not exist"):
            InputValidator.validate_file_path("/nonexistent/file.txt")
    
    def test_validate_file_path_with_allowed_dirs(self):
        """Test file path validation with allowed directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")
            
            # Should succeed with allowed directory
            result = InputValidator.validate_file_path(test_file, [tmpdir])
            assert os.path.exists(result)
            
            # Should fail with different allowed directory
            with pytest.raises(ValidationError, match="not in allowed directories"):
                InputValidator.validate_file_path(test_file, ["/other/dir"])
    
    def test_validate_cache_key_normal(self):
        """Test normal cache key validation"""
        key = "cache_key_123"
        result = InputValidator.validate_cache_key(key)
        assert result == key
    
    def test_validate_cache_key_invalid(self):
        """Test invalid cache key validation"""
        with pytest.raises(ValidationError, match="Cache key cannot be empty"):
            InputValidator.validate_cache_key("")
        
        with pytest.raises(ValidationError, match="Cache key too long"):
            InputValidator.validate_cache_key("a" * 501)
        
        with pytest.raises(ValidationError, match="invalid characters"):
            InputValidator.validate_cache_key("key with spaces")
    
    def test_sanitize_filename_normal(self):
        """Test normal filename sanitization"""
        filename = "document.pdf"
        result = InputValidator.sanitize_filename(filename)
        assert result == filename
    
    def test_sanitize_filename_dangerous(self):
        """Test dangerous filename sanitization"""
        test_cases = [
            ("../../../etc/passwd", "etc_passwd"),
            (".hidden_file", "file_hidden_file"),
            ("file with spaces.txt", "file_with_spaces.txt"),
            ("file@#$%^&*().txt", "file________.txt"),
            ("a" * 300 + ".txt", "a" * 251 + ".txt")  # Length truncation
        ]
        
        for dangerous, expected_safe in test_cases:
            result = InputValidator.sanitize_filename(dangerous)
            assert len(result) <= 255
            assert not result.startswith(".")
            assert "/" not in result
            assert "\\" not in result
    
    def test_validate_model_name_normal(self):
        """Test normal model name validation"""
        valid_names = ["phi3:mini", "mistral-7b", "llama2_chat", "gpt-3.5-turbo"]
        for name in valid_names:
            result = InputValidator.validate_model_name(name)
            assert result == name
    
    def test_validate_model_name_invalid(self):
        """Test invalid model name validation"""
        invalid_names = [
            "",
            "model with spaces",
            "model@invalid",
            "model" + "x" * 100  # Too long
        ]
        
        for name in invalid_names:
            with pytest.raises(ValidationError):
                InputValidator.validate_model_name(name)
    
    def test_validate_config_value_types(self):
        """Test configuration value type validation"""
        # Valid cases
        assert InputValidator.validate_config_value("test_int", 5, int) == 5
        assert InputValidator.validate_config_value("test_str", "hello", str) == "hello"
        assert InputValidator.validate_config_value("test_float", 0.5, float) == 0.5
        
        # Invalid types
        with pytest.raises(ValidationError, match="must be of type"):
            InputValidator.validate_config_value("test", "not_int", int)
    
    def test_validate_config_value_ranges(self):
        """Test configuration value range validation"""
        # Invalid negative values for int
        with pytest.raises(ValidationError, match="must be non-negative"):
            InputValidator.validate_config_value("chunk_size", -1, int)
        
        # Invalid large values for specific keys
        with pytest.raises(ValidationError, match="too large"):
            InputValidator.validate_config_value("chunk_size", 20000, int)
        
        # Invalid float range
        with pytest.raises(ValidationError, match="must be between 0.0 and 2.0"):
            InputValidator.validate_config_value("temperature", 3.0, float)

class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_safe_query(self):
        """Test safe_query convenience function"""
        query = "test query"
        result = safe_query(query)
        assert result == query
    
    def test_safe_query_invalid(self):
        """Test safe_query with invalid input"""
        with pytest.raises(ValidationError):
            safe_query("../malicious")
    
    def test_safe_filename(self):
        """Test safe_filename convenience function"""
        filename = "test.txt"
        result = safe_filename(filename)
        assert result == filename
    
    def test_safe_filename_dangerous(self):
        """Test safe_filename with dangerous input"""
        result = safe_filename("../dangerous.txt")
        assert "../" not in result

class TestSecurityPatterns:
    """Test security pattern detection"""
    
    def test_directory_traversal_patterns(self):
        """Test detection of directory traversal patterns"""
        patterns = [
            "../",
            "..\\",
            "../../etc/passwd",
            "..\\..\\windows\\system32"
        ]
        
        for pattern in patterns:
            with pytest.raises(ValidationError):
                InputValidator.validate_query(f"show files in {pattern}")
    
    def test_script_injection_patterns(self):
        """Test detection of script injection patterns"""
        patterns = [
            "<script>alert(1)</script>",
            "javascript:alert(1)",
            "<img src=x onerror=alert(1)>"
        ]
        
        for pattern in patterns:
            with pytest.raises(ValidationError):
                InputValidator.validate_query(pattern)
    
    def test_code_execution_patterns(self):
        """Test detection of code execution patterns"""
        patterns = [
            "eval(malicious_code)",
            "exec(dangerous_function())",
            "import os; os.system('rm -rf /')",
            "__import__('os').system('ls')"
        ]
        
        for pattern in patterns:
            with pytest.raises(ValidationError):
                InputValidator.validate_query(pattern)

if __name__ == "__main__":
    pytest.main([__file__])