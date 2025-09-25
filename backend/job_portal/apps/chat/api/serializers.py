from rest_framework import serializers
from utils.serializers import (
    AbstractTimestampedModelSerializer,
    AbstractChoiceFieldSerializerMixin,
)
from ..models import ChatRoom, ChatMessage, ChatParticipant




class MessageSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    sender_name = serializers.SerializerMethodField()
    message_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'chat_room', 'sender', 'sender_name', 'content', 'message_type',
            'message_type_display', 'attachment', 'attachment_name', 'attachment_size',
            'is_read', 'read_at', 'created_at'
        ]
    
    def get_sender_name(self, obj):
        if obj.sender:
            return f"{obj.sender.first_name} {obj.sender.last_name}".strip() or obj.sender.username
        return "Unknown User"
    
    def get_message_type_display(self, obj):
        return self.get_choice_display(obj, 'message_type')






class WebSocketInfoSerializer(serializers.Serializer):
    """Serializer for WebSocket connection information."""
    websocket_url = serializers.CharField(help_text='Base WebSocket URL')
    temp_token = serializers.CharField(help_text='Temporary token for WebSocket connection')
    user_id = serializers.IntegerField(help_text='User ID for WebSocket connection')


# Mobile-Optimized Serializers
class ChatConversationSerializer(AbstractTimestampedModelSerializer):
    """Mobile-optimized serializer for chat conversation list."""
    other_participant_name = serializers.SerializerMethodField()
    other_participant_avatar = serializers.SerializerMethodField()
    other_participant_online = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    service_category = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'title', 'chat_type', 'other_participant_name', 'other_participant_avatar',
            'other_participant_online', 'last_message_preview', 'last_message_time',
            'service_category', 'unread_count', 'is_active', 'created_at'
        ]
    
    def get_other_participant_name(self, obj):
        """Get the other participant's name (not current user)."""
        request = self.context.get('request')
        if not request or not request.user:
            return "Unknown"
        
        other_participant = obj.participants.exclude(id=request.user.id).first()
        if other_participant:
            return f"{other_participant.first_name} {other_participant.last_name}".strip() or other_participant.username
        return "Unknown"
    
    def get_other_participant_avatar(self, obj):
        """Get the other participant's avatar."""
        request = self.context.get('request')
        if not request or not request.user:
            return None
        
        other_participant = obj.participants.exclude(id=request.user.id).first()
        if other_participant and hasattr(other_participant, 'photo_url'):
            return other_participant.photo_url
        return None
    
    def get_other_participant_online(self, obj):
        """Check if other participant is online."""
        request = self.context.get('request')
        if not request or not request.user:
            return False
        
        other_participant = obj.participants.exclude(id=request.user.id).first()
        if other_participant:
            participant_status = obj.participant_status.filter(user=other_participant).first()
            return participant_status.is_online if participant_status else False
        return False
    
    def get_last_message_preview(self, obj):
        """Get preview of last message."""
        last_message = obj.messages.filter(is_deleted=False).last()
        if last_message:
            return last_message.content[:100] + "..." if len(last_message.content) > 100 else last_message.content
        return ""
    
    def get_last_message_time(self, obj):
        """Get formatted last message time."""
        if obj.last_message_at:
            return obj.last_message_at
        return obj.created_at
    
    def get_service_category(self, obj):
        """Get service category from related order."""
        if obj.order and obj.order.service_subcategory:
            return obj.order.service_subcategory.name
        return "General Chat"
    
    def get_unread_count(self, obj):
        """Get unread count for current user."""
        request = self.context.get('request')
        if not request or not request.user:
            return 0
        
        participant_status = obj.participant_status.filter(user=request.user).first()
        return participant_status.unread_count if participant_status else 0


class ChatConversationDetailSerializer(AbstractTimestampedModelSerializer):
    """Mobile-optimized serializer for chat conversation details with messages."""
    messages = serializers.SerializerMethodField()
    other_participant_info = serializers.SerializerMethodField()
    service_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'title', 'chat_type', 'messages', 'other_participant_info',
            'service_info', 'is_active', 'created_at'
        ]
    
    def get_messages(self, obj):
        """Get messages for this conversation."""
        messages = obj.messages.filter(is_deleted=False).order_by('created_at')[:50]
        return MessageSerializer(messages, many=True, context=self.context).data
    
    def get_other_participant_info(self, obj):
        """Get other participant's detailed info."""
        request = self.context.get('request')
        if not request or not request.user:
            return {}
        
        other_participant = obj.participants.exclude(id=request.user.id).first()
        if not other_participant:
            return {}
        
        participant_status = obj.participant_status.filter(user=other_participant).first()
        
        return {
            'id': other_participant.id,
            'name': f"{other_participant.first_name} {other_participant.last_name}".strip() or other_participant.username,
            'avatar': getattr(other_participant, 'photo_url', None),
            'is_online': participant_status.is_online if participant_status else False,
            'last_seen': participant_status.last_seen if participant_status else None,
        }
    
    def get_service_info(self, obj):
        """Get service information from related order."""
        if obj.order:
            return {
                'order_id': obj.order.id,
                'order_title': obj.order.title,
                'service_name': obj.order.service_subcategory.name if obj.order.service_subcategory else None,
                'service_category': obj.order.service_subcategory.category.name if obj.order.service_subcategory and obj.order.service_subcategory.category else None,
            }
        return None


class ChatSendMessageSerializer(serializers.Serializer):
    """Serializer for sending messages via mobile API."""
    message = serializers.CharField(max_length=1000, help_text='Message content')
    message_type = serializers.ChoiceField(
        choices=[('text', 'Text'), ('image', 'Image'), ('file', 'File')],
        default='text',
        help_text='Message type'
    )
    attachment = serializers.FileField(required=False, allow_null=True, help_text='File attachment')