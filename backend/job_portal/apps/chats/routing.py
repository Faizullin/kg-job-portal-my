from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # WebSocket endpoint for chat rooms
    # Format: ws://domain/ws/chat/{room_id}/?token={firebase_token}
    re_path(r'ws/chat/(?P<room_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]
