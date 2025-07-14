# watch_folder.py — S3 On-Prem AI Assistant v1.4
import os
import time
from pathlib import Path
from PyPDF2 import PdfReader

DOCS_DIR = "docs"
SEEN = set()

def convert_pdf_to_txt(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        txt_path = pdf_path.with_suffix(".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Converted: {pdf_path.name}")
    except Exception as e:
        print(f"Failed: {pdf_path.name} — {e}")

def monitor_docs():
    print("Watching folder for new PDFs...")
    while True:
        for file in Path(DOCS_DIR).glob("*.pdf"):
            if file.name not in SEEN:
                SEEN.add(file.name)
                convert_pdf_to_txt(file)
        time.sleep(10)

if __name__ == "__main__":
    monitor_docs()