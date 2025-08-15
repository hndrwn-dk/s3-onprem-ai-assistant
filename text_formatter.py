#!/usr/bin/env python3
"""
Text formatter for improving readability of PDF-extracted text
"""

import re

def smart_format_text(text: str, max_length: int = 800) -> str:
    """
    Intelligently format PDF-extracted text for human readability
    """
    if not text:
        return ""
    
    # Take the text portion we want
    text = text[:max_length * 2]  # Get more text to work with
    
    # Step 1: Fix common PDF extraction issues
    # Remove excessive whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Step 2: Add spaces around common patterns
    # Add space before capital letters that follow lowercase (camelCase fixes)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Add space around numbers and letters
    text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
    
    # Step 3: Fix technical terms and commands
    # Add spaces around common technical terms
    technical_terms = [
        'API', 'POST', 'GET', 'PUT', 'DELETE', 'HTTP', 'HTTPS', 'JSON', 'XML',
        'admin', 'config', 'hsctl', 'bucket', 'purge', 'delete', 'restore',
        'CLI', 'GUI', 'URL', 'URI', 'ID', 'UUID'
    ]
    
    for term in technical_terms:
        # Add space before term if preceded by letter/number
        pattern = rf'([a-zA-Z0-9]){term}'
        text = re.sub(pattern, rf'\1 {term}', text, flags=re.IGNORECASE)
        
        # Add space after term if followed by letter/number
        pattern = rf'{term}([a-zA-Z0-9])'
        text = re.sub(pattern, rf'{term} \1', text, flags=re.IGNORECASE)
    
    # Step 4: Fix command line patterns
    # Add space around command separators
    text = re.sub(r'([a-zA-Z])#', r'\1 #', text)
    text = re.sub(r'#([a-zA-Z])', r'# \1', text)
    
    # Add space around equals signs in commands
    text = re.sub(r'([a-zA-Z])=', r'\1 = ', text)
    text = re.sub(r'=([a-zA-Z])', r'= \1', text)
    
    # Step 5: Fix sentence boundaries
    # Add space after periods if followed by letter
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    
    # Add space after colons
    text = re.sub(r':([a-zA-Z])', r': \1', text)
    
    # Step 6: Fix common word boundaries
    # Common words that get stuck together
    common_fixes = [
        (r'withthe', 'with the'),
        (r'ofthe', 'of the'),
        (r'inthe', 'in the'),
        (r'tothe', 'to the'),
        (r'onthe', 'on the'),
        (r'forthe', 'for the'),
        (r'andthe', 'and the'),
        (r'whenthe', 'when the'),
        (r'ifthe', 'if the'),
        (r'thisthe', 'this the'),
        (r'thatthe', 'that the'),
        (r'bythe', 'by the'),
        (r'fromthe', 'from the'),
        (r'underthe', 'under the'),
        (r'throughthe', 'through the'),
    ]
    
    for pattern, replacement in common_fixes:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Step 7: Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Step 8: Truncate to desired length at word boundary
    if len(text) > max_length:
        text = text[:max_length]
        # Find last complete word
        last_space = text.rfind(' ')
        if last_space > max_length * 0.8:  # Don't cut too much
            text = text[:last_space]
    
    return text

def format_document_snippet(doc, doc_number: int) -> str:
    """
    Format a single document snippet for display
    """
    src = doc.metadata.get("source", "unknown")
    filename = src.split('\\')[-1].split('/')[-1]  # Get just filename
    
    # Use smart formatting
    content = smart_format_text(doc.page_content, max_length=600)
    
    return f"""
📄 Document {doc_number}: {filename}
{'─' * 60}
{content}...

"""

def extract_key_info(text: str, query: str) -> str:
    """
    Extract the most relevant sentences from the text based on query
    """
    # Split into sentences (rough)
    sentences = re.split(r'[.!?]+', text)
    
    # Score sentences based on query terms
    query_terms = query.lower().split()
    scored_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:  # Skip very short sentences
            continue
            
        score = 0
        sentence_lower = sentence.lower()
        
        for term in query_terms:
            if term in sentence_lower:
                score += sentence_lower.count(term)
        
        if score > 0:
            scored_sentences.append((score, sentence))
    
    # Return top sentences
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    top_sentences = [sent[1] for sent in scored_sentences[:3]]
    
    return '. '.join(top_sentences) if top_sentences else text[:400]