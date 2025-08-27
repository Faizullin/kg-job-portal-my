from django.urls import path
from .api.views import (
    ChatRoomApiView, ChatRoomDetailApiView, ChatRoomCreateApiView, MessageApiView,
    MessageDetailApiView, MessageCreateApiView, ChatParticipantApiView,
    ChatParticipantCreateApiView, ChatAttachmentApiView, ChatAttachmentCreateApiView,
    ChatAttachmentDetailApiView, WebSocketInfoApiView
)

app_name = 'chat'

urlpatterns = [
    # Chat Rooms
    path('api/v1/chat/rooms/', ChatRoomApiView.as_view(), name='chat-rooms'),
    path('api/v1/chat/rooms/create/', ChatRoomCreateApiView.as_view(), name='chat-room-create'),
    path('api/v1/chat/rooms/<int:pk>/', ChatRoomDetailApiView.as_view(), name='chat-room-detail'),
    
    # Messages
    path('api/v1/chat/messages/', MessageApiView.as_view(), name='messages'),
    path('api/v1/chat/messages/create/', MessageCreateApiView.as_view(), name='message-create'),
    path('api/v1/chat/messages/<int:pk>/', MessageDetailApiView.as_view(), name='message-detail'),
    
    # Chat Participants
    path('api/v1/chat/participants/', ChatParticipantApiView.as_view(), name='participants'),
    path('api/v1/chat/participants/create/', ChatParticipantCreateApiView.as_view(), name='participant-create'),
    
    # Chat Attachments
    path('api/v1/chat/attachments/', ChatAttachmentApiView.as_view(), name='attachments'),
    path('api/v1/chat/attachments/create/', ChatAttachmentCreateApiView.as_view(), name='attachment-create'),
    path('api/v1/chat/attachments/<int:pk>/', ChatAttachmentDetailApiView.as_view(), name='attachment-detail'),
    
    # WebSocket connection information
    path('api/v1/chat/websocket-info/', WebSocketInfoApiView.as_view(), name='websocket-info'),
]
