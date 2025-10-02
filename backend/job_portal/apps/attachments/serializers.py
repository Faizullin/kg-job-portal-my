from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Attachment

UserModel = get_user_model()


class AttachmentSerializer(serializers.ModelSerializer):
    """Generic serializer for attachments."""

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = [
            "id",
            "original_filename",
            "file_url",
            "size",
            "file_type",
            "mime_type",
            "uploaded_by",
            "description",
            "is_public",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None
