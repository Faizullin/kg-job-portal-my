from django.core.exceptions import PermissionDenied
from rest_framework import permissions


def HasSpecificPermission(required_permissions):
    """
    Factory function to create permission classes for specific permissions.
    Usage: permission_classes = [HasSpecificPermission(['app.add_model'])]
    """

    class PermissionClass(permissions.BasePermission):
        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False

            # Superuser has all permissions
            if request.user.is_superuser:
                return True

            # Check if user has all required permissions
            return all(request.user.has_perm(perm) for perm in required_permissions)

    return PermissionClass


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
