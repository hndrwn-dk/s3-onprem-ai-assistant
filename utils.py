# utils.py - v1.8
import os
import json
import pickle
import subprocess
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

INDEX_FILE = "s3_all_docs"
CHUNKS_FILE = "s3_all_chunks.pkl"
DOCS_DIR = "docs"
history_file = "recent_questions.txt"

def load_embeddings():
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(INDEX_FILE, embedding, allow_dangerous_deserialization=True)

def get_recent_questions():
    if not Path(history_file).exists():
        return []
    with open(history_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_question(q):
    q = q.strip()
    if not q:
        return
    history = get_recent_questions()
    if q not in history:
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(q + "\n")

def query_llm(prompt, vectorstore=None):
    try:
        docs = vectorstore.similarity_search(prompt, k=5) if vectorstore else []
        context = "\n\n".join(doc.page_content for doc in docs)
        full_prompt = f"""You are a helpful assistant for S3 On-Prem systems.

Documentation:
{context}

Question:
{prompt}
"""
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=full_prompt.encode("utf-8"),
            capture_output=True,
            timeout=60
        )
        return result.stdout.decode("utf-8").strip()
    except Exception as e:
        return f"[Vector Search Error] {e}"

def query_json(user_query):
    json_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".json")]
    for jf in json_files:
        try:
            with open(os.path.join(DOCS_DIR, jf), "r", encoding="utf-8") as f:
                data = json.load(f)
                for entry in data:
                    for k, v in entry.items():
                        if isinstance(v, str) and user_query.lower() in v.lower():
                            return f"[Metadata Match] {k}: {v}\nFull entry: {json.dumps(entry, indent=2)}"
        except Exception:
            continue
    return None

def search_txt_documents(user_query):
    matches = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    if user_query.lower() in content.lower():
                        snippet = content.lower().split(user_query.lower(), 1)
                        preview = snippet[0][-300:] + user_query + snippet[1][:300] if len(snippet) > 1 else content[:600]
                        matches.append((filename, preview))
            except Exception:
                continue
    return matches
