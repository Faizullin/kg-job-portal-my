from rest_framework import permissions


class JobAccessPermission(permissions.BasePermission):
    """
    Custom permission to only allow owners of a job or applicants to access it.
    Employers can manage applications for their jobs.
    """

    def has_object_permission(self, request, view, obj):
        # Assuming `obj` is a Job instance
        if request.user.is_staff:
            return True  # Admins have full access

        if hasattr(obj, 'employer_profile') and obj.employer == request.user:
            return True  # Employers can manage their own jobs

        return False  # Deny access by default"""
