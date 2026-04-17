"""
Simple TTL Cache for API responses
Prevents excessive API calls and respects free tier rate limits.
"""
import time
import functools
from typing import Any, Callable, TypeVar, Optional

T = TypeVar("T")
_cache: dict[str, tuple[Any, float]] = {}


def ttl_cache(ttl_seconds: int = 300) -> Callable:
    """
    Decorator cache with TTL for async functions.
    ttl_seconds: how long to cache results (default 5 minutes)
    
    Example:
        @ttl_cache(ttl_seconds=600)
        async def get_weather(city: str) -> str:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create cache key from function name, args, and kwargs
            key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            now = time.time()
            
            # Check if cached value exists and is not expired
            if key in _cache:
                value, expires_at = _cache[key]
                if now < expires_at:
                    return value
            
            # Call actual function
            result = await func(*args, **kwargs)
            
            # Store in cache with expiration time
            _cache[key] = (result, now + ttl_seconds)
            return result
        
        return wrapper
    return decorator


def clear_cache() -> None:
    """Clear all cached values."""
    global _cache
    _cache.clear()


def get_cache_stats() -> dict:
    """Get cache statistics."""
    return {
        "entries": len(_cache),
        "expired": sum(1 for _, (_, expires_at) in _cache.items() if time.time() > expires_at),
    }
