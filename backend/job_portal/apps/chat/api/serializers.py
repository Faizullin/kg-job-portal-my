from rest_framework import serializers
from utils.serializers import (
    AbstractTimestampedModelSerializer,
    AbstractSoftDeleteModelSerializer,
    AbstractChoiceFieldSerializerMixin,
    AbstractComputedFieldSerializerMixin
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
    
    def get_file_size_display(self, obj):
        if obj.file_size:
            size_kb = obj.file_size / 1024
            if size_kb > 1024:
                return f"{size_kb/1024:.1f} MB"
            return f"{size_kb:.0f} KB"
        return '-'


class ChatParticipantSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    role_display = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatParticipant
        fields = [
            'id', 'chat_room', 'user', 'user_name', 'role', 'role_display',
            'joined_at', 'last_read_at', 'is_active'
        ]
    
    def get_role_display(self, obj):
        return self.get_choice_display(obj, 'role')
    
    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
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
            return f"{obj.sender.first_name} {obj.sender.last_name}"
        return "Unknown User"
    
    def get_message_type_display(self, obj):
        return self.get_choice_display(obj, 'message_type')


class ChatRoomSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    participants = ChatParticipantSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    room_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'room_type', 'room_type_display', 'order', 'participants',
            'last_message', 'unread_count', 'created_at', 'updated_at'
        ]
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'content': last_msg.content[:100] + '...' if len(last_msg.content) > 100 else last_msg.content,
                'sender': last_msg.sender.first_name if last_msg.sender else 'Unknown',
                'created_at': last_msg.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        # This would be calculated based on current user
        return 0
    
    def get_room_type_display(self, obj):
        return self.get_choice_display(obj, 'room_type')


class MessageCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['chat_room', 'content', 'message_type']


class ChatRoomCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['name', 'room_type', 'order']


class ChatParticipantCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ChatParticipant
        fields = ['chat_room', 'user', 'role']


class ChatAttachmentCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ChatAttachment
        fields = ['message', 'file_name', 'file_type', 'file_size', 'file_url', 'thumbnail_url']


class MessageUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['content', 'message_type']


class ChatRoomUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['name', 'room_type']
