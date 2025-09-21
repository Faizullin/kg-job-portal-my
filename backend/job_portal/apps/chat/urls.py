from django.urls import path
from .api.views import (
    WebSocketInfoApiView,
    ChatConversationListApiView, ChatConversationDetailApiView, ChatSendMessageApiView
)

app_name = 'chat'

urlpatterns = [
    # Mobile Chat Endpoints (Conversations = Chat Rooms)
    path('api/v1/chat/conversations/', ChatConversationListApiView.as_view(), name='chat-conversations'),
    path('api/v1/chat/conversations/<int:pk>/', ChatConversationDetailApiView.as_view(), name='chat-conversation-detail'),
    path('api/v1/chat/conversations/<int:pk>/send/', ChatSendMessageApiView.as_view(), name='chat-send-message'),
    
    # WebSocket connection information
    path('api/v1/chat/websocket-info/', WebSocketInfoApiView.as_view(), name='websocket-info'),
]
