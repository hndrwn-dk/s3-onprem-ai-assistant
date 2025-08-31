# bucket_index.py - Pre-indexed bucket search for instant results

import os
import re
from collections import defaultdict
from config import (
    FLATTENED_TXT_PATH,
    DOCS_PATH,
    QUICK_SEARCH_MAX_RESULTS,
    QUICK_SEARCH_ENABLE_KEYWORD_FALLBACK,
)
from utils import logger


class BucketIndex:
    def __init__(self):
        self.dept_index = defaultdict(list)
        self.label_index = defaultdict(list)
        self.name_index = defaultdict(list)
        self.all_lines = []
        self.enabled = bool(FLATTENED_TXT_PATH)
        self.build_index()

    def build_index(self):
        """Build search indexes from bucket metadata"""
        if not self.enabled:
            logger.info("Bucket index disabled (FLATTENED_TXT_PATH not set)")
            return

        txt_file = FLATTENED_TXT_PATH
        if not os.path.exists(txt_file):
            logger.warning(f"Bucket metadata file not found: {txt_file}")
            self.enabled = False
            return

        dept_pattern = re.compile(r'dept(?:artment)?\s*:?\s*"?([\w\-\s]+)"?')
        label_pattern = re.compile(r'label\s*:?\s*"?([\w\-:\.]+)"?')
        name_pattern = re.compile(r'(?:bucket|name)\s*:?\s*"?([a-zA-Z0-9_\-\.]+)"?')

        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    self.all_lines.append((line_num, line))
                    line_lower = line.lower()

                    # Index departments
                    for dept in dept_pattern.findall(line_lower):
                        self.dept_index[dept.strip()].append((line_num, line))

                    # Index labels
                    for label in label_pattern.findall(line_lower):
                        self.label_index[label.strip()].append((line_num, line))

                    # Index bucket names
                    for name in name_pattern.findall(line_lower):
                        self.name_index[name.strip()].append((line_num, line))

            logger.info(
                f"Bucket index built: {len(self.all_lines)} lines, "
                f"{len(self.dept_index)} departments, "
                f"{len(self.label_index)} labels"
            )
        except Exception as e:
            logger.error(f"Failed to build bucket index: {e}")
            self.enabled = False

    def search_by_dept(self, dept: str) -> list:
        """Search buckets by department"""
        return self.dept_index.get(dept.lower(), [])

    def search_by_label(self, label: str) -> list:
        """Search buckets by label"""
        return self.label_index.get(label.lower(), [])

    def search_by_name(self, name: str) -> list:
        """Search buckets by name"""
        return self.name_index.get(name.lower(), [])

    def _is_bucket_query(self, query_lower: str) -> bool:
        """Heuristic: only treat as bucket query if explicit bucket metadata hints exist (requires colon)."""
        return (
            re.search(r"\bdept(?:artment)?\s*:", query_lower) is not None
            or re.search(r"\blabel\s*:", query_lower) is not None
            or re.search(r"\bbucket(?:\s*name)?\s*:", query_lower) is not None
        )

    def quick_search(self, query: str) -> str:
        """Fast search for common bucket queries. Only triggers for explicit bucket metadata patterns."""
        if not self.enabled:
            return ""

        query_lower = query.lower()
        if not self._is_bucket_query(query_lower):
            # Do not engage quick search for general questions
            return ""

        results = []

        # Department search
        dept_match = re.search(r'dept(?:artment)?\s*:?\s*"?([\w\-\s]+)"?', query_lower)
        if dept_match:
            dept = dept_match.group(1)
            dept_results = self.search_by_dept(dept)
            if dept_results:
                results.extend(dept_results)

        # Label search
        label_match = re.search(r'label\s*:?\s*"?([\w\-:\.]+)"?', query_lower)
        if label_match:
            label = label_match.group(1)
            label_results = self.search_by_label(label)
            if label_results:
                results.extend(label_results)

        # Keyword fallback only if explicitly enabled and we already determined it's a bucket query
        if not results and QUICK_SEARCH_ENABLE_KEYWORD_FALLBACK:
            keywords = re.findall(r"\b([\w\-:\.]+)\b", query_lower)
            for keyword in keywords:
                if len(keyword) > 2:  # Skip short words
                    for line_num, line in self.all_lines:
                        if keyword in line.lower():
                            results.append((line_num, line))
                            if len(results) >= QUICK_SEARCH_MAX_RESULTS:
                                break
                    if results:
                        break

        if results:
            # Remove duplicates and format
            unique_results = list(dict.fromkeys(results))[:QUICK_SEARCH_MAX_RESULTS]
            return "\n".join([f"Line {num}: {line}" for num, line in unique_results])

        return ""


# Global bucket index
bucket_index = BucketIndex()
