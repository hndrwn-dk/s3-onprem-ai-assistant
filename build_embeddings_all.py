# build_embeddings_all.py — S3 On-Prem AI Assistant v1.4
import os
import json
import pickle
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, JSONLoader, UnstructuredMarkdownLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

INDEX_FILE = "s3_all_docs"
CHUNKS_FILE = "s3_all_chunks.pkl"
DOCS_DIR = "docs"

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
all_docs = []

for file in os.listdir(DOCS_DIR):
    path = os.path.join(DOCS_DIR, file)
    try:
        if file.endswith(".txt"):
            loader = TextLoader(path, encoding="utf-8")
        elif file.endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif file.endswith(".json"):
            loader = JSONLoader(path, jq_schema=".", text_content=False)
        elif file.endswith(".md"):
            loader = UnstructuredMarkdownLoader(path)
        else:
            continue
        docs = loader.load()
        all_docs.extend(splitter.split_documents(docs))
        print(f"Loaded: {file}")
    except Exception as e:
        print(f"Skipping {file}: {e}")

print(f"Total chunks: {len(all_docs)}")
with open(CHUNKS_FILE, "wb") as f:
    pickle.dump([doc.page_content for doc in all_docs], f)

vectorstore = FAISS.from_documents(all_docs, embedding)
vectorstore.save_local(INDEX_FILE)
print("Embedding completed. Index and chunks saved.")