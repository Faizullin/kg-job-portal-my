from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404

from utils.crud_base.views import AbstractBaseListApiView, AbstractBaseApiView
from utils.permissions import AbstractIsAuthenticatedOrReadOnly
from ..models import ChatRoom, ChatMessage, ChatParticipant, ChatAttachment
from .serializers import (
    ChatRoomSerializer, MessageSerializer, ChatParticipantSerializer,
    ChatAttachmentSerializer, ChatRoomCreateSerializer, MessageCreateSerializer,
    ChatParticipantCreateSerializer, ChatAttachmentCreateSerializer,
    MessageUpdateSerializer, ChatRoomUpdateSerializer
)


class ChatRoomApiView(AbstractBaseListApiView):
    serializer_class = ChatRoomSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['room_type', 'order']
    search_fields = ['name']
    ordering_fields = ['last_message', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            participants__user=user, participants__is_active=True, is_deleted=False
        ).prefetch_related('participants__user', 'messages').annotate(
            last_message=Max('messages__created_at')
        )
    
    @action(detail=False, methods=['get'])
    def my_rooms(self, request):
        """Get chat rooms where user is a participant."""
        rooms = ChatRoom.objects.filter(
            participants__user=request.user, participants__is_active=True, is_deleted=False
        ).prefetch_related('participants__user', 'messages')
        
        serializer = ChatRoomSerializer(rooms, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def order_chat(self, request):
        """Get chat room for a specific order."""
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response({'error': 'order_id is required'}, status=400)
        
        room = ChatRoom.objects.filter(
            order_id=order_id,
            participants__user=request.user,
            participants__is_active=True,
            is_deleted=False
        ).first()
        
        if room:
            serializer = ChatRoomSerializer(room)
            return Response(serializer.data)
        else:
            return Response({'error': 'Chat room not found'}, status=404)


class ChatRoomDetailApiView(AbstractBaseApiView):
    serializer_class = ChatRoomUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            participants__user=user, participants__is_active=True, is_deleted=False
        ).prefetch_related('participants__user', 'messages')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ChatRoomSerializer
        return ChatRoomUpdateSerializer
    
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChatRoomCreateApiView(AbstractBaseApiView):
    serializer_class = ChatRoomCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_room = serializer.save()
        
        # Add creator as participant
        ChatParticipant.objects.create(
            chat_room=chat_room,
            user=self.request.user,
            role='admin'
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageApiView(AbstractBaseListApiView):
    serializer_class = MessageSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['chat_room', 'message_type', 'is_read']
    search_fields = ['content']
    ordering_fields = ['created_at', 'is_read']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return ChatMessage.objects.filter(
            chat_room__participants__user=user,
            chat_room__participants__is_active=True,
            is_deleted=False
        ).select_related('sender', 'chat_room').prefetch_related('attachments')
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread messages for current user."""
        messages = ChatMessage.objects.filter(
            chat_room__participants__user=request.user,
            chat_room__participants__is_active=True,
            is_read=False,
            is_deleted=False
        ).select_related('sender', 'chat_room')
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        return ChatMessage.objects.filter(
            chat_room__participants__user=user,
            chat_room__participants__is_active=True,
            is_deleted=False
        ).select_related('sender', 'chat_room')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MessageSerializer
        return MessageUpdateSerializer


class MessageCreateApiView(generics.CreateAPIView):
    serializer_class = MessageCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ChatParticipantApiView(AbstractBaseListApiView):
    serializer_class = ChatParticipantSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['chat_room', 'role', 'is_active']
    ordering_fields = ['joined_at', 'last_read_at']
    ordering = ['-joined_at']
    
    def get_queryset(self):
        user = self.request.user
        return ChatParticipant.objects.filter(
            chat_room__participants__user=user,
            chat_room__participants__is_active=True,
            is_deleted=False
        ).select_related('user', 'chat_room')


class ChatParticipantCreateApiView(generics.CreateAPIView):
    serializer_class = ChatParticipantCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        # Check if user has permission to add participants to this chat room
        chat_room = serializer.validated_data['chat_room']
        if not chat_room.participants.filter(user=self.request.user, role__in=['admin', 'moderator']).exists():
            raise PermissionError("You don't have permission to add participants to this chat room")
        
        serializer.save()


class ChatAttachmentApiView(AbstractBaseListApiView):
    serializer_class = ChatAttachmentSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['message', 'file_type']
    search_fields = ['file_name']
    ordering_fields = ['file_size', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return ChatAttachment.objects.filter(
            message__chat_room__participants__user=user,
            message__chat_room__participants__is_active=True,
            is_deleted=False
        ).select_related('message')


class ChatAttachmentCreateApiView(generics.CreateAPIView):
    serializer_class = ChatAttachmentCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        # Check if user has permission to add attachments to this message
        message = serializer.validated_data['message']
        if not message.chat_room.participants.filter(user=self.request.user, is_active=True).exists():
            raise PermissionError("You don't have permission to add attachments to this message")
        
        serializer.save()


class ChatAttachmentDetailApiView(generics.RetrieveDestroyAPIView):
    serializer_class = ChatAttachmentSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        return ChatAttachment.objects.filter(
            message__chat_room__participants__user=user,
            message__chat_room__participants__is_active=True,
            is_deleted=False
        ).select_related('message')


class WebSocketInfoApiView(AbstractBaseApiView):
    """Get WebSocket connection information for the current user."""
    
    def get(self, request, *args, **kwargs):
        return Response({
            'websocket_url': f"ws://{request.get_host()}/ws/chat/",
            'auth_required': True,
            'token_param': 'token',
            'connection_format': f"ws://{request.get_host()}/ws/chat/{{room_id}}/?token={{drf_token}}",
            'message_types': [
                'chat_message'
            ]
        })
