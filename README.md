# S3 On-Prem AI Assistant (v1.4)

This is an **offline AI assistant** tailored for on-premise S3-compatible platforms (e.g. Cloudian, IBM Object Storage, MinIO, PureBlade, Huawei OceanStor S3).

It uses:
- Local documents (`.txt`, `.pdf`, `.json`, `.md`) inside the `docs/` folder
- FAISS for fast vector-based search
- Optional JSON fallback search (for bucket metadata)
- Local LLM via `ollama run mistral`

---

## Folder Structure


s3_onprem_ai_assistant/
│
├── build_embeddings_all.py      # Build embeddings from docs (vector + pickle)
├── convert_all_pdfs.py          # Convert PDF → TXT
├── watch_folder.py              # Auto-scan folder for new PDFs
├── s3ai_query.py                # CLI query tool
├── streamlit_ui.py              # Main Streamlit UI
├── utils.py                     # Shared helper functions
├── requirements.txt             # Python packages
├── README.md
│
├── docs/                        # Documentation sources
│   ├── Cloudian Admin Guide_v-8.2.pdf
│   ├── Cloudian Admin Guide_v-8.2.txt
│   ├── sample_bucket_metadata.json
│   └── ...
│
├── s3_docs_index/               # FAISS vector index
│   └── index.faiss
│
├── s3_docs_chunks.pkl           # Original content chunks
├── recent_questions.txt         # Past user queries


---

## How to Use

### 1. Install Requirements

pip install -r requirements.txt


### 2. Prepare Your Documents

Put your `.pdf`, `.txt`, `.md`, or `.json` files in the `docs/` folder.

You can also use `convert_all_pdfs.py` or run `watch_folder.py` to convert PDFs automatically.

### 3. Build Embeddings


python build_embeddings_all.py


This will:
- Convert documents into searchable chunks
- Create `s3_docs_index/` and `s3_docs_chunks.pkl`

### 4. Ask Questions via UI

streamlit run streamlit_ui.py

Or

python -m streamlit run streamlit_ui.py


Or CLI:


python s3ai_query.py "How to purge bucket in Cloudian?"


---

## Features

- Supports `.pdf`, `.txt`, `.json`, `.md` files
- Local-only, no internet needed
- Answers from documentation first, then JSON if found
- Tracks recent questions
- Easy copy-to-clipboard

---

## LLM Backend

This app uses [Ollama](https://ollama.com/) with the `mistral` model. You can change the model in `utils.py`.

---

## License

MIT License — customize and use freely in your organization.