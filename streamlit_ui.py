# streamlit_ui.py (v2.3.0) - Ultra Fast UI

import streamlit as st
import time
import os
from model_cache import ModelCache
from response_cache import response_cache
from bucket_index import bucket_index
from langchain.chains import RetrievalQA
from utils import logger, search_in_fallback_text, load_txt_documents
from config import VECTOR_SEARCH_K, RECENT_QUESTIONS_FILE, DOCS_PATH

st.set_page_config(
    page_title="S3 On-Prem AI Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimalist styling
st.markdown(
    """
    <style>
    body { background-color: #f8f9fb; }
    .stApp { max-width: 1100px; margin: 0 auto; }
    h1, h2, h3 { font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif; }
    .block-container { padding-top: 1.5rem; }
    .metric-card { background: #ffffff; border: 1px solid #eaecef; border-radius: 12px; padding: 12px; }
    .section-card { background: #ffffff; border: 1px solid #eaecef; border-radius: 12px; padding: 16px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("S3 On-Prem AI Assistant")
st.caption("Ultra-fast queries for Cloudian, IBM, MinIO, and bucket metadata")

# Sidebar: performance + data management
with st.sidebar:
    st.subheader("Performance")
    perf = ModelCache.get_load_times()
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("LLM", f"{perf.get('llm', 0):.2f}s")
    with col_b:
        vs = perf.get('vector_store')
        st.metric("Vector Store", f"{vs:.2f}s" if vs else "-")

    st.markdown("---")
    st.subheader("Data management")
    uploaded_files = st.file_uploader(
        "Upload PDF/TXT/MD/JSON/DOCX",
        type=["pdf", "txt", "md", "json", "docx"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        os.makedirs(DOCS_PATH, exist_ok=True)
        saved = []
        for uf in uploaded_files:
            save_path = os.path.join(DOCS_PATH, uf.name)
            with open(save_path, "wb") as f:
                f.write(uf.getbuffer())
            saved.append(save_path)
        st.success(f"Saved {len(saved)} file(s) to {DOCS_PATH}")

    if st.button("Rebuild embeddings"):
        with st.spinner("Rebuilding embeddings..."):
            try:
                from build_embeddings_all import build_vector_index
                build_vector_index()
                ModelCache.reset_vector_store()
                ModelCache.get_vector_store()
                st.success("Embeddings rebuilt and vector store reloaded")
            except Exception as e:
                st.error(f"Embedding rebuild failed: {e}")
                st.info("If missing packages, run: pip install sentence-transformers 'huggingface_hub<0.20'")

# Main: query panel
st.markdown("---")
with st.container():
    st.subheader("Ask a question")
    query = st.text_input(
        "Enter your question:",
        placeholder="e.g., show all buckets under dept: engineering",
        key="query_input",
    )
    col1, col2 = st.columns([3, 1])
    with col1:
        submit = st.button("Ask", type="primary")
    with col2:
        clear_cache = st.button("Clear Cache")

if clear_cache:
    response_cache.clear_expired()
    st.success("Cache cleared")

if 'query_history' not in st.session_state:
    st.session_state.query_history = []

if submit and query:
    start_time = time.time()
    st.session_state.query_history.append(query)

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Cache
        progress_bar.progress(10)
        status_text.text("Checking cache...")
        cached_response = response_cache.get(query)
        if cached_response:
            progress_bar.progress(100)
            status_text.empty()
            rt = time.time() - start_time
            st.success(f"Cached Result ({rt:.2f}s)")
            st.write(cached_response)
            with st.expander("Performance Details"):
                st.write("Source: Cache hit")
                st.write(f"Response time: {rt:.2f} seconds")
        else:
            # Quick
            progress_bar.progress(30)
            status_text.text("Quick bucket search...")
            quick_result = bucket_index.quick_search(query)
            if quick_result:
                progress_bar.progress(60)
                status_text.text("Processing with AI...")
                llm = ModelCache.get_llm()
                prompt = f"""Based on this bucket information:
{quick_result}

Question: {query}
Answer:"""
                try:
                    answer = llm(prompt)
                    progress_bar.progress(100)
                    status_text.empty()
                    rt = time.time() - start_time
                    st.info(f"Quick Search Result ({rt:.2f}s)")
                    st.write(answer)
                    response_cache.set(query, answer, "quick_search")
                    with st.expander("Raw bucket data"):
                        st.code(quick_result)
                    with st.expander("Performance Details"):
                        st.write("Source: Quick bucket search")
                        st.write(f"Response time: {rt:.2f} seconds")
                except Exception as e:
                    progress_bar.progress(100)
                    status_text.empty()
                    rt = time.time() - start_time
                    st.warning(f"Raw Results ({rt:.2f}s)")
                    st.code(quick_result)
                    logger.error(f"LLM error in quick search: {e}")
            else:
                # Vector
                progress_bar.progress(50)
                status_text.text("Vector search...")
                try:
                    vector_store = ModelCache.get_vector_store()
                    retriever = vector_store.as_retriever(search_kwargs={"k": VECTOR_SEARCH_K})
                    llm = ModelCache.get_llm()
                    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
                    progress_bar.progress(80)
                    status_text.text("AI processing...")
                    response = qa_chain.run(query)
                    if response and response.strip():
                        progress_bar.progress(100)
                        status_text.empty()
                        rt = time.time() - start_time
                        st.success(f"Vector Search Result ({rt:.2f}s)")
                        st.write(response)
                        response_cache.set(query, response, "vector")
                        with st.expander("Performance Details"):
                            st.write("Source: Vector search")
                            st.write(f"Response time: {rt:.2f} seconds")
                    else:
                        raise ValueError("Empty response from vector search")
                except Exception as e:
                    logger.warning(f"Vector search failed: {e}")
                    # Fallback
                    progress_bar.progress(90)
                    status_text.text("Fallback search...")
                    fallback_text = load_txt_documents()
                    if fallback_text:
                        relevant_context = search_in_fallback_text(query, fallback_text)
                        if relevant_context:
                            llm = ModelCache.get_llm()
                            prompt = f"""Based on this information:
{relevant_context}

Question: {query}
Answer:"""
                            try:
                                result = llm(prompt)
                                progress_bar.progress(100)
                                status_text.empty()
                                rt = time.time() - start_time
                                st.info(f"Fallback Search Result ({rt:.2f}s)")
                                st.write(result)
                                response_cache.set(query, result, "txt_fallback")
                                with st.expander("Raw matching content"):
                                    st.code(relevant_context)
                                with st.expander("Performance Details"):
                                    st.write("Source: Text fallback")
                                    st.write(f"Response time: {rt:.2f} seconds")
                            except Exception as llm_error:
                                progress_bar.progress(100)
                                status_text.empty()
                                rt = time.time() - start_time
                                st.warning(f"Raw Fallback Content ({rt:.2f}s)")
                                st.code(relevant_context)
                                logger.error(f"LLM error in fallback: {llm_error}")
                        else:
                            progress_bar.progress(100)
                            status_text.empty()
                            rt = time.time() - start_time
                            st.error(f"No Results Found ({rt:.2f}s)")
                            st.write("No relevant information found for your question.")
                    else:
                        progress_bar.progress(100)
                        status_text.empty()
                        rt = time.time() - start_time
                        st.error(f"No Data Available ({rt:.2f}s)")
                        st.write("No data available to answer your question.")

    except Exception as e:
        progress_bar.progress(100)
        status_text.empty()
        st.error(f"Error: {str(e)}")
        logger.error(f"Unexpected error: {e}")

# History
if st.session_state.query_history:
    st.subheader("Recent Queries")
    for i, hist_query in enumerate(reversed(st.session_state.query_history[-5:])):
        st.write(f"- {hist_query}")