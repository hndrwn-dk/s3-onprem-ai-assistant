# config.py (v2.2.6) - Speed Optimized

import os

# Paths
DOCS_PATH = "docs"
VECTOR_INDEX_PATH = "s3_all_docs"
CHUNKS_PATH = "s3_all_chunks.pkl"
RECENT_QUESTIONS_FILE = "recent_questions.txt"
CACHE_DIR = "cache"

# Updated to check both locations for the bucket metadata file
FLATTENED_TXT_PATH = os.path.join(DOCS_PATH, "sample_bucket_metadata_converted.txt")

# Embedding model
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Performance settings
VECTOR_SEARCH_K = 3  # Reduced from 5 for speed
CHUNK_SIZE = 800     # Reduced from 1000
CHUNK_OVERLAP = 100  # Reduced from 200
CACHE_TTL_HOURS = 24