# bucket_index.py - Pre-indexed bucket search for instant results

import os
import re
from collections import defaultdict
from config import FLATTENED_TXT_PATH, DOCS_PATH
from utils import logger

class BucketIndex:
    def __init__(self):
        self.dept_index = defaultdict(list)
        self.label_index = defaultdict(list)
        self.name_index = defaultdict(list)
        self.all_lines = []
        self.build_index()
    
    def build_index(self):
        """Build search indexes from bucket metadata"""
        txt_file = FLATTENED_TXT_PATH
        if not os.path.exists(txt_file):
            txt_file = os.path.join(DOCS_PATH, "sample_bucket_metadata_converted.txt")
        
        if not os.path.exists(txt_file):
            logger.warning(f"Bucket metadata file not found: {txt_file}")
            return
        
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    self.all_lines.append((line_num, line))
                    line_lower = line.lower()
                    
                    # Index departments
                    dept_matches = re.findall(r'dept(?:artment)?:?\s*(\w+)', line_lower)
                    for dept in dept_matches:
                        self.dept_index[dept].append((line_num, line))
                    
                    # Index labels
                    label_matches = re.findall(r'label:?\s*(\w+)', line_lower)
                    for label in label_matches:
                        self.label_index[label].append((line_num, line))
                    
                    # Index bucket names
                    name_matches = re.findall(r'(?:bucket|name):?\s*([a-zA-Z0-9\-_]+)', line_lower)
                    for name in name_matches:
                        self.name_index[name].append((line_num, line))
            
            logger.info(f"Bucket index built: {len(self.all_lines)} lines, "
                       f"{len(self.dept_index)} departments, "
                       f"{len(self.label_index)} labels")
        except Exception as e:
            logger.error(f"Failed to build bucket index: {e}")
    
    def search_by_dept(self, dept: str) -> list:
        """Search buckets by department"""
        return self.dept_index.get(dept.lower(), [])
    
    def search_by_label(self, label: str) -> list:
        """Search buckets by label"""
        return self.label_index.get(label.lower(), [])
    
    def search_by_name(self, name: str) -> list:
        """Search buckets by name"""
        return self.name_index.get(name.lower(), [])
    
    def quick_search(self, query: str) -> str:
        """Fast search for common bucket queries"""
        query_lower = query.lower()
        results = []
        
        # Department search
        dept_match = re.search(r'dept(?:artment)?:?\s*(\w+)', query_lower)
        if dept_match:
            dept = dept_match.group(1)
            dept_results = self.search_by_dept(dept)
            if dept_results:
                results.extend(dept_results)
        
        # Label search
        label_match = re.search(r'label:?\s*(\w+)', query_lower)
        if label_match:
            label = label_match.group(1)
            label_results = self.search_by_label(label)
            if label_results:
                results.extend(label_results)
        
        # General keyword search
        if not results:
            keywords = re.findall(r'\b(\w+)\b', query_lower)
            for keyword in keywords:
                if len(keyword) > 2:  # Skip short words
                    for line_num, line in self.all_lines:
                        if keyword in line.lower():
                            results.append((line_num, line))
                            if len(results) >= 10:  # Limit results
                                break
                    if results:
                        break
        
        if results:
            # Remove duplicates and format
            unique_results = list(dict.fromkeys(results))[:10]
            return '\n'.join([f"Line {num}: {line}" for num, line in unique_results])
        
        return ""

# Global bucket index
bucket_index = BucketIndex()