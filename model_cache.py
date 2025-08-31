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
                    cls._load_times["llm"] = time.time() - start_time
                    logger.info(f"LLM loaded in {cls._load_times['llm']:.2f} seconds")
        return cls._llm

    @classmethod
    def get_embeddings(cls):
        if cls._embeddings is None:
            with cls._lock:
                if cls._embeddings is None:
                    start_time = time.time()
                    # Prefer same device settings used during build for consistency
                    from config import EMBED_DEVICE, EMBED_BATCH_SIZE

                    cls._embeddings = HuggingFaceEmbeddings(
                        model_name=EMBED_MODEL,
                        model_kwargs={"device": EMBED_DEVICE},
                        encode_kwargs={"batch_size": EMBED_BATCH_SIZE},
                    )
                    cls._load_times["embeddings"] = time.time() - start_time
                    logger.info(
                        f"Embeddings loaded in {cls._load_times['embeddings']:.2f} seconds"
                    )
        return cls._embeddings

    @classmethod
    def get_vector_store(cls):
        if cls._vector_store is None:
            with cls._lock:
                if cls._vector_store is None:
                    start_time = time.time()
                    try:
                        # Import here to avoid circular imports
                        from utils import (
                            check_vector_index_exists,
                            ensure_documents_for_embedding,
                        )

                        # First check if vector index exists
                        logger.info(f"Checking vector index at {VECTOR_INDEX_PATH}...")
                        if not check_vector_index_exists():
                            logger.error(
                                f"Vector index not found at {VECTOR_INDEX_PATH}. Please run: python build_embeddings_all.py"
                            )
                            raise FileNotFoundError(
                                f"Vector index missing: {VECTOR_INDEX_PATH}"
                            )

                        logger.info(
                            "Vector index files found. Loading embeddings model..."
                        )
                        embeddings = cls.get_embeddings()
                        logger.info(f"Loading FAISS index from {VECTOR_INDEX_PATH}...")
                        try:
                            # Try with allow_dangerous_deserialization for newer langchain versions
                            cls._vector_store = FAISS.load_local(
                                VECTOR_INDEX_PATH,
                                embeddings,
                                allow_dangerous_deserialization=ALLOW_DANGEROUS_DESERIALIZATION,
                            )
                        except TypeError:
                            # Fall back to older langchain versions without the parameter
                            logger.info(
                                "Falling back to loading without allow_dangerous_deserialization parameter"
                            )
                            cls._vector_store = FAISS.load_local(
                                VECTOR_INDEX_PATH,
                                embeddings,
                            )
                        cls._load_times["vector_store"] = time.time() - start_time
                        logger.info(
                            f"Vector store loaded successfully in {cls._load_times['vector_store']:.2f} seconds"
                        )
                    except Exception as e:
                        cls._vector_store = None
                        cls._load_times["vector_store_error"] = str(e)
                        logger.error(f"Vector store loading failed: {e}")

                        # Provide helpful diagnostics
                        from utils import ensure_documents_for_embedding

                        if ensure_documents_for_embedding():
                            logger.info(
                                "Documents are available - run 'python build_embeddings_all.py' to build vector index"
                            )
                        else:
                            logger.warning(
                                "No documents found for vector search - system will fall back to text search"
                            )
        return cls._vector_store

    @classmethod
    def reset_vector_store(cls):
        """Reset the cached vector store so it can be reloaded after a rebuild."""
        with cls._lock:
            cls._vector_store = None
            if "vector_store" in cls._load_times:
                del cls._load_times["vector_store"]
            if "vector_store_error" in cls._load_times:
                del cls._load_times["vector_store_error"]
        logger.info("Vector store cache reset")

    @classmethod
    def get_load_times(cls):
        return cls._load_times
