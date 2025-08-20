from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .consumer_actions import Action

"""
NOT USED FOR NOW
"""

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.connected_time = None

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            """
            if user is not authenticated, close the connection
            """
            await self.accept()
            await self.send(text_data=await Action.error("You must be logged in to chat."))
            await self.close()
            return

        self.connected_time = timezone.now()
        await self.channel_layer.group_add(f'user{self.user.pk}', self.channel_name)
        await self.accept()
        await self.send(await Action.success(data="Connected"))

    async def disconnect(self, close_code):
        # Leave room group
        if self.user.is_anonymous:
            return

        await self.channel_layer.group_discard(f'user{self.user.pk}', self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        # action: Action = await Action.from_json(text_data)
        await self.send(text_data=Action.error('Unknown action.'))

    async def send_message(self, event):
        await self.send(text_data=event["action"])

    # HOW TO SEND MESSAGE TO A GROUP?? EASY!
    #
    # async_to_sync(channel_layer.group_send)(
    #                 WebsocketGroups.FARM,
    #                 {
    #                     "type": "send.message",
    #                     "action": Action,
    #                 }
    #             )

    @database_sync_to_async
    def has_perm(self, permission):
        return self.user.has_perm(permission)
