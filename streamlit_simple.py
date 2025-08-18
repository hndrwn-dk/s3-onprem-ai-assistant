# streamlit_simple.py - Clean working version
import streamlit as st
import time
import os
from model_cache import ModelCache
from response_cache import response_cache
from bucket_index import bucket_index
from utils import logger, search_in_fallback_text, load_txt_documents
from config import VECTOR_SEARCH_K, DOCS_PATH

st.set_page_config(
    page_title="S3 On-Premise AI Assistant",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 S3 On-Premise AI Assistant")
st.caption("Fully offline-capable AI assistant for answering operational, admin, and troubleshooting questions for on-premises S3-compatible platforms")

# Query input
query = st.text_input("Enter your query:", placeholder="e.g., 'how to purge bucket in cloudian hyperstore'")

# Search options
col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("🔍 Full Search", type="primary")
with col2:
    fast_search = st.button("⚡ Fast Search")
with col3:
    clear_cache = st.button("🗑️ Clear Cache")

# Fast search option
use_fast_search = st.checkbox("⚡ Always use fast search (skips slow vector loading)", value=True)

if clear_cache:
    response_cache.clear_expired()
    st.success("✅ Cache cleared")

if 'query_history' not in st.session_state:
    st.session_state.query_history = []

if (submit or fast_search) and query:
    start_time = time.time()
    st.session_state.query_history.append(query)
    
    with st.spinner("Processing query..."):
        try:
            # Check cache first
            cached_response = response_cache.get(query)
            if cached_response:
                rt = time.time() - start_time
                st.success(f"⚡ Cached Result ({rt:.2f}s)")
                st.write(cached_response)
            else:
                # Try quick bucket search
                quick_result = bucket_index.quick_search(query)
                if quick_result:
                    rt = time.time() - start_time
                    st.info(f"🚀 Quick Search ({rt:.2f}s)")
                    st.write(quick_result)
                    response_cache.set(query, quick_result, "quick_search")
                
                # If fast search is enabled or requested, use smart search
                elif use_fast_search or fast_search:
                    # Use smart search (fast PDF + AI formatting)
                    try:
                        from smart_search import smart_search
                        smart_results = smart_search(query)
                        rt = time.time() - start_time
                        st.success(f"🎯 Smart Search ({rt:.2f}s)")
                        st.markdown(smart_results)
                        response_cache.set(query, smart_results, "smart_search")
                    except Exception as e:
                        # Fallback to raw PDF search
                        try:
                            from fast_pdf_search import search_pdfs_directly
                            pdf_results = search_pdfs_directly(query, max_results=5)
                            rt = time.time() - start_time
                            st.info(f"⚡ Fast PDF Search ({rt:.2f}s)")
                            st.markdown(pdf_results)
                            response_cache.set(query, pdf_results, "fast_pdf_search")
                        except Exception as e2:
                            st.error(f"Search failed: {e2}")
                
                # Vector search (only if not using fast search)
                else:
                    st.warning("🎯 Attempting vector search (may take 30+ seconds)...")
                    
                    try:
                        # Set a reasonable timeout
                        import signal
                        
                        def timeout_handler(signum, frame):
                            raise TimeoutError("Vector search timed out")
                        
                        # This approach works better in some environments
                        vector_store = ModelCache.get_vector_store()
                        
                        if vector_store:
                            from langchain.chains import RetrievalQA
                            retriever = vector_store.as_retriever(search_kwargs={"k": VECTOR_SEARCH_K})
                            llm = ModelCache.get_llm()
                            qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
                            
                            response = qa_chain.run(query)
                            
                            if response and response.strip():
                                rt = time.time() - start_time
                                st.success(f"🎯 Vector Search ({rt:.2f}s)")
                                st.write(response)
                                response_cache.set(query, response, "vector")
                            else:
                                st.error("Empty response from vector search")
                        else:
                            st.error("Vector store not available")
                            
                    except Exception as e:
                        st.error(f"Vector search failed: {e}")
                        st.info("Falling back to text search...")
                        
                        # Fallback to text search
                        fallback_text = load_txt_documents()
                        if fallback_text:
                            relevant_context = search_in_fallback_text(query, fallback_text)
                            if relevant_context:
                                rt = time.time() - start_time
                                st.info(f"🔄 Fallback Search ({rt:.2f}s)")
                                st.write(relevant_context)
                                response_cache.set(query, relevant_context, "fallback")
                            else:
                                st.error("No results found")
                        else:
                            st.error("No data available")
                            
        except Exception as e:
            st.error(f"Query failed: {str(e)}")
            logger.error(f"Query error: {e}")

# Show recent queries
if st.session_state.query_history:
    st.subheader("📝 Recent Queries")
    for hist_query in reversed(st.session_state.query_history[-5:]):
        st.write(f"• {hist_query}")

# File upload section
with st.expander("📁 Document Management"):
    uploaded_files = st.file_uploader(
        "Upload S3 Documentation",
        type=["pdf", "txt", "md", "json"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("📤 Upload Files"):
            os.makedirs(DOCS_PATH, exist_ok=True)
            saved = []
            for uf in uploaded_files:
                save_path = os.path.join(DOCS_PATH, uf.name)
                with open(save_path, "wb") as f:
                    f.write(uf.getbuffer())
                saved.append(save_path)
            st.success(f"✅ Uploaded {len(saved)} files")
    
    if st.button("🔄 Rebuild Index"):
        with st.spinner("Building index..."):
            try:
                from build_embeddings_all import build_vector_index
                build_vector_index()
                ModelCache.reset_vector_store()
                st.success("✅ Index rebuilt successfully")
            except Exception as e:
                st.error(f"❌ Index rebuild failed: {e}")