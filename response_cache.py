# response_cache.py - Response caching for instant answers

import hashlib
import json
import os
from datetime import datetime, timedelta
from config import CACHE_DIR, CACHE_TTL_HOURS
import tempfile
import threading


class ResponseCache:
    def __init__(self, cache_dir=CACHE_DIR, ttl_hours=CACHE_TTL_HOURS):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        os.makedirs(cache_dir, exist_ok=True)
        self._lock = threading.Lock()

    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()

    def get(self, query: str):
        """Get cached response if available and not expired"""
        cache_key = self._get_cache_key(query)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        if os.path.exists(cache_file):
            try:
                with self._lock:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                cached_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cached_time < self.ttl:
                    return data['response']
            except Exception:
                pass  # Ignore cache errors
        return None

    def set(self, query: str, response: str, source: str = "unknown"):
        """Cache response for future use"""
        cache_key = self._get_cache_key(query)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        data = {
            'query': query,
            'response': response,
            'source': source,
            'timestamp': datetime.now().isoformat(),
        }

        try:
            with self._lock:
                fd, tmp_path = tempfile.mkstemp(dir=self.cache_dir, suffix=".tmp")
                try:
                    with os.fdopen(fd, 'w', encoding='utf-8') as tmp_f:
                        json.dump(data, tmp_f, indent=2)
                    os.replace(tmp_path, cache_file)
                finally:
                    if os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass
        except Exception:
            pass  # Ignore cache errors

    def clear_expired(self):
        """Clear expired cache entries"""
        if not os.path.exists(self.cache_dir):
            return

        now = datetime.now()
        for file in os.listdir(self.cache_dir):
            if file.endswith('.json'):
                file_path = os.path.join(self.cache_dir, file)
                try:
                    with self._lock:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    cached_time = datetime.fromisoformat(data['timestamp'])
                    if now - cached_time > self.ttl:
                        os.remove(file_path)
                except Exception:
                    try:
                        os.remove(file_path)  # Remove corrupted cache files
                    except Exception:
                        pass

    def clear_all(self):
        """Clear all cache entries"""
        if not os.path.exists(self.cache_dir):
            return
        for file in os.listdir(self.cache_dir):
            if file.endswith('.json'):
                file_path = os.path.join(self.cache_dir, file)
                try:
                    with self._lock:
                        os.remove(file_path)
                except Exception:
                    pass


# Global cache instance
response_cache = ResponseCache()