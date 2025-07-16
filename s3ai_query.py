# s3ai_query.py – v2.2
import os
import pickle
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from utils import load_txt_documents, logger
from config import INDEX_FILE, CHUNKS_FILE, EMBED_MODEL, DOCS_DIR

def load_embeddings():
    embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    db = FAISS.load_local(INDEX_FILE, embedding, allow_dangerous_deserialization=True)
    with open(CHUNKS_FILE, "rb") as f:
        docs_chunks = pickle.load(f)
    return db, docs_chunks

def answer_question(query):
    try:
        db, docs_chunks = load_embeddings()
        relevant_docs = db.similarity_search(query, k=3)

        if relevant_docs:
            llm = OpenAI(temperature=0)
            chain = load_qa_chain(llm, chain_type="stuff")
            answer = chain.run(input_documents=relevant_docs, question=query)
            return answer
        else:
            raise ValueError("No vector match")
    except Exception:
        logger.warning("Vector Search Failed. Falling back to .txt search.")
        txt_docs = load_txt_documents(DOCS_DIR)
        matched = [d for d in txt_docs if query.lower() in d.page_content.lower()]
        if matched:
            result = "\n".join([doc.page_content for doc in matched[:3]])
            return f"{result}\n\n[TXT Fallback Matches Found]"
        else:
            return "No metadata match found."

