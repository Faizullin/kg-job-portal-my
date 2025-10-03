from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import parsers, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.serializers import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from job_portal.apps.attachments.models import create_attachments
from .permissions import IsChatMessageOwner, IsChatOwner
from .serializers import (
    ChatRoomCreateSerializer,
    ChatRoomForSearchResponseSerializer,
    ChatRoomSerializer,
    InitChatRequestSerializer,
    InitChatResponseSerializer,
    MessageCreateSerializer,
    MessageSerializer,
    MessageUpdateSerializer,
)
from ..models import (
    ChatMessage,
    ChatParticipant,
    ChatRole,
    ChatRoom,
    ChatType,
    MessageType,
)
from ..utils import get_chat_channel_name
from ...users.models import Master

UserModel = get_user_model()


def get_participant_from_user(chat_room: ChatRoom, user: UserModel) -> ChatParticipant:
    try:
        participant = ChatParticipant.objects.get(chat_room=chat_room, user=user)
        return participant
    except ChatParticipant.DoesNotExist:
        raise PermissionDenied("Not a participant in this chat room")


class ChatRoomAPIViewSet(ModelViewSet):
    """
    ViewSet for managing chat rooms
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title"]
    filterset_fields = {
        "chat_type": ["exact"],
        "is_active": ["exact"],
        "id": ["in"],
        "job": ["exact"],
    }
    ordering_fields = ["created_at", "last_message_at"]
    ordering = ["-last_message_at", "-created_at"]

    def get_queryset(self):
        """Return chat rooms where user is a participant"""

        qs = (
            ChatRoom.objects.select_related("job")
            .prefetch_related("participants", "participant_status")
            .filter(
                participants=self.request.user,
                # is_active=True,
            )
        )
        return qs

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, id=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action == "create":
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    def get_permissions(self):
        perms = super().get_permissions()
        if self.action == "delete":
            perms.append(IsChatOwner())
        return perms

    @extend_schema(description="Leave a chat room", operation_id="v1_chats_rooms_leave")
    @action(detail=True, methods=["post"])
    def leave(self, request, _pk=None):
        """Leave a chat room"""
        chat_room = self.get_object()

        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=request.user
            )
        except ChatParticipant.DoesNotExist:
            raise ValidationError("Current user not found in chat")
        participant.delete()
        self._broadcast_user_left(chat_room, request.user)
        return Response({"message": "Successfully left chat room"})

    @extend_schema(
        description="Get chats for master",
        operation_id="v1_chats_rooms_for_master",
        parameters=[
            OpenApiParameter(
                name="master_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,  # Indicates it's a query parameter (e.g., ?master_id=123)
                required=True,
            ),
        ],
        responses={
            200: ChatRoomForSearchResponseSerializer(many=True),
        },
    )
    @action(
        detail=False,
        methods=["get"],
        pagination_class=None,
        filter_backends=[],
    )
    def for_master(self, request):
        self.pagination_class = None
        master_id = request.GET.get("master_id", None)
        if master_id is None:
            raise ValidationError("Master ID is required")
        try:
            master_id = int(master_id)
        except ValueError:
            raise ValidationError("Master ID is not valid")
        try:
            master = Master.objects.get(
                id=master_id,
            )
        except Master.DoesNotExist:
            raise ValidationError("Master not found")

        qs = self.get_queryset().filter(
            participants__id__in=[self.request.user.id, master.id],
        )
        return Response(ChatRoomForSearchResponseSerializer(qs, many=True).data)

    @extend_schema(
        description="Initialize chat with another user - find existing or create new",
        request=InitChatRequestSerializer,
        responses={200: InitChatResponseSerializer},
        operation_id="v1_chats_rooms_init_chat",
    )
    @action(detail=False, methods=["post"])
    def init_chat(self, request):
        """Initialize chat with another user - find existing or create new."""
        serializer = InitChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        title = serializer.validated_data.get('title', '')
        
        # Validate that user exists
        try:
            target_user = UserModel.objects.get(id=user_id, is_active=True)
        except UserModel.DoesNotExist:
            raise ValidationError("Target user not found or inactive")
        
        # Prevent self-chat
        if target_user.id == request.user.id:
            raise ValidationError("Cannot create chat with yourself")
        
        # Try to find existing chat between these two users
        existing_chat = ChatRoom.objects.filter(
            participants=request.user,
            # chat_type=ChatType.GENERAL_CHAT
        ).filter(
            participants=target_user
        ).first()
        
        if existing_chat:
            # Return existing chat
            return Response({
                "message": "Existing chat found",
                "data": InitChatResponseSerializer(existing_chat).data
            })
        
        # Create new chat
        chat_title = title or f"Chat with {target_user.get_full_name() or target_user.username}"
        
        chat_room = ChatRoom.objects.create(
            title=chat_title,
            chat_type=ChatType.GENERAL_CHAT,
            is_active=True
        )
        
        # Add both users as participants
        ChatParticipant.objects.create(
            chat_room=chat_room,
            user=request.user,
            role=ChatRole.MEMBER
        )
        ChatParticipant.objects.create(
            chat_room=chat_room,
            user=target_user,
            role=ChatRole.MEMBER
        )
        
        return Response({
            "message": "New chat created successfully",
            "data": InitChatResponseSerializer(chat_room).data
        }, status=status.HTTP_201_CREATED)

    def _broadcast_user_left(self, chat_room, user):
        """Broadcast user left event via WebSocket."""

        channel_layer = get_channel_layer()
        chat_room_channel_name = get_chat_channel_name(chat_room)

        async_to_sync(channel_layer.group_send)(
            chat_room_channel_name,
            {
                "type": "user_left",
                "user_id": user.id,
                "username": user.get_full_name() or user.username,
            },
        )


class ChatContextDto:
    chat_room: ChatRoom
    participant: ChatParticipant

    def __init__(self, chat_room: ChatRoom, participant: ChatParticipant):
        self.chat_room = chat_room
        self.participant = participant


class ChatRoomMessageAPIViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["content"]
    filterset_fields = ["message_type", "is_read"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def _get_chat_context(self):
        """
        Fetches the Chat object and caches it on the request object.
        It checks for the cached value first to avoid repeating the DB query.
        """
        if hasattr(self.request, "_chat_context_dto"):
            return self.request._chat_context_dto

        chat_room_id = self.kwargs.get("chat_room_id")
        try:
            chat = ChatRoom.objects.prefetch_related("participants").get(
                id=chat_room_id
            )
        except ChatRoom.DoesNotExist:
            raise NotFound("Chat not found.")

        participant = get_participant_from_user(chat, self.request.user)
        self.request._chat_context_dto = ChatContextDto(
            chat_room=chat, participant=participant
        )
        return self.request._chat_context_dto

    def get_queryset(self):
        chat_context = self._get_chat_context()
        return ChatMessage.objects.select_related("sender", "chat_room").prefetch_related("attachments").filter(
            chat_room=chat_context.chat_room
        )

    def get_serializer_class(self):
        if self.action == "create":
            return MessageCreateSerializer
        elif self.action == "update":
            return MessageUpdateSerializer
        return MessageSerializer

    def get_permissions(self):
        perms = super().get_permissions()
        if self.action in ["update", "destroy"]:
            perms += [IsChatMessageOwner()]
        return perms

    def perform_create(self, serializer):
        chat_context = self._get_chat_context()
        user = self.request.user
        message_content = serializer.validated_data.get("content", "")
        message_type = serializer.validated_data.get("message_type")
        attachments_files = serializer.validated_data["attachments_files"]
        if (
                not message_content
                and len(attachments_files) > 0
                and message_type == MessageType.IMAGE
        ):
            if len(attachments_files) > 1:
                raise ValidationError("Only one image is allowed")
            message_content = "📷 Image"

        chat_message = serializer.save(
            chat_room=chat_context.chat_room,
            sender=user,
            content=message_content,
            message_type=message_type,
        )
        print("performe.create", attachments_files)
        if attachments_files is not None:
            created_attachments = create_attachments(attachments_files, user, chat_message)
            chat_message.attachments.add(*created_attachments)

        ChatParticipant.objects.filter(chat_room=chat_context.chat_room).exclude(
            user=user
        ).update(unread_count=models.F("unread_count") + 1)
        chat_context.chat_room.last_message_at = chat_message.created_at
        chat_context.chat_room.save(update_fields=["last_message_at"])
        self._broadcast_message_add(chat_context.chat_room, chat_message, self.request)
        return Response(
            MessageSerializer(chat_message, context={"request": self.request}).data
        )

    def perform_update(self, serializer):
        chat_context = self._get_chat_context()
        serializer.save()
        self._broadcast_message_edit(
            chat_context.chat_room, serializer.instance, self.request
        )

    def perform_destroy(self, instance: ChatMessage):
        chat_context = self._get_chat_context()
        instance.attachments.all().delete()
        instance.delete()
        self._broadcast_message_deletion(chat_context.chat_room, instance, self.request)

    def _broadcast_message_add(self, chat_room, message, request):
        """Broadcast new message via WebSocket."""
        channel_layer = get_channel_layer()
        chat_room_channel_name = get_chat_channel_name(chat_room)

        # Prepare attachments data
        attachments = []
        for attachment in message.attachments.all():
            attachments.append(
                {
                    "id": attachment.id,
                    "name": attachment.original_filename,
                    "url": request.build_absolute_uri(attachment.file.url),
                    "size": attachment.size,
                    "type": attachment.file_type,
                }
            )

        async_to_sync(channel_layer.group_send)(
            chat_room_channel_name,
            {
                "type": "chat_message",
                "message_id": message.id,
                "message_type": message.message_type,
                "content": message.content,
                "sender": {
                    "id": request.user.id,
                    "full_name": request.user.get_full_name() or request.user.username,
                },
                "attachments": attachments,
                "created_at": message.created_at.isoformat(),
                "updated_at": message.updated_at.isoformat(),
            },
        )

    def _broadcast_message_edit(self, chat_room, message, request):
        """Broadcast message edit via WebSocket."""
        channel_layer = get_channel_layer()
        chat_room_channel_name = get_chat_channel_name(chat_room)

        async_to_sync(channel_layer.group_send)(
            chat_room_channel_name,
            {
                "type": "message_edited",
                "message_id": message.id,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "updated_at": message.updated_at.isoformat(),
            },
        )

    def _broadcast_message_deletion(self, chat_room, message, request):
        """Broadcast message deletion via WebSocket."""

        channel_layer = get_channel_layer()
        chat_room_channel_name = get_chat_channel_name(chat_room)

        async_to_sync(channel_layer.group_send)(
            chat_room_channel_name,
            {
                "type": "message_deleted",
                "message_id": message.id,
                "deleted_by": request.user.id,
                "created_at": message.created_at.isoformat(),
                "updated_at": message.updated_at.isoformat(),
            },
        )
