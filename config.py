# config.py (v2.3.0) - Speed Optimized and Secure

import os

# Paths
DOCS_PATH = "docs"  # This is where users upload their proprietary S3 vendor PDFs
VECTOR_INDEX_PATH = "s3_all_docs"
CHUNKS_PATH = "s3_all_chunks.pkl"
RECENT_QUESTIONS_FILE = "recent_questions.txt"
CACHE_DIR = "cache"

# Optional flattened bucket metadata file path (set via env to enable)
FLATTENED_TXT_PATH = os.getenv("FLATTENED_TXT_PATH", "")

# Embedding model
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBED_DEVICE = os.getenv("EMBED_DEVICE", "cpu")
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "64"))

# Performance settings
VECTOR_SEARCH_K = int(os.getenv("VECTOR_SEARCH_K", "3"))  # Reduced from 5 for speed
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))     # Reduced from 1000
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))  # Reduced from 200
CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "20"))

# Quick search settings
QUICK_SEARCH_MAX_RESULTS = int(os.getenv("QUICK_SEARCH_MAX_RESULTS", "10"))
QUICK_SEARCH_ENABLE_KEYWORD_FALLBACK = os.getenv("QUICK_SEARCH_ENABLE_KEYWORD_FALLBACK", "false").lower() in ("1", "true", "yes")

# LLM model configuration
MODEL = os.getenv("MODEL", "phi3:mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
NUM_PREDICT = int(os.getenv("NUM_PREDICT", "512"))
TOP_K = int(os.getenv("TOP_K", "10"))
TOP_P = float(os.getenv("TOP_P", "0.9"))

# Security
API_KEY = os.getenv("API_KEY", "")  # If set, required for protected endpoints
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

# FAISS loading safety
ALLOW_DANGEROUS_DESERIALIZATION = os.getenv("ALLOW_DANGEROUS_DESERIALIZATION", "true").lower() == "true"