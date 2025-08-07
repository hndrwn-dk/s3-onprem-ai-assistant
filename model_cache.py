# model_cache.py - Secure Model caching for faster responses

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from config import VECTOR_INDEX_PATH, EMBED_MODEL
import time
import os
from utils import logger
from typing import Optional

class ModelCache:
    _llm = None
    _embeddings = None
    _vector_store = None
    _load_times = {}
    
    @classmethod
    def get_llm(cls) -> Ollama:
        """Get or create LLM instance with proper error handling"""
        if cls._llm is None:
            start_time = time.time()
            try:
                cls._llm = Ollama(
                    model="phi3:mini",  # Much faster than mistral
                    temperature=0.3,
                    num_predict=512,    # Limit response length for speed
                    top_k=10,          # Reduce sampling complexity
                    top_p=0.9,
                    timeout=30,        # Add timeout for safety
                    base_url="http://localhost:11434"  # Explicit base URL
                )
                cls._load_times['llm'] = time.time() - start_time
                logger.info(f"LLM loaded in {cls._load_times['llm']:.2f} seconds")
            except Exception as e:
                logger.error(f"Failed to load LLM: {e}")
                raise RuntimeError(f"LLM initialization failed: {e}")
        return cls._llm
    
    @classmethod
    def get_embeddings(cls) -> HuggingFaceEmbeddings:
        """Get or create embeddings instance with proper error handling"""
        if cls._embeddings is None:
            start_time = time.time()
            try:
                cls._embeddings = HuggingFaceEmbeddings(
                    model_name=EMBED_MODEL,
                    model_kwargs={'device': 'cpu'},  # Explicit device setting
                    encode_kwargs={'normalize_embeddings': True}  # Better embeddings
                )
                cls._load_times['embeddings'] = time.time() - start_time
                logger.info(f"Embeddings loaded in {cls._load_times['embeddings']:.2f} seconds")
            except Exception as e:
                logger.error(f"Failed to load embeddings: {e}")
                raise RuntimeError(f"Embeddings initialization failed: {e}")
        return cls._embeddings
    
    @classmethod
    def get_vector_store(cls) -> FAISS:
        """Get or create vector store with secure deserialization"""
        if cls._vector_store is None:
            start_time = time.time()
            try:
                if not os.path.exists(VECTOR_INDEX_PATH):
                    raise FileNotFoundError(f"Vector index not found at {VECTOR_INDEX_PATH}")
                
                embeddings = cls.get_embeddings()
                # SECURITY FIX: Remove dangerous deserialization
                cls._vector_store = FAISS.load_local(
                    VECTOR_INDEX_PATH, 
                    embeddings,
                    allow_dangerous_deserialization=False  # FIXED: Security vulnerability
                )
                cls._load_times['vector_store'] = time.time() - start_time
                logger.info(f"Vector store loaded in {cls._load_times['vector_store']:.2f} seconds")
            except Exception as e:
                logger.error(f"Failed to load vector store: {e}")
                raise RuntimeError(f"Vector store initialization failed: {e}")
        return cls._vector_store
    
    @classmethod
    def get_load_times(cls) -> dict:
        """Get model loading times for monitoring"""
        return cls._load_times.copy()  # Return copy to prevent modification
    
    @classmethod
    def health_check(cls) -> dict:
        """Health check for all cached models"""
        health = {
            'llm': cls._llm is not None,
            'embeddings': cls._embeddings is not None,
            'vector_store': cls._vector_store is not None,
            'load_times': cls.get_load_times()
        }
        return health
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached models (useful for testing)"""
        cls._llm = None
        cls._embeddings = None
        cls._vector_store = None
        cls._load_times = {}
        logger.info("Model cache cleared")