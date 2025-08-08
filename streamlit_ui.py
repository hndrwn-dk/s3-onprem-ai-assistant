# streamlit_ui.py (v2.2.7) - Enhanced UI with Document Upload

import streamlit as st
import time
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
import pandas as pd
from model_cache import ModelCache
from response_cache import response_cache
from bucket_index import bucket_index
from langchain.chains import RetrievalQA
from utils import logger, search_in_fallback_text, load_txt_documents, load_documents_from_path
from config import VECTOR_SEARCH_K, RECENT_QUESTIONS_FILE, DOCS_PATH
from validation import safe_query, safe_filename, ValidationError

# Page configuration
st.set_page_config(
    page_title="S3 On-Premises AI Assistant", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/hndrwn-dk/s3-onprem-ai-assistant',
        'Report a bug': 'https://github.com/hndrwn-dk/s3-onprem-ai-assistant/issues',
        'About': "S3 On-Premises AI Assistant v2.2.7 - Secure & Enhanced"
    }
)

# Custom CSS for better UI/UX
st.markdown("""
<style>
/* Main container styling */
.main-container {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
}

/* Upload area styling */
.upload-container {
    border: 2px dashed #007bff;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    background-color: #f8f9ff;
    margin: 10px 0;
}

/* Performance metrics styling */
.metric-container {
    background-color: #e9ecef;
    border-radius: 8px;
    padding: 15px;
    margin: 5px 0;
}

/* Query results styling */
.result-container {
    background-color: white;
    border-left: 4px solid #28a745;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Error styling */
.error-container {
    background-color: #fff5f5;
    border-left: 4px solid #dc3545;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
}

/* Warning styling */
.warning-container {
    background-color: #fffbf0;
    border-left: 4px solid #ffc107;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
}

/* Info styling */
.info-container {
    background-color: #f0f8ff;
    border-left: 4px solid #17a2b8;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
}

/* Button styling */
.stButton > button {
    border-radius: 5px;
    border: none;
    padding: 0.5rem 1rem;
    font-weight: 500;
}

/* Progress bar styling */
.stProgress .st-bo {
    background-color: #007bff;
}

/* File uploader styling */
.stFileUploader {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'embeddings_built' not in st.session_state:
        st.session_state.embeddings_built = False
    if 'documents_loaded' not in st.session_state:
        st.session_state.documents_loaded = False

def check_embeddings_exist() -> bool:
    """Check if embeddings have been built"""
    vector_path = Path("s3_all_docs")
    return vector_path.exists() and any(vector_path.iterdir())

def get_uploaded_files_info() -> List[dict]:
    """Get information about uploaded files"""
    docs_path = Path(DOCS_PATH)
    if not docs_path.exists():
        return []
    
    files_info = []
    for file_path in docs_path.iterdir():
        if file_path.is_file():
            try:
                stat = file_path.stat()
                files_info.append({
                    'name': file_path.name,
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'extension': file_path.suffix.lower()
                })
            except Exception as e:
                logger.error(f"Error getting file info for {file_path}: {e}")
    
    return files_info

def save_uploaded_file(uploaded_file, docs_path: str) -> bool:
    """Save uploaded file to docs directory"""
    try:
        # Validate filename
        safe_name = safe_filename(uploaded_file.name)
        file_path = Path(docs_path) / safe_name
        
        # Create docs directory if it doesn't exist
        Path(docs_path).mkdir(parents=True, exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        logger.info(f"File uploaded successfully: {safe_name}")
        return True
    except Exception as e:
        logger.error(f"Error saving uploaded file: {e}")
        return False

def build_embeddings_async() -> bool:
    """Build embeddings using the build script"""
    try:
        # Run the build embeddings script
        result = subprocess.run(
            ["python", "build_embeddings_all.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            logger.info("Embeddings built successfully")
            return True
        else:
            logger.error(f"Error building embeddings: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("Embedding build process timed out")
        return False
    except Exception as e:
        logger.error(f"Error running embedding build: {e}")
        return False

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def render_sidebar():
    """Render the sidebar with upload functionality and system info"""
    with st.sidebar:
        st.title("S3 AI Assistant")
        st.caption("v2.2.7 - Enhanced Edition")
        
        # System Status
        st.subheader("System Status")
        
        # Check if embeddings exist
        embeddings_exist = check_embeddings_exist()
        
        if embeddings_exist:
            st.success("Embeddings: Ready")
        else:
            st.warning("Embeddings: Not built")
        
        # Performance metrics
        load_times = ModelCache.get_load_times()
        if load_times:
            st.subheader("Performance Metrics")
            
            col1, col2 = st.columns(2)
            with col1:
                if 'llm' in load_times:
                    st.metric("LLM Load", f"{load_times['llm']:.2f}s")
            with col2:
                if 'vector_store' in load_times:
                    st.metric("Vector Store", f"{load_times['vector_store']:.2f}s")
        
        # Document Management Section
        st.subheader("Document Management")
        
        # File upload area
        st.markdown("**Upload Documents**")
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['pdf', 'txt', 'json', 'md'],
            accept_multiple_files=True,
            help="Supported formats: PDF, TXT, JSON, MD"
        )
        
        if uploaded_files:
            if st.button("Upload Files", type="primary"):
                success_count = 0
                with st.spinner("Uploading files..."):
                    for uploaded_file in uploaded_files:
                        if save_uploaded_file(uploaded_file, DOCS_PATH):
                            success_count += 1
                
                if success_count > 0:
                    st.success(f"Successfully uploaded {success_count} file(s)")
                    st.session_state.documents_loaded = True
                    st.session_state.embeddings_built = False
                    st.rerun()
                else:
                    st.error("Failed to upload files")
        
        # Build embeddings button
        if st.session_state.documents_loaded or not embeddings_exist:
            if st.button("Build Embeddings", type="secondary"):
                with st.spinner("Building embeddings... This may take a few minutes."):
                    progress_bar = st.progress(0)
                    
                    # Simulate progress updates
                    for i in range(0, 101, 20):
                        progress_bar.progress(i)
                        time.sleep(0.5)
                    
                    success = build_embeddings_async()
                    
                    if success:
                        st.success("Embeddings built successfully!")
                        st.session_state.embeddings_built = True
                        st.session_state.documents_loaded = False
                        st.rerun()
                    else:
                        st.error("Failed to build embeddings. Check logs for details.")
        
        # Current documents
        files_info = get_uploaded_files_info()
        if files_info:
            st.subheader("Current Documents")
            
            # Create a summary
            total_files = len(files_info)
            total_size = sum(f['size'] for f in files_info)
            
            st.metric("Total Files", total_files)
            st.metric("Total Size", format_file_size(total_size))
            
            # File list
            with st.expander("View File Details"):
                for file_info in files_info[:10]:  # Show first 10 files
                    st.text(f"{file_info['name']} ({format_file_size(file_info['size'])})")
                
                if len(files_info) > 10:
                    st.text(f"... and {len(files_info) - 10} more files")
        
        # Cache management
        st.subheader("Cache Management")
        if st.button("Clear Cache"):
            response_cache.clear_expired()
            st.success("Cache cleared!")

def render_main_content():
    """Render the main content area"""
    st.title("S3 On-Premises AI Assistant")
    st.markdown("**Ask questions about your S3 storage infrastructure, bucket metadata, and operational procedures**")
    
    # Check if system is ready
    embeddings_exist = check_embeddings_exist()
    
    if not embeddings_exist:
        st.warning("""
        **System Setup Required**
        
        Please upload your documents and build embeddings before asking questions:
        1. Upload PDF, TXT, JSON, or MD files using the sidebar
        2. Click 'Build Embeddings' to process your documents
        3. Start asking questions!
        """)
        
        # Show example documents section
        st.subheader("Example Questions")
        st.info("""
        Once your documents are processed, you can ask questions like:
        - "Show all buckets under dept: engineering"
        - "How to configure S3 access policies?"
        - "What are the backup procedures for critical buckets?"
        - "Find buckets with label: production"
        """)
        return
    
    # Main query interface
    st.subheader("Ask Your Question")
    
    # Query input
    query = st.text_area(
        "Enter your question:",
        placeholder="e.g., show all buckets under dept: engineering",
        height=100,
        help="Ask about bucket metadata, S3 procedures, or operational questions"
    )
    
    # Query options
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        submit = st.button("Ask Question", type="primary", disabled=not query.strip())
    
    with col2:
        include_raw = st.checkbox("Show Raw Data", help="Include raw search results")
    
    with col3:
        include_metrics = st.checkbox("Show Metrics", value=True, help="Show performance metrics")
    
    # Process query
    if submit and query.strip():
        process_query(query.strip(), include_raw, include_metrics)
    
    # Query history
    if st.session_state.query_history:
        st.subheader("Recent Questions")
        
        with st.expander("View Query History", expanded=False):
            for i, hist_query in enumerate(reversed(st.session_state.query_history[-10:])):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(hist_query)
                with col2:
                    if st.button("Re-ask", key=f"reask_{i}"):
                        process_query(hist_query, include_raw, include_metrics)

def process_query(query: str, include_raw: bool = False, include_metrics: bool = True):
    """Process a user query and display results"""
    start_time = time.time()
    
    # Add to history
    if query not in st.session_state.query_history:
        st.session_state.query_history.append(query)
        if len(st.session_state.query_history) > 50:  # Keep only last 50 queries
            st.session_state.query_history = st.session_state.query_history[-50:]
    
    # Validate query
    try:
        validated_query = safe_query(query)
    except ValidationError as e:
        st.error(f"Invalid query: {e}")
        return
    
    # Progress tracking
    progress_container = st.container()
    result_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        # Check cache first
        progress_bar.progress(10)
        status_text.text("Checking cache...")
        
        cached_response = response_cache.get(validated_query)
        if cached_response:
            progress_bar.progress(100)
            status_text.empty()
            response_time = time.time() - start_time
            
            with result_container:
                st.success(f"**Cached Result** (Response time: {response_time:.2f}s)")
                
                st.markdown("**Answer:**")
                st.write(cached_response)
                
                if include_metrics:
                    with st.expander("Performance Details"):
                        st.json({
                            "source": "cache",
                            "response_time": f"{response_time:.2f}s",
                            "cached": True
                        })
            return
        
        # Quick bucket search
        progress_bar.progress(30)
        status_text.text("Performing quick bucket search...")
        
        quick_result = bucket_index.quick_search(validated_query)
        if quick_result:
            progress_bar.progress(60)
            status_text.text("Processing with AI...")
            
            try:
                llm = ModelCache.get_llm()
                prompt = f"""Based on this bucket information:
{quick_result}

Question: {validated_query}
Answer clearly and concisely:"""
                
                answer = llm(prompt)
                progress_bar.progress(100)
                status_text.empty()
                response_time = time.time() - start_time
                
                with result_container:
                    st.info(f"**Quick Search Result** (Response time: {response_time:.2f}s)")
                    
                    st.markdown("**Answer:**")
                    st.write(answer)
                    
                    # Cache the response
                    response_cache.set(validated_query, answer, "quick_search")
                    
                    if include_raw:
                        with st.expander("Raw Bucket Data"):
                            st.code(quick_result)
                    
                    if include_metrics:
                        with st.expander("Performance Details"):
                            st.json({
                                "source": "quick_search",
                                "response_time": f"{response_time:.2f}s",
                                "matches_found": len(quick_result.split('\n')),
                                "confidence": 0.9
                            })
                return
                
            except Exception as e:
                progress_bar.progress(100)
                status_text.empty()
                response_time = time.time() - start_time
                
                with result_container:
                    st.warning(f"**Raw Results** (Response time: {response_time:.2f}s)")
                    st.code(quick_result)
                    st.caption("AI processing failed, showing raw search results")
                return
        
        # Vector search
        progress_bar.progress(50)
        status_text.text("Performing vector search...")
        
        try:
            vector_store = ModelCache.get_vector_store()
            retriever = vector_store.as_retriever(search_kwargs={"k": VECTOR_SEARCH_K})
            llm = ModelCache.get_llm()
            qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
            
            progress_bar.progress(80)
            status_text.text("AI processing...")
            
            response = qa_chain.run(validated_query)
            
            if response and response.strip():
                progress_bar.progress(100)
                status_text.empty()
                response_time = time.time() - start_time
                
                with result_container:
                    st.success(f"**Vector Search Result** (Response time: {response_time:.2f}s)")
                    
                    st.markdown("**Answer:**")
                    st.write(response)
                    
                    # Cache the response
                    response_cache.set(validated_query, response, "vector")
                    
                    if include_metrics:
                        with st.expander("Performance Details"):
                            st.json({
                                "source": "vector_search",
                                "response_time": f"{response_time:.2f}s",
                                "search_results": VECTOR_SEARCH_K,
                                "confidence": 0.8
                            })
                return
            else:
                raise ValueError("Empty response from vector search")

        except Exception as e:
            logger.warning(f"Vector search failed: {e}")
            
            # Final fallback
            progress_bar.progress(90)
            status_text.text("Trying fallback search...")
            
            fallback_text = load_txt_documents()
            if fallback_text:
                relevant_context = search_in_fallback_text(validated_query, fallback_text)
                
                if relevant_context:
                    try:
                        llm = ModelCache.get_llm()
                        prompt = f"""Based on this information:
{relevant_context}

Question: {validated_query}
Answer accurately and concisely:"""
                        
                        result = llm(prompt)
                        progress_bar.progress(100)
                        status_text.empty()
                        response_time = time.time() - start_time
                        
                        with result_container:
                            st.info(f"**Fallback Search Result** (Response time: {response_time:.2f}s)")
                            
                            st.markdown("**Answer:**")
                            st.write(result)
                            
                            # Cache the response
                            response_cache.set(validated_query, result, "txt_fallback")
                            
                            if include_raw:
                                with st.expander("Raw Matching Content"):
                                    st.code(relevant_context)
                            
                            if include_metrics:
                                with st.expander("Performance Details"):
                                    st.json({
                                        "source": "text_fallback",
                                        "response_time": f"{response_time:.2f}s",
                                        "matches_found": len(relevant_context.split('\n')),
                                        "confidence": 0.6
                                    })
                        return
                        
                    except Exception as llm_error:
                        progress_bar.progress(100)
                        status_text.empty()
                        response_time = time.time() - start_time
                        
                        with result_container:
                            st.warning(f"**Raw Fallback Content** (Response time: {response_time:.2f}s)")
                            st.code(relevant_context)
                            st.caption("AI processing failed, showing raw matching content")
                        return
                else:
                    progress_bar.progress(100)
                    status_text.empty()
                    response_time = time.time() - start_time
                    
                    with result_container:
                        st.error(f"**No Results Found** (Response time: {response_time:.2f}s)")
                        st.write("No relevant information found for your question.")
                        
                        st.info("""
                        **Suggestions:**
                        - Try rephrasing your question
                        - Use more specific terms
                        - Check if relevant documents are uploaded
                        - Rebuild embeddings if you recently added documents
                        """)
            else:
                progress_bar.progress(100)
                status_text.empty()
                response_time = time.time() - start_time
                
                with result_container:
                    st.error(f"**No Data Available** (Response time: {response_time:.2f}s)")
                    st.write("No data available to answer your question.")
                    st.info("Please upload documents and build embeddings first.")
        
        # Save recent question
        try:
            with open(RECENT_QUESTIONS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{validated_query}\n")
        except Exception as e:
            logger.warning(f"Could not save recent question: {e}")
            
    except Exception as e:
        progress_bar.progress(100)
        status_text.empty()
        
        with result_container:
            st.error(f"**Error**: {str(e)}")
            st.info("Please try again or check the system logs for more details.")
        logger.error(f"Unexpected error: {e}")

def render_footer():
    """Render footer with helpful information"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Speed Tips:**
        - Cached queries are instant
        - Use specific department or label names
        - Include keywords like 'bucket', 'dept:', 'label:'
        """)
    
    with col2:
        st.markdown("""
        **Supported Formats:**
        - PDF documents
        - Text files (.txt, .md)
        - JSON metadata files
        - Bucket configuration files
        """)
    
    with col3:
        st.markdown("""
        **Maintenance:**
        - Rebuild embeddings after uploading new documents
        - Clear cache if experiencing issues
        - Check performance metrics in sidebar
        """)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Render components
    render_sidebar()
    render_main_content()
    render_footer()

if __name__ == "__main__":
    main()