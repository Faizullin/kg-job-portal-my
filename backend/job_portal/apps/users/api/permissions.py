from rest_framework import permissions


class HasMasterProfile(permissions.BasePermission):
    """Permission to check if user has a master profile."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        try:
            return hasattr(request.user, 'master_profile')
        except:
            return False


class HasEmployerProfile(permissions.BasePermission):
    """Permission to check if user has an employer profile."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        try:
            return hasattr(request.user, 'employer_profile')
        except:
            return False
