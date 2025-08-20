from rest_framework.permissions import IsAuthenticated


class IsAuthenticatedWithBlocked(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        if not is_authenticated:
            return False
        return not request.user.blocked


class IsPaidUser(IsAuthenticatedWithBlocked):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_paid()
