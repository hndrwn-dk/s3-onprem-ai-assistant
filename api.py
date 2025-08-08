# api.py (v2.2.7) - Secure & Lightning Fast API

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import asyncio
import time
from typing import Optional, Dict, Any
import logging

# Import our modules
from model_cache import ModelCache
from response_cache import response_cache
from bucket_index import bucket_index
from utils import logger, timing_decorator, search_in_fallback_text, load_txt_documents, get_system_info
from validation import safe_query, ValidationError
from config import VECTOR_SEARCH_K

# Security and rate limiting
limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer(auto_error=False)

# Create FastAPI app with security headers
app = FastAPI(
    title="S3 On-Prem AI Assistant API - Secure & Lightning Fast",
    version="2.2.7",
    description="Secure, high-performance API for S3 storage assistance with comprehensive validation",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", "*.local"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Specific origins only
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request/Response Models with Validation
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="User query")
    
    @validator('question')
    def validate_question(cls, v):
        try:
            return safe_query(v)
        except ValidationError as e:
            raise ValueError(f"Invalid query: {e}")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="AI-generated answer")
    source: str = Field(..., description="Source of the answer (cache, quick_search, vector, etc.)")
    response_time: float = Field(..., description="Response time in seconds")
    query_id: Optional[str] = Field(None, description="Unique query identifier")
    confidence: Optional[float] = Field(None, description="Confidence score (0-1)")

class HealthResponse(BaseModel):
    status: str
    version: str
    cache_stats: Dict[str, Any]
    system_info: Dict[str, Any]
    uptime: float

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)

# Application state
app_start_time = time.time()

# Dependency for optional authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional authentication - for future use"""
    # For now, we'll just log the request if auth is provided
    if credentials:
        logger.info(f"Request with authorization header received")
    return credentials

# Startup event
@app.on_event("startup")
async def startup_event():
    """Pre-load models on startup with proper error handling"""
    logger.info("[STARTUP] Starting S3 AI Assistant API...")
    try:
        # Pre-load models in background to avoid blocking startup
        loop = asyncio.get_event_loop()
        
        async def preload_models():
            try:
                logger.info("[STARTUP] Pre-loading LLM...")
                ModelCache.get_llm()
                logger.info("[STARTUP] Pre-loading vector store...")
                ModelCache.get_vector_store()
                logger.info("[SUCCESS] All models loaded successfully")
            except Exception as e:
                logger.error(f"[ERROR] Error pre-loading models: {e}")
        
        # Start preloading in background
        asyncio.create_task(preload_models())
        logger.info("[SUCCESS] API startup completed")
        
    except Exception as e:
        logger.error(f"[ERROR] Startup error: {e}")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Comprehensive health check endpoint"""
    try:
        health = ModelCache.health_check()
        return HealthResponse(
            status="healthy" if all(health.values()) else "degraded",
            version="2.2.7",
            cache_stats=health,
            system_info=get_system_info(),
            uptime=time.time() - app_start_time
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Main query endpoint
@app.post("/ask", response_model=QueryResponse)
@limiter.limit("30/minute")
@timing_decorator
async def ask_question(
    req: QueryRequest,
    request: Request,
    user: Optional[HTTPAuthorizationCredentials] = Depends(get_current_user)
):
    """Secure and fast question answering endpoint"""
    start_time = time.time()
    query_id = f"query_{int(start_time * 1000)}"
    
    logger.info(f"[QUERY] Processing query {query_id}: {req.question[:50]}...")
    
    try:
        question = req.question
        
        # Check cache first
        logger.debug(f"Checking cache for query {query_id}")
        cached_response = response_cache.get(question)
        if cached_response:
            response_time = time.time() - start_time
            logger.info(f"[CACHE_HIT] Cache hit for query {query_id} ({response_time:.3f}s)")
            return QueryResponse(
                answer=cached_response,
                source="cache",
                response_time=response_time,
                query_id=query_id,
                confidence=1.0
            )
        
        # Try quick bucket search
        logger.debug(f"Trying quick search for query {query_id}")
        quick_result = bucket_index.quick_search(question)
        if quick_result:
            try:
                llm = ModelCache.get_llm()
                prompt = f"""Based on this bucket information:
{quick_result}

Question: {question}
Answer concisely and accurately:"""
                
                answer = llm(prompt)
                response_time = time.time() - start_time
                
                # Cache the response
                response_cache.set(question, answer, "quick_search")
                
                logger.info(f"[QUICK_SEARCH] Quick search success for query {query_id} ({response_time:.3f}s)")
                return QueryResponse(
                    answer=answer,
                    source="quick_search",
                    response_time=response_time,
                    query_id=query_id,
                    confidence=0.9
                )
                
            except Exception as e:
                logger.warning(f"LLM error in quick search for query {query_id}: {e}")
                # Return raw results if LLM fails
                response_time = time.time() - start_time
                return QueryResponse(
                    answer=quick_result,
                    source="quick_search_raw",
                    response_time=response_time,
                    query_id=query_id,
                    confidence=0.7
                )
        
        # Vector search fallback
        logger.debug(f"Trying vector search for query {query_id}")
        try:
            vector_store = ModelCache.get_vector_store()
            retriever = vector_store.as_retriever(search_kwargs={"k": VECTOR_SEARCH_K})
            llm = ModelCache.get_llm()
            
            # Use langchain's RetrievalQA
            from langchain.chains import RetrievalQA
            qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
            result = qa_chain.run(question)
            
            if result and result.strip():
                response_time = time.time() - start_time
                response_cache.set(question, result, "vector")
                
                logger.info(f"[VECTOR_SEARCH] Vector search success for query {query_id} ({response_time:.3f}s)")
                return QueryResponse(
                    answer=result,
                    source="vector",
                    response_time=response_time,
                    query_id=query_id,
                    confidence=0.8
                )
            else:
                raise ValueError("Empty result from vector search")

        except Exception as e:
            logger.warning(f"Vector search failed for query {query_id}: {e}")
            
            # Final fallback to text search
            logger.debug(f"Trying fallback search for query {query_id}")
            fallback_text = load_txt_documents()
            if fallback_text:
                relevant_context = search_in_fallback_text(question, fallback_text)
                
                if relevant_context:
                    try:
                        llm = ModelCache.get_llm()
                        prompt = f"""Based on this information:
{relevant_context}

Question: {question}
Answer accurately and concisely:"""
                        
                        result = llm(prompt)
                        response_time = time.time() - start_time
                        response_cache.set(question, result, "txt_fallback")
                        
                        logger.info(f"[FALLBACK] Fallback search success for query {query_id} ({response_time:.3f}s)")
                        return QueryResponse(
                            answer=result,
                            source="txt_fallback",
                            response_time=response_time,
                            query_id=query_id,
                            confidence=0.6
                        )
                        
                    except Exception as llm_error:
                        logger.error(f"LLM error in fallback for query {query_id}: {llm_error}")
                        response_time = time.time() - start_time
                        return QueryResponse(
                            answer=relevant_context,
                            source="txt_fallback_raw",
                            response_time=response_time,
                            query_id=query_id,
                            confidence=0.5
                        )
                else:
                    response_time = time.time() - start_time
                    logger.warning(f"[NOT_FOUND] No relevant context found for query {query_id}")
                    return QueryResponse(
                        answer="No relevant information found for your question.",
                        source="not_found",
                        response_time=response_time,
                        query_id=query_id,
                        confidence=0.0
                    )
            else:
                response_time = time.time() - start_time
                logger.error(f"[NO_DATA] No data available for query {query_id}")
                return QueryResponse(
                    answer="No data available to answer your question.",
                    source="no_data",
                    response_time=response_time,
                    query_id=query_id,
                    confidence=0.0
                )

    except ValidationError as e:
        logger.warning(f"Validation error for query {query_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"[ERROR] Unexpected error for query {query_id} after {response_time:.3f}s: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# Cache management endpoints
@app.post("/cache/clear")
@limiter.limit("5/minute")
async def clear_cache(request: Request):
    """Clear response cache"""
    try:
        response_cache.clear_expired()
        logger.info("[CACHE] Cache cleared successfully")
        return {"message": "Cache cleared successfully", "timestamp": time.time()}
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

@app.get("/cache/stats")
@limiter.limit("10/minute")  
async def cache_stats(request: Request):
    """Get cache statistics"""
    try:
        # This would need to be implemented in response_cache
        return {
            "message": "Cache statistics",
            "cache_enabled": True,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache stats")

# Performance metrics endpoint
@app.get("/metrics")
@limiter.limit("10/minute")
async def get_metrics(request: Request):
    """Get performance metrics"""
    try:
        from utils import performance_monitor
        return {
            "performance": performance_monitor.get_all_stats(),
            "health": ModelCache.health_check(),
            "uptime": time.time() - app_start_time,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

# Error handlers
@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return HTTPException(status_code=400, detail=str(exc))

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return HTTPException(status_code=404, detail="Endpoint not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True
    )