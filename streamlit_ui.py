# streamlit_ui.py - v2.2
import streamlit as st
from s3ai_query import answer_question
from config import RECENT_QUESTIONS_FILE

st.set_page_config(page_title="S3 On-Prem AI Assistant", layout="wide")
st.title("🧠 S3 On-Prem AI Assistant v2.2")
st.caption("Ask your Cloudian / MinIO / IBM S3 Docs anything.")

question = st.text_input("Enter your question")

if st.button("Submit") and question:
    answer = answer_question(question)
    st.markdown("### 📘 Answer:")
    st.success(answer)

    with open(RECENT_QUESTIONS_FILE, "a") as f:
        f.write(question + "\n")

if st.button("🧹 Clear History"):
    open(RECENT_QUESTIONS_FILE, "w").close()
    st.success("Recent question history cleared.")

if os.path.exists(RECENT_QUESTIONS_FILE):
    st.sidebar.markdown("### 🕘 Recent Questions")
    with open(RECENT_QUESTIONS_FILE) as f:
        for line in f.readlines()[-10:]:
            st.sidebar.write(line.strip())
