# tests/test_response_cache.py

import os
import tempfile

from response_cache import ResponseCache


def test_get_stats_tracks_hits_and_misses():
    with tempfile.TemporaryDirectory() as tmp:
        cache = ResponseCache(cache_dir=tmp, ttl_hours=24)
        assert cache.get("missing") is None
        cache.set("hello", "world", "test")
        assert cache.get("hello") == "world"
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["entries"] == 1
        assert stats["hit_rate"] == 0.5
        assert os.path.exists(
            os.path.join(tmp, cache._get_cache_key("hello") + ".json")
        )
