from rest_framework import serializers
from utils.serializers import (
    AbstractTimestampedModelSerializer,
    AbstractSoftDeleteModelSerializer,
    AbstractChoiceFieldSerializerMixin,
    AbstractComputedFieldSerializerMixin
)
from ..models import UserNotification, NotificationTemplate, NotificationPreference, NotificationLog


class NotificationTemplateSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    notification_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'notification_type_display', 'subject',
            'message', 'short_message', 'variables', 'is_active', 'created_at'
        ]
    
    def get_notification_type_display(self, obj):
        return self.get_choice_display(obj, 'notification_type')


class NotificationSettingSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'email_notifications', 'push_notifications', 'sms_notifications',
            'in_app_notifications', 'order_updates', 'bid_notifications', 'payment_notifications',
            'chat_notifications', 'promotional_notifications', 'system_notifications',
            'quiet_hours_start', 'quiet_hours_end', 'timezone', 'digest_frequency'
        ]


class NotificationLogSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'notification', 'delivery', 'action', 'status_display',
            'details', 'error_message', 'processing_time', 'created_at'
        ]
    
    def get_status_display(self, obj):
        return self.get_choice_display(obj, 'action')


class NotificationSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    priority_display = serializers.SerializerMethodField()
    is_read_display = serializers.SerializerMethodField()
    
    class Meta:
        model = UserNotification
        fields = [
            'id', 'user', 'template', 'subject', 'message', 'short_message', 'context_data',
            'related_object_type', 'related_object_id', 'status', 'priority', 'priority_display',
            'is_read', 'is_read_display', 'read_at', 'sent_at', 'delivered_at',
            'created_at'
        ]
    
    def get_priority_display(self, obj):
        return self.get_choice_display(obj, 'priority')
    
    def get_is_read_display(self, obj):
        return "Read" if obj.is_read else "Unread"


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
