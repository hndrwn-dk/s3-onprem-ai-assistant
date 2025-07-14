# 🧠 S3 On-Prem AI Assistant

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://python.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A powerful, **offline-ready AI assistant** for answering operational, admin, and troubleshooting questions for **S3-compatible On-Prem platforms** such as:

- 📦 Cloudian HyperStore
- 🏢 IBM Cloud Object Storage
- ⚡ Pure FlashBlade
- 🧊 Huawei OceanStor
- 🐳 MinIO and others

It supports both **vector search** on `.txt/.pdf`/`.md` docs and **structured lookups** on flattened `.json` metadata.

---

## 📁 Project Structure

```bash
s3_onprem_ai_assistant/
├── docs/                           # All input files (.txt/.pdf/.json)
│   ├── sample_bucket_metadata.json
│   ├── bucket_metadata_flattened.txt
│   └── *.txt / *.pdf files
├── s3ai_query.py                  # CLI tool to query docs + metadata
├── streamlit_ui.py                # Web UI for the assistant
├── build_embeddings_all.py        # Indexes all documents to FAISS
├── convert_json_to_txt.py         # Converts JSON to readable .txt
├── flatten_json_to_txt.py         # Flattens structured JSON metadata
├── watch_folder.py                # Watches `docs/` for new files
├── utils.py                       # Shared utility functions
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🧰 Prerequisites

Before you begin:

1. **Install Python 3.12+**
   > https://www.python.org/downloads/

2. **Install Ollama**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh

3. Pull the Mistral model

ollama run mistral

> Leave Ollama running in the background or use ollama serve.

## 🚀 Quickstart

### 1. 🔧 Install dependencies

```bash
pip install -r requirements.txt
```

### 2. 📚 Prepare your documents

- Place `.txt`, `.pdf`, `.md`, and `.json` files into the `docs/` folder.
- Use `flatten_json_to_txt.py` to flatten bucket metadata.

```bash
python flatten_json_to_txt.py
```

### 3. 🏗 Build the vector index

```bash
python build_embeddings_all.py
```

### 4. 🤖 Run the assistant via CLI

```bash
python s3ai_query.py "What's bucket name for Finance Dept?"
```

### 5. 🌐 Or launch Streamlit UI

```bash
streamlit run streamlit_ui.py
```

---

## 💡 Features

✅ Hybrid Vector + Metadata Search  
✅ Offline Mode (No API key needed)  
✅ Supports PDF, Markdown, Text, JSON  
✅ Extensible with new documents or metadata  
✅ Uses FAISS + HuggingFace Sentence Transformers  

---

## 🧠 Sample Question Types

| Type                  | Example                                               |
|-----------------------|-------------------------------------------------------|
| 🔍 Operational        | “How to purge bucket in Cloudian S3?”                 |
| 📊 Metadata Lookup    | “What's bucket name for Finance Dept?”                |
| ⚙️ Admin Commands     | “How to check S3 object count in Cloudian S3”         |
| 🛠 Troubleshooting     | “What does error code 500 in IBM S3?”                 |

---

## 🧪 Tested On

- Windows 10/11, Python 3.12  
- Streamlit v1.35+  
- LangChain v0.2+  
- Sentence Transformers: `all-MiniLM-L6-v2`  
- FAISS CPU (v1.7.4)

---

## 📘 License

This project is licensed under the MIT License.

---

## 📸 Screenshot (UI)

_Add a screenshot here after launching the Streamlit app._

---

## 🙋‍♂️ Contributions

Feel free to fork and enhance — especially to add support for other vendors (e.g. NetApp, Dell ECS). PRs welcome!
