from django.db.models import Max
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from utils.exceptions import StandardizedViewMixin
from utils.pagination import CustomPagination
from utils.permissions import AbstractIsAuthenticatedOrReadOnly

from ..models import ChatAttachment, ChatMessage, ChatParticipant, ChatRoom
from .serializers import (
    ChatAttachmentCreateSerializer,
    ChatAttachmentSerializer,
    ChatParticipantCreateSerializer,
    ChatParticipantSerializer,
    ChatRoomCreateSerializer,
    ChatRoomSerializer,
    ChatRoomUpdateSerializer,
    MessageCreateSerializer,
    MessageSerializer,
    MessageUpdateSerializer,
    WebSocketInfoSerializer,
)


class ChatRoomApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["chat_type", "is_active"]
    search_fields = ["title", "order__title"]
    ordering_fields = ["last_message_at", "created_at"]
    ordering = ["-last_message_at", "-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        # Simple filtering - manager automatically handles is_deleted
        return (
            ChatRoom.objects.filter(
                participant_status__user=self.request.user, is_active=True
            )
            .prefetch_related("participant_status", "messages")
            .annotate(last_message=Max("messages__created_at"))
        )

    @action(detail=False, methods=["get"])
    def my_rooms(self, request):
        """Get chat rooms where user is a participant."""
        # Simple filtering - manager automatically handles is_deleted
        rooms = ChatRoom.objects.filter(
            participant_status__user=request.user, is_active=True
        ).prefetch_related("participant_status", "messages")

        serializer = ChatRoomSerializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def order_chat(self, request):
        """Get chat room for a specific order."""
        order_id = request.query_params.get("order_id")
        if not order_id:
            return Response({"error": "order_id is required"}, status=400)

        # Simple filtering - manager automatically handles is_deleted
        room = ChatRoom.objects.filter(
            order_id=order_id,
            participant_status__user=request.user,
            is_active=True,
        ).first()

        if room:
            serializer = ChatRoomSerializer(room)
            return Response(serializer.data)
        else:
            return Response({"error": "Chat room not found"}, status=404)


class ChatRoomDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    serializer_class = ChatRoomUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Simple filtering - manager automatically handles is_deleted
        return ChatRoom.objects.filter(
            participant_status__user=self.request.user, is_active=True
        ).prefetch_related("participant_status", "messages")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ChatRoomSerializer
        return ChatRoomUpdateSerializer


class ChatRoomCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = ChatRoomCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # All creation logic is handled inside serializer.create to avoid passing
        # unsupported writable fields to ChatRoom.objects.create()
        serializer.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Re-serialize created instance with full serializer to include id and computed fields
        try:
            # Find the latest room created by this user recently
            room = ChatRoom.objects.filter(participant_status__user=request.user).order_by('-id').first()
            if room:
                serializer = ChatRoomSerializer(room, context={'request': request})
                return Response(serializer.data, status=201)
        except Exception:
            pass
        return response


class MessageApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["chat_room", "message_type", "is_read"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        # Simple filtering - manager automatically handles is_deleted
        queryset = ChatMessage.objects.filter(
            chat_room__participant_status__user=self.request.user,
            chat_room__is_active=True,
        ).select_related("sender", "chat_room")
        
        # Filter by chat_room if provided in query params
        chat_room_id = self.request.query_params.get('chat_room')
        if chat_room_id:
            queryset = queryset.filter(chat_room_id=chat_room_id)
            
        return queryset

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """Get unread messages for current user."""
        # Simple filtering - manager automatically handles is_deleted
        messages = ChatMessage.objects.filter(
            chat_room__participants=request.user,
            chat_room__is_active=True,
            is_read=False,
        ).select_related("sender", "chat_room")

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageDetailApiView(
    StandardizedViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = MessageUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return ChatMessage.objects.filter(
            chat_room__participants=user,
            chat_room__is_active=True,
        ).select_related("sender", "chat_room")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return MessageSerializer
        return MessageUpdateSerializer


class MessageCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = MessageCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # All creation handled in serializer to avoid passing unsupported fields
        message = serializer.save()
        # Update room last_message_at and basic unread handling
        ChatRoom.objects.filter(id=message.chat_room_id).update(last_message_at=message.created_at)


class ChatParticipantApiView(StandardizedViewMixin,generics.ListAPIView):
    serializer_class = ChatParticipantSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["chat_room", "is_online", "notifications_enabled"]
    ordering_fields = ["last_seen", "created_at"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return ChatParticipant.objects.filter(
            chat_room__participants=user,
            chat_room__is_active=True,
        ).select_related("user", "chat_room")


class ChatParticipantCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = ChatParticipantCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Check if user has permission to add participants to this chat room
        chat_room = serializer.validated_data["chat_room"]
        if not ChatParticipant.objects.filter(
            chat_room=chat_room, user=self.request.user, role__in=["admin", "moderator"]
        ).exists():
            raise PermissionError(
                "You don't have permission to add participants to this chat room"
            )
        participant = serializer.save()
        # Keep M2M participants in sync
        try:
            chat_room.participants.add(participant.user_id)
        except Exception:
            pass


class ChatAttachmentApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = ChatAttachmentSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["message", "file_type"]
    ordering_fields = ["file_size", "created_at"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return ChatAttachment.objects.filter(
            message__chat_room__participants=user,
            message__chat_room__is_active=True,
        ).select_related("message", "message__chat_room")


class ChatAttachmentCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = ChatAttachmentCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Check if user has permission to add attachments to this message
        message = serializer.validated_data["message"]
        if not ChatParticipant.objects.filter(
            chat_room=message.chat_room, user=self.request.user
        ).exists():
            raise PermissionError(
                "You don't have permission to add attachments to this message"
            )

        serializer.save()


class ChatAttachmentDetailApiView(
    StandardizedViewMixin, generics.RetrieveDestroyAPIView
):
    serializer_class = ChatAttachmentSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return ChatAttachment.objects.filter(
            message__chat_room__participants=user,
            message__chat_room__is_active=True,
        ).select_related("message")


class WebSocketInfoApiView(StandardizedViewMixin, generics.GenericAPIView):
    """Get WebSocket connection information for the current user."""

    serializer_class = WebSocketInfoSerializer

    def get(self, request, *args, **kwargs):
        response_data = {
            "websocket_url": f"ws://{request.get_host()}/ws/chat/",
            "auth_required": True,
            "token_param": "token",
            "connection_format": f"ws://{request.get_host()}/ws/chat/{{room_id}}/?token={{drf_token}}",
            "message_types": ["chat_message"],
        }
        serializer = self.get_serializer(response_data)
        return Response(serializer.data)
