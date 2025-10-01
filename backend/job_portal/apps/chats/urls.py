from django.urls import path, include
from rest_framework.routers import DefaultRouter

from job_portal.apps.chats.api.views import ChatRoomAPIViewSet, ChatRoomMessageAPIViewSet

app_name = 'chats'

router = DefaultRouter()
router.register(r'api/v1/chats/rooms', ChatRoomAPIViewSet, basename='chat_room')
router.register("api/v1/chats/rooms/(?P<chat_room_id>[^/.]+)/messages", ChatRoomMessageAPIViewSet,
                basename="chat_room_message")

urlpatterns = [
    path('', include(router.urls)),
]
