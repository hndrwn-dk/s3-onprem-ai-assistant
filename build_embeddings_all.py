# build_embeddings_all.py – v2.2

import os
import pickle
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from utils import load_and_convert_documents, logger
from config import DOCS_DIR, INDEX_FILE, CHUNKS_FILE, EMBED_MODEL

def main(dry_run=False):
    logger.info("🔍 Scanning documents...")

    documents = load_and_convert_documents(DOCS_DIR)
    if dry_run:
        logger.info(f"✅ Dry run: {len(documents)} documents ready for processing.")
        for doc in documents[:10]:
            logger.info(f"— {doc.metadata.get('source', 'unknown')}")
        return

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs_chunks = text_splitter.split_documents(documents)
    logger.info(f"🧩 Total chunks: {len(docs_chunks)}")

    embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    db = FAISS.from_documents(docs_chunks, embedding)

    db.save_local(INDEX_FILE)
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(docs_chunks, f)

    logger.info(f"✅ Embedding complete. Saved to '{INDEX_FILE}' and chunks to '{CHUNKS_FILE}'.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="List files only, no embedding")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
