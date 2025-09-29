from rest_framework import serializers
from utils.serializers import AbstractTimestampedModelSerializer

from ..models import Notification


class NotificationSerializer(AbstractTimestampedModelSerializer):
    """Serializer for Notification model."""

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "level",
            "verb",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "read_at",
        )


class NotificationCreateSerializer(AbstractTimestampedModelSerializer):
    """Serializer for creating notifications."""

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "title",
            "message",
            "level",
            "verb",
        ]
        read_only_fields = ["id"]


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notification read status."""

    class Meta:
        model = Notification
        fields = ["is_read"]

    def update(self, instance, validated_data):
        """Update notification with proper read_at handling."""
        is_read = validated_data.get("is_read")

        if is_read and not instance.is_read:
            # Mark as read - timestamp will be set in view
            instance.is_read = True
        elif is_read is False and instance.is_read:
            # Mark as unread
            instance.is_read = False
            instance.read_at = None

        return super().update(instance, validated_data)
