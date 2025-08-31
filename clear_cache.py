#!/usr/bin/env python
"""
Clear Response Cache - Remove old AI hallucinations
"""


def clear_all_caches():
    """Clear all caches to remove old AI responses"""
    print("Clearing all response caches...")

    try:
        from response_cache import response_cache

        # Clear response cache
        cache_size_before = (
            len(response_cache._cache) if hasattr(response_cache, "_cache") else 0
        )
        response_cache.clear_expired()

        # Also clear all entries (not just expired)
        if hasattr(response_cache, "_cache"):
            response_cache._cache.clear()
            print(f"Cleared {cache_size_before} cached responses")
        else:
            print("Response cache cleared")

        # Clear model cache
        try:
            from model_cache import ModelCache

            ModelCache.reset_vector_store()
            print("Model cache cleared")
        except Exception as e:
            print(f"Model cache clear warning: {e}")

        print("All caches cleared - queries will now use actual documents")

    except Exception as e:
        print(f"Cache clear failed: {e}")


def main():
    print("S3 On-Premise AI Assistant - Cache Cleaner")
    print("=" * 50)
    print("This removes old AI hallucinations from cache")
    print("Forces system to use actual vendor documentation")
    print()

    clear_all_caches()

    print("\n" + "=" * 50)
    print("Next Steps:")
    print("1. Run your query again: python s3ai_query.py 'bucketops'")
    print("2. Should now use actual Cloudian documentation")
    print("3. Or use fast search: python fast_pdf_search.py bucketops")


if __name__ == "__main__":
    main()
