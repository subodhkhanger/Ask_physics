"""
Simple in-memory caching for API responses.
"""

from functools import wraps
from typing import Any, Callable
import hashlib
import json
from cachetools import TTLCache
import logging

try:
    from .config import settings
except ImportError:
    from config import settings

logger = logging.getLogger(__name__)

# In-memory cache (TTL-based)
# For production, consider Redis
_cache = TTLCache(maxsize=100, ttl=settings.cache_ttl)


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key_data = {
        "args": args,
        "kwargs": kwargs
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cache_response(ttl: int = None):
    """
    Decorator to cache API responses.

    Args:
        ttl: Time-to-live in seconds (uses settings.cache_ttl if None)

    Usage:
        @cache_response(ttl=300)
        async def my_endpoint():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if disabled
            if not settings.cache_enabled:
                return await func(*args, **kwargs)

            # Generate cache key
            key = f"{func.__name__}:{cache_key(*args, **kwargs)}"

            # Check cache
            if key in _cache:
                logger.debug(f"Cache hit: {key}")
                return _cache[key]

            # Execute function
            logger.debug(f"Cache miss: {key}")
            result = await func(*args, **kwargs)

            # Store in cache
            _cache[key] = result

            return result

        return wrapper
    return decorator


def clear_cache():
    """Clear all cached responses."""
    _cache.clear()
    logger.info("Cache cleared")


def get_cache_stats() -> dict:
    """Get cache statistics."""
    return {
        "size": len(_cache),
        "maxsize": _cache.maxsize,
        "ttl": _cache.ttl,
        "hits": _cache.currsize if hasattr(_cache, 'currsize') else None
    }
