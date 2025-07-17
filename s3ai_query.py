# s3ai_query.py (v2.2.6) - Super Fast CLI

import sys
import os
import time
from model_cache import ModelCache
from response_cache import response_cache
from bucket_index import bucket_index
from langchain.chains import RetrievalQA
from config import VECTOR_SEARCH_K
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
            llm = ModelCache.get_llm()
            prompt = f"Based on this bucket information:\n{quick_result}\n\nQuestion: {query}\nAnswer:"
            answer = llm(prompt)
            print(f"\n[AI Response] Total time: {time.time() - start_time:.2f} seconds")
            print("Answer:", answer)
            
            # Cache the response
            response_cache.set(query, answer, "quick_search")
            return
        except Exception as e:
            print(f"LLM error: {e}")
            return
    
    # Vector search fallback
    print("[Vector search...]")
    try:
        vector_store = ModelCache.get_vector_store()
        retriever = vector_store.as_retriever(search_kwargs={"k": VECTOR_SEARCH_K})
        llm = ModelCache.get_llm()
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        
        result = qa_chain.run(query)
        
        if result and result.strip():
            print(f"[Vector Search Hit] Total time: {time.time() - start_time:.2f} seconds")
            print("Answer:", result)
            response_cache.set(query, result, "vector")
        else:
            print("[Vector search returned empty result]")
            
    except Exception as e:
        print(f"[Vector Search Failed] {e}")
        print("Try rebuilding embeddings: python build_embeddings_all.py")

if __name__ == "__main__":
    main()