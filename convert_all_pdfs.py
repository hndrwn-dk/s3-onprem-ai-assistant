# convert_all_pdfs.py - v1.4
import os
from pathlib import Path
from PyPDF2 import PdfReader

DOCS_DIR = "docs"

def convert_pdf_to_txt(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        txt_path = pdf_path.with_suffix(".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Converted: {pdf_path.name} → {txt_path.name}")
    except Exception as e:
        print(f"Failed to convert {pdf_path.name}: {e}")

def convert_all():
    print("Scanning for PDF files...")
    for file in Path(DOCS_DIR).glob("*.pdf"):
        txt_version = file.with_suffix(".txt")
        if not txt_version.exists():
            convert_pdf_to_txt(file)

if __name__ == "__main__":
    convert_all()