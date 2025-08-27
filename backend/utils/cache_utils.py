from django.core.cache import cache
from typing import Any, Optional, Union
import hashlib
import json


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


def clear_cache_pattern(pattern: str) -> None:
    """
    Clear cache keys matching pattern (Redis only).
    
    Args:
        pattern (str): Pattern to match keys (e.g., "user_*")
    """
    try:
        # This works with Redis backend
        cache.delete_pattern(pattern)
    except AttributeError:
        # Fallback for other backends
        pass


def cache_function_result(
    prefix: str, 
    timeout: int = 300, 
    key_args: Optional[list] = None,
    key_kwargs: Optional[list] = None
):
    """
    Decorator to cache function results.
    
    Args:
        prefix (str): Cache key prefix
        timeout (int): Cache timeout in seconds
        key_args (list): List of arg indices to include in cache key
        key_kwargs (list): List of kwarg names to include in cache key
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_args = []
            cache_kwargs = {}
            
            if key_args:
                cache_args = [args[i] for i in key_args if i < len(args)]
            
            if key_kwargs:
                cache_kwargs = {k: v for k, v in kwargs.items() if k in key_kwargs}
            
            cache_key = cache_key_generator(prefix, *cache_args, **cache_kwargs)
            
            # Try to get from cache
            result = get_cache(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            set_cache(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def cache_view_response(
    prefix: str = "view",
    timeout: int = 300,
    include_user: bool = True,
    include_query_params: bool = False
):
    """
    Decorator to cache view responses.
    
    Args:
        prefix (str): Cache key prefix
        timeout (int): Cache timeout in seconds
        include_user (bool): Include user ID in cache key
        include_query_params (bool): Include query parameters in cache key
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Generate cache key
            key_parts = [prefix, request.path]
            
            if include_user and hasattr(request, 'user') and request.user.is_authenticated:
                key_parts.append(f"user_{request.user.id}")
            
            if include_query_params and request.GET:
                # Sort query params for consistent keys
                query_string = "&".join(f"{k}={v}" for k, v in sorted(request.GET.items()))
                key_parts.append(f"query_{hashlib.md5(query_string.encode()).hexdigest()}")
            
            cache_key = "_".join(key_parts)
            
            # Try to get from cache
            result = get_cache(cache_key)
            if result is not None:
                return result
            
            # Execute view and cache result
            result = view_func(request, *args, **kwargs)
            set_cache(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator
