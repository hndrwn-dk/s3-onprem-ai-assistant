# utils.py (v2.2.7) - Security Enhanced & Improved Error Handling

import os
import json
import logging
import time
import sys
from pathlib import Path
from typing import List, Optional, Union
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from config import DOCS_PATH, FLATTENED_TXT_PATH
from validation import safe_file_path, ValidationError

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_timing(self, operation: str, duration: float):
        """Record timing for an operation"""
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(duration)
        logger.info(f"Performance: {operation} took {duration:.2f}s")
    
    def get_stats(self, operation: str) -> dict:
        """Get statistics for an operation"""
        if operation not in self.metrics:
            return {}
        
        times = self.metrics[operation]
        return {
            'count': len(times),
            'total': sum(times),
            'average': sum(times) / len(times),
            'min': min(times),
            'max': max(times)
        }
    
    def get_all_stats(self) -> dict:
        """Get all performance statistics"""
        return {op: self.get_stats(op) for op in self.metrics.keys()}

# Global performance monitor
performance_monitor = PerformanceMonitor()

def timing_decorator(func):
    """Enhanced decorator to measure function execution time with error handling"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        operation_name = f"{func.__module__}.{func.__name__}"
        
        try:
            logger.debug(f"Starting operation: {operation_name}")
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            performance_monitor.record_timing(operation_name, duration)
            logger.info(f"✅ {operation_name} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ {operation_name} failed after {duration:.2f}s: {e}", exc_info=True)
            raise
    return wrapper

class DocumentLoadError(Exception):
    """Custom exception for document loading errors"""
    pass

class SafeDocumentLoader:
    """Secure document loader with comprehensive error handling"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.json', '.md'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit
    
    def __init__(self, docs_path: str = DOCS_PATH):
        self.docs_path = docs_path
        self.allowed_dirs = [docs_path]
        
    def _validate_file(self, file_path: str) -> Path:
        """Validate file before processing"""
        try:
            # Security validation
            validated_path = safe_file_path(file_path, self.allowed_dirs)
            path_obj = Path(validated_path)
            
            # Extension validation
            if path_obj.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                raise DocumentLoadError(f"Unsupported file extension: {path_obj.suffix}")
            
            # Size validation
            if path_obj.stat().st_size > self.MAX_FILE_SIZE:
                raise DocumentLoadError(f"File too large: {path_obj.stat().st_size} bytes")
            
            return path_obj
            
        except ValidationError as e:
            raise DocumentLoadError(f"File validation failed: {e}")
        except Exception as e:
            raise DocumentLoadError(f"Unexpected error validating file: {e}")
    
    def _load_pdf_document(self, file_path: Path) -> List[Document]:
        """Safely load PDF document"""
        try:
            loader = PyPDFLoader(str(file_path))
            docs = loader.load()
            
            if not docs:
                logger.warning(f"No content extracted from PDF: {file_path}")
                return []
            
            # Validate content
            for doc in docs:
                if not doc.page_content.strip():
                    logger.warning(f"Empty page found in PDF: {file_path}")
            
            logger.info(f"✅ Loaded {len(docs)} pages from PDF: {file_path}")
            return docs
            
        except Exception as e:
            logger.error(f"Failed to load PDF {file_path}: {e}")
            raise DocumentLoadError(f"PDF loading failed: {e}")
    
    def _load_text_document(self, file_path: Path) -> List[Document]:
        """Safely load text document"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    loader = TextLoader(str(file_path), encoding=encoding)
                    docs = loader.load()
                    
                    if docs and docs[0].page_content.strip():
                        logger.info(f"✅ Loaded text document: {file_path} (encoding: {encoding})")
                        return docs
                except UnicodeDecodeError:
                    continue
            
            raise DocumentLoadError(f"Could not decode text file with any supported encoding")
            
        except DocumentLoadError:
            raise
        except Exception as e:
            logger.error(f"Failed to load text file {file_path}: {e}")
            raise DocumentLoadError(f"Text loading failed: {e}")
    
    def _load_json_document(self, file_path: Path) -> List[Document]:
        """Safely load JSON document"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Convert JSON to readable text format
            if isinstance(json_data, (dict, list)):
                content = json.dumps(json_data, indent=2, ensure_ascii=False)
            else:
                content = str(json_data)
            
            if not content.strip():
                logger.warning(f"Empty JSON content: {file_path}")
                return []
            
            doc = Document(
                page_content=content,
                metadata={
                    "source": str(file_path),
                    "type": "json",
                    "size": len(content)
                }
            )
            
            logger.info(f"✅ Loaded JSON document: {file_path}")
            return [doc]
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            raise DocumentLoadError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Failed to load JSON {file_path}: {e}")
            raise DocumentLoadError(f"JSON loading failed: {e}")

@timing_decorator
def load_documents_from_path(path: str = DOCS_PATH) -> List[Document]:
    """Enhanced document loader with comprehensive error handling"""
    docs = []
    loader = SafeDocumentLoader(path)
    
    if not os.path.exists(path):
        logger.warning(f"📁 Path does not exist: {path}")
        return docs
    
    try:
        for root, _, files in os.walk(path):
            for file in files:
                file_path = Path(root) / file
                
                try:
                    # Validate file
                    validated_path = loader._validate_file(str(file_path))
                    logger.debug(f"Processing file: {validated_path}")
                    
                    # Load based on extension
                    if validated_path.suffix.lower() == '.pdf':
                        file_docs = loader._load_pdf_document(validated_path)
                    elif validated_path.suffix.lower() in ['.txt', '.md']:
                        file_docs = loader._load_text_document(validated_path)
                    elif validated_path.suffix.lower() == '.json':
                        file_docs = loader._load_json_document(validated_path)
                    else:
                        logger.warning(f"Skipping unsupported file: {validated_path}")
                        continue
                    
                    docs.extend(file_docs)
                    
                except DocumentLoadError as e:
                    logger.error(f"❌ Document loading error for {file_path}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"❌ Unexpected error processing {file_path}: {e}", exc_info=True)
                    continue
    
    except Exception as e:
        logger.error(f"❌ Error scanning directory {path}: {e}", exc_info=True)
        raise DocumentLoadError(f"Directory scanning failed: {e}")
    
    logger.info(f"📚 Total documents loaded: {len(docs)} from {path}")
    return docs

def load_txt_documents(file_path: str = FLATTENED_TXT_PATH) -> str:
    """Enhanced TXT file loader with better error handling"""
    search_paths = [
        file_path,
        os.path.join(DOCS_PATH, "sample_bucket_metadata_converted.txt"),
        os.path.join(DOCS_PATH, "bucket_metadata.txt"),
        os.path.join(DOCS_PATH, "metadata.txt")
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            try:
                # Validate path security
                validated_path = safe_file_path(path, [DOCS_PATH])
                
                # Try different encodings
                encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
                
                for encoding in encodings:
                    try:
                        with open(validated_path, "r", encoding=encoding) as f:
                            content = f.read()
                        
                        if content.strip():
                            logger.info(f"✅ Loaded {len(content)} characters from {path} (encoding: {encoding})")
                            return content
                    except UnicodeDecodeError:
                        continue
                
                logger.warning(f"Could not decode file with any supported encoding: {path}")
                
            except ValidationError as e:
                logger.error(f"Security validation failed for {path}: {e}")
                continue
            except Exception as e:
                logger.error(f"Failed to load TXT file {path}: {e}")
                continue
    
    logger.warning(f"❌ No readable TXT file found in any of: {search_paths}")
    return ""

def quick_relevance_check(query: str, text: str, threshold: int = 1) -> bool:
    """Enhanced relevance check with better text processing"""
    if not query or not text:
        return False
    
    try:
        query_words = [word.lower() for word in query.split() if len(word) > 2]
        text_lower = text.lower()
        
        matches = sum(1 for word in query_words if word in text_lower)
        relevance_score = matches / len(query_words) if query_words else 0
        
        logger.debug(f"Relevance check: {matches}/{len(query_words)} words matched (score: {relevance_score:.2f})")
        return matches >= threshold
        
    except Exception as e:
        logger.error(f"Error in relevance check: {e}")
        return False

def search_in_fallback_text(query: str, text: str, max_results: int = 10) -> str:
    """Enhanced fallback text search with better matching"""
    if not text or not query:
        return ""
    
    try:
        query_lower = query.lower()
        lines = text.split('\n')
        matching_lines = []
        
        # Multi-pass search for better results
        search_terms = query_lower.split()
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Exact phrase match (highest priority)
            if query_lower in line_lower:
                matching_lines.append((f"Line {i+1}", line.strip(), 3))
            # Multiple term match (medium priority)
            elif len(search_terms) > 1 and sum(1 for term in search_terms if term in line_lower) >= 2:
                matching_lines.append((f"Line {i+1}", line.strip(), 2))
            # Single term match (lowest priority)
            elif any(term in line_lower for term in search_terms if len(term) > 2):
                matching_lines.append((f"Line {i+1}", line.strip(), 1))
        
        # Sort by relevance and limit results
        matching_lines.sort(key=lambda x: x[2], reverse=True)
        matching_lines = matching_lines[:max_results]
        
        result = '\n'.join([f"{line_ref}: {line_content}" for line_ref, line_content, _ in matching_lines])
        
        if result:
            logger.info(f"✅ Fallback search found {len(matching_lines)} matches for query: {query[:50]}...")
        else:
            logger.warning(f"❌ No fallback matches found for query: {query[:50]}...")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in fallback text search: {e}")
        return ""

def get_system_info() -> dict:
    """Get system information for monitoring"""
    try:
        import psutil
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'python_version': sys.version,
            'platform': sys.platform
        }
    except ImportError:
        logger.warning("psutil not available, returning basic system info")
        return {
            'python_version': sys.version,
            'platform': sys.platform
        }