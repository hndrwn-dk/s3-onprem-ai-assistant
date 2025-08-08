# model_cache.py - Model caching for faster responses

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from config import (
    VECTOR_INDEX_PATH,
    EMBED_MODEL,
    MODEL,
    TEMPERATURE,
    TOP_K,
    TOP_P,
    ALLOW_DANGEROUS_DESERIALIZATION,
)
import time
from utils import logger
import threading
import os


class ModelCache:
    _llm = None
    _embeddings = None
    _vector_store = None
    _load_times = {}
    _lock = threading.Lock()

    @classmethod
    def get_llm(cls):
        if cls._llm is None:
            with cls._lock:
                if cls._llm is None:
                    start_time = time.time()
                    base_url = os.getenv("OLLAMA_HOST") or os.getenv("OLLAMA_BASE_URL")
                    kwargs = dict(
                        model=MODEL,
                        temperature=TEMPERATURE,
                        top_k=TOP_K,
                        top_p=TOP_P,
                    )
                    if base_url:
                        kwargs["base_url"] = base_url
                    cls._llm = Ollama(**kwargs)
                    cls._load_times['llm'] = time.time() - start_time
                    logger.info(f"LLM loaded in {cls._load_times['llm']:.2f} seconds")
        return cls._llm

    @classmethod
    def get_embeddings(cls):
        if cls._embeddings is None:
            with cls._lock:
                if cls._embeddings is None:
                    start_time = time.time()
                    cls._embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
                    cls._load_times['embeddings'] = time.time() - start_time
                    logger.info(f"Embeddings loaded in {cls._load_times['embeddings']:.2f} seconds")
        return cls._embeddings

    @classmethod
    def get_vector_store(cls):
        if cls._vector_store is None:
            with cls._lock:
                if cls._vector_store is None:
                    start_time = time.time()
                    try:
                        embeddings = cls.get_embeddings()
                        cls._vector_store = FAISS.load_local(
                            VECTOR_INDEX_PATH,
                            embeddings,
                            allow_dangerous_deserialization=ALLOW_DANGEROUS_DESERIALIZATION,
                        )
                        cls._load_times['vector_store'] = time.time() - start_time
                        logger.info(
                            f"Vector store loaded in {cls._load_times['vector_store']:.2f} seconds"
                        )
                    except Exception as e:
                        cls._vector_store = None
                        cls._load_times['vector_store_error'] = str(e)
                        logger.warning(f"Vector store not available: {e}")
        return cls._vector_store

    @classmethod
    def get_load_times(cls):
        return cls._load_times