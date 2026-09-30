#!/usr/bin/env python
"""
s3ai_query.py - S3 AI Query Interface
Uses the same hybrid retrieval engine as the API and web UI.
"""

import argparse
import sys
import time

from query_engine import ask
from validation import ValidationError


def main_query(query, search_mode="auto"):
    """Run a question through the unified query engine."""
    print(f"Query: '{query}'")
    print("-" * 50)
    start_time = time.time()
    result = ask(query, search_mode=search_mode, generate_follow_ups=False)
    elapsed = time.time() - start_time

    print(f"Source: {result.source}")
    print(f"Time: {result.response_time:.2f}s (wall {elapsed:.2f}s)")
    if result.rewritten_query:
        print(f"Rewritten search: {result.rewritten_query}")
    print()
    print(result.answer)

    if result.citations:
        print()
        print("---")
        print("Sources:")
        for item in result.citations:
            page = f" page {item.page}" if item.page is not None else ""
            print(f"- {item.filename}{page} [{item.origin}]")
            print(f"  {item.excerpt[:180]}")
    return result.answer


def main():
    parser = argparse.ArgumentParser(
        description="S3 On-Premise AI Assistant - unified RAG query"
    )
    parser.add_argument("question", nargs="+", help="Question to ask")
    parser.add_argument(
        "--mode",
        choices=["auto", "bucket", "vector", "fast_text"],
        default="auto",
        help="Search mode (default: auto)",
    )
    args = parser.parse_args()
    query = " ".join(args.question)

    print("S3 On-Premise AI Assistant")
    print("=" * 50)
    print("Hybrid search over your vendor documentation")
    print()

    try:
        main_query(query, search_mode=args.mode)
    except ValidationError as exc:
        print(f"Invalid query: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
