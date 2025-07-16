# config.py - v2.2
import os

DOCS_DIR = "docs"
INDEX_FILE = "s3_all_docs"
CHUNKS_FILE = "s3_all_chunks.pkl"
RECENT_QUESTIONS_FILE = "recent_questions.txt"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CONFIDENCE_THRESHOLD = 0.4

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
