import secrets
from typing import Optional
from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from app.core.config import settings

# API Key security scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def generate_api_key(length: int = 32) -> str:
    """
    Generate a secure API key.
    
    Args:
        length (int): Length of the API key
        
    Returns:
        str: Generated API key
    """
    return secrets.token_urlsafe(length)

def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """
    Validate API key from request.
    
    Args:
        api_key_header (str): API key from request header
        
    Returns:
        str: API key if valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    # Skip API key validation if not configured
    if not settings.API_KEY_REQUIRED:
        return api_key_header
    
    if api_key_header == settings.API_KEY:
        return api_key_header
    
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Invalid API Key",
    )

def rate_limit(
    request_count: int = 100,
    time_window: int = 60  # seconds
) -> callable:
    """
    Create a rate limiter dependency.
    
    Args:
        request_count (int): Maximum number of requests in time window
        time_window (int): Time window in seconds
        
    Returns:
        callable: Rate limiter dependency
    """
    # In a production app, this would use Redis or another
    # distributed cache/store to track requests
    from time import time
    import threading
    
    # Simple in-memory rate limiter
    # Not suitable for production with multiple workers
    rate_limits = {}
    lock = threading.Lock()
    
    def check_rate_limit(api_key: str = Depends(get_api_key)) -> None:
        # Skip rate limiting if not configured
        if not settings.RATE_LIMIT_ENABLED:
            return None
        
        # Use IP address if no API key
        client_id = api_key or "anonymous"
        
        with lock:
            now = time()
            # Initialize or reset expired entry
            if client_id not in rate_limits or now - rate_limits[client_id]["start"] > time_window:
                rate_limits[client_id] = {
                    "start": now,
                    "count": 1
                }
                return None
            
            # Increment count if within window
            rate_limits[client_id]["count"] += 1
            
            # Check if limit exceeded
            if rate_limits[client_id]["count"] > request_count:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Try again later."
                )
    
    return check_rate_limit 