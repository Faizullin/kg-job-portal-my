from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator, get_available_image_extensions
from rest_framework import serializers

from job_portal.apps.attachments.serializers import AttachmentSerializer
from job_portal.apps.users.api.serializers import (
    PublicMasterProfileSerializer,
    UserDetailChildSerializer,
)
from utils.serializers import (
    AbstractTimestampedModelSerializer,
)

from ..models import ChatMessage, ChatParticipant, ChatRole, ChatRoom, MessageType

UserModel = get_user_model()


class ChatParticipantSerializer(serializers.ModelSerializer):
    """Serializer for chat participants."""

    user = UserDetailChildSerializer(read_only=True)

    class Meta:
        model = ChatParticipant
        fields = [
            "id",
            "user",
            "role",
            "is_online",
            "last_seen",
            "unread_count",
            "notifications_enabled",
            "mute_until",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for chat rooms."""

    participants = ChatParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "job",
            "title",
            "is_active",
            "chat_type",
            "last_message_at",
            "participants",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "last_message_at", "created_at", "updated_at"]


def add_initial_chat_room_participants(chat_room: ChatRoom, users_ids: list[int]):
    not_found_ids = []
    users = []
    for i in users_ids:
        try:
            user = UserModel.objects.get(id=i)
            users.append(user)
        except UserModel.DoesNotExist:
            not_found_ids.append(i)
    if len(not_found_ids) > 0:
        raise serializers.ValidationError(f"Following users not found: {not_found_ids}")
    chat_participants = []
    for u in users:
        c = ChatParticipant.objects.get_or_create(
            chat_room=chat_room, user=u, defaults={"role": "member"}
        )
        chat_participants.append(c)
    return chat_participants


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating chat rooms."""

    participants_users_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of user IDs to add as participants",
        required=False,
        default=list,
    )
    participants = ChatParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "title",
            "participants_users_ids",
            "participants",
            "job",
            "chat_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        participants_users_ids = validated_data.pop("participants_users_ids", [])
        chat_room = ChatRoom.objects.create(
            **validated_data,
            is_active=True,
        )
        add_initial_chat_room_participants(chat_room, participants_users_ids)
        user = self.context["request"].user
        ChatParticipant.objects.create(
            chat_room=chat_room,
            user=user,
            role=ChatRole.ADMIN,
        )
        return chat_room


class MessageSerializer(AbstractTimestampedModelSerializer):
    """Serializer for chat messages."""

    sender = UserDetailChildSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    reply_to_sender = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "chat_room",
            "sender",
            "content",
            "message_type",
            "attachments",
            "reply_to",
            "reply_to_sender",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "sender",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
        ]

    def get_reply_to_sender(self, obj):
        if obj.reply_to:
            return {
                "id": obj.reply_to.sender.id,
                "full_name": obj.reply_to.sender.get_full_name()
                or obj.reply_to.sender.username,
            }
        return None


def validate_file_size(file_obj):
    max_size = 1024 * 1024  # 1MB
    if file_obj.size > max_size:
        raise serializers.ValidationError(f"File is larger than {max_size=}")


def validate_total_size(file_list):
    total_size = sum(f.size for f in file_list)
    max_mb_size = 10
    max_size = 1024 * 1024 * max_mb_size
    if total_size > max_size:
        current_mb = total_size / (1024 * 1024)
        raise serializers.ValidationError(
            f"The total size of all attachments ({current_mb:.2f} MB) "
            f"exceeds the maximum allowed total size of {max_mb_size:.0f} MB."
        )


class MessageCreateSerializer(serializers.ModelSerializer):
    message_type = serializers.ChoiceField(
        choices=[
            MessageType.TEXT,
            MessageType.IMAGE,
            MessageType.FILE,
        ]
    )
    attachments = AttachmentSerializer(many=True, read_only=True)
    attachments_files = serializers.ListField(
        child=serializers.FileField(
            validators=[
                FileExtensionValidator(
                    allowed_extensions=get_available_image_extensions()
                ),
                validate_file_size,
            ],
        ),
        allow_empty=False,
        write_only=True,
        validators=[validate_total_size],
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "chat_room",
            "sender",
            "message_type",
            "content",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
            "attachments",
            "attachments_files",
        ]
        read_only_fields = [
            "id",
            "chat_room",
            "sender",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
        ]

    # def validate(self, data):
    #     """Validate that attachments_files is required for image/file messages."""
    #     message_type = data.get('message_type')
    #     attachments_files = data.get('attachments_files', [])
        
    #     # Handle both list and None cases
    #     if attachments_files is None:
    #         attachments_files = []
        
    #     if message_type in [MessageType.IMAGE, MessageType.FILE]:
    #         if not attachments_files:
    #             raise serializers.ValidationError({
    #                 'attachments_files': 'This field is required for image and file messages.'
    #             })
    #     elif message_type == MessageType.TEXT:
    #         if attachments_files:
    #             raise serializers.ValidationError({
    #                 'attachments_files': 'This field is not allowed for text messages.'
    #             })
        
    #     return data


class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "chat_room", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "chat_room"]

    def update(self, instance, validated_data):
        if instance.message_type != MessageType.TEXT:
            raise serializers.ValidationError("Only text messages can be edited")
        return super().update(instance, validated_data)


class ChatRoomForSearchResponseSerializer(serializers.ModelSerializer):
    master = PublicMasterProfileSerializer(read_only=True)

    class Meta:
        model = ChatRoom
        fields = ["id", "master"]


class InitChatRequestSerializer(serializers.Serializer):
    """Serializer for init_chat action request."""
    user_id = serializers.IntegerField(help_text="User ID to create or find chat with")
    title = serializers.CharField(required=False, allow_blank=True, help_text="Optional chat title")


class InitChatResponseSerializer(serializers.ModelSerializer):
    """Serializer for init_chat action response."""
    participants = ChatParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            "id", "job", "title", "is_active", "last_message_at", 
            "chat_type", "participants", "created_at", "updated_at"
        ]