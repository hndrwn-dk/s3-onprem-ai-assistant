#!/usr/bin/env python3
"""
Test script to verify bucket query logic fix
"""

import sys
import os
sys.path.append('.')

def test_bucket_index_logic():
    """Test that operational queries skip bucket metadata search"""
    from bucket_index import BucketIndex
    
    bucket_index = BucketIndex()
    
    # Test operational queries (should skip bucket metadata)
    operational_queries = [
        'how to purge bucket in Cloudian Hyperstore',
        'steps to delete bucket', 
        'configure bucket settings',
        'bucket setup procedure',
        'how do I create a bucket',
        'bucket management process',
        'enable bucket versioning',
        'disable bucket logging'
    ]
    
    # Test metadata queries (should use bucket metadata if available)
    metadata_queries = [
        'show all buckets under dept: engineering',
        'list buckets with label: archive', 
        'find bucket sales',
        'display engineering buckets',
        'get all buckets'
    ]
    
    print("=== Testing Operational Queries (should skip bucket metadata) ===")
    operational_failures = 0
    for query in operational_queries:
        result = bucket_index.quick_search(query)
        is_skipped = not bool(result)
        status = "✓ SKIP (correct)" if is_skipped else "✗ SEARCH (incorrect)"
        print(f"{status}: {query}")
        if not is_skipped:
            operational_failures += 1
    
    print("\n=== Testing Metadata Queries (should search bucket metadata) ===")
    metadata_hits = 0
    for query in metadata_queries:
        result = bucket_index.quick_search(query)
        has_result = bool(result)
        # Note: May not have results if no bucket metadata file exists
        status = "✓ SEARCH" if has_result else "- SKIP (no metadata file?)"
        print(f"{status}: {query}")
        if has_result:
            metadata_hits += 1
    
    print(f"\n=== Results ===")
    print(f"Operational queries correctly skipped: {len(operational_queries) - operational_failures}/{len(operational_queries)}")
    print(f"Metadata queries with results: {metadata_hits}/{len(metadata_queries)}")
    
    if operational_failures == 0:
        print("✓ SUCCESS: All operational queries correctly skip bucket metadata search!")
        print("  These queries will now proceed to vector search for PDF content.")
        return True
    else:
        print("✗ FAILURE: Some operational queries incorrectly used bucket metadata search!")
        return False

if __name__ == "__main__":
    success = test_bucket_index_logic()
    sys.exit(0 if success else 1)