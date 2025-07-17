# model_cache.py - Model caching for faster responses

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from config import VECTOR_INDEX_PATH, EMBED_MODEL
import time
from utils import logger

class ModelCache:
    _llm = None
    _embeddings = None
    _vector_store = None
    _load_times = {}
    
    @classmethod
    def get_llm(cls):
        if cls._llm is None:
            start_time = time.time()
            cls._llm = Ollama(
                model="phi3:mini",  # Much faster than mistral
                temperature=0.3,
                num_predict=512,    # Limit response length for speed
                top_k=10,          # Reduce sampling complexity
                top_p=0.9
            )
            cls._load_times['llm'] = time.time() - start_time
            logger.info(f"LLM loaded in {cls._load_times['llm']:.2f} seconds")
        return cls._llm
    
    @classmethod
    def get_embeddings(cls):
        if cls._embeddings is None:
            start_time = time.time()
            cls._embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
            cls._load_times['embeddings'] = time.time() - start_time
            logger.info(f"Embeddings loaded in {cls._load_times['embeddings']:.2f} seconds")
        return cls._embeddings
    
    @classmethod
    def get_vector_store(cls):
        if cls._vector_store is None:
            start_time = time.time()
            embeddings = cls.get_embeddings()
            cls._vector_store = FAISS.load_local(
                VECTOR_INDEX_PATH, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
            cls._load_times['vector_store'] = time.time() - start_time
            logger.info(f"Vector store loaded in {cls._load_times['vector_store']:.2f} seconds")
        return cls._vector_store
    
    @classmethod
    def get_load_times(cls):
        return cls._load_times