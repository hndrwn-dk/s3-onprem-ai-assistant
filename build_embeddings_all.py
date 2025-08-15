# build_embeddings_all.py (v2.2.6) - Speed Optimized

import os
import pickle
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils import load_documents_from_path, logger, timing_decorator, ensure_documents_for_embedding
from config import VECTOR_INDEX_PATH, CHUNKS_PATH, EMBED_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, EMBED_DEVICE, EMBED_BATCH_SIZE

@timing_decorator
def build_vector_index():
    logger.info("=== Starting vector index build ===")
    
    # Check if we have real documents to process
    if not ensure_documents_for_embedding():
        logger.error("No documents found for embedding! Please upload documents to the 'docs' folder.")
        logger.info("Supported formats: PDF, TXT, MD, JSON")
        return False
    
    logger.info("Scanning documents...")
    documents = load_documents_from_path()
    if not documents:
        logger.warning("No documents found.")
        return False

    logger.info(f"Total documents loaded: {len(documents)}")
    
    # Log document sources for debugging
    sources = set()
    for doc in documents:
        source = doc.metadata.get("source", "unknown")
        sources.add(source)
    
    logger.info("Document sources:")
    for source in sorted(sources):
        count = sum(1 for doc in documents if doc.metadata.get("source") == source)
        logger.info(f"  - {source}: {count} documents")
    
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
    logger.info(f"Creating embeddings using model: {EMBED_MODEL}")
    logger.info(f"Device: {EMBED_DEVICE}, Batch size: {EMBED_BATCH_SIZE}")
    
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL, 
            model_kwargs={"device": EMBED_DEVICE}, 
            encode_kwargs={"batch_size": EMBED_BATCH_SIZE}
        )
        logger.info("Embeddings model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load embeddings model: {e}")
        logger.info("For air-gapped environments, ensure the model is pre-downloaded or use a local path")
        return False
    
    logger.info("Building FAISS vector store...")
    try:
        vector_store = FAISS.from_documents(chunks, embeddings)
        logger.info("FAISS vector store created successfully")
    except Exception as e:
        logger.error(f"Failed to create FAISS vector store: {e}")
        return False
    
    # Ensure directory exists
    os.makedirs(VECTOR_INDEX_PATH, exist_ok=True)
    
    # Save vector store
    logger.info(f"Saving vector store to: {VECTOR_INDEX_PATH}")
    try:
        vector_store.save_local(VECTOR_INDEX_PATH)
        logger.info("Vector store saved successfully")
    except Exception as e:
        logger.error(f"Failed to save vector store: {e}")
        return False

    # Save chunks for debugging
    logger.info(f"Saving chunks to: {CHUNKS_PATH}")
    try:
        with open(CHUNKS_PATH, "wb") as f:
            pickle.dump(chunks, f)
        logger.info("Chunks saved successfully")
    except Exception as e:
        logger.error(f"Failed to save chunks: {e}")
        return False

    logger.info("=== Vector index build completed successfully ===")
    logger.info(f"Vector store saved to: {VECTOR_INDEX_PATH}")
    logger.info(f"Chunks saved to: {CHUNKS_PATH}")
    logger.info(f"Total documents processed: {len(documents)}")
    logger.info(f"Total chunks created: {len(chunks)}")
    
    return True

if __name__ == "__main__":
    success = build_vector_index()
    if not success:
        logger.error("Vector index build failed!")
        exit(1)
    else:
        logger.info("Vector index build completed successfully!")