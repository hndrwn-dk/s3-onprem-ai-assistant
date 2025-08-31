# api.py (v2.3.0) - Lightning Fast API with Security

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from langchain.chains import RetrievalQA
from model_cache import ModelCache
from response_cache import response_cache
from bucket_index import bucket_index
from utils import logger, timing_decorator, search_in_fallback_text, load_txt_documents
from config import VECTOR_SEARCH_K, API_KEY, CORS_ORIGINS
import time
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="S3 On-Prem AI Assistant API - Lightning Fast", version="2.3.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    source: str
    response_time: float


def verify_api_key(x_api_key: str | None = Header(default=None)):
    if API_KEY:
        if not x_api_key or x_api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.on_event("startup")
async def startup_event():
    """Pre-load models on startup"""
    logger.info("Pre-loading models...")
    try:
        ModelCache.get_llm()
    except Exception as e:
        logger.warning(f"LLM preload failed: {e}")

    # Skip vector store preload by default to avoid blocking startup (downloads)
    preload_vector = os.getenv("PRELOAD_VECTOR", "0").lower() in ("1", "true", "yes")
    if preload_vector:
        try:
            # Load vector store directly to avoid threading issues
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import FAISS
            from config import VECTOR_INDEX_PATH, EMBED_MODEL

            embeddings = HuggingFaceEmbeddings(
                model_name=EMBED_MODEL, model_kwargs={"device": "cpu"}
            )
            FAISS.load_local(VECTOR_INDEX_PATH, embeddings)
            logger.info("Vector store preloaded successfully")
        except Exception as e:
            logger.warning(f"Vector store preload failed: {e}")
    else:
        logger.info("Vector store preload skipped (set PRELOAD_VECTOR=1 to enable)")

    logger.info("Startup initialization completed")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "cache_stats": ModelCache.get_load_times()}


@app.post("/ask", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
@timing_decorator
def ask_question(req: QueryRequest):
    question = req.question.strip()
    start_time = time.time()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        # Check cache first
        cached_response = response_cache.get(question)
        if cached_response:
            return QueryResponse(
                answer=cached_response,
                source="cache",
                response_time=time.time() - start_time,
            )

        # Try quick bucket search
        quick_result = bucket_index.quick_search(question)
        if quick_result:
            llm = ModelCache.get_llm()
            prompt = f"""Based on this bucket information:
{quick_result}

Question: {question}
Answer:"""

            try:
                import concurrent.futures
                from config import LLM_TIMEOUT_SECONDS

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    fut = ex.submit(llm, prompt)
                    answer = fut.result(timeout=LLM_TIMEOUT_SECONDS)
                response_cache.set(question, answer, "quick_search")
                return QueryResponse(
                    answer=answer,
                    source="quick_search",
                    response_time=time.time() - start_time,
                )
            except concurrent.futures.TimeoutError:
                return QueryResponse(
                    answer=quick_result,
                    source="quick_search_timeout_raw",
                    response_time=time.time() - start_time,
                )
            except Exception as e:
                logger.error(f"LLM error in quick search: {e}")
                # Return raw results if LLM fails
                return QueryResponse(
                    answer=quick_result,
                    source="quick_search_raw",
                    response_time=time.time() - start_time,
                )

        # Vector search fallback
        try:
            # Load vector store directly to avoid threading issues
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import FAISS
            from config import VECTOR_INDEX_PATH, EMBED_MODEL

            embeddings = HuggingFaceEmbeddings(
                model_name=EMBED_MODEL, model_kwargs={"device": "cpu"}
            )
            vector_store = FAISS.load_local(VECTOR_INDEX_PATH, embeddings)
            if vector_store is None:
                raise RuntimeError(
                    "Vector store not available - please run 'python build_embeddings_all.py' after uploading documents"
                )
            retriever = vector_store.as_retriever(search_kwargs={"k": VECTOR_SEARCH_K})
            docs = retriever.get_relevant_documents(question)

            if docs:
                # Try LLM processing with fallback
                try:
                    # Method 1: Try direct LLM call with shorter context
                    context = "\n\n".join([d.page_content[:600] for d in docs])
                    prompt = f"""You are a technical documentation assistant. The user asked: "{question}"

Based on this information from technical documents, provide a clear, step-by-step answer:

{context}

Please provide:
1. A direct answer to the question
2. Step-by-step instructions if applicable  
3. Any important configuration details
4. Relevant commands or API calls

Answer:"""

                    llm = ModelCache.get_llm()
                    result = llm.invoke(prompt)

                    if result and result.strip():
                        response_cache.set(question, result, "vector_llm")
                        return QueryResponse(
                            answer=result,
                            source="vector_llm",
                            response_time=time.time() - start_time,
                        )
                    else:
                        raise ValueError("Empty LLM response")

                except Exception as e:
                    logger.warning(
                        f"LLM processing failed: {e}, falling back to snippets"
                    )

                    # Fallback: Format document snippets for better readability
                    from text_formatter import smart_format_text

                    snippets = []
                    for i, doc in enumerate(docs, 1):
                        src = doc.metadata.get("source", "unknown")
                        filename = src.split("\\")[-1].split("/")[-1]
                        content = smart_format_text(doc.page_content, max_length=600)
                        snippets.append(
                            f" Document {i}: {filename}\n{'-' * 60}\n{content}...\n"
                        )

                    result = "\n".join(snippets)
                    response_cache.set(question, result, "vector_snippets_fallback")
                    return QueryResponse(
                        answer=f"Found {len(docs)} relevant documents (LLM processing failed):\n\n{result}",
                        source="vector_snippets_fallback",
                        response_time=time.time() - start_time,
                    )
            else:
                raise ValueError("No relevant documents found")

        except Exception as e:
            logger.warning(f"Vector search failed: {e}")

            # Final fallback to text search
            fallback_text = load_txt_documents()
            if fallback_text:
                relevant_context = search_in_fallback_text(question, fallback_text)

                if relevant_context:
                    llm = ModelCache.get_llm()
                    prompt = f"""Based on this information:
{relevant_context}

Question: {question}
Answer:"""

                    try:
                        result = llm(prompt)
                        response_cache.set(question, result, "txt_fallback")
                        return QueryResponse(
                            answer=result,
                            source="txt_fallback",
                            response_time=time.time() - start_time,
                        )
                    except Exception as llm_error:
                        logger.error(f"LLM error in fallback: {llm_error}")
                        return QueryResponse(
                            answer=relevant_context,
                            source="txt_fallback_raw",
                            response_time=time.time() - start_time,
                        )
                else:
                    return QueryResponse(
                        answer="No relevant information found for your question.",
                        source="not_found",
                        response_time=time.time() - start_time,
                    )
            else:
                return QueryResponse(
                    answer="No data available to answer your question.",
                    source="no_data",
                    response_time=time.time() - start_time,
                )

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear-cache", dependencies=[Depends(verify_api_key)])
async def clear_cache():
    """Clear expired cache entries"""
    response_cache.clear_expired()
    return {"message": "Expired cache cleared successfully"}


@app.post("/clear-all-cache", dependencies=[Depends(verify_api_key)])
async def clear_all_cache():
    """Clear all cache entries"""
    response_cache.clear_all()
    return {"message": "All cache cleared successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
