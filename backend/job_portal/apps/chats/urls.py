from django.urls import path
from .api.views import (
    WebSocketInfoApiView,
    ChatConversationListApiView, ChatConversationDetailApiView, ChatSendMessageApiView,
    ChatRoomCreateApiView, ChatRoomAddParticipantApiView
)

app_name = 'chat'

urlpatterns = [
    path('api/v1/chat/conversations/', ChatConversationListApiView.as_view(), name='chat-conversations'),
    path('api/v1/chat/conversations/create/', ChatRoomCreateApiView.as_view(), name='chat-room-create'),
    path('api/v1/chat/conversations/<int:pk>/', ChatConversationDetailApiView.as_view(), name='chat-conversation-detail'),
    path('api/v1/chat/conversations/<int:pk>/send/', ChatSendMessageApiView.as_view(), name='chat-send-message'),
    path('api/v1/chat/conversations/<int:pk>/add-participant/', ChatRoomAddParticipantApiView.as_view(), name='chat-add-participant'),
    
    # WebSocket connection information
    path('api/v1/chat/websocket-info/', WebSocketInfoApiView.as_view(), name='websocket-info'),
]
