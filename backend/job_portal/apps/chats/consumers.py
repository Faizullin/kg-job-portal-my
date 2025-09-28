import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import ChatRoom, ChatMessage, ChatParticipant
from django.db import models

UserModel = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    """
    Simple WebSocket consumer for real-time chat functionality.
    Handles basic message sending and broadcasting.
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close(code=4001)  # Unauthorized
            return
        
        # Check if user has access to this chat room
        if not await self.can_access_room():
            await self.close(code=4003)  # Forbidden
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'room_id': self.room_id,
            'user_id': self.user.id,
            # 'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""

        print("Received data:", text_data)
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'chat_message')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def handle_chat_message(self, data):
        """Handle incoming chat messages."""
        content = data.get('message', '').strip()
        if not content:
            return
        
        # Save message to database
        saved_message = await self.save_message(content)
        
        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': content,
                'sender_id': self.user.id,
                'sender_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
                'message_id': saved_message.id,
                'timestamp': saved_message.created_at.isoformat(),
            }
        )
    
    # WebSocket message handlers for group broadcasts
    
    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp'],
        }))
    
    # Database operations
    
    @database_sync_to_async
    def can_access_room(self):
        """Check if user can access this chat room."""
        try:
            room = ChatRoom.objects.get(id=self.room_id, is_active=True)
            # Check if user is a participant via ChatParticipant
            return ChatParticipant.objects.filter(chat_room=room, user=self.user).exists()
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """Save message to database."""
        room = ChatRoom.objects.get(id=self.room_id)
        
        message = ChatMessage.objects.create(
            chat_room=room,
            sender=self.user,
            content=content,
            message_type='text'
        )
        
        # Update unread count for other participants
        ChatParticipant.objects.filter(
            chat_room=room
        ).exclude(user=self.user).update(
            unread_count=models.F('unread_count') + 1
        )
        
        return message
