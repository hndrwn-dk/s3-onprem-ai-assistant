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

    try:
        ModelCache.get_vector_store()
    except Exception as e:
        logger.warning(f"Vector store preload failed: {e}")

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
                answer = llm(prompt)
                response_cache.set(question, answer, "quick_search")
                return QueryResponse(
                    answer=answer,
                    source="quick_search",
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
            vector_store = ModelCache.get_vector_store()
            if vector_store is None:
                raise RuntimeError("Vector store not available")
            retriever = vector_store.as_retriever(search_kwargs={"k": VECTOR_SEARCH_K})
            llm = ModelCache.get_llm()
            qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
            result = qa_chain.run(question)

            if result and result.strip():
                response_cache.set(question, result, "vector")
                return QueryResponse(
                    answer=result,
                    source="vector",
                    response_time=time.time() - start_time,
                )
            else:
                raise ValueError("Empty result from vector search")

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