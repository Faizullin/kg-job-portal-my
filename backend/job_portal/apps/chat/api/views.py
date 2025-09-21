from django.db.models import Max, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from utils.exceptions import StandardizedViewMixin
from utils.pagination import CustomPagination
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.permissions import IsAuthenticated

from accounts.models import UserModel
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
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["chat_type", "is_active"]
    search_fields = ["title", "order__title"]
    ordering_fields = ["last_message_at", "created_at"]
    ordering = ["-last_message_at", "-created_at"]
    pagination_class = CustomPagination
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        return (
            ChatRoom.objects.filter(
                participants=self.request.user, is_active=True
            )
            .prefetch_related("participant_status__user", "messages__sender")
            .select_related("order")
            .annotate(last_message_time=Max("messages__created_at"))
        )

    @action(detail=False, methods=["get"])
    def my_rooms(self, request):
        """Get chat rooms where user is a participant."""
        rooms = self.get_queryset()
        serializer = ChatRoomSerializer(rooms, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def order_chat(self, request):
        """Get chat room for a specific order."""
        order_id = request.query_params.get("order_id")
        if not order_id:
            return Response({"error": "order_id is required"}, status=400)

        room = self.get_queryset().filter(order_id=order_id).first()

        if room:
            serializer = ChatRoomSerializer(room, context={'request': request})
            return Response(serializer.data)
        else:
            return Response({"error": "Chat room not found"}, status=404)


class ChatRoomDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    serializer_class = ChatRoomUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(
            participants=self.request.user, is_active=True
        ).prefetch_related("participant_status__user", "messages__sender").select_related("order")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ChatRoomSerializer
        return ChatRoomUpdateSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ChatRoomCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = ChatRoomCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        chat_room = serializer.save()
        ChatParticipant.objects.create(
            chat_room=chat_room, user=self.request.user, role="admin"
        )
        
        # Add additional participants if provided
        participant_ids = self.request.POST.get('participants', [])
        for participant_id in participant_ids:
            if participant_id != self.request.user.id:
                try:
                    user = UserModel.objects.get(id=participant_id)
                    ChatParticipant.objects.get_or_create(
                        chat_room=chat_room, 
                        user=user,
                        defaults={'role': 'member'}
                    )
                except UserModel.DoesNotExist:
                    continue


class MessageApiView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["chat_room", "message_type", "is_read"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        # Simple filtering - manager automatically handles is_deleted
        return ChatMessage.objects.filter(
            chat_room__participants=self.request.user,
            chat_room__is_active=True,
        ).select_related("sender", "chat_room")

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)
        
        ChatParticipant.objects.filter(
            chat_room=message.chat_room
        ).exclude(user=self.request.user).update(
            unread_count=F('unread_count') + 1
        )
        
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{message.chat_room.id}'
        
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'chat_message',
                'message': message.content,
                'sender_id': self.request.user.id,
                'sender_name': f"{self.request.user.username}".strip(),
                'message_id': message.id,
                'timestamp': message.created_at.isoformat(),
            }
        )


class ChatParticipantApiView(generics.ListAPIView):
    serializer_class = ChatParticipantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["chat_room", "role", "is_online"]
    ordering_fields = ["created_at", "last_seen"]
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
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Check if user has permission to add participants to this chat room
        chat_room = serializer.validated_data["chat_room"]
        if not chat_room.participant_status.filter(
            user=self.request.user, role__in=["admin", "moderator"]
        ).exists():
            raise PermissionError(
                "You don't have permission to add participants to this chat room"
            )

        serializer.save()


class ChatAttachmentApiView(generics.ListAPIView):
    serializer_class = ChatAttachmentSerializer
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Check if user has permission to add attachments to this message
        message = serializer.validated_data["message"]
        if not message.chat_room.participant_status.filter(
            user=self.request.user
        ).exists():
            raise PermissionError(
                "You don't have permission to add attachments to this message"
            )

        serializer.save()


class ChatAttachmentDetailApiView(
    StandardizedViewMixin, generics.RetrieveDestroyAPIView
):
    serializer_class = ChatAttachmentSerializer
    permission_classes = [IsAuthenticated]

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
