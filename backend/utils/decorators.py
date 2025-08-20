from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response


class PermissionRequiredMixin:
    """Mixin to require specific permissions for class-based views."""
    
    permission_required = None
    
    def dispatch(self, request, *args, **kwargs):
        if self.permission_required:
            if not request.user.has_perm(self.permission_required):
                raise PermissionDenied("You don't have permission to access this resource.")
        
        return super().dispatch(request, *args, **kwargs)


class GroupRequiredMixin:
    """Mixin to require specific group membership for class-based views."""
    
    group_required = None
    
    def dispatch(self, request, *args, **kwargs):
        if self.group_required:
            if not request.user.groups.filter(name=self.group_required).exists():
                raise PermissionDenied("You don't have permission to access this resource.")
        
        return super().dispatch(request, *args, **kwargs)


class OwnerRequiredMixin:
    """Mixin to require object ownership for class-based views."""
    
    owner_field = 'user'  # Field name that contains the owner
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        
        if hasattr(obj, self.owner_field):
            owner = getattr(obj, self.owner_field)
            if owner != request.user and not request.user.is_staff:
                raise PermissionDenied("You don't have permission to access this resource.")
        
        return super().dispatch(request, *args, **kwargs)


class CacheResponseMixin:
    """Mixin to add caching to class-based views."""
    
    cache_timeout = 300  # 5 minutes default
    cache_key_prefix = None
    
    def get_cache_key(self, request, *args, **kwargs):
        """Generate cache key for the view."""
        if self.cache_key_prefix:
            return f"{self.cache_key_prefix}_{request.path}_{request.user.id if request.user.is_authenticated else 'anonymous'}"
        return f"view_{request.path}_{request.user.id if request.user.is_authenticated else 'anonymous'}"
    
    def dispatch(self, request, *args, **kwargs):
        from django.core.cache import cache
        
        # Generate cache key
        cache_key = self.get_cache_key(request, *args, **kwargs)
        
        # Try to get from cache
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return cached_response
        
        # Execute view and cache result
        response = super().dispatch(request, *args, **kwargs)
        cache.set(cache_key, response, self.cache_timeout)
        
        return response


class RateLimitMixin:
    """Mixin to implement rate limiting for class-based views."""
    
    max_requests = 100
    window = 3600  # 1 hour
    
    def dispatch(self, request, *args, **kwargs):
        from django.core.cache import cache
        from django.http import HttpResponseTooManyRequests
        
        # Generate rate limit key
        key = f"rate_limit_{request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR')}"
        
        # Check current request count
        current_requests = cache.get(key, 0)
        if current_requests >= self.max_requests:
            return HttpResponseTooManyRequests("Rate limit exceeded")
        
        # Increment request count
        cache.set(key, current_requests + 1, self.window)
        
        return super().dispatch(request, *args, **kwargs)


class LogActionMixin:
    """Mixin to log user actions for class-based views."""
    
    action_name = None
    
    def dispatch(self, request, *args, **kwargs):
        if self.action_name:
            import logging
            
            logger = logging.getLogger('user_actions')
            logger.info(f"User {request.user.id if request.user.is_authenticated else 'anonymous'} "
                       f"performed action: {self.action_name}")
        
        return super().dispatch(request, *args, **kwargs)


class ValidationMixin:
    """Mixin to validate request data for class-based views."""
    
    required_fields = None
    optional_fields = None
    
    def validate_request_data(self, request):
        """Validate request data before processing."""
        if self.required_fields:
            missing_fields = []
            for field in self.required_fields:
                if field not in request.data:
                    missing_fields.append(field)
            
            if missing_fields:
                return False, missing_fields
        
        return True, []
    
    def dispatch(self, request, *args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            is_valid, missing_fields = self.validate_request_data(request)
            if not is_valid:
                return Response({
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().dispatch(request, *args, **kwargs)


class APIViewMixin:
    """Mixin to apply common API view settings for class-based views."""
    
    permission_classes = None
    throttle_classes = None
    
    def dispatch(self, request, *args, **kwargs):
        # Apply permission classes if specified
        if self.permission_classes:
            for permission_class in self.permission_classes:
                if not permission_class().has_permission(request, self):
                    return Response({
                        'error': 'Permission denied'
                    }, status=status.HTTP_403_FORBIDDEN)
        
        # Apply throttle classes if specified
        if self.throttle_classes:
            for throttle_class in self.throttle_classes:
                throttle = throttle_class()
                if not throttle.allow_request(request, self):
                    return Response({
                        'error': 'Request throttled'
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        return super().dispatch(request, *args, **kwargs)


def method_decorator_list(*decorators):
    """
    Apply multiple decorators to a class-based view method.
    
    Usage:
        @method_decorator_list(cache_response(300), log_action('view_profile'))
        def get(self, request):
            pass
    """
    def decorator(method):
        for decorator_func in reversed(decorators):
            method = method_decorator(decorator_func)(method)
        return method
    return decorator
