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