# api.py (v3.0.0) - Unified query engine with streaming and hybrid providers

import json
import os

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from config import API_KEY, CORS_ORIGINS, VALID_SEARCH_MODES
from conversation import ConversationMemory
from llm_factory import provider_health
from model_cache import ModelCache
from prompts import SYSTEM_ASSISTANT
from query_engine import ask, prepare_query, suggest_follow_ups, summarize_document
from response_cache import response_cache
from utils import logger, timing_decorator
from validation import ValidationError

app = FastAPI(title="S3 On-Prem AI Assistant API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str
    search_mode: str | None = None
    conversation: list[dict] | None = None
    generate_follow_ups: bool = True


class CitationModel(BaseModel):
    filename: str
    excerpt: str
    score: float = 0.0
    origin: str = "vector"
    page: int | None = None


class QueryResponse(BaseModel):
    answer: str
    source: str
    response_time: float
    citations: list[CitationModel] = Field(default_factory=list)
    follow_ups: list[str] = Field(default_factory=list)
    rewritten_query: str | None = None


class SummarizeRequest(BaseModel):
    filename: str


def verify_api_key(x_api_key: str | None = Header(default=None)):
    if API_KEY:
        if not x_api_key or x_api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")


def _memory_from_request(req: QueryRequest) -> ConversationMemory | None:
    if not req.conversation:
        return None
    return ConversationMemory.from_dicts(req.conversation)


@app.on_event("startup")
async def startup_event():
    """Pre-load models on startup"""
    logger.info("Pre-loading models...")
    try:
        ModelCache.get_llm()
    except Exception as exc:
        logger.warning("LLM preload failed: %s", exc)

    preload_vector = os.getenv("PRELOAD_VECTOR", "0").lower() in ("1", "true", "yes")
    if preload_vector:
        try:
            ModelCache.get_vector_store()
            logger.info("Vector store preloaded successfully")
        except Exception as exc:
            logger.warning("Vector store preload failed: %s", exc)
    else:
        logger.info("Vector store preload skipped (set PRELOAD_VECTOR=1 to enable)")

    logger.info("Startup initialization completed")


@app.get("/health")
async def health_check():
    """Provider, index, and cache health. Secrets are never returned."""
    health = provider_health()
    status = "healthy" if health.get("ok") else "degraded"
    return {
        "status": status,
        "provider": health,
        "cache_stats": response_cache.get_stats(),
        "load_times": ModelCache.get_load_times(),
    }


@app.post("/ask", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
@timing_decorator
def ask_question(req: QueryRequest):
    if req.search_mode and req.search_mode not in VALID_SEARCH_MODES:
        raise HTTPException(
            status_code=400,
            detail=f"search_mode must be one of: {', '.join(VALID_SEARCH_MODES)}",
        )
    try:
        result = ask(
            req.question,
            search_mode=req.search_mode,
            memory=_memory_from_request(req),
            generate_follow_ups=req.generate_follow_ups,
        )
        return QueryResponse(**result.to_dict())
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/ask/stream", dependencies=[Depends(verify_api_key)])
def ask_question_stream(req: QueryRequest):
    if req.search_mode and req.search_mode not in VALID_SEARCH_MODES:
        raise HTTPException(
            status_code=400,
            detail=f"search_mode must be one of: {', '.join(VALID_SEARCH_MODES)}",
        )

    def event_stream():
        try:
            memory = _memory_from_request(req)
            prepared = prepare_query(
                req.question, search_mode=req.search_mode, memory=memory
            )
            yield _sse(
                {
                    "event": "meta",
                    "source": prepared.source,
                    "citations": [item.to_dict() for item in prepared.citations],
                    "rewritten_query": prepared.rewritten_query,
                }
            )
            if prepared.cached_answer is not None:
                yield _sse({"event": "token", "token": prepared.cached_answer})
                yield _sse(
                    {
                        "event": "done",
                        "answer": prepared.cached_answer,
                        "follow_ups": [],
                    }
                )
                return

            from llm_factory import get_llm_client

            llm = get_llm_client()
            collected = []
            for token in llm.stream(prepared.prompt, system=SYSTEM_ASSISTANT):
                collected.append(token)
                yield _sse({"event": "token", "token": token})
            answer = "".join(collected).strip()
            if prepared.use_cache and answer:
                response_cache.set(prepared.question, answer, prepared.source)
            follow_ups = []
            if req.generate_follow_ups:
                follow_ups = suggest_follow_ups(req.question, answer)
            yield _sse({"event": "done", "answer": answer, "follow_ups": follow_ups})
        except ValidationError as exc:
            yield _sse({"event": "error", "detail": str(exc)})
        except Exception as exc:
            logger.error("Stream error: %s", exc)
            yield _sse({"event": "error", "detail": str(exc)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/summarize", dependencies=[Depends(verify_api_key)])
def summarize(req: SummarizeRequest):
    try:
        summary = summarize_document(req.filename)
        return {"filename": req.filename, "summary": summary}
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Summarize error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


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


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=True)}\n\n"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
