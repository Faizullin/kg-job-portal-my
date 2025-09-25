from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response

from utils.cache_utils import get_cache, set_cache


class GroupRequiredMixin:
    """Mixin to require specific group membership for class-based views."""

    group_required = None

    def dispatch(self, request, *args, **kwargs):
        if self.group_required:
            if not request.user.groups.filter(name=self.group_required).exists():
                raise PermissionDenied("You don't have permission to access this resource.")

        return super().dispatch(request, *args, **kwargs)


class RateLimitMixin:
    """Mixin to implement rate limiting for class-based views."""

    max_requests = 100
    window = 3600  # 1 hour

    def dispatch(self, request, *args, **kwargs):
        # Generate rate limit key
        user_id = request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR')
        key = f"rate_limit_{user_id}"

        # Check current request count
        current_requests = get_cache(key, 0)
        if current_requests >= self.max_requests:
            return Response({
                'error': 'Rate limit exceeded. Try again later.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Increment request count
        set_cache(key, current_requests + 1, self.window)

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
