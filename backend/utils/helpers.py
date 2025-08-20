import hashlib
import json
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.utils import timezone
from django.utils.crypto import get_random_string


def generate_unique_id(length: int = 8) -> str:
    """
    Generate a unique alphanumeric ID.
    
    Args:
        length (int): Length of the ID to generate
        
    Returns:
        str: Unique alphanumeric ID
    """
    return get_random_string(length, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """
    Hash a string using the specified algorithm.
    
    Args:
        text (str): Text to hash
        algorithm (str): Hashing algorithm to use
        
    Returns:
        str: Hashed string
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    Safely load JSON data with error handling.
    
    Args:
        data (str): JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON data or default value
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = '{}') -> str:
    """
    Safely dump data to JSON string with error handling.
    
    Args:
        data: Data to serialize
        default (str): Default string if serialization fails
        
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return default


def paginate_queryset(queryset: QuerySet, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Paginate a queryset and return pagination info.
    
    Args:
        queryset: Django queryset to paginate
        page (int): Page number (1-based)
        page_size (int): Number of items per page
        
    Returns:
        Dict with pagination info and results
    """
    paginator = Paginator(queryset, page_size)
    
    try:
        page_obj = paginator.page(page)
    except:
        page_obj = paginator.page(1)
    
    return {
        'results': page_obj.object_list,
        'pagination': {
            'page': page_obj.number,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        }
    }


def search_queryset(queryset: QuerySet, search_term: str, search_fields: List[str]) -> QuerySet:
    """
    Search a queryset using multiple fields.
    
    Args:
        queryset: Django queryset to search
        search_term (str): Search term
        search_fields (List[str]): List of field names to search in
        
    Returns:
        Filtered queryset
    """
    if not search_term:
        return queryset
    
    q_objects = Q()
    for field in search_fields:
        q_objects |= Q(**{f"{field}__icontains": search_term})
    
    return queryset.filter(q_objects)


def get_client_ip(request: HttpRequest) -> str:
    """
    Get the client's IP address from the request.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request: HttpRequest) -> str:
    """
    Get the user agent from the request.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        str: User agent string
    """
    return request.META.get('HTTP_USER_AGENT', '')


def is_ajax_request(request: HttpRequest) -> bool:
    """
    Check if the request is an AJAX request.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        bool: True if AJAX request, False otherwise
    """
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
           request.content_type == 'application/json'


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted file size
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
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
    
    return text[:max_length - len(suffix)] + suffix


def generate_random_password(length: int = 12) -> str:
    """
    Generate a random password.
    
    Args:
        length (int): Length of the password
        
    Returns:
        str: Random password
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


def cache_key_generator(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from prefix and arguments.
    
    Args:
        prefix (str): Cache key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments
        
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
    
    return "_".join(key_parts)


def time_ago(dt: datetime) -> str:
    """
    Get a human-readable time ago string.
    
    Args:
        dt (datetime): Datetime to compare
        
    Returns:
        str: Time ago string
    """
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"


def is_valid_email(email: str) -> bool:
    """
    Check if an email address is valid.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def clean_phone_number(phone: str) -> str:
    """
    Clean and format a phone number.
    
    Args:
        phone (str): Phone number to clean
        
    Returns:
        str: Cleaned phone number
    """
    import re
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone)
    
    # Remove leading zeros and country code if present
    if cleaned.startswith('00'):
        cleaned = cleaned[2:]
    elif cleaned.startswith('0'):
        cleaned = cleaned[1:]
    
    return cleaned


def get_setting_value(setting_name: str, default: Any = None) -> Any:
    """
    Get a setting value with fallback to default.
    
    Args:
        setting_name (str): Name of the setting
        default: Default value if setting not found
        
    Returns:
        Setting value or default
    """
    return getattr(settings, setting_name, default)
