import json
import logging
from typing import Any, Dict, Optional

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.db import models

from job_portal.apps.chats.utils import get_chat_channel_name

from .models import ChatMessage, ChatParticipant, ChatRoom

logger = logging.getLogger(__name__)
UserModel = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Simple WebSocket consumer for real-time chat functionality.
    Handles basic message sending and broadcasting.
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = get_chat_channel_name(self.room_id)
        self.user = self.scope["user"]

        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close(code=4001)  # Unauthorized
            return

        # Check if user has access to this chat room
        if not await self.can_access_room():
            await self.close(code=4003)  # Forbidden
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send connection confirmation
        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection_established",
                    "room_id": self.room_id,
                    "user_id": self.user.id,
                }
            )
        )

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""

        print("Received data:", text_data)
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "chat_message")

            if message_type == "chat_message":
                await self.handle_chat_message(data)
            else:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {message_type}",
                        }
                    )
                )

        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Invalid JSON format"}
                )
            )
        except Exception as e:
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    async def handle_chat_message(self, data: Dict[str, Any]) -> None:
        """Handle incoming chat messages."""
        try:
            content = data.get("message", "").strip()
            if not content:
                await self.send_error("Message content cannot be empty")
                return

            # Validate message length
            if len(content) > 1000:
                await self.send_error(
                    "Message too long. Maximum 1000 characters allowed."
                )
                return

            # Save message to database
            saved_message = await self.save_message(content)
            if not saved_message:
                await self.send_error("Failed to save message")
                return

            # Prepare attachments data
            attachments = await self.get_message_attachments(saved_message)

            # Broadcast message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message_id": saved_message.id,
                    "message_type": saved_message.message_type,
                    "content": content,
                    "sender": {
                        "id": self.user.id,
                        "full_name": f"{self.user.first_name} {self.user.last_name}".strip()
                        or self.user.username,
                    },
                    "attachments": attachments,
                    "created_at": saved_message.created_at.isoformat(),
                    "updated_at": saved_message.updated_at.isoformat(),
                },
            )
        except Exception as e:
            logger.error(f"Error handling chat message: {e}")
            await self.send_error("An error occurred while processing your message")

    # WebSocket message handlers for group broadcasts

    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat_message",
                    "message_id": event["message_id"],
                    "message_type": event["message_type"],
                    "content": event["content"],
                    "sender": event["sender"],
                    "attachments": event["attachments"],
                    "created_at": event["created_at"],
                    "updated_at": event["updated_at"],
                }
            )
        )

    async def send_error(self, message: str) -> None:
        """Send error message to WebSocket."""
        await self.send(text_data=json.dumps({"type": "error", "message": message}))

    @database_sync_to_async
    def get_message_attachments(self, message: ChatMessage) -> list:
        """Get attachments for a message."""
        attachments = []
        for attachment in message.attachments.all():
            attachments.append(
                {
                    "id": attachment.id,
                    "name": attachment.original_filename,
                    "size": attachment.size,
                    "type": attachment.file_type,
                    "url": attachment.file.url if attachment.file else None,
                }
            )
        return attachments

    @database_sync_to_async
    def can_access_room(self) -> bool:
        """Check if user can access this chat room."""
        try:
            room = ChatRoom.objects.get(id=self.room_id, is_active=True)
            return ChatParticipant.objects.filter(
                chat_room=room, user=self.user
            ).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content: str) -> Optional[ChatMessage]:
        """Save message to database."""
        try:
            room = ChatRoom.objects.get(id=self.room_id)

            message = ChatMessage.objects.create(
                chat_room=room, sender=self.user, content=content, message_type="text"
            )

            # Update unread count for other participants
            ChatParticipant.objects.filter(chat_room=room).exclude(
                user=self.user
            ).update(unread_count=models.F("unread_count") + 1)

            # Update last message timestamp
            room.last_message_at = message.created_at
            room.save(update_fields=["last_message_at"])

            return message
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None
