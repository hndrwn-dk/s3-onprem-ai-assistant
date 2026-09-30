# tests/test_query_engine.py

from unittest.mock import patch

from conversation import ConversationMemory
from query_engine import (
    Citation,
    PreparedQuery,
    _parse_follow_ups,
    hybrid_retrieve,
    prepare_query,
)


def test_parse_follow_ups_strips_numbering():
    raw = "1. How do I purge a bucket?\n- What about versioning?\n* IAM policies?"
    parsed = _parse_follow_ups(raw)
    assert parsed[0] == "How do I purge a bucket?"
    assert "What about versioning?" in parsed


@patch("query_engine.response_cache.get", return_value="cached-answer")
def test_prepare_query_uses_cache(_mock_get):
    prepared = prepare_query("how to list buckets", use_cache=True)
    assert isinstance(prepared, PreparedQuery)
    assert prepared.source == "cache"
    assert prepared.cached_answer == "cached-answer"


@patch("query_engine.response_cache.get", return_value=None)
@patch("query_engine.bucket_index.quick_search", return_value="")
@patch("query_engine._rewrite_query", side_effect=lambda q, m, o: q)
@patch("query_engine.hybrid_retrieve", return_value=[])
@patch("query_engine.load_txt_documents", return_value="")
def test_prepare_query_not_found(_txt, _hybrid, _rewrite, _bucket, _cache):
    prepared = prepare_query("no such topic at all")
    assert prepared.source == "not_found"
    assert prepared.cached_answer


@patch("query_engine.response_cache.get", return_value=None)
@patch("query_engine.bucket_index.quick_search")
def test_prepare_query_bucket_mode(mock_quick, _cache):
    mock_quick.return_value = "Line 1: dept: engineering bucket: eng-logs"
    prepared = prepare_query("dept: engineering", search_mode="bucket")
    assert prepared.source == "quick_search"
    assert "engineering" in prepared.prompt
    assert prepared.citations


def test_conversation_history_text():
    memory = ConversationMemory(max_turns=4)
    memory.add_user("first")
    memory.add_assistant("reply")
    memory.add_user("second")
    text = memory.history_text(exclude_last_user=True)
    assert "first" in text
    assert "second" not in text


@patch("query_engine._vector_citations", return_value=[])
@patch("query_engine._keyword_citations")
@patch("query_engine._pdf_citations", return_value=[])
def test_hybrid_retrieve_merges_keyword(_pdf, mock_keyword, _vector):
    mock_keyword.return_value = [
        Citation(
            filename="guide.txt", excerpt="purge bucket", score=0.8, origin="keyword"
        )
    ]
    hits = hybrid_retrieve("purge", limit=3)
    assert hits
    assert hits[0].filename == "guide.txt"
