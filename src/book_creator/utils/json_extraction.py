"""
JSON extraction utilities for parsing LLM responses.

Provides robust extraction of JSON objects and arrays from text,
handling nested structures, string literals with braces/brackets,
and escape sequences properly using json.JSONDecoder.
"""

import json
from typing import Optional


def extract_json_object(text: str) -> Optional[dict]:
    """
    Extract a JSON object from text, handling nested structures and string literals.
    
    Uses json.JSONDecoder().raw_decode() for robust parsing that properly
    handles escape sequences and strings containing braces.
    
    Args:
        text: Text containing a JSON object
        
    Returns:
        The extracted dictionary, or None if no valid JSON object found
    """
    start = text.find('{')
    if start == -1:
        return None
    
    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(text[start:])
        if isinstance(obj, dict):
            return obj
        return None
    except json.JSONDecodeError:
        return None


def extract_json_array(text: str) -> Optional[list]:
    """
    Extract a JSON array from text, handling nested structures and string literals.
    
    Uses json.JSONDecoder().raw_decode() for robust parsing that properly
    handles escape sequences and strings containing brackets.
    
    Args:
        text: Text containing a JSON array
        
    Returns:
        The extracted list, or None if no valid JSON array found
    """
    start = text.find('[')
    if start == -1:
        return None
    
    decoder = json.JSONDecoder()
    try:
        arr, _ = decoder.raw_decode(text[start:])
        if isinstance(arr, list):
            return arr
        return None
    except json.JSONDecodeError:
        return None
