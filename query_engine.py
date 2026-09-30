# query_engine.py - Unified retrieval and generation for API, CLI, and UI

from __future__ import annotations

import concurrent.futures
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from bucket_index import bucket_index
from config import (
    DOCS_PATH,
    ENABLE_FOLLOW_UPS,
    ENABLE_QUERY_REWRITE,
    LLM_TIMEOUT_SECONDS,
    MAX_FOLLOW_UPS,
    SEARCH_MODE,
    VALID_SEARCH_MODES,
    VECTOR_SEARCH_K,
)
from conversation import ConversationMemory
from llm_factory import LLMError, get_llm_client
from prompts import (
    BUCKET_PROMPT,
    FALLBACK_PROMPT,
    FOLLOW_UP_PROMPT,
    RAG_PROMPT,
    REWRITE_PROMPT,
    SUMMARIZE_PROMPT,
    SYSTEM_ASSISTANT,
)
from response_cache import response_cache
from text_formatter import smart_format_text
from utils import (
    check_vector_index_exists,
    load_txt_documents,
    logger,
    search_in_fallback_text,
)
from validation import ValidationError, safe_filename, safe_query


@dataclass
class Citation:
    filename: str
    excerpt: str
    score: float = 0.0
    origin: str = "vector"
    page: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "filename": self.filename,
            "excerpt": self.excerpt,
            "score": round(self.score, 4),
            "origin": self.origin,
        }
        if self.page is not None:
            payload["page"] = self.page
        return payload


@dataclass
class QueryResult:
    answer: str
    source: str
    response_time: float
    citations: List[Citation] = field(default_factory=list)
    follow_ups: List[str] = field(default_factory=list)
    rewritten_query: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "source": self.source,
            "response_time": self.response_time,
            "citations": [c.to_dict() for c in self.citations],
            "follow_ups": self.follow_ups,
            "rewritten_query": self.rewritten_query,
        }


@dataclass
class PreparedQuery:
    question: str
    prompt: str
    source: str
    citations: List[Citation]
    cached_answer: Optional[str] = None
    rewritten_query: Optional[str] = None
    use_cache: bool = True


def _normalize_mode(search_mode: Optional[str]) -> str:
    mode = (search_mode or SEARCH_MODE or "auto").strip().lower()
    return mode if mode in VALID_SEARCH_MODES else "auto"


def _filename_from_source(source: str) -> str:
    if not source:
        return "unknown"
    return os.path.basename(str(source).replace("\\", "/"))


def _invoke_llm(llm, prompt: str, timeout: int = LLM_TIMEOUT_SECONDS) -> str:
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(llm.invoke, prompt, SYSTEM_ASSISTANT)
        return future.result(timeout=timeout)


def _rewrite_query(
    question: str,
    memory: Optional[ConversationMemory],
    llm_overrides: Optional[Dict[str, Any]],
) -> str:
    if not ENABLE_QUERY_REWRITE:
        return question
    if re.search(r"\b(dept|department|label|bucket)\s*:", question.lower()):
        return question
    try:
        llm = get_llm_client(llm_overrides)
        history = memory.history_text() if memory else "(none)"
        rewritten = _invoke_llm(
            llm,
            REWRITE_PROMPT.format(history=history, question=question),
            timeout=min(LLM_TIMEOUT_SECONDS, 12),
        ).strip()
        rewritten = rewritten.splitlines()[0].strip().strip('"')
        if rewritten and 3 <= len(rewritten) <= 400:
            return rewritten
    except Exception as exc:
        logger.warning("Query rewrite skipped: %s", exc)
    return question


def _keyword_citations(query: str, limit: int) -> List[Citation]:
    citations: List[Citation] = []
    try:
        from fast_search import fast_search

        for item in fast_search.search(query, max_results=limit):
            citations.append(
                Citation(
                    filename=item.get("filename", "unknown"),
                    excerpt=smart_format_text(item.get("snippet", ""), 500),
                    score=min(1.0, float(item.get("score", 0)) / 20.0),
                    origin="keyword",
                )
            )
    except Exception as exc:
        logger.warning("Keyword search skipped: %s", exc)
    return citations


def _pdf_citations(query: str, limit: int) -> List[Citation]:
    citations: List[Citation] = []
    try:
        from fast_pdf_search import collect_pdf_matches

        for item in collect_pdf_matches(query, max_results=limit):
            citations.append(
                Citation(
                    filename=item.get("file", "unknown"),
                    excerpt=smart_format_text(item.get("context", ""), 500),
                    score=min(1.0, float(item.get("relevance", 0)) / 10.0),
                    origin="pdf",
                    page=item.get("page"),
                )
            )
    except Exception as exc:
        logger.warning("PDF search skipped: %s", exc)
    return citations


def _vector_citations(query: str, limit: int) -> List[Citation]:
    citations: List[Citation] = []
    if not check_vector_index_exists():
        return citations
    try:
        from model_cache import ModelCache

        vector_store = ModelCache.get_vector_store()
        if vector_store is None:
            return citations
        try:
            pairs = vector_store.similarity_search_with_score(query, k=limit)
            docs = []
            for doc, score in pairs:
                docs.append((doc, float(score)))
        except Exception:
            docs = [
                (doc, 0.5) for doc in vector_store.similarity_search(query, k=limit)
            ]

        for doc, score in docs:
            # FAISS L2: lower is better. Convert to a 0-1-ish relevance.
            relevance = 1.0 / (1.0 + max(score, 0.0)) if score is not None else 0.5
            citations.append(
                Citation(
                    filename=_filename_from_source(doc.metadata.get("source", "")),
                    excerpt=smart_format_text(doc.page_content, 600),
                    score=relevance,
                    origin="vector",
                    page=doc.metadata.get("page"),
                )
            )
    except Exception as exc:
        logger.warning("Vector search skipped: %s", exc)
    return citations


def hybrid_retrieve(query: str, limit: int = VECTOR_SEARCH_K) -> List[Citation]:
    """Merge vector, keyword, and PDF hits; keep the strongest unique excerpts."""
    merged: List[Citation] = []
    merged.extend(_vector_citations(query, limit))
    merged.extend(_keyword_citations(query, limit))
    merged.extend(_pdf_citations(query, limit))

    unique: List[Citation] = []
    seen = set()
    for item in sorted(merged, key=lambda c: c.score, reverse=True):
        key = (item.filename, item.excerpt[:80])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
        if len(unique) >= max(limit, 5):
            break
    return unique


def _context_from_citations(citations: List[Citation]) -> str:
    blocks = []
    for index, item in enumerate(citations, 1):
        page = f" (page {item.page})" if item.page is not None else ""
        blocks.append(
            f"[{index}] {item.filename}{page} ({item.origin})\n{item.excerpt}"
        )
    return "\n\n".join(blocks)


def _parse_follow_ups(raw: str) -> List[str]:
    lines = []
    for line in (raw or "").splitlines():
        cleaned = re.sub(r"^[\s\-\*\d\.\)\(]+", "", line).strip().strip('"')
        if cleaned:
            lines.append(cleaned)
        if len(lines) >= MAX_FOLLOW_UPS:
            break
    return lines


def suggest_follow_ups(
    question: str,
    answer: str,
    llm_overrides: Optional[Dict[str, Any]] = None,
) -> List[str]:
    if not ENABLE_FOLLOW_UPS or not answer:
        return []
    try:
        llm = get_llm_client(llm_overrides)
        raw = _invoke_llm(
            llm,
            FOLLOW_UP_PROMPT.format(
                count=MAX_FOLLOW_UPS, question=question, answer=answer[:1200]
            ),
            timeout=min(LLM_TIMEOUT_SECONDS, 15),
        )
        return _parse_follow_ups(raw)
    except Exception as exc:
        logger.warning("Follow-up generation skipped: %s", exc)
        return []


def _bucket_citations(raw: str) -> List[Citation]:
    citations = []
    for line in raw.splitlines():
        excerpt = line.strip()
        if excerpt:
            citations.append(
                Citation(
                    filename="bucket-metadata",
                    excerpt=excerpt[:500],
                    score=1.0,
                    origin="bucket",
                )
            )
    return citations[: VECTOR_SEARCH_K * 2]


def prepare_query(
    question: str,
    search_mode: Optional[str] = None,
    memory: Optional[ConversationMemory] = None,
    llm_overrides: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
) -> PreparedQuery:
    question = safe_query(question)
    mode = _normalize_mode(search_mode)
    history = memory.history_text() if memory else "(none)"
    skip_cache = bool(memory and memory.has_history())
    cache_enabled = use_cache and not skip_cache

    if cache_enabled:
        cached = response_cache.get(question)
        if cached:
            return PreparedQuery(
                question=question,
                prompt="",
                source="cache",
                citations=[],
                cached_answer=cached,
                use_cache=True,
            )

    if mode in ("auto", "bucket"):
        quick = bucket_index.quick_search(question)
        if quick:
            return PreparedQuery(
                question=question,
                prompt=BUCKET_PROMPT.format(context=quick, question=question),
                source="quick_search",
                citations=_bucket_citations(quick),
                use_cache=cache_enabled,
            )
        if mode == "bucket":
            return PreparedQuery(
                question=question,
                prompt="",
                source="not_found",
                citations=[],
                cached_answer="No matching bucket metadata found for that query.",
                use_cache=False,
            )

    search_query = question
    rewritten = None
    if mode in ("auto", "vector"):
        search_query = _rewrite_query(question, memory, llm_overrides)
        rewritten = search_query if search_query != question else None

    citations: List[Citation] = []
    source = "not_found"
    prompt = ""

    if mode == "fast_text":
        citations = _keyword_citations(question, VECTOR_SEARCH_K)
        citations.extend(_pdf_citations(question, VECTOR_SEARCH_K))
        fallback = load_txt_documents()
        extra = search_in_fallback_text(question, fallback) if fallback else ""
        if extra:
            citations.append(
                Citation(
                    filename="flattened-text",
                    excerpt=smart_format_text(extra, 800),
                    score=0.4,
                    origin="text",
                )
            )
        if citations:
            source = "fast_text"
            prompt = FALLBACK_PROMPT.format(
                context=_context_from_citations(citations), question=question
            )
    elif mode == "vector":
        citations = _vector_citations(search_query, VECTOR_SEARCH_K)
        if citations:
            source = "vector_llm"
            prompt = RAG_PROMPT.format(
                history=history,
                question=question,
                context=_context_from_citations(citations),
            )
    else:
        citations = hybrid_retrieve(search_query, VECTOR_SEARCH_K)
        if citations:
            source = "hybrid"
            prompt = RAG_PROMPT.format(
                history=history,
                question=question,
                context=_context_from_citations(citations),
            )
        else:
            fallback = load_txt_documents()
            extra = search_in_fallback_text(question, fallback) if fallback else ""
            if extra:
                source = "txt_fallback"
                citations = [
                    Citation(
                        filename="flattened-text",
                        excerpt=smart_format_text(extra, 800),
                        score=0.4,
                        origin="text",
                    )
                ]
                prompt = FALLBACK_PROMPT.format(context=extra, question=question)

    if not prompt:
        return PreparedQuery(
            question=question,
            prompt="",
            source="not_found",
            citations=[],
            cached_answer="No relevant information found for your question.",
            rewritten_query=rewritten,
            use_cache=False,
        )

    return PreparedQuery(
        question=question,
        prompt=prompt,
        source=source,
        citations=citations,
        rewritten_query=rewritten,
        use_cache=cache_enabled,
    )


def _result_from_prepared(
    prepared: PreparedQuery,
    answer: str,
    started: float,
    follow_ups: Optional[List[str]] = None,
) -> QueryResult:
    if prepared.use_cache and prepared.source != "cache":
        response_cache.set(prepared.question, answer, prepared.source)
    return QueryResult(
        answer=answer,
        source=prepared.source,
        response_time=time.time() - started,
        citations=prepared.citations,
        follow_ups=follow_ups or [],
        rewritten_query=prepared.rewritten_query,
    )


def ask(
    question: str,
    search_mode: Optional[str] = None,
    memory: Optional[ConversationMemory] = None,
    llm_overrides: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
    generate_follow_ups: bool = True,
) -> QueryResult:
    started = time.time()
    prepared = prepare_query(
        question,
        search_mode=search_mode,
        memory=memory,
        llm_overrides=llm_overrides,
        use_cache=use_cache,
    )
    if prepared.cached_answer is not None:
        return QueryResult(
            answer=prepared.cached_answer,
            source=prepared.source,
            response_time=time.time() - started,
            citations=prepared.citations,
            follow_ups=[],
            rewritten_query=prepared.rewritten_query,
        )

    llm = get_llm_client(llm_overrides)
    try:
        answer = _invoke_llm(llm, prepared.prompt)
        if not answer:
            raise LLMError("Empty LLM response")
    except (LLMError, concurrent.futures.TimeoutError) as exc:
        logger.warning("LLM failed (%s); returning retrieved excerpts", exc)
        snippets = _context_from_citations(prepared.citations) or str(exc)
        return _result_from_prepared(
            prepared,
            snippets,
            started,
            follow_ups=[],
        )

    follow_ups = (
        suggest_follow_ups(question, answer, llm_overrides)
        if generate_follow_ups
        else []
    )
    return _result_from_prepared(prepared, answer, started, follow_ups=follow_ups)


def stream_ask(
    question: str,
    search_mode: Optional[str] = None,
    memory: Optional[ConversationMemory] = None,
    llm_overrides: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
) -> Iterator[str]:
    """Yield answer tokens. Caller should collect the full answer for follow-ups."""
    prepared = prepare_query(
        question,
        search_mode=search_mode,
        memory=memory,
        llm_overrides=llm_overrides,
        use_cache=use_cache,
    )
    if prepared.cached_answer is not None:
        yield prepared.cached_answer
        return

    llm = get_llm_client(llm_overrides)
    collected: List[str] = []
    try:
        for token in llm.stream(prepared.prompt, system=SYSTEM_ASSISTANT):
            collected.append(token)
            yield token
    except LLMError as exc:
        fallback = _context_from_citations(prepared.citations) or str(exc)
        yield fallback
        collected = [fallback]

    answer = "".join(collected).strip()
    if prepared.use_cache and answer:
        response_cache.set(prepared.question, answer, prepared.source)


def summarize_document(
    filename: str,
    llm_overrides: Optional[Dict[str, Any]] = None,
    content: Optional[str] = None,
) -> str:
    safe_name = safe_filename(filename)
    text = content
    if text is None:
        path = os.path.join(DOCS_PATH, safe_name)
        if not os.path.isfile(path):
            raise ValidationError(f"Document not found: {safe_name}")
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            text = handle.read()
    if not text.strip():
        raise ValidationError("Document is empty")
    llm = get_llm_client(llm_overrides)
    return _invoke_llm(
        llm,
        SUMMARIZE_PROMPT.format(filename=safe_name, content=text[:12000]),
    )


def summarize_citations(
    citations: List[Citation],
    llm_overrides: Optional[Dict[str, Any]] = None,
) -> str:
    if not citations:
        raise ValidationError("No retrieved content to summarize")
    blob = _context_from_citations(citations)
    return summarize_document("retrieved-context", llm_overrides, content=blob)
