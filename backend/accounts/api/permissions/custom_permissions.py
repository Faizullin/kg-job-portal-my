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


class HasPermission(permissions.BasePermission):
    """
    Custom permission to check if user has a specific permission.
    Usage: permission_classes = [HasPermission('can_view_users')]
    """
    
    def __init__(self, permission_codename):
        self.permission_codename = permission_codename
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user has the required permission
        return request.user.has_perm(self.permission_codename)


class HasGroup(permissions.BasePermission):
    """
    Custom permission to check if user has a specific group.
    Usage: permission_classes = [HasGroup('admin')]
    """
    
    def __init__(self, group_name):
        self.group_name = group_name
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superusers have all groups
        if request.user.is_superuser:
            return True
        
        # Check if user has the required group
        return request.user.groups.filter(name=self.group_name).exists()


class IsOwnerOrStaff(permissions.BasePermission):
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


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow staff to perform any action, others can only read.
    """
    
    def has_permission(self, request, view):
        # Allow read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow write permissions only for staff
        return request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow owners of an object to edit it, others can only read.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        # Default to False if ownership can't be determined
        return False


class HasAnyGroup(permissions.BasePermission):
    """
    Custom permission to check if user has any of the specified groups.
    Usage: permission_classes = [HasAnyGroup(['admin', 'moderator'])]
    """
    
    def __init__(self, group_name):
        self.group_name = group_name if isinstance(group_name, list) else [group_name]
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superusers have all groups
        if request.user.is_superuser:
            return True
        
        # Check if user has any of the required groups
        return request.user.groups.filter(name__in=self.group_name).exists()


class HasAllGroups(permissions.BasePermission):
    """
    Custom permission to check if user has all of the specified groups.
    Usage: permission_classes = [HasAllGroups(['admin', 'moderator'])]
    """
    
    def __init__(self, group_name):
        self.group_name = group_name if isinstance(group_name, list) else [group_name]
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superusers have all groups
        if request.user.is_superuser:
            return True
        
        # Check if user has all of the required groups
        user_group_names = set(request.user.groups.values_list('name', flat=True))
        return set(self.group_name).issubset(user_group_names)
