import hashlib
from typing import Any

from django.core.cache import cache


def cache_key_generator(prefix: str, *args, **kwargs) -> str:
    """
    Generate a consistent cache key from prefix and arguments.
    
    Args:
        prefix (str): Cache key prefix
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
        
    Returns:
        str: Generated cache key
    """
    key_parts = [prefix]

    # Add positional arguments
    for arg in args:
        key_parts.append(str(arg))

    # Add keyword arguments (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}:{value}")

    # Create hash for long keys
    key_string = "_".join(key_parts)
    if len(key_string) > 200:  # Redis key length limit
        return f"{prefix}_{hashlib.md5(key_string.encode()).hexdigest()}"

    return key_string


def get_cache(key: str, default: Any = None) -> Any:
    """
    Get value from cache with default fallback.
    
    Args:
        key (str): Cache key
        default: Default value if key not found
        
    Returns:
        Cached value or default
    """
    return cache.get(key, default)


def set_cache(key: str, value: Any, timeout: int = 300) -> None:
    """
    Set value in cache with timeout.
    
    Args:
        key (str): Cache key
        value: Value to cache
        timeout (int): Cache timeout in seconds (default: 5 minutes)
    """
    cache.set(key, value, timeout)


def delete_cache(key: str) -> None:
    """
    Delete specific key from cache.
    
    Args:
        key (str): Cache key to delete
    """
    cache.delete(key)
