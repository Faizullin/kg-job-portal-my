from utils.serializers import (
    AbstractTimestampedModelSerializer,
    AbstractChoiceFieldSerializerMixin,
)
from ..models import UserNotification


class NotificationSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    """Serializer for UserNotification model."""
    
    class Meta:
        model = UserNotification
        fields = [
            'id', 'user', 'title', 'message', 'notification_type',
            'is_read', 'read_at', 'order', 'bid', 'created_at'
        ]
        read_only_fields = ('id', 'created_at', 'read_at')


class NotificationCreateSerializer(AbstractTimestampedModelSerializer):
    """Serializer for creating notifications."""
    
    class Meta:
        model = UserNotification
        fields = [
            'user', 'title', 'message', 'notification_type', 'order', 'bid'
        ]


class NotificationUpdateSerializer(AbstractTimestampedModelSerializer):
    """Serializer for updating notification read status."""
    
    class Meta:
        model = UserNotification
        fields = ['is_read', 'read_at']