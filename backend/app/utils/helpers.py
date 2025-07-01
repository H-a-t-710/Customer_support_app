import os
import re
import json
import uuid
import datetime
from typing import Any, Dict, List, Optional, Union

def generate_unique_id(prefix: str = "doc") -> str:
    """
    Generate a unique ID.
    
    Args:
        prefix (str): ID prefix
        
    Returns:
        str: Unique ID
    """
    return f"{prefix}_{uuid.uuid4().hex}"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to make it safe for filesystem operations.
    
    Args:
        filename (str): Filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Replace unsafe characters
    sanitized = re.sub(r'[^\w\-\.]', '_', filename)
    return sanitized

def ensure_dir(directory: str) -> str:
    """
    Ensure a directory exists.
    
    Args:
        directory (str): Directory path
        
    Returns:
        str: Directory path
    """
    os.makedirs(directory, exist_ok=True)
    return directory

def save_json(data: Any, filepath: str) -> str:
    """
    Save data as JSON to a file.
    
    Args:
        data (Any): Data to save
        filepath (str): File path
        
    Returns:
        str: File path
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Custom JSON encoder for handling special types
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            elif isinstance(obj, uuid.UUID):
                return str(obj)
            return super().default(obj)
    
    # Save data
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, cls=CustomEncoder, ensure_ascii=False, indent=2)
    
    return filepath

def load_json(filepath: str) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        filepath (str): File path
        
    Returns:
        Any: Loaded data
    """
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        suffix (str): Suffix to add if truncated
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length].rstrip() + suffix

def format_file_size(size: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size (int): Size in bytes
        
    Returns:
        str: Formatted size
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    
    return f"{size:.2f} PB" 