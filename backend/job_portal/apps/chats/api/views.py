from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import (
    MessageSerializer,
    MessageCreateSerializer,
    MessageUpdateSerializer,
    ChatRoomCreateSerializer,
    ChatRoomSerializer,
)
from ..models import ChatMessage, ChatParticipant, ChatRoom, MessageType, ChatAttachment
from ..utils import get_chat_channel_name

UserModel = get_user_model()


def get_participant_from_user(chat_room: ChatRoom, user: UserModel) -> ChatParticipant:
    try:
        participant = ChatParticipant.objects.get(chat_room=chat_room, user=user)
        return participant
    except ChatParticipant.DoesNotExist:
        raise PermissionDenied('Not a participant in this chat room')


class ChatRoomAPIViewSet(ModelViewSet):
    """
    ViewSet for managing chat rooms
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title']
    filterset_fields = ["chat_type", "is_active"]
    ordering_fields = ['created_at', 'last_message_at']
    ordering = ['-last_message_at', '-created_at']

    def get_queryset(self):
        """Return chat rooms where user is a participant"""

        qs = ChatRoom.objects.filter(
            participants=self.request.user,
            is_active=True,
        ).select_related('job').prefetch_related(
            'participants__user', 'participant_status'
        )
        return qs

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            obj = queryset.get(
                id=self.kwargs["pk"],
            )
        except ChatRoom.DoesNotExist:
            raise NotFound('Chat room not found or access denied')
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a chat room"""
        chat_room = self.get_object()

        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=request.user
            )
        except ChatParticipant.DoesNotExist:
            raise ValidationError(
                "Current user not found in chat"
            )
        participant.delete()
        self._broadcast_user_left(chat_room, request.user)
        return Response({'message': 'Successfully left chat room'})

    @action(detail=True, methods=["post"])
    def add_participants(self, request, pk=None):
        chat_room = self.get_object()

        user_ids = request.data.get("user_ids", [])
        try:
            requester = ChatParticipant.objects.get(chat_room=chat_room, user=request.user)
            if requester.role not in ["admin", "moderator"]:
                return Response({
                    "error": "Only admins can add participants"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except ChatParticipant.DoesNotExist:
            return Response({"error": "Not a participant"}, status=status.HTTP_403_FORBIDDEN, )

        added = []
        for uid in user_ids:
            try:
                user = UserModel.objects.get(id=uid)
                _, created = ChatParticipant.objects.get_or_create(chat_room=chat_room, user=user,
                                                                   defaults={"role": "member"})
                if created:
                    added.append({
                        "id": user.id,
                        "name": f"{user.first_name} {user.last_name}".strip() or user.username})
            except UserModel.DoesNotExist:
                continue

        return Response({"message": f"Added {len(added)} users", "users": added})

    @extend_schema(
        description="List all messages in a chat room with filtering and search",
        parameters=[
            OpenApiParameter(name='search', description='Search in message content', type=str),
            OpenApiParameter(name='message_type', description='Filter by message type', type=str),
        ],
        responses={200: MessageSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """List all messages in a chat room with filtering and search."""
        chat_room = self.get_object()
        get_participant_from_user(chat_room, request.user)
        queryset = ChatMessage.objects.filter(
            chat_room=chat_room,
            is_deleted=False
        ).select_related(
            'sender',
            'reply_to__sender'
        ).prefetch_related(
            'attachments'
        ).order_by('created_at')

        # Search in content
        search_query = request.query_params.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(content__icontains=search_query)

        # Filter by message type
        message_type = request.query_params.get('message_type')
        if message_type:
            queryset = queryset.filter(message_type=message_type)

        serializer = MessageSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        description="Send message to chat room",
        request=MessageCreateSerializer,
        responses={
            200: MessageSerializer,
        }
    )
    @action(detail=True, methods=["post"])
    def send_message(self, request, pk=None):
        """Custom action to send a message in a conversation."""

        chat_room = self.get_object()
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message_content = serializer.validated_data.get('message', '')
        message_type = serializer.validated_data.get('message_type')
        attachment_file = serializer.validated_data.pop('attachment_file', None)
        print("send", "attachment_files", attachment_file)

        if not message_content and attachment_file and message_type == MessageType.IMAGE:
            message_content = "📷 Image"

        chat_message = ChatMessage.objects.create(
            chat_room=chat_room,
            sender=request.user,
            content=message_content,
            message_type=message_type,
        )

        if attachment_file is not None:
            ChatAttachment.objects.create(
                message=chat_message,
                file=attachment_file
            )

        ChatParticipant.objects.filter(
            chat_room=chat_room
        ).exclude(user=request.user).update(
            unread_count=models.F('unread_count') + 1
        )
        chat_room.last_message_at = chat_message.created_at
        chat_room.save(update_fields=['last_message_at'])

        self._broadcast_message_add(chat_room, chat_message, request)
        return Response(MessageSerializer(chat_message, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path="messages/(?P<message_id>[^/.]+)/edit")
    def edit_message(self, request, pk=None, message_id=None):
        """Edit an existing message in the chat room."""

        chat_room = self.get_object()
        try:
            message = ChatMessage.objects.get(id=message_id, chat_room=chat_room, sender=request.user)
        except ChatMessage.DoesNotExist:
            return Response({"detail": "Message not found or no permission."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = MessageUpdateSerializer(message, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self._broadcast_message_edit(chat_room, message, request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path="messages/(?P<message_id>[^/.]+)")
    def delete_message(self, request, pk=None, message_id=None):
        """Remove message"""

        chat_room = self.get_object()
        try:
            message = ChatMessage.objects.get(id=message_id, chat_room=chat_room, sender=request.user)
        except ChatMessage.DoesNotExist:
            return Response({"detail": "Message not found or no permission."},
                            status=status.HTTP_404_NOT_FOUND)

        message.delete()
        self._broadcast_message_deletion(chat_room, message, request)
        return Response({
            "message": "Successfully deleted"
        }, status=status.HTTP_200_OK)

    def _broadcast_message_add(self, chat_room, message, request):
        """Broadcast new message via WebSocket."""
        channel_layer = get_channel_layer()
        chat_room_channel_name = get_chat_channel_name(chat_room)

        # Prepare attachments data
        attachments = []
        for attachment in message.attachments.all():
            attachments.append({
                'id': attachment.id,
                'name': attachment.original_filename,
                'url': request.build_absolute_uri(attachment.file.url),
                'size': attachment.size,
                'type': attachment.file_type
            })

        async_to_sync(channel_layer.group_send)(
            chat_room_channel_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'message_type': message.message_type,
                'content': message.content,
                'sender': {
                    'id': request.user.id,
                    'full_name': request.user.get_full_name() or request.user.username,
                },
                'attachments': attachments,
                'created_at': message.created_at.isoformat(),
                'updated_at': message.updated_at.isoformat(),
            }
        )

    def _broadcast_message_edit(self, chat_room, message, request):
        """Broadcast message edit via WebSocket."""
        channel_layer = get_channel_layer()
        chat_room_channel_name = get_chat_channel_name(chat_room)

        async_to_sync(channel_layer.group_send)(
            chat_room_channel_name,
            {
                'type': 'message_edited',
                'message_id': message.id,
                'content': message.content,
                'created_at': message.created_at.isoformat(),
                'updated_at': message.updated_at.isoformat(),
            }
        )

    def _broadcast_message_deletion(self, chat_room, message, request):
        """Broadcast message deletion via WebSocket."""

        channel_layer = get_channel_layer()
        chat_room_channel_name = get_chat_channel_name(chat_room)

        async_to_sync(channel_layer.group_send)(
            chat_room_channel_name,
            {
                'type': 'message_deleted',
                'message_id': message.id,
                'deleted_by': request.user.id,
                'created_at': message.created_at.isoformat(),
                'updated_at': message.updated_at.isoformat(),
            }
        )

    def _broadcast_user_left(self, chat_room, user):
        """Broadcast user left event via WebSocket."""

        channel_layer = get_channel_layer()
        chat_room_channel_name = get_chat_channel_name(chat_room)

        async_to_sync(channel_layer.group_send)(
            chat_room_channel_name,
            {
                'type': 'user_left',
                'user_id': user.id,
                'username': user.get_full_name() or user.username,
            }
        )
