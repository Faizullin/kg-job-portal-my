from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsAuthenticatedWithBlocked(permissions.IsAuthenticated):
    """
    Custom permission to check if user is authenticated and not blocked.
    Replaces api_users.permissions.IsAuthenticatedWithBlocked
    """
    
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not super().has_permission(request, view):
            return False
        
        # Check if user is blocked
        if hasattr(request.user, 'blocked') and request.user.blocked:
            return False
        
        return True

    """
    Custom permission to allow owners of an object or staff to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if request.user.is_staff:
            return True
        
        # Check if the user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        # Default to False if ownership can't be determined
        return False