# 🧠 S3 On-Prem AI Assistant

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2%2B-green.svg)](https://python.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Offline AI](https://img.shields.io/badge/Offline-AI-important.svg)](https://ollama.com/)
[![Mistral Powered](https://img.shields.io/badge/LLM-Mistral_7B-ff69b4.svg)](https://ollama.com/library/mistral)

A fully offline-capable AI assistant for answering operational, admin, and troubleshooting questions for on-premises S3-compatible platforms such as:

- 📦 Cloudian HyperStore
- 🧊 Huawei OceanStor
- ⚡ Pure FlashBlade
- 🏢 IBM Cloud Object Storage
- 🐳 MinIO and more

## Supports

- ⚡ Hybrid vector + structured fallback
- 🧾 JSON-based metadata lookups
- 🌐 Streamlit UI and FastAPI endpoint
- 🧠 Mistral 7B running via Ollama (no API key needed)

---

## 📁 Folder Structure

```bash
s3_onprem_ai_assistant/
├── api.py                  # FastAPI REST API
├── build_embeddings_all.py # Unified embedding + conversion
├── config.py               # Central settings and paths
├── s3ai_query.py           # CLI query tool
├── streamlit_ui.py         # Streamlit web UI
├── utils.py                # Utility + fallback handler
├── docs/                   # Place .pdf / .md / .json here
│   ├── *.pdf               # Admin guides
│   ├── *.json              # Metadata
│   └── *.txt / *.md        # Optional raw or converted text
```

---

## 🧰 Requirements

- Python 3.12+
- Ollama + Mistral 7B

### 1️⃣ Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Install Ollama + Mistral

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run mistral
```

---

## 🚀 Quickstart

### 1. 🗂 Prepare your files in docs/

Drop any combination of .pdf, .md, .json, or .txt.

### 2. 🧠 Build or rebuild the index

```bash
python build_embeddings_all.py
```

✅ Auto-converts .pdf, .md, .json to .txt
🧪 Use --dry-run for test mode
📊 Prints loaded document summary

### 3. 🔍 Query using CLI

```bash
python s3ai_query.py "What's bucket name for Finance Dept?"
```

### 4. 🌐 Launch the Streamlit UI

```bash
streamlit run streamlit_ui.py
```
### 5. 🔌 Call the API

```bash
uvicorn api:app --reload --port 8000
```
Access: http://localhost:8000/docs

## 🧠 Answering Logic
✅ Vector search – top-k content from .pdf/.md/.txt
📄 JSON lookup fallback – if vector is low-score
📂 TXT fallback – shows matching lines from .txt docs (tagged as [TXT Fallback Matches])

## 💬 Example Queries

| Type               | Example                                                                  |
| ------------------ | ------------------------------------------------------------------------ |
| 🔧 Troubleshooting | “What does error code 403 in Huawei OBS?”                                |
| 📊 Metadata Lookup | “Show requestor\_email for Bucket-001”                                   |
| 🛠 Admin Tasks     | “How to purge a versioned bucket in Cloudian?”                           |
| 🧾 Lookup          | “Find bucket\_name with [alert1@support.com](mailto:alert1@support.com)” |

## 🧾 Postman Collection

```json
{
  "info": {
    "name": "S3 On-Prem AI Assistant",
    "_postman_id": "abcd1234-5678-9012-efgh-34567890ijkl",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Ask AI",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"query\": \"pc code 619X\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/query",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["query"]
        }
      },
      "response": []
    }
  ]
}
```

## 🖼 Streamlit Dashboard Preview

Example dashboard layout after launching streamlit_ui.py
- Place `.txt`, `.pdf`, `.md`, and `.json` files into the `docs/` folder.
- Use `flatten_json_to_txt.py` to flatten bucket metadata.

## Feature Highlights

✅ Offline Mode (no cloud dependency)
✅ Auto .pdf/.json/.md to .txt conversion
✅ FAISS + HuggingFace embeddings
✅ LLM powered by Mistral 7B
✅ Vector + Metadata fallback
✅ Central config/logging (via config.py)
✅ API + CLI + Web UI
✅ Clear history button + copy result


## 🧪 Tested On

- Python 3.12
- LangChain 0.2+
- Streamlit 1.35+
- FAISS CPU 1.7.4
- Ollama (Mistral 7B)

## 📘 License

This project is licensed under the MIT License

## 🙋‍♂️ Contributions

Feel free to fork and enhance — especially to add support for other vendors (e.g. NetApp, Dell ECS). PRs welcome!
