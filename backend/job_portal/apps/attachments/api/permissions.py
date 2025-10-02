from rest_framework import permissions

from job_portal.apps.attachments.models import Attachment


class IsAttachmentOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj: Attachment):
        return request.user == obj.uploaded_by
