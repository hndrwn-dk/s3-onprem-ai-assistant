# s3ai_query.py (v2.2.6) - Super Fast CLI

import sys
import os
import time
from model_cache import ModelCache
from response_cache import response_cache
from bucket_index import bucket_index
from langchain.chains import RetrievalQA
from config import VECTOR_SEARCH_K, LLM_TIMEOUT_SECONDS, VECTOR_LOAD_TIMEOUT_SECONDS
from utils import logger, timing_decorator

@timing_decorator
def main():
    if len(sys.argv) < 2:
        print("Usage: python s3ai_query.py <your-question>")
        print("Example: python s3ai_query.py \"show all buckets under dept: engineering\"")
        return
    
    query = " ".join(sys.argv[1:])
    print(f"Query: {query}")
    
    start_time = time.time()
    
    # Check cache first
    print("[Checking cache...]")
    cached_response = response_cache.get(query)
    if cached_response:
        print(f"[Cache Hit] Found in {time.time() - start_time:.2f} seconds")
        print("Answer:", cached_response)
        return
    
    # Try quick bucket search
    print("[Quick bucket search...]")
    quick_result = bucket_index.quick_search(query)
    if quick_result:
        print(f"[Quick Search Hit] Found in {time.time() - start_time:.2f} seconds")
        print("[Bucket Matches]")
        print(quick_result)
        
        # Use LLM to format the answer
        try:
            import concurrent.futures
            def format_with_llm():
                llm = ModelCache.get_llm()
                prompt = f"Based on this bucket information:\n{quick_result}\n\nQuestion: {query}\nAnswer:"
                return llm(prompt)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(format_with_llm)
                answer = fut.result(timeout=LLM_TIMEOUT_SECONDS)
            print(f"\n[AI Response] Total time: {time.time() - start_time:.2f} seconds")
            print("Answer:", answer)
            
            # Cache the response
            response_cache.set(query, answer, "quick_search")
            return
        except concurrent.futures.TimeoutError:
            print("[LLM Timeout] Returning raw matches from quick search")
            print("Answer:")
            print(quick_result)
            response_cache.set(query, quick_result, "quick_search_timeout_raw")
            return
        except Exception as e:
            print(f"LLM error: {e}")
            print("Answer:")
            print(quick_result)
            response_cache.set(query, quick_result, "quick_search_raw")
            return
    
    # Vector search
    print("[Vector search...]")
    try:
        import concurrent.futures
        # Load vector store (bypass ModelCache to avoid threading issues)
        print("[Vector store: loading...]")
        vector_load_start = time.time()
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        from config import VECTOR_INDEX_PATH, EMBED_MODEL
        
        print("[Loading embeddings directly...]")
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL,
            model_kwargs={"device": "cpu"}
        )
        print("[Loading FAISS index...]")
        vector_store = FAISS.load_local(VECTOR_INDEX_PATH, embeddings)
        print(f"[Vector store: loaded in {time.time() - vector_load_start:.2f}s]")
        if vector_store is None:
            raise RuntimeError("Vector store not available")
        
        # Build retriever
        retriever = vector_store.as_retriever(search_kwargs={"k": VECTOR_SEARCH_K})
        
        # Retrieve docs with timeout
        print("[Retrieval: fetching relevant documents...]")
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            fut_docs = ex.submit(retriever.get_relevant_documents, query)
            docs = fut_docs.result(timeout=LLM_TIMEOUT_SECONDS)
        
        if not docs:
            print("[No relevant documents found]")
            return
        
        # Skip LLM processing for now - show snippets directly
        print(f"[Vector Search Success] Found {len(docs)} relevant documents in {time.time() - start_time:.2f} seconds")
        print("[Note: Showing document snippets directly - LLM processing disabled due to hanging issue]")
        
        # Show snippets immediately
        print("Relevant document snippets:")
        snippets = []
        for i, doc in enumerate(docs, 1):
            src = doc.metadata.get("source", "unknown")
            text = doc.page_content[:500].replace('\n', ' ')
            snippets.append(f"[{i}] {src}: {text}")
        print("\n\n".join(snippets))
    except concurrent.futures.TimeoutError as e:
        # Determine which operation timed out based on context
        current_time = time.time()
        if 'vector_load_start' in locals() and current_time - vector_load_start > VECTOR_LOAD_TIMEOUT_SECONDS - 5:
            print(f"[Vector Load Timeout] Vector store loading exceeded {VECTOR_LOAD_TIMEOUT_SECONDS}s timeout.")
            print("This can happen with large indices. Try:")
            print("1. Set VECTOR_LOAD_TIMEOUT_SECONDS to a higher value (e.g., 300)")
            print("2. Check available system memory")
            print("3. Consider rebuilding with smaller chunks: python build_embeddings_all.py")
        else:
            print(f"[Operation Timeout] Operation exceeded the configured timeout.")
            print("Check vector store availability and LLM readiness.")
    except Exception as e:
        print(f"[Vector Search Failed] {e}")
        print("Try rebuilding embeddings: python build_embeddings_all.py")

if __name__ == "__main__":
    main()