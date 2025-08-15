# utils.py (v2.3.0) - Speed Optimized

import os
import json
import logging
import time
import functools
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from config import DOCS_PATH, FLATTENED_TXT_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

@timing_decorator
def load_documents_from_path(path: str = DOCS_PATH) -> list[Document]:
    """Load documents from various file types in the specified path"""
    docs = []
    
    if not os.path.exists(path):
        logger.warning(f"Path {path} does not exist")
        return docs
    
    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            logger.info(f"Processing file: {file_path}")
            
            if file.endswith(".pdf"):
                try:
                    loader = PyPDFLoader(file_path)
                    pdf_docs = loader.load()
                    docs.extend(pdf_docs)
                    logger.info(f"Loaded {len(pdf_docs)} pages from {file_path}")
                except Exception as e:
                    logger.error(f"Failed to load PDF: {file_path} ({e})")
                    
            elif file.endswith(".txt"):
                try:
                    loader = TextLoader(file_path, encoding='utf-8')
                    txt_docs = loader.load()
                    docs.extend(txt_docs)
                    logger.info(f"Loaded {len(txt_docs)} documents from {file_path}")
                except Exception as e:
                    logger.error(f"Failed to load TXT: {file_path} ({e})")
                    
            elif file.endswith(".json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    # Convert JSON to text format for better embedding
                    if isinstance(json_data, dict):
                        content = json.dumps(json_data, indent=2)
                    elif isinstance(json_data, list):
                        content = json.dumps(json_data, indent=2)
                    else:
                        content = str(json_data)
                    
                    doc = Document(
                        page_content=content,
                        metadata={"source": file_path, "type": "json"}
                    )
                    docs.append(doc)
                    logger.info(f"Loaded JSON document from {file_path}")
                except Exception as e:
                    logger.error(f"Failed to load JSON: {file_path} ({e})")
                    
            elif file.endswith(".md"):
                try:
                    loader = TextLoader(file_path, encoding='utf-8')
                    md_docs = loader.load()
                    docs.extend(md_docs)
                    logger.info(f"Loaded {len(md_docs)} documents from {file_path}")
                except Exception as e:
                    logger.error(f"Failed to load MD: {file_path} ({e})")
    
    logger.info(f"Total documents loaded: {len(docs)}")
    return docs

def load_txt_documents(file_path: str = FLATTENED_TXT_PATH) -> str:
    """Load content from the flattened TXT file"""
    # First try the configured path
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                logger.info(f"Loaded {len(content)} characters from {file_path}")
                return content
        except Exception as e:
            logger.error(f"Failed to load TXT file {file_path}: {e}")
    
    # If not found, try looking in docs/ folder
    docs_txt_path = os.path.join(DOCS_PATH, "sample_bucket_metadata_converted.txt")
    if os.path.exists(docs_txt_path):
        try:
            with open(docs_txt_path, "r", encoding="utf-8") as f:
                content = f.read()
                logger.info(f"Loaded {len(content)} characters from {docs_txt_path}")
                return content
        except Exception as e:
            logger.error(f"Failed to load TXT file {docs_txt_path}: {e}")
    
    logger.warning(f"Flattened TXT file not found in either {file_path} or {docs_txt_path}")
    return ""

def check_vector_index_exists() -> bool:
    """Check if vector index exists and is valid"""
    from config import VECTOR_INDEX_PATH
    index_file = os.path.join(VECTOR_INDEX_PATH, "index.faiss")
    pkl_file = os.path.join(VECTOR_INDEX_PATH, "index.pkl")
    return os.path.exists(index_file) and os.path.exists(pkl_file)

def ensure_documents_for_embedding() -> bool:
    """Ensure there are documents available for embedding beyond just the sample file"""
    docs = load_documents_from_path()
    
    # Filter out the sample file to see if we have real documents
    real_docs = [doc for doc in docs if not doc.metadata.get("source", "").endswith("sample_bucket_metadata_converted.txt")]
    
    if len(real_docs) == 0:
        logger.warning("No real documents found for embedding - only sample file exists")
        return False
    
    logger.info(f"Found {len(real_docs)} real documents for embedding")
    return True

def quick_relevance_check(query: str, text: str, threshold: int = 1) -> bool:
    """Quick check if text is relevant before expensive processing"""
    query_words = query.lower().split()
    text_lower = text.lower()
    matches = sum(1 for word in query_words if word in text_lower and len(word) > 2)
    return matches >= threshold

def search_in_fallback_text(query: str, text: str, max_results: int = 10) -> str:
    """Search for query in fallback text and return relevant context"""
    if not text:
        return ""
    
    query_lower = query.lower()
    lines = text.split('\n')
    matching_lines = []
    
    for i, line in enumerate(lines):
        if query_lower in line.lower():
            matching_lines.append(f"Line {i+1}: {line.strip()}")
            if len(matching_lines) >= max_results:
                break
    
    return '\n'.join(matching_lines) if matching_lines else ""