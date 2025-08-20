from rest_framework import serializers

from lms.apps.attachments.models import Attachment


class BaseAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = (
            "id", "attachment_type", "file_type", "content_type", "object_id",
            "name", "original_name", "extension", "alt", "url", "size",)
