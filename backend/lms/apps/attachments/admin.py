from lms.apps.core.utils.admin import BaseAdmin, admin
from .models import Attachment


@admin.register(Attachment)
class AttachmentAdmin(BaseAdmin):
    list_display = (
        "id",
        "attachment_type",
        "name",
        "size",
        "content_object",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "attachment_type")
    list_filter = ("attachment_type",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 20
