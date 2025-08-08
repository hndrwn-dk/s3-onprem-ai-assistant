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
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better performance indicators
st.markdown("""
<style>
.stMetric > div > div > div > div {
    background-color: #f0f2f6;
    border-radius: 5px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("S3 On-Prem AI Assistant")
st.markdown("_Ultra-fast queries for Cloudian, IBM, MinIO, and bucket metadata_")

# Performance metrics in sidebar
with st.sidebar:
    st.subheader("Performance")
    load_times = ModelCache.get_load_times()
    if load_times:
        if 'llm' in load_times:
            st.metric("LLM Load Time", f"{load_times['llm']:.2f}s")
        if 'vector_store' in load_times:
            st.metric("Vector Store", f"{load_times['vector_store']:.2f}s")

# Uploader and build section
st.markdown("---")
st.subheader("Upload documentation and rebuild index")
uploaded_files = st.file_uploader(
    "Upload PDF/TXT/MD/JSON/DOCX files",
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
    st.write(f"Saved {len(saved)} file(s) to {DOCS_PATH}")

if st.button("Rebuild embeddings now"):
    with st.spinner("Rebuilding embeddings..."):
        try:
            # Lazy import to avoid startup cost
            from build_embeddings_all import build_vector_index
            build_vector_index()
            ModelCache.reset_vector_store()
            # Load it immediately for UI
            ModelCache.get_vector_store()
            st.success("Embeddings rebuilt and vector store reloaded")
        except Exception as e:
            st.error(f"Embedding rebuild failed: {e}")
            logger.error(f"Embedding rebuild failed: {e}")

st.markdown("---")

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Main query interface
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

if submit and query:
    start_time = time.time()

    # Add to history
    st.session_state.query_history.append(query)

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Check cache first
        progress_bar.progress(10)
        status_text.text("Checking cache...")

        cached_response = response_cache.get(query)
        if cached_response:
            progress_bar.progress(100)
            status_text.empty()
            response_time = time.time() - start_time

            st.success(f"Cached Result ({response_time:.2f}s)")
            st.write(cached_response)

            with st.expander("Performance Details"):
                st.write("Source: Cache hit")
                st.write(f"Response time: {response_time:.2f} seconds")
        else:
            # Quick bucket search
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
                    response_time = time.time() - start_time

                    st.info(f"Quick Search Result ({response_time:.2f}s)")
                    st.write(answer)

                    # Cache the response
                    response_cache.set(query, answer, "quick_search")

                    with st.expander("Raw bucket data"):
                        st.code(quick_result)

                    with st.expander("Performance Details"):
                        st.write("Source: Quick bucket search")
                        st.write(f"Response time: {response_time:.2f} seconds")
                        st.write(f"Matches found: {len(quick_result.split(chr(10)))}")

                except Exception as e:
                    progress_bar.progress(100)
                    status_text.empty()
                    response_time = time.time() - start_time

                    st.warning(f"Raw Results ({response_time:.2f}s)")
                    st.code(quick_result)
                    logger.error(f"LLM error in quick search: {e}")
            else:
                # Vector search
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
                        response_time = time.time() - start_time

                        st.success(f"Vector Search Result ({response_time:.2f}s)")
                        st.write(response)

                        # Cache the response
                        response_cache.set(query, response, "vector")

                        with st.expander("Performance Details"):
                            st.write("Source: Vector search")
                            st.write(f"Response time: {response_time:.2f} seconds")
                            st.write(f"Search results: {VECTOR_SEARCH_K} chunks")
                    else:
                        raise ValueError("Empty response from vector search")

                except Exception as e:
                    logger.warning(f"Vector search failed: {e}")

                    # Final fallback
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
                                response_time = time.time() - start_time

                                st.info(f"Fallback Search Result ({response_time:.2f}s)")
                                st.write(result)

                                # Cache the response
                                response_cache.set(query, result, "txt_fallback")

                                with st.expander("Raw matching content"):
                                    st.code(relevant_context)

                                with st.expander("Performance Details"):
                                    st.write("Source: Text fallback")
                                    st.write(f"Response time: {response_time:.2f} seconds")
                                    st.write(f"Matches found: {len(relevant_context.split(chr(10)))}")

                            except Exception as llm_error:
                                progress_bar.progress(100)
                                status_text.empty()
                                response_time = time.time() - start_time

                                st.warning(f"Raw Fallback Content ({response_time:.2f}s)")
                                st.code(relevant_context)
                                logger.error(f"LLM error in fallback: {llm_error}")
                        else:
                            progress_bar.progress(100)
                            status_text.empty()
                            response_time = time.time() - start_time

                            st.error(f"No Results Found ({response_time:.2f}s)")
                            st.write("No relevant information found for your question.")
                    else:
                        progress_bar.progress(100)
                        status_text.empty()
                        response_time = time.time() - start_time

                        st.error(f"No Data Available ({response_time:.2f}s)")
                        st.write("No data available to answer your question.")

        # Save recent question
        try:
            with open(RECENT_QUESTIONS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{query}\n")
        except Exception as e:
            logger.warning(f"Could not save recent question: {e}")

    except Exception as e:
        progress_bar.progress(100)
        status_text.empty()
        st.error(f"Error: {str(e)}")
        logger.error(f"Unexpected error: {e}")

# Query history in sidebar
if st.session_state.query_history:
    with st.sidebar:
        st.subheader("Recent Queries")
        for i, hist_query in enumerate(reversed(st.session_state.query_history[-5:])):
            if st.button(f"{hist_query[:30]}...", key=f"hist_{i}"):
                st.session_state.query_input = hist_query
                st.rerun()

# Footer with tips
st.markdown("---")
st.markdown(
    """
### Speed Tips:
- Cached queries are instant
- Bucket queries use "dept: engineering" format
- Common patterns are pre-indexed for speed
- Vector search handles complex questions

### Maintenance:
- Rebuild embeddings: `python build_embeddings_all.py`
- Clear cache: Use button above or restart app
- Check logs: Look for timing information
"""
)