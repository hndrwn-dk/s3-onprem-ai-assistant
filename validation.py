# validation.py - Input validation and security checks

import re
import os
from pathlib import Path
from typing import Optional, List
from utils import logger


class ValidationError(Exception):
    """Custom exception for validation errors"""

    pass


class InputValidator:
    """Secure input validation for all user inputs"""

    # Security patterns
    SUSPICIOUS_PATTERNS = [
        r"\.\./",  # Directory traversal
        r"\.\.\\",  # Windows directory traversal
        r"<script",  # XSS attempts
        r"javascript:",  # JavaScript injection
        r"eval\(",  # Code evaluation
        r"exec\(",  # Code execution
        r"import\s+",  # Python imports
        r"__.*__",  # Python magic methods
        r"file://",  # File protocol
        r"ftp://",  # FTP protocol
    ]

    @staticmethod
    def validate_query(query: str) -> str:
        """Validate and sanitize user query"""
        if not query:
            raise ValidationError("Query cannot be empty")

        query = query.strip()

        # Length validation
        if len(query) == 0:
            raise ValidationError("Query cannot be empty after trimming")
        if len(query) > 2000:  # Reasonable limit
            raise ValidationError("Query too long (max 2000 characters)")

        # Security validation
        for pattern in InputValidator.SUSPICIOUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"Suspicious pattern detected in query: {pattern}")
                raise ValidationError("Query contains potentially dangerous content")

        # Basic sanitization
        query = re.sub(r"[^\w\s\-:.,?!@#$%^&*()+=\[\]{}|;\'\"/<>]", "", query)

        return query

    @staticmethod
    def validate_file_path(file_path: str, allowed_dirs: List[str] = None) -> str:
        """Validate file path to prevent directory traversal"""
        if not file_path:
            raise ValidationError("File path cannot be empty")

        # Resolve path to prevent traversal
        try:
            resolved_path = Path(file_path).resolve()
        except Exception as e:
            raise ValidationError(f"Invalid file path: {e}")

        # Check if file exists
        if not resolved_path.exists():
            raise ValidationError(f"File does not exist: {file_path}")

        # Validate against allowed directories
        if allowed_dirs:
            allowed = False
            for allowed_dir in allowed_dirs:
                try:
                    allowed_resolved = Path(allowed_dir).resolve()
                    if resolved_path.is_relative_to(allowed_resolved):
                        allowed = True
                        break
                except Exception:
                    continue

            if not allowed:
                raise ValidationError(
                    f"File path not in allowed directories: {file_path}"
                )

        return str(resolved_path)

    @staticmethod
    def validate_cache_key(key: str) -> str:
        """Validate cache key for safety"""
        if not key:
            raise ValidationError("Cache key cannot be empty")

        # Length validation
        if len(key) > 500:
            raise ValidationError("Cache key too long")

        # Character validation
        if not re.match(r"^[a-zA-Z0-9\-_]+$", key):
            raise ValidationError("Cache key contains invalid characters")

        return key

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        if not filename:
            raise ValidationError("Filename cannot be empty")

        # Remove path components
        filename = os.path.basename(filename)

        # Replace dangerous characters
        filename = re.sub(r"[^\w\-_.]", "_", filename)

        # Prevent hidden files
        if filename.startswith("."):
            filename = "file_" + filename[1:]

        # Length limit
        if len(filename) > 255:
            filename = filename[:255]

        return filename

    @staticmethod
    def validate_model_name(model_name: str) -> str:
        """Validate LLM model name"""
        if not model_name:
            raise ValidationError("Model name cannot be empty")

        # Allow only alphanumeric, dash, underscore, and colon
        if not re.match(r"^[a-zA-Z0-9\-_:]+$", model_name):
            raise ValidationError("Invalid model name format")

        # Length validation
        if len(model_name) > 100:
            raise ValidationError("Model name too long")

        return model_name

    @staticmethod
    def validate_config_value(key: str, value: any, expected_type: type) -> any:
        """Validate configuration values"""
        if not isinstance(value, expected_type):
            raise ValidationError(
                f"Configuration {key} must be of type {expected_type.__name__}"
            )

        # Type-specific validations
        if expected_type == int:
            if value < 0:
                raise ValidationError(f"Configuration {key} must be non-negative")
            if key in ["chunk_size", "chunk_overlap"] and value > 10000:
                raise ValidationError(f"Configuration {key} too large (max 10000)")

        elif expected_type == str:
            if len(value) > 1000:
                raise ValidationError(f"Configuration {key} too long")

        elif expected_type == float:
            if not 0.0 <= value <= 2.0:
                raise ValidationError(
                    f"Configuration {key} must be between 0.0 and 2.0"
                )

        return value


# Convenience functions
def safe_query(query: str) -> str:
    """Safely validate and return query"""
    return InputValidator.validate_query(query)


def safe_file_path(path: str, allowed_dirs: List[str] = None) -> str:
    """Safely validate and return file path"""
    return InputValidator.validate_file_path(path, allowed_dirs)


def safe_filename(filename: str) -> str:
    """Safely validate and return filename"""
    return InputValidator.sanitize_filename(filename)
