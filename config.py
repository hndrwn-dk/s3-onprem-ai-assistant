# config.py (v2.2.7) - Enhanced Configuration Management

import os
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, field
from validation import InputValidator

@dataclass
class AppConfig:
    """Application configuration with validation and environment variable support"""
    
    # Core paths
    docs_path: str = "docs"
    vector_index_path: str = "s3_all_docs"
    chunks_path: str = "s3_all_chunks.pkl"
    recent_questions_file: str = "recent_questions.txt"
    cache_dir: str = "cache"
    log_file: str = "app.log"
    
    # Model settings
    embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model: str = "phi3:mini"
    ollama_base_url: str = "http://localhost:11434"
    
    # Performance settings
    vector_search_k: int = 3
    chunk_size: int = 800
    chunk_overlap: int = 100
    cache_ttl_hours: int = 24
    
    # LLM settings
    llm_temperature: float = 0.3
    llm_num_predict: int = 512
    llm_top_k: int = 10
    llm_top_p: float = 0.9
    llm_timeout: int = 30
    
    # Security settings
    max_query_length: int = 2000
    max_file_size_mb: int = 100
    allowed_origins: List[str] = field(default_factory=lambda: [
        "http://localhost:3000", 
        "http://127.0.0.1:3000"
    ])
    trusted_hosts: List[str] = field(default_factory=lambda: [
        "localhost", 
        "127.0.0.1", 
        "0.0.0.0", 
        "*.local"
    ])
    
    # Rate limiting
    rate_limit_per_minute: int = 30
    health_check_rate_limit: int = 10
    cache_ops_rate_limit: int = 5
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    enable_docs: bool = True
    
    # Development settings
    debug_mode: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._load_from_env()
        self._validate_config()
        self._ensure_directories()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Core paths
        self.docs_path = os.getenv("S3AI_DOCS_PATH", self.docs_path)
        self.vector_index_path = os.getenv("S3AI_VECTOR_INDEX_PATH", self.vector_index_path)
        self.cache_dir = os.getenv("S3AI_CACHE_DIR", self.cache_dir)
        
        # Model settings
        self.embed_model = os.getenv("S3AI_EMBED_MODEL", self.embed_model)
        self.llm_model = os.getenv("S3AI_LLM_MODEL", self.llm_model)
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", self.ollama_base_url)
        
        # Performance settings
        self.vector_search_k = int(os.getenv("S3AI_VECTOR_SEARCH_K", self.vector_search_k))
        self.chunk_size = int(os.getenv("S3AI_CHUNK_SIZE", self.chunk_size))
        self.chunk_overlap = int(os.getenv("S3AI_CHUNK_OVERLAP", self.chunk_overlap))
        self.cache_ttl_hours = int(os.getenv("S3AI_CACHE_TTL_HOURS", self.cache_ttl_hours))
        
        # LLM settings
        self.llm_temperature = float(os.getenv("S3AI_LLM_TEMPERATURE", self.llm_temperature))
        self.llm_num_predict = int(os.getenv("S3AI_LLM_NUM_PREDICT", self.llm_num_predict))
        self.llm_timeout = int(os.getenv("S3AI_LLM_TIMEOUT", self.llm_timeout))
        
        # Security settings
        self.max_query_length = int(os.getenv("S3AI_MAX_QUERY_LENGTH", self.max_query_length))
        self.max_file_size_mb = int(os.getenv("S3AI_MAX_FILE_SIZE_MB", self.max_file_size_mb))
        
        # API settings
        self.api_host = os.getenv("S3AI_API_HOST", self.api_host)
        self.api_port = int(os.getenv("S3AI_API_PORT", self.api_port))
        self.api_workers = int(os.getenv("S3AI_API_WORKERS", self.api_workers))
        
        # Development settings
        self.debug_mode = os.getenv("S3AI_DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("S3AI_LOG_LEVEL", self.log_level).upper()
        self.enable_docs = os.getenv("S3AI_ENABLE_DOCS", "true").lower() == "true"
        
        # Rate limiting
        self.rate_limit_per_minute = int(os.getenv("S3AI_RATE_LIMIT", self.rate_limit_per_minute))
        
        # Parse list environment variables
        if origins := os.getenv("S3AI_ALLOWED_ORIGINS"):
            self.allowed_origins = [origin.strip() for origin in origins.split(",")]
        
        if hosts := os.getenv("S3AI_TRUSTED_HOSTS"):
            self.trusted_hosts = [host.strip() for host in hosts.split(",")]
    
    def _validate_config(self):
        """Validate all configuration values"""
        # Validate paths
        InputValidator.validate_config_value("vector_search_k", self.vector_search_k, int)
        InputValidator.validate_config_value("chunk_size", self.chunk_size, int)
        InputValidator.validate_config_value("chunk_overlap", self.chunk_overlap, int)
        InputValidator.validate_config_value("cache_ttl_hours", self.cache_ttl_hours, int)
        
        # Validate LLM settings
        InputValidator.validate_config_value("llm_temperature", self.llm_temperature, float)
        InputValidator.validate_config_value("llm_num_predict", self.llm_num_predict, int)
        InputValidator.validate_config_value("llm_timeout", self.llm_timeout, int)
        
        # Validate model names
        InputValidator.validate_model_name(self.llm_model)
        
        # Validate security settings
        if self.max_query_length <= 0 or self.max_query_length > 10000:
            raise ValueError("max_query_length must be between 1 and 10000")
        
        if self.max_file_size_mb <= 0 or self.max_file_size_mb > 1000:
            raise ValueError("max_file_size_mb must be between 1 and 1000")
        
        # Validate API settings
        if not 1000 <= self.api_port <= 65535:
            raise ValueError("api_port must be between 1000 and 65535")
        
        if self.api_workers <= 0:
            raise ValueError("api_workers must be positive")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(f"log_level must be one of: {valid_log_levels}")
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            self.docs_path,
            self.cache_dir,
            os.path.dirname(self.vector_index_path) if "/" in self.vector_index_path else ".",
            os.path.dirname(self.log_file) if "/" in self.log_file else "."
        ]
        
        for directory in directories:
            if directory and directory != ".":
                Path(directory).mkdir(parents=True, exist_ok=True)
    
    @property
    def flattened_txt_path(self) -> str:
        """Get path to flattened TXT file"""
        return os.path.join(self.docs_path, "sample_bucket_metadata_converted.txt")
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024
    
    def get_ollama_config(self) -> dict:
        """Get Ollama configuration dictionary"""
        return {
            "model": self.llm_model,
            "temperature": self.llm_temperature,
            "num_predict": self.llm_num_predict,
            "top_k": self.llm_top_k,
            "top_p": self.llm_top_p,
            "timeout": self.llm_timeout,
            "base_url": self.ollama_base_url
        }
    
    def get_embedding_config(self) -> dict:
        """Get embedding configuration dictionary"""
        return {
            "model_name": self.embed_model,
            "model_kwargs": {"device": "cpu"},
            "encode_kwargs": {"normalize_embeddings": True}
        }
    
    def get_chunking_config(self) -> dict:
        """Get text chunking configuration"""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "length_function": len,
            "separators": ["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        }
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            "docs_path": self.docs_path,
            "vector_index_path": self.vector_index_path,
            "cache_dir": self.cache_dir,
            "embed_model": self.embed_model,
            "llm_model": self.llm_model,
            "vector_search_k": self.vector_search_k,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "cache_ttl_hours": self.cache_ttl_hours,
            "llm_temperature": self.llm_temperature,
            "max_query_length": self.max_query_length,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "debug_mode": self.debug_mode,
            "log_level": self.log_level
        }

# Global configuration instance
config = AppConfig()

# Backward compatibility exports
DOCS_PATH = config.docs_path
VECTOR_INDEX_PATH = config.vector_index_path
CHUNKS_PATH = config.chunks_path
RECENT_QUESTIONS_FILE = config.recent_questions_file
CACHE_DIR = config.cache_dir
FLATTENED_TXT_PATH = config.flattened_txt_path
EMBED_MODEL = config.embed_model
VECTOR_SEARCH_K = config.vector_search_k
CHUNK_SIZE = config.chunk_size
CHUNK_OVERLAP = config.chunk_overlap
CACHE_TTL_HOURS = config.cache_ttl_hours