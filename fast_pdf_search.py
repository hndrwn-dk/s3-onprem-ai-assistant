#!/usr/bin/env python
"""
Fast PDF Search - Direct search without slow vector loading
Searches your actual Cloudian PDFs instantly
"""

import sys
import time
from pathlib import Path


def _extract_page_hits(reader, pdf_file, query, max_results, page_limit=None):
    results = []
    pages = reader.pages[:page_limit] if page_limit else reader.pages
    query_lower = query.lower()
    for page_num, page in enumerate(pages):
        page_text = page.extract_text() or ""
        if query_lower in page_text.lower():
            query_pos = page_text.lower().find(query_lower)
            start = max(0, query_pos - 200)
            end = min(len(page_text), query_pos + 300)
            results.append(
                {
                    "file": pdf_file.name,
                    "page": page_num + 1,
                    "context": page_text[start:end],
                    "relevance": page_text.lower().count(query_lower),
                }
            )
            if len(results) >= max_results:
                break
    return results


def collect_pdf_matches(query, max_results=5, verbose=False):
    """Return structured PDF hits without requiring vector search."""
    docs_path = Path("docs")
    if not docs_path.exists():
        return []

    pdf_files = list(docs_path.glob("*.pdf"))
    results = []
    for pdf_file in pdf_files:
        if verbose:
            print(f"Checking: {pdf_file.name}")
        try:
            try:
                import PyPDF2

                with open(pdf_file, "rb") as handle:
                    reader = PyPDF2.PdfReader(handle)
                    results.extend(
                        _extract_page_hits(
                            reader, pdf_file, query, max_results - len(results)
                        )
                    )
            except ImportError:
                import pypdf

                with open(pdf_file, "rb") as handle:
                    reader = pypdf.PdfReader(handle)
                    results.extend(
                        _extract_page_hits(
                            reader,
                            pdf_file,
                            query,
                            max_results - len(results),
                            page_limit=20,
                        )
                    )
        except Exception as exc:
            if verbose:
                print(f"  Error reading {pdf_file.name}: {exc}")
        if len(results) >= max_results:
            break

    results.sort(key=lambda item: item["relevance"], reverse=True)
    return results[:max_results]


def search_pdfs_directly(query, max_results=5):
    """Search PDFs directly without vector loading"""
    print(f"Fast PDF Search for: '{query}'")
    print("-" * 50)

    start_time = time.time()
    docs_path = Path("docs")
    if not docs_path.exists():
        return "docs/ folder not found"

    pdf_files = list(docs_path.glob("*.pdf"))
    print(f"Searching {len(pdf_files)} PDF files...")
    results = collect_pdf_matches(query, max_results=max_results, verbose=True)
    search_time = time.time() - start_time

    if not results:
        return f"No matches found for '{query}' in {len(pdf_files)} PDF files (searched in {search_time:.2f}s)"

    # Sort by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)

    # Format response
    response_parts = [
        f"Found {len(results)} matches for '{query}' in your vendor documentation:",
        f"Search completed in {search_time:.2f} seconds",
        "",
    ]

    for i, result in enumerate(results, 1):
        response_parts.append(f"{i}. **{result['file']}** (Page {result['page']})")
        response_parts.append(f"   Relevance: {result['relevance']} mentions")
        response_parts.append(f"   Context: {result['context']}")
        response_parts.append("")

    return "\n".join(response_parts)


def search_text_files(query):
    """Search text files directly"""
    print(f"Searching text files for: '{query}'")

    docs_path = Path("docs")
    txt_files = list(docs_path.glob("*.txt")) + list(docs_path.glob("*.md"))

    results = []
    for txt_file in txt_files:
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read()
                if query.lower() in content.lower():
                    # Extract context
                    query_pos = content.lower().find(query.lower())
                    start = max(0, query_pos - 200)
                    end = min(len(content), query_pos + 300)
                    context = content[start:end]

                    results.append(
                        {
                            "file": txt_file.name,
                            "context": context,
                            "relevance": content.lower().count(query.lower()),
                        }
                    )
        except Exception as e:
            print(f"Error reading {txt_file.name}: {e}")

    return results


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "bucketops"

    print("S3 On-Premise AI Assistant - Fast PDF Search")
    print("=" * 60)
    print("This searches your ACTUAL vendor documentation")
    print("No vector loading delays - instant results")
    print()

    # Search PDFs directly
    pdf_results = search_pdfs_directly(query)
    print(pdf_results)

    # Search text files
    print("\nChecking text files...")
    txt_results = search_text_files(query)
    if txt_results:
        print(f"Found {len(txt_results)} matches in text files")
        for result in txt_results:
            print(f"  • {result['file']}: {result['context'][:100]}...")
    else:
        print("No matches in text files")


if __name__ == "__main__":
    main()
