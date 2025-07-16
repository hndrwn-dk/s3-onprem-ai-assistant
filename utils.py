# utils.py – v2.2
import os
import json
import logging
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.docstore.document import Document
from config import LOG_FORMAT, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("S3AI")

def load_and_convert_documents(docs_dir):
    documents = []

    for fname in os.listdir(docs_dir):
        fpath = os.path.join(docs_dir, fname)
        ext = os.path.splitext(fname)[1].lower()

        try:
            if ext == ".pdf":
                loader = PyPDFLoader(fpath)
                documents.extend(loader.load())
            elif ext == ".txt":
                loader = TextLoader(fpath)
                documents.extend(loader.load())
            elif ext == ".json":
                with open(fpath) as f:
                    data = json.load(f)
                for entry in data if isinstance(data, list) else [data]:
                    content = "\n".join(f"{k}: {v}" for k, v in entry.items())
                    documents.append(Document(page_content=content, metadata={"source": fname}))
        except Exception as e:
            logger.warning(f"Skipped {fname}: {e}")

    return documents

def load_txt_documents(docs_dir):
    txt_docs = []
    for fname in os.listdir(docs_dir):
        if fname.endswith(".txt"):
            try:
                loader = TextLoader(os.path.join(docs_dir, fname))
                txt_docs.extend(loader.load())
            except Exception as e:
                logger.warning(f"Failed to load {fname}: {e}")
    return txt_docs
