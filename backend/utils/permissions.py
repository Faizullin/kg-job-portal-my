from django.core.exceptions import PermissionDenied
from rest_framework import permissions


class AbstractIsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user


class AbstractIsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to everyone, but require authentication for write operations.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions require authentication
        return request.user and request.user.is_authenticated


class AbstractHasGroupPermission(permissions.BasePermission):
    """
    Custom permission to check if user belongs to specific groups.
    """

    def __init__(self, required_groups=None):
        self.required_groups = required_groups or []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superuser has all permissions
        if request.user.is_superuser:
            return True

        # Check if user belongs to any of the required groups
        user_groups = request.user.groups.all()
        return any(group.name in self.required_groups for group in user_groups)


def HasSpecificPermission(required_permissions):
    """
    Factory function to create permission classes for specific permissions.
    Usage: permission_classes = [HasSpecificPermission(['app.add_model'])]
    """

    class PermissionClass(permissions.BasePermission):
        def has_permission(self, request, view):
            print("required_permissions", required_permissions)
            if not request.user or not request.user.is_authenticated:
                return False

            # Superuser has all permissions
            if request.user.is_superuser:
                return True

            # Check if user has all required permissions
            return all(request.user.has_perm(perm) for perm in required_permissions)

    return PermissionClass


class AbstractHasSpecificPermission(permissions.BasePermission):
    """
    Custom permission to check for specific user permissions.
    This class is deprecated - use HasSpecificPermission() factory function instead.
    """

    def __init__(self, required_permissions=None):
        self.required_permissions = required_permissions or []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superuser has all permissions
        if request.user.is_superuser:
            return True

        # Check if user has all required permissions
        return all(request.user.has_perm(perm) for perm in self.required_permissions)


class AbstractPermissionRequiredMixin:
    """
    Mixin to require specific permissions for views.
    """

    permission_required = None

    def dispatch(self, request, *args, **kwargs):
        if self.permission_required:
            if not request.user.has_perm(self.permission_required):
                raise PermissionDenied("You don't have permission to access this resource.")

        return super().dispatch(request, *args, **kwargs)


class AbstractGroupRequiredMixin:
    """
    Mixin to require specific group membership for views.
    """

    group_required = None

    def dispatch(self, request, *args, **kwargs):
        if self.group_required:
            if not request.user.groups.filter(name=self.group_required).exists():
                raise PermissionDenied("You don't have permission to access this resource.")

        return super().dispatch(request, *args, **kwargs)


class AbstractOwnerRequiredMixin:
    """
    Mixin to require object ownership for views.
    """

    owner_field = 'user'  # Field name that contains the owner

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if hasattr(obj, self.owner_field):
            owner = getattr(obj, self.owner_field)
            if owner != request.user and not request.user.is_staff:
                raise PermissionDenied("You don't have permission to access this resource.")

        return super().dispatch(request, *args, **kwargs)


def has_permission(user, permission_name):
    """
    Check if a user has a specific permission.
    
    Args:
        user: User object to check
        permission_name (str): Name of the permission to check
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.has_perm(permission_name)


def has_group(user, group_name):
    """
    Check if a user belongs to a specific group.
    
    Args:
        user: User object to check
        group_name (str): Name of the group to check
        
    Returns:
        bool: True if user belongs to group, False otherwise
    """
    if not user or not user.is_authenticated:
        return False

    return user.groups.filter(name=group_name).exists()


def is_owner(user, obj, owner_field='user'):
    """
    Check if a user is the owner of an object.
    
    Args:
        user: User object to check
        obj: Object to check ownership of
        owner_field (str): Field name that contains the owner
        
    Returns:
        bool: True if user is owner, False otherwise
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if hasattr(obj, owner_field):
        owner = getattr(obj, owner_field)
        return owner == user

    return False


class HasClientProfile(permissions.BasePermission):
    """Permission to check if user has a client profile."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        try:
            return hasattr(request.user, 'job_portal_profile') and hasattr(request.user.job_portal_profile,
                                                                           'client_profile')
        except:
            return False


class HasServiceProviderProfile(permissions.BasePermission):
    """Permission to check if user has a service provider profile."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        try:
            return hasattr(request.user, 'job_portal_profile') and hasattr(request.user.job_portal_profile,
                                                                           'service_provider_profile')
        except:
            return False
