import secrets

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Max
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from accounts.api.permissions.custom_permissions import IsAuthenticatedWithBlocked
from utils.pagination import CustomPagination
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
from ..models import ChatMessage, ChatParticipant, ChatRoom, ChatType
from ...jobs.models import Job


class ChatConversationListApiView(generics.ListAPIView):
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


class ChatConversationDetailApiView(generics.RetrieveAPIView):
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


class ChatSendMessageApiView(generics.GenericAPIView):
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


class WebSocketInfoApiView(generics.GenericAPIView):
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


class ChatRoomCreateApiView(generics.GenericAPIView):
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


class ChatRoomAddParticipantApiView(generics.GenericAPIView):
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


# job_portal/apps/chat/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView, get_object_or_404
from django.db.models import Q, Count, F, Max
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

# Chat Room ViewSet
class ChatRoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat rooms
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ChatRoomFilter
    search_fields = ['title']
    ordering_fields = ['created_at', 'last_message_at']
    ordering = ['-last_message_at', '-created_at']

    def get_queryset(self):
        """Return chat rooms where user is a participant"""
        return ChatRoom.objects.filter(
            participants=self.request.user,
            is_deleted=False
        ).select_related('job').prefetch_related(
            'participants', 'participant_status'
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatRoomListSerializer
        elif self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a chat room"""
        chat_room = self.get_object()
        user = request.user

        participant, created = ChatParticipant.objects.get_or_create(
            chat_room=chat_room,
            user=user,
            defaults={'role': 'member'}
        )

        if created:
            return Response({'message': 'Successfully joined chat room'})
        return Response({'message': 'Already a member of this chat room'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a chat room"""
        chat_room = self.get_object()
        user = request.user

        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=user
            )
            participant.delete()
            return Response({'message': 'Successfully left chat room'})
        except ChatParticipant.DoesNotExist:
            return Response(
                {'error': 'Not a member of this chat room'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a chat room with pagination"""
        chat_room = self.get_object()

        # Check if user is participant
        if not chat_room.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not a participant in this chat room'},
                status=status.HTTP_403_FORBIDDEN
            )

        messages = chat_room.messages.select_related(
            'sender', 'reply_to__sender'
        ).filter(is_deleted=False)

        # Apply filters
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 50)), 100)

        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_messages = messages[start:end]

        serializer = ChatMessageSerializer(
            paginated_messages, many=True, context={'request': request}
        )

        return Response({
            'results': serializer.data,
            'has_more': messages.count() > end,
            'total_count': messages.count()
        })

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark messages as read in this chat room"""
        chat_room = self.get_object()

        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=request.user
            )

            # Reset unread count
            participant.unread_count = 0
            participant.last_seen = timezone.now()
            participant.save(update_fields=['unread_count', 'last_seen'])

            # Mark messages as read
            unread_messages = chat_room.messages.filter(
                is_read=False
            ).exclude(sender=request.user)

            unread_messages.update(
                is_read=True,
                read_at=timezone.now()
            )

            return Response({'message': 'Messages marked as read'})

        except ChatParticipant.DoesNotExist:
            return Response(
                {'error': 'Not a participant in this chat room'},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=True, methods=['post'])
    def add_participants(self, request, pk=None):
        """Add new participants to chat room"""
        chat_room = self.get_object()
        user_ids = request.data.get('user_ids', [])

        # Check if requester is admin/moderator
        try:
            requester_participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=request.user
            )
            if requester_participant.role not in ['admin', 'moderator']:
                return Response(
                    {'error': 'Only admins can add participants'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except ChatParticipant.DoesNotExist:
            return Response(
                {'error': 'Not a participant in this chat room'},
                status=status.HTTP_403_FORBIDDEN
            )

        added_users = []
        for user_id in user_ids:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)

                participant, created = ChatParticipant.objects.get_or_create(
                    chat_room=chat_room,
                    user=user,
                    defaults={'role': 'member'}
                )

                if created:
                    added_users.append({
                        'id': user.id,
                        'name': f"{user.first_name} {user.last_name}".strip() or user.username
                    })

            except User.DoesNotExist:
                continue

        return Response({
            'message': f'Added {len(added_users)} participants',
            'added_users': added_users
        })


# Chat Message ViewSet
class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat messages
    """
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatParticipant]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ChatMessageFilter
    ordering = ['created_at']

    def get_queryset(self):
        """Return messages from chat rooms where user is a participant"""
        return ChatMessage.objects.filter(
            chat_room__participants=self.request.user,
            is_deleted=False
        ).select_related('sender', 'chat_room', 'reply_to__sender')

    def get_serializer_class(self):
        if self.action == 'create':
            return ChatMessageCreateSerializer
        return ChatMessageSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsMessageSender])
    def edit(self, request, pk=None):
        """Edit a message (only sender can edit)"""
        message = self.get_object()
        new_content = request.data.get('content', '').strip()

        if not new_content:
            return Response(
                {'error': 'Content cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Only allow editing text messages
        if message.message_type != MessageType.TEXT:
            return Response(
                {'error': 'Only text messages can be edited'},
                status=status.HTTP_400_BAD_REQUEST
            )

        message.content = new_content
        message.save(update_fields=['content', 'updated_at'])

        serializer = ChatMessageSerializer(message, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add reaction to a message"""
        message = self.get_object()
        reaction = request.data.get('reaction', '').strip()

        if not reaction:
            return Response(
                {'error': 'Reaction cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # This would require a MessageReaction model in a full implementation
        # For now, just return success
        return Response({
            'message': f'Added reaction "{reaction}" to message'
        })


# Participant Management
class ChatParticipantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat participants
    """
    serializer_class = ChatParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatParticipant.objects.filter(
            chat_room__participants=self.request.user
        ).select_related('user', 'chat_room')

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ChatParticipantUpdateSerializer
        return ChatParticipantSerializer

    @action(detail=True, methods=['post'])
    def update_online_status(self, request, pk=None):
        """Update user's online status"""
        participant = self.get_object()

        if participant.user != request.user:
            return Response(
                {'error': 'Can only update your own status'},
                status=status.HTTP_403_FORBIDDEN
            )

        is_online = request.data.get('is_online', False)
        participant.is_online = is_online
        if not is_online:
            participant.last_seen = timezone.now()

        participant.save(update_fields=['is_online', 'last_seen'])

        serializer = OnlineStatusSerializer({
            'is_online': participant.is_online,
            'last_seen': participant.last_seen
        })
        return Response(serializer.data)


# Standalone Views
class SendMessageView(CreateAPIView):
    """Send a new message to chat room"""
    serializer_class = ChatMessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class MyChatsView(ListAPIView):
    """List current user's chat rooms"""
    serializer_class = ChatRoomListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(
            participants=self.request.user,
            is_deleted=False
        ).select_related('job').prefetch_related('participants').distinct()


class StartJobChatView(APIView):
    """Start a chat for a specific job between employer and master"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)

        user = request.user

        # Determine other participant
        other_user = None
        if hasattr(user, 'employer') and job.employer == user.employer:
            # Employer starting chat - need to find assigned master
            try:
                assignment = job.assignment
                other_user = assignment.master.user
            except:
                return Response(
                    {'error': 'No master assigned to this job yet'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif hasattr(user, 'master'):
            # Master starting chat
            other_user = job.employer.user
        else:
            raise PermissionDenied("Invalid user.")

        # Check if chat already exists
        existing_chat = ChatRoom.objects.filter(
            job=job,
            participants__in=[user, other_user],
            is_deleted=False
        ).annotate(
            participant_count=Count('participants')
        ).filter(participant_count=2).first()

        if existing_chat:
            serializer = ChatRoomSerializer(existing_chat, context={'request': request})
            return Response(serializer.data)

        # Create new chat room
        with transaction.atomic():
            chat_room = ChatRoom.objects.create(
                title=f"Job: {job.title}",
                chat_type=ChatType.JOB_CHAT,
                job=job,
                is_active=True
            )

            # Add both participants
            ChatParticipant.objects.create(
                chat_room=chat_room,
                user=user,
                role='member'
            )
            ChatParticipant.objects.create(
                chat_room=chat_room,
                user=other_user,
                role='member'
            )

        serializer = ChatRoomSerializer(chat_room, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UnreadMessagesView(APIView):
    """Get count of unread messages for current user"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total_unread = ChatParticipant.objects.filter(
            user=request.user,
            chat_room__is_deleted=False
        ).aggregate(
            total=Count('unread_count')
        )['total'] or 0

        return Response({'unread_count': total_unread})


class UpdateOnlineStatusView(APIView):
    """Update user's online status across all chats"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        is_online = request.data.get('is_online', False)

        update_fields = {'is_online': is_online}
        if not is_online:
            update_fields['last_seen'] = timezone.now()

        ChatParticipant.objects.filter(
            user=request.user