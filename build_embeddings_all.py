# build_embeddings_all.py (v2.2.6) - Speed Optimized

import os
import pickle
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils import load_documents_from_path, logger, timing_decorator
from config import VECTOR_INDEX_PATH, CHUNKS_PATH, EMBED_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

@timing_decorator
def build_vector_index():
    logger.info("Scanning documents...")
    documents = load_documents_from_path()
    if not documents:
        logger.warning("No documents found.")
        return

    logger.info(f"Total documents loaded: {len(documents)}")
    
    # Split documents into optimized chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,      # Optimized size
        chunk_overlap=CHUNK_OVERLAP, # Optimized overlap
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    
    logger.info("Splitting documents into chunks...")
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Total chunks after splitting: {len(chunks)}")
    
    # Create embeddings and vector store
    logger.info("Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    
    logger.info("Building FAISS vector store...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Save vector store
    logger.info("Saving vector store...")
    vector_store.save_local(VECTOR_INDEX_PATH)

    # Save chunks for debugging
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    logger.info(f"Embedding build complete. Vector store saved to {VECTOR_INDEX_PATH}")
    logger.info(f"Chunks saved to {CHUNKS_PATH}")

if __name__ == "__main__":
    build_vector_index()