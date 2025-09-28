from utils.serializers import (
    AbstractTimestampedModelSerializer,
    AbstractChoiceFieldSerializerMixin,
)
from ..models import Notification


class NotificationSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    """Serializer for Notification model."""

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'title', 'message',
            'is_read', 'read_at', 'level', 'verb', 'actor', 'target', 'created_at'
        ]
        read_only_fields = ('id', 'created_at', 'read_at')


class NotificationCreateSerializer(AbstractTimestampedModelSerializer):
    """Serializer for creating notifications."""

    class Meta:
        model = Notification
        fields = [
            'recipient', 'title', 'message', 'level', 'verb', 'actor', 'target'
        ]


class NotificationUpdateSerializer(AbstractTimestampedModelSerializer):
    """Serializer for updating notification read status."""

    class Meta:
        model = Notification
        fields = ['is_read', 'read_at']
