from rest_framework import serializers
from utils.serializers import (
    AbstractTimestampedModelSerializer,
    AbstractSoftDeleteModelSerializer,
    AbstractChoiceFieldSerializerMixin,
    AbstractComputedFieldSerializerMixin
)
from ..models import UserNotification, NotificationTemplate, NotificationPreference


class NotificationTemplateSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'subject',
            'message', 'short_message', 'variables', 'is_active', 'created_at'
        ]
    


class NotificationSettingSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'email_notifications', 'push_notifications', 'sms_notifications',
            'in_app_notifications', 'order_updates', 'bid_notifications', 'payment_notifications',
            'chat_notifications', 'promotional_notifications', 'system_notifications',
            'quiet_hours_start', 'quiet_hours_end', 'timezone', 'digest_frequency'
        ]


class NotificationSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    
    class Meta:
        model = UserNotification
        fields = [
            'id', 'user', 'template', 'subject', 'message', 'short_message', 'context_data',
            'related_object_type', 'related_object_id', 'status', 'priority',
            'is_read', 'read_at', 'sent_at', 'delivered_at',
            'created_at'
        ]


class NotificationCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = UserNotification
        fields = ['user', 'template', 'subject', 'message', 'short_message', 'context_data', 'related_object_type', 'related_object_id', 'priority']


class NotificationUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = UserNotification
        fields = ['is_read', 'read_at']


class NotificationSettingUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_notifications', 'push_notifications', 'sms_notifications',
            'in_app_notifications', 'order_updates', 'bid_notifications', 'payment_notifications',
            'chat_notifications', 'promotional_notifications', 'system_notifications',
            'quiet_hours_start', 'quiet_hours_end', 'timezone', 'digest_frequency'
        ]


class NotificationTemplateCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = ['name', 'notification_type', 'subject', 'message', 'short_message', 'variables', 'is_active']


class NotificationTemplateUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = ['subject', 'message', 'short_message', 'variables', 'is_active']


class NotificationSettingCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_notifications', 'push_notifications', 'sms_notifications',
            'in_app_notifications', 'quiet_hours_start', 'quiet_hours_end', 'timezone'
        ]
