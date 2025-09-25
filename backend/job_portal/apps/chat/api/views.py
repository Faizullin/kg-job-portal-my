# Django imports
from django.db.models import Max
from django.utils import timezone
from django.db import models
import secrets

# DRF imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Channels imports
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Local imports
from utils.exceptions import StandardizedViewMixin
from utils.pagination import CustomPagination
from ..models import ChatMessage, ChatParticipant, ChatRoom
from .serializers import (
    MessageSerializer,
    WebSocketInfoSerializer,
    ChatConversationSerializer,
    ChatConversationDetailSerializer,
    ChatSendMessageSerializer,
)


class ChatConversationListApiView(StandardizedViewMixin, generics.ListAPIView):
    """Mobile-optimized view for chat conversation list."""
    serializer_class = ChatConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["chat_type", "is_active"]
    search_fields = ["title", "participants__first_name", "participants__last_name"]
    ordering_fields = ["last_message_at", "created_at"]
    ordering = ["-last_message_at", "-created_at"]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        """Get user's chat conversations with mobile-optimized data."""
        return (
            ChatRoom.objects.filter(
                participants=self.request.user, 
                is_active=True
            )
            .prefetch_related(
                "participant_status__user", 
                "messages__sender",
                "participants"
            )
            .select_related("order__service_subcategory__category")
            .annotate(last_message_time=Max("messages__created_at"))
        )


class ChatConversationDetailApiView(StandardizedViewMixin, generics.RetrieveAPIView):
    """Mobile-optimized view for chat conversation details with messages."""
    serializer_class = ChatConversationDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get user's accessible chat rooms."""
        return ChatRoom.objects.filter(
            participants=self.request.user,
            is_active=True
        ).prefetch_related(
            "participant_status__user",
            "messages__sender",
            "participants"
        ).select_related("order__service_subcategory__category")
    
    def get_object(self):
        """Get chat room and mark messages as read."""
        obj = super().get_object()
        
        # Mark messages as read for current user
        ChatMessage.objects.filter(
            chat_room=obj,
            is_read=False
        ).exclude(sender=self.request.user).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        # Reset unread count for current user
        ChatParticipant.objects.filter(
            chat_room=obj,
            user=self.request.user
        ).update(unread_count=0)
        
        return obj


class ChatSendMessageApiView(StandardizedViewMixin, generics.GenericAPIView):
    """Mobile-optimized view for sending messages."""
    serializer_class = ChatSendMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Send a message to a chat room."""
        try:
            # Get chat room
            chat_room = ChatRoom.objects.filter(
                id=pk,
                participants=request.user,
                is_active=True
            ).first()
            
            if not chat_room:
                return Response(
                    {'error': 'Chat room not found or access denied'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validate message data
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Create message
            message = ChatMessage.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=serializer.validated_data['message'],
                message_type=serializer.validated_data.get('message_type', 'text'),
                attachment=serializer.validated_data.get('attachment'),
                attachment_name=serializer.validated_data.get('attachment').name if serializer.validated_data.get('attachment') else '',
                attachment_size=serializer.validated_data.get('attachment').size if serializer.validated_data.get('attachment') else None
            )
            
            # Update unread count for other participants
            ChatParticipant.objects.filter(
                chat_room=chat_room
            ).exclude(user=request.user).update(
                unread_count=models.F('unread_count') + 1
            )
            
            # Update last message time
            chat_room.last_message_at = message.created_at
            chat_room.save(update_fields=['last_message_at'])
            
            # Broadcast via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{chat_room.id}',
                {
                    'type': 'chat_message',
                    'message': message.content,
                    'sender_id': request.user.id,
                    'sender_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                    'message_id': message.id,
                    'timestamp': message.created_at.isoformat(),
                    'message_type': message.message_type,
                    'attachment_url': message.attachment.url if message.attachment else '',
                }
            )
            
            return Response({
                'message': 'Message sent successfully',
                'message_data': MessageSerializer(message, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to send message: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WebSocketInfoApiView(StandardizedViewMixin, generics.GenericAPIView):
    """Provide WebSocket connection information for mobile app."""
    serializer_class = WebSocketInfoSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get WebSocket connection info for the user."""
        # Generate a temporary token for WebSocket connection instead of exposing auth token
        temp_token = secrets.token_urlsafe(32)
        
        serializer = WebSocketInfoSerializer({
            'websocket_url': f'ws://{request.get_host()}/ws/chat/',
            'temp_token': temp_token,  # Use temporary token instead of auth token
            'user_id': request.user.id
        })
        return Response(serializer.data, status=status.HTTP_200_OK)