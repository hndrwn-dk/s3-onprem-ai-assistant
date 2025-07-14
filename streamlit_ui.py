# streamlit_ui.py – v1.6
import streamlit as st
import subprocess
import os
import json
import pickle
import faiss
from sentence_transformers import SentenceTransformer

INDEX_FILE = "s3_all_docs/index.faiss"
CHUNKS_FILE = "s3_all_chunks.pkl"
DOCS_DIR = "docs"

st.set_page_config(page_title="S3 On-Prem AI Assistant", layout="wide")
st.title("S3 On-Prem AI Assistant")
st.caption("Ask a question about your S3 system:")

query = st.text_input("", placeholder="e.g. what's bucket name for finance dept")

if st.button("Submit") and query:
    try:
        index = faiss.read_index(INDEX_FILE)
        with open(CHUNKS_FILE, "rb") as f:
            chunks = pickle.load(f)
        model = SentenceTransformer("all-MiniLM-L6-v2")
        q_embed = model.encode([query])
        _, I = index.search(q_embed, 5)
        context = "\n\n".join([chunks[i] for i in I[0]])
    except Exception as e:
        context = ""
        st.warning(f"[Vector Search Error] {e}")

    prompt = f"""You are a helpful assistant for S3 On-Prem systems.

Documentation:
{context}

Question:
{query}
"""
    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=60
        )
        st.subheader("LLM Answer (Doc Search)")
        st.write(result.stdout.decode("utf-8").strip())
    except Exception as e:
        st.error(f"LLM Error: {e}")

    # Metadata fallback
    st.markdown("---")
    st.subheader("Metadata Match (JSON Fallback)")
    found = False
    for jf in os.listdir(DOCS_DIR):
        if jf.endswith(".json"):
            try:
                with open(os.path.join(DOCS_DIR, jf), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for entry in data:
                        for v in entry.values():
                            if isinstance(v, str) and query.lower() in v.lower():
                                st.json(entry)
                                found = True
            except Exception:
                continue
    if not found:
        st.info("No metadata match found.")
