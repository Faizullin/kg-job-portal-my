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
from accounts.api.permissions.custom_permissions import IsAuthenticatedWithBlocked

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
    ChatRoomCreateSerializer,
    ChatRoomAddParticipantSerializer,
    ChatRoomSerializer,
)


class ChatConversationListApiView(StandardizedViewMixin, generics.ListAPIView):
    """Mobile-optimized view for chat conversation list."""
    serializer_class = ChatConversationSerializer
    permission_classes = [IsAuthenticatedWithBlocked]
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
    permission_classes = [IsAuthenticatedWithBlocked]
    
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
    permission_classes = [IsAuthenticatedWithBlocked]
    
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
            attachment = serializer.validated_data.get('attachment')
            message_content = serializer.validated_data.get('message', '')
            
            # If it's an image message without text, add a default message
            if not message_content and attachment and serializer.validated_data.get('message_type') == 'image':
                message_content = "📷 Image"
            
            message = ChatMessage.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=message_content,
                message_type=serializer.validated_data.get('message_type', 'text'),
                attachment=attachment,
                attachment_name=attachment.name if attachment else '',
                attachment_size=attachment.size if attachment else None
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
                    'attachment_url': request.build_absolute_uri(message.attachment.url) if message.attachment else '',
                    'attachment_name': message.attachment_name,
                    'attachment_size': message.attachment_size,
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
    permission_classes = [IsAuthenticatedWithBlocked]
    
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


class ChatRoomCreateApiView(StandardizedViewMixin, generics.GenericAPIView):
    """Create a new chat room."""
    serializer_class = ChatRoomCreateSerializer
    permission_classes = [IsAuthenticatedWithBlocked]
    
    def post(self, request):
        """Create a new chat room."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        # Create chat room
        chat_room = ChatRoom.objects.create(
            title=validated_data['title'],
            chat_type=validated_data['chat_type'],
            order_id=validated_data.get('order_id')
        )
        
        # Add current user as participant
        ChatParticipant.objects.create(
            chat_room=chat_room,
            user=request.user,
            role='admin'
        )
        
        # Add other participants
        for user_id in validated_data['participants']:
            from accounts.models import UserModel
            user = UserModel.objects.get(id=user_id)
            ChatParticipant.objects.create(
                chat_room=chat_room,
                user=user,
                role='member'
            )
        
        # Serialize and return the chat room
        response_serializer = ChatRoomSerializer(chat_room, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ChatRoomAddParticipantApiView(StandardizedViewMixin, generics.GenericAPIView):
    """Add participant to existing chat room."""
    serializer_class = ChatRoomAddParticipantSerializer
    permission_classes = [IsAuthenticatedWithBlocked]
    
    def post(self, request, pk):
        """Add a participant to a chat room."""
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
        
        # Validate request data
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        participant_id = serializer.validated_data['participant_id']
        
        # Check if participant is already in the chat
        if chat_room.participants.filter(id=participant_id).exists():
            return Response(
                {'error': 'User is already a participant in this chat'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add participant to chat room
        from accounts.models import UserModel
        participant_user = UserModel.objects.get(id=participant_id)
        ChatParticipant.objects.create(
            chat_room=chat_room,
            user=participant_user,
            role='member'
        )
        
        return Response({
            'message': 'Participant added successfully',
            'participant_name': f"{participant_user.first_name} {participant_user.last_name}".strip() or participant_user.username
        }, status=status.HTTP_201_CREATED)