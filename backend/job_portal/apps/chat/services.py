from django.db import transaction
from django.utils import timezone
from .models import ChatRoom, ChatMessage, ChatParticipant

class ChatService:
    """Simple service class for basic chat operations."""
    
    @staticmethod
    def create_chat_room(order, title=None):
        """Create a new chat room for an order."""
        with transaction.atomic():
            # Create chat room
            chat_room = ChatRoom.objects.create(
                order=order,
                title=title or f"Chat for Order #{order.id}",
                status='active'
            )
            
            # Add order participants to chat
            participants = []
            
            # Add order owner
            if order.user:
                participants.append(ChatParticipant(
                    chat_room=chat_room,
                    user=order.user,
                    role='owner',
                    is_active=True
                ))
            
            # Add service provider
            if hasattr(order, 'service_provider') and order.service_provider:
                participants.append(ChatParticipant(
                    chat_room=chat_room,
                    user=order.service_provider,
                    role='provider',
                    is_active=True
                ))
            
            # Bulk create participants
            if participants:
                ChatParticipant.objects.bulk_create(participants)
            
            return chat_room
    
    @staticmethod
    def get_user_chat_rooms(user):
        """Get all chat rooms for a user."""
        return ChatRoom.objects.filter(
            participants=user,
            is_active=True,
        ).select_related('order')
    
    @staticmethod
    def get_unread_count(user, chat_room):
        """Get unread message count for a user in a chat room."""
        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room,
                user=user
            )
            return participant.unread_count
        except ChatParticipant.DoesNotExist:
            return 0
