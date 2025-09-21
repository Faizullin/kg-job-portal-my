from rest_framework import serializers
from utils.serializers import (
    AbstractTimestampedModelSerializer,
    AbstractChoiceFieldSerializerMixin,
)
from ..models import ChatRoom, ChatMessage, ChatParticipant, ChatAttachment


class ChatAttachmentSerializer(AbstractTimestampedModelSerializer):
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatAttachment
        fields = [
            'id', 'message', 'file_name', 'file_type', 'file_size', 'file_size_display',
            'file_url', 'thumbnail_url', 'created_at'
        ]
    
    def get_file_size_display(self, obj):
        if obj.file_size:
            size_kb = obj.file_size / 1024
            if size_kb > 1024:
                return f"{size_kb/1024:.1f} MB"
            return f"{size_kb:.0f} KB"
        return '-'


class ChatParticipantSerializer(AbstractTimestampedModelSerializer):
    user_name = serializers.SerializerMethodField()
    chat_room_title = serializers.CharField(source='chat_room.title', read_only=True)
    
    class Meta:
        model = ChatParticipant
        fields = [
            'id', 'chat_room', 'chat_room_title', 'user', 'user_name',
            'is_online', 'last_seen', 'unread_count', 
            'notifications_enabled', 'mute_until', 'created_at', 'updated_at'
        ]
    
    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return "Unknown User"


class MessageSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    attachments = ChatAttachmentSerializer(many=True, read_only=True)
    sender_name = serializers.SerializerMethodField()
    message_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'chat_room', 'sender', 'sender_name', 'content', 'message_type',
            'message_type_display', 'attachments', 'is_read', 'read_at', 'created_at'
        ]
    
    def get_sender_name(self, obj):
        if obj.sender:
            return f"{obj.sender.first_name} {obj.sender.last_name}".strip() or obj.sender.username
        return "Unknown User"
    
    def get_message_type_display(self, obj):
        return self.get_choice_display(obj, 'message_type')


class ChatRoomSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    participants = ChatParticipantSerializer(source='participant_status', many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    chat_type_display = serializers.SerializerMethodField()
    order_title = serializers.CharField(source='order.title', read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'title', 'chat_type', 'chat_type_display', 'order', 'order_title', 
            'participants', 'is_active', 'last_message_at', 'last_message', 'unread_count', 
            'created_at', 'updated_at'
        ]
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'content': last_msg.content[:100] + '...' if len(last_msg.content) > 100 else last_msg.content,
                'sender': f"{last_msg.sender.first_name} {last_msg.sender.last_name}".strip() or last_msg.sender.username if last_msg.sender else 'Unknown',
                'created_at': last_msg.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            participant = obj.participant_status.filter(user=request.user).first()
            return participant.unread_count if participant else 0
        return 0
    
    def get_chat_type_display(self, obj):
        return self.get_choice_display(obj, 'chat_type')


class MessageCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['chat_room', 'content', 'message_type']


class ChatRoomCreateSerializer(AbstractTimestampedModelSerializer):
    participants = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text='List of user IDs to add as participants'
    )

    class Meta:
        model = ChatRoom
        fields = ['id', 'title', 'chat_type', 'order', 'is_active', 'participants']
        read_only_fields = ['id', 'is_active']


class ChatParticipantCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ChatParticipant
        fields = ['id', 'chat_room', 'user', 'is_online', 'notifications_enabled']


class ChatAttachmentCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ChatAttachment
        fields = ['id', 'message', 'file_name', 'file_type', 'file_size', 'file_url', 'thumbnail_url']


class MessageUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'content', 'message_type']


class ChatRoomUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'title', 'chat_type', 'is_active']


class WebSocketInfoSerializer(serializers.Serializer):
    """Serializer for WebSocket connection information."""
    websocket_url = serializers.CharField(help_text='Base WebSocket URL')
    auth_required = serializers.BooleanField(help_text='Whether authentication is required')
    token_param = serializers.CharField(help_text='Token parameter name')
    connection_format = serializers.CharField(help_text='Connection URL format with placeholders')
    message_types = serializers.ListField(
        child=serializers.CharField(),
        help_text='Available message types'
    )


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
        if other_participant and other_participant.photo:
            request = self.context.get('request')
            return request.build_absolute_uri(other_participant.photo.url)
        return other_participant.photo_url if other_participant else None
    
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
            'avatar': request.build_absolute_uri(other_participant.photo.url) if other_participant.photo else other_participant.photo_url,
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
        choices=[('text', 'Text'), ('image', 'Image')],
        default='text',
        help_text='Message type'
    )
    attachment_url = serializers.URLField(required=False, allow_blank=True, help_text='Attachment URL for images')