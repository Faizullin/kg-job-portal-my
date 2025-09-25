from rest_framework import permissions


def HasSpecificPermission(required_permissions: list[str]):
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
