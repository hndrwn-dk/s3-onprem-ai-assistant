# streamlit_ui.py (v3.0.0) - Enterprise Grade AI Assistant

import streamlit as st
import time
import os
from model_cache import ModelCache
from response_cache import response_cache
from bucket_index import bucket_index
from langchain.chains import RetrievalQA
from utils import logger, search_in_fallback_text, load_txt_documents
from config import VECTOR_SEARCH_K, RECENT_QUESTIONS_FILE, DOCS_PATH

# Enterprise page configuration
st.set_page_config(
    page_title="S3 On-Premise AI Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional Enterprise Styling - Compact Version
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    }
    
    /* Compact Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        letter-spacing: -0.025em;
    }
    
    h1 { font-size: 1.75rem !important; margin-bottom: 0.4rem !important; }
    h2 { font-size: 1.25rem !important; margin-bottom: 0.5rem !important; }
    h3 { font-size: 1.1rem !important; margin-bottom: 0.4rem !important; }
    
    /* Compact Main Container */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1.2rem !important;
        max-width: 1400px !important;
    }
    
    /* Compact Header Section */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.2rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header h1 {
        color: #ffffff !important;
        margin-bottom: 0.3rem !important;
        font-size: 1.75rem !important;
        font-weight: 600 !important;
    }
    
    .main-header .subtitle {
        color: #cbd5e1 !important;
        font-size: 0.85rem !important;
        font-weight: 400 !important;
        opacity: 0.9;
        line-height: 1.4;
    }
    
    /* Compact Cards */
    .enterprise-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease;
    }
    
    .enterprise-card:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
        transform: translateY(-1px);
    }
    
    /* Compact Metrics */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        text-align: center;
        box-shadow: 0 1px 2px -1px rgba(0, 0, 0, 0.06);
    }
    
    .metric-label {
        font-size: 0.6rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.2rem;
    }
    
    .metric-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Compact Input Styles */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 6px !important;
        padding: 0.6rem 0.8rem !important;
        font-size: 0.85rem !important;
        font-weight: 400 !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Compact Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.025em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Secondary Button */
    .secondary-btn button {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #374151 !important;
        border: 2px solid #d1d5db !important;
    }
    
    .secondary-btn button:hover {
        background: #f9fafb !important;
        border-color: #9ca3af !important;
    }
    
    /* Compact Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        height: 6px !important;
    }
    
    /* Compact Success/Error Messages */
    .stAlert {
        border-radius: 6px !important;
        border: none !important;
        font-size: 0.8rem !important;
        padding: 0.75rem !important;
    }
    
    /* Compact Sidebar */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-success {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    
    .status-warning {
        background: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    
    .status-info {
        background: #dbeafe;
        color: #1e40af;
        border: 1px solid #bfdbfe;
    }
    
    /* Compact Query History */
    .query-history {
        background: rgba(255, 255, 255, 0.6);
        border-left: 3px solid #3b82f6;
        padding: 0.5rem 0.75rem;
        margin: 0.3rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.8rem;
        color: #374151;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .css-1rs6os {visibility: hidden;}
    .css-17ziqus {visibility: hidden;}
    
    /* Compact Responsive Design */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        
        .main-header {
            padding: 1rem !important;
        }
        
        .main-header h1 {
            font-size: 1.5rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Main Header
st.markdown(
    """
    <div class="main-header">
        <h1> S3 On-Premise AI Assistant</h1>
        <p class="subtitle">Fully offline-capable AI assistant for answering operational, admin, and troubleshooting questions for on-premises S3-compatible platforms</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Compact Performance Dashboard
st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
st.markdown("###  System Performance")

perf = ModelCache.get_load_times()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label"> LLM Response</div>
            <div class="metric-value">{perf.get('llm', 0):.2f}s</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    vs = perf.get('vector_store')
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label"> Vector Search</div>
            <div class="metric-value">{'%.2fs' % vs if vs else 'N/A'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    cache_stats = response_cache.get_stats() if hasattr(response_cache, 'get_stats') else {}
    hit_rate = cache_stats.get('hit_rate', 0)
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label"> Cache Hit Rate</div>
            <div class="metric-value">{hit_rate:.1%}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label"> Status</div>
            <div class="metric-value">Online</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('</div>', unsafe_allow_html=True)

# Compact Query Interface
st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
st.markdown("###  Query Interface")

query = st.text_input(
    "",
    placeholder=" Enter your query (e.g., 'Show all buckets for engineering department')",
    key="query_input",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    submit = st.button(" Execute Query", type="primary", use_container_width=True)
with col2:
    fast_search = st.button(" Fast Search", use_container_width=True, help="Skip vector search for instant results")
with col3:
    clear_cache = st.button(" Clear Cache", use_container_width=True)

# Fast search option
st.session_state.use_fast_search = st.checkbox(" Skip vector search (faster but less comprehensive)", value=False, help="Use text-based search only - much faster but may miss some results")

st.markdown('</div>', unsafe_allow_html=True)

# Compact Data Management
with st.expander("📁 Data Management", expanded=False):
    st.markdown("Upload documents to enhance the knowledge base:")
    uploaded_files = st.file_uploader(
        "Select files",
        type=["pdf", "txt", "md", "json", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if uploaded_files:
            if st.button("📤 Upload Files", use_container_width=True):
                os.makedirs(DOCS_PATH, exist_ok=True)
                saved = []
                for uf in uploaded_files:
                    save_path = os.path.join(DOCS_PATH, uf.name)
                    with open(save_path, "wb") as f:
                        f.write(uf.getbuffer())
                    saved.append(save_path)
                st.success(f" Successfully uploaded {len(saved)} file(s)")
    
    with col2:
        if st.button(" Rebuild Index", use_container_width=True):
            with st.spinner("Rebuilding knowledge base..."):
                try:
                    from build_embeddings_all import build_vector_index
                    build_vector_index()
                    ModelCache.reset_vector_store()
                    ModelCache.get_vector_store()
                    st.success(" Knowledge base successfully updated")
                except Exception as e:
                    st.error(f" Index rebuild failed: {e}")

# Clear cache functionality
if clear_cache:
    response_cache.clear_expired()
    st.success(" Cache cleared successfully")

# Initialize query history
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Query Processing
if (submit or fast_search) and query:
    start_time = time.time()
    st.session_state.query_history.append(query)

    # Compact progress indicators
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()

    try:
        # Cache check
        progress_bar.progress(10)
        status_text.markdown(" **Checking cache...**")
        cached_response = response_cache.get(query)
        
        if cached_response:
            progress_bar.progress(100)
            status_text.empty()
            rt = time.time() - start_time
            
            st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="status-indicator status-success"> Cached Result • {rt:.2f}s</div>', unsafe_allow_html=True)
            st.markdown("---")
            st.markdown(cached_response)
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.expander(" Performance Details"):
                st.markdown("**Source:** Cache hit")
                st.markdown(f"**Response time:** {rt:.2f} seconds")
        else:
            # Quick search
            progress_bar.progress(30)
            status_text.markdown(" **Performing quick bucket search...**")
            quick_result = bucket_index.quick_search(query)
            
            if quick_result:
                progress_bar.progress(60)
                status_text.markdown(" **Processing with AI...**")
                llm = ModelCache.get_llm()
                prompt = f"""Based on this bucket information:
{quick_result}

Question: {query}
Answer:"""
                try:
                    use_ai_format = st.session_state.get("use_ai_format", False)
                    if use_ai_format:
                        import concurrent.futures
                        from config import LLM_TIMEOUT_SECONDS
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                            fut = ex.submit(llm, prompt)
                            answer = fut.result(timeout=LLM_TIMEOUT_SECONDS)
                    else:
                        answer = quick_result
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    rt = time.time() - start_time
                    
                    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="status-indicator status-info"> Quick Search • {rt:.2f}s</div>', unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown(answer)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    response_cache.set(query, answer, "quick_search")
                    with st.expander("📋 Raw Data"):
                        st.code(quick_result, language="json")
                        
                except Exception as e:
                    progress_bar.progress(100)
                    status_text.empty()
                    rt = time.time() - start_time
                    
                    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="status-indicator status-warning">⚠️ Raw Results • {rt:.2f}s</div>', unsafe_allow_html=True)
                    st.markdown("---")
                    st.code(quick_result, language="json")
                    st.markdown('</div>', unsafe_allow_html=True)
                    logger.error(f"LLM error in quick search: {e}")
            else:
                # Check if fast search is enabled or requested
                use_fast_search = st.session_state.get("use_fast_search", False) or fast_search
                
                if use_fast_search:
                    # Skip vector search, go directly to text fallback
                    progress_bar.progress(90)
                    status_text.markdown(" **Fast text search...**")
                    fallback_text = load_txt_documents()
                    
                    if fallback_text:
                        relevant_context = search_in_fallback_text(query, fallback_text)
                        if relevant_context:
                            progress_bar.progress(100)
                            status_text.empty()
                            rt = time.time() - start_time
                            
                            st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
                            st.markdown(f'<div class="status-indicator status-info"> Fast Search • {rt:.2f}s</div>', unsafe_allow_html=True)
                            st.markdown("---")
                            st.markdown(relevant_context)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            response_cache.set(query, relevant_context, "fast_search")
                        else:
                            st.error(f" No Results Found ({time.time() - start_time:.2f}s)")
                    else:
                        st.error(f" No Data Available ({time.time() - start_time:.2f}s)")
                else:
                    # Vector search with timeout
                    progress_bar.progress(50)
                    status_text.markdown(" **Performing vector search...**")
                    try:
                        # Add timeout to prevent hanging in Streamlit
                        import concurrent.futures
                        
                        def load_vector_store():
                            return ModelCache.get_vector_store()
                        
                        # Try to load vector store with 30 second timeout
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(load_vector_store)
                            try:
                                vector_store = future.result(timeout=30)  # 30 second timeout
                            except concurrent.futures.TimeoutError:
                                raise TimeoutError("Vector store loading timed out after 30 seconds. Index may be too large.")
                        
                        retriever = vector_store.as_retriever(search_kwargs={"k": VECTOR_SEARCH_K})
                        llm = ModelCache.get_llm()
                        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
                        
                        progress_bar.progress(80)
                        status_text.markdown(" **AI processing...**")
                        from config import LLM_TIMEOUT_SECONDS
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                            fut = ex.submit(qa_chain.run, query)
                            response = fut.result(timeout=LLM_TIMEOUT_SECONDS)
                        
                        if response and response.strip():
                            progress_bar.progress(100)
                            status_text.empty()
                            rt = time.time() - start_time
                            
                            st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
                            st.markdown(f'<div class="status-indicator status-success">🎯 Vector Search • {rt:.2f}s</div>', unsafe_allow_html=True)
                            st.markdown("---")
                            st.markdown(response)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            response_cache.set(query, response, "vector")
                            with st.expander(" Performance Details"):
                                st.markdown("**Source:** Vector search")
                                st.markdown(f"**Response time:** {rt:.2f} seconds")
                        else:
                            raise ValueError("Empty response from vector search")
                        
                except Exception as e:
                    if "timed out" in str(e).lower():
                        logger.warning(f"Vector search timed out: {e}")
                        st.warning("⚠️ Vector search is taking too long (>30s). Using faster text search instead.")
                    else:
                        logger.warning(f"Vector search failed: {e}")
                    
                    # Fallback search
                    progress_bar.progress(90)
                    status_text.markdown(" **Fallback search...**")
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
                                
                                st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
                                st.markdown(f'<div class="status-indicator status-info"> Fallback Search • {rt:.2f}s</div>', unsafe_allow_html=True)
                                st.markdown("---")
                                st.markdown(result)
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                response_cache.set(query, result, "txt_fallback")
                                with st.expander("📋 Raw Content"):
                                    st.code(relevant_context)
                                with st.expander(" Performance Details"):
                                    st.markdown("**Source:** Text fallback")
                                    st.markdown(f"**Response time:** {rt:.2f} seconds")
                            except Exception as llm_error:
                                progress_bar.progress(100)
                                status_text.empty()
                                rt = time.time() - start_time
                                
                                st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
                                st.markdown(f'<div class="status-indicator status-warning">⚠️ Raw Content • {rt:.2f}s</div>', unsafe_allow_html=True)
                                st.markdown("---")
                                st.code(relevant_context)
                                st.markdown('</div>', unsafe_allow_html=True)
                                logger.error(f"LLM error in fallback: {llm_error}")
                        else:
                            progress_bar.progress(100)
                            status_text.empty()
                            rt = time.time() - start_time
                            st.error(f" No Results Found ({rt:.2f}s)")
                            st.markdown("No relevant information found for your query.")
                    else:
                        progress_bar.progress(100)
                        status_text.empty()
                        rt = time.time() - start_time
                        st.error(f" No Data Available ({rt:.2f}s)")
                        st.markdown("No data available to process your query.")

    except Exception as e:
        progress_bar.progress(100)
        status_text.empty()
        st.error(f" System Error: {str(e)}")
        logger.error(f"Unexpected error: {e}")

# Compact Query History
if st.session_state.query_history:
    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Recent Queries")
    for i, hist_query in enumerate(reversed(st.session_state.query_history[-3:])):
        st.markdown(f'<div class="query-history"> {hist_query}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)